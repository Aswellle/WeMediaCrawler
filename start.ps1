# MediaCrawler 一键启动脚本
# 双击或在 PowerShell 中运行: .\start.ps1
# 可选: .\start.ps1 -Tunnel  额外建立 ngrok 公网隧道（默认不开启：
#       API 无认证，公网隧道意味着任何访客都能驱动爬虫/读取数据）

param(
    [switch]$Tunnel  # 显式开启 ngrok 隧道
)

# 项目根目录 = 本脚本所在目录（不再硬编码绝对路径）
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
# ngrok 可执行文件：默认从 PATH 查找，可用环境变量 MEDIACRAWLER_NGROK_EXE 指定完整路径
$ngrokExe = if ($env:MEDIACRAWLER_NGROK_EXE) { $env:MEDIACRAWLER_NGROK_EXE } else { "ngrok" }
# 后端端口须与 webui/vite.config.ts 的 /api 代理目标一致（8083）
$backendPort = 8083

# ── 1. 启动后端 API ──
Write-Host "[1/2] 启动后端 API (port $backendPort) ..." -ForegroundColor Cyan
$backend = Start-Process -FilePath "uv" -ArgumentList "run","uvicorn","api.main:app","--port","$backendPort","--reload" -WorkingDirectory $projectRoot -PassThru -WindowStyle Normal
Start-Sleep -Seconds 3

# 验证后端是否就绪
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$backendPort/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✓ 后端就绪: $($resp.Content)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 后端启动失败: $_" -ForegroundColor Red
    exit 1
}

# ── 2.（可选）启动 ngrok 隧道 ──
if ($Tunnel) {
    Write-Host "[2/2] 启动 ngrok 隧道 (→ localhost:$backendPort) ..." -ForegroundColor Cyan
    $ngrok = Start-Process -FilePath $ngrokExe -ArgumentList "http","$backendPort","--region=us" -PassThru -WindowStyle Normal
    Start-Sleep -Seconds 3

    # 从 ngrok API 获取公网 URL
    try {
        $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5
        $pubUrl = $tunnels.tunnels[0].public_url
        Write-Host "  ✓ ngrok 隧道已建立: $pubUrl" -ForegroundColor Green
        Write-Host "  ⚠ API 当前无认证，公网访客可驱动爬虫并读取采集数据，请自行评估风险" -ForegroundColor Yellow
    } catch {
        Write-Host "  ! ngrok 启动中，请稍候在 https://localhost:4040 查看" -ForegroundColor Yellow
    }
} else {
    Write-Host "[2/2] 跳过 ngrok 隧道（如需公网访问请运行: .\start.ps1 -Tunnel）" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "── 服务已启动 ──" -ForegroundColor White
Write-Host "  后端 API : http://localhost:$backendPort"
Write-Host "  API 文档 : http://localhost:$backendPort/docs"
Write-Host "  前端本地 : http://localhost:5173  (需另外执行: cd webui && npm run dev)"
if ($Tunnel) { Write-Host "  ngrok    : https://localhost:4040  (管理面板)" }
Write-Host ""
Write-Host "按 Ctrl+C 退出（后端和 ngrok 进程将继续运行，需手动关闭）" -ForegroundColor Gray

# 等待用户按任意键退出
Read-Host "按回车键退出此脚本"
