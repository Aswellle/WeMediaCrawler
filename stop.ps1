# MediaCrawler 一键停止脚本
# 双击或在 PowerShell 中运行: .\stop.ps1

$backendPorts = @(9090, 8083)

foreach ($port in $backendPorts) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $procId = $conn.OwningProcess
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "  ✓ 关闭后端 (port $port, PID $procId)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ 关闭 port $port 失败: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  - port $port 未被占用，跳过" -ForegroundColor Gray
    }
}

Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
if ($?) { Write-Host "  ✓ 关闭 ngrok" -ForegroundColor Green } else { Write-Host "  - ngrok 未运行，跳过" -ForegroundColor Gray }

Write-Host "`n已清理完毕。" -ForegroundColor White