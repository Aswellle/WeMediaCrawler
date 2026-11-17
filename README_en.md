# 🔥 WeMediaCrawler - Social Media Platform Crawler 🕷️

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/Aswellle/WeMediaCrawler?style=social)](https://github.com/Aswellle/WeMediaCrawler/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Aswellle/WeMediaCrawler?style=social)](https://github.com/Aswellle/WeMediaCrawler/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Aswellle/WeMediaCrawler)](https://github.com/Aswellle/WeMediaCrawler/issues)
[![License](https://img.shields.io/badge/license-Non--Commercial%20Learning%201.1-blue)](LICENSE)
[![中文](https://img.shields.io/badge/🇨🇳_中文-Available-blue)](README.md)
[![English](https://img.shields.io/badge/🇺🇸_English-Current-green)](README_en.md)
[![Español](https://img.shields.io/badge/🇪🇸_Español-Available-green)](README_es.md)

</div>

---

> ### 🔗 Project Origin & Fork Declaration
>
> **This repository is a fork of [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler).**
>
> The original project was created and maintained by **[NanmiCoder (Programmer Jiang-Relakkes)](https://github.com/NanmiCoder)**, a highly-starred open-source multi-platform social media data collection project.
>
> This fork, maintained by **Aswellle**, delivers UI/UX improvements and feature enhancements on top of the original project, aiming to provide a modernized web interface and a better user experience while preserving the excellent architecture of the original project.
>
> **The copyright, license, and disclaimer of the original project belong to NanmiCoder/relakkes, while modifications added by this fork are the responsibility of Aswellle.** See the [Disclaimer](#disclaimer) section below for details.

---

> **⚠️ Disclaimer (Summary)**
>
> All content in this repository is for learning and research purposes only. Commercial use is prohibited. No person or organization may use the content of this repository for illegal purposes or to infringe upon the legitimate rights of others. For any legal liability arising from the use of this repository's content, the corresponding responsible party shall bear the liability according to their contributions.
>
> This repository is licensed under [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE), with original copyright belonging to relakkes@gmail.com.
>
> 👉 [Click to jump to the full disclaimer](#disclaimer)

---

## 📝 Branch Contributions

This fork introduces the following major changes on top of the original project:

- **Complete WebUI Redesign** — UI/UX overhaul of the `webui/` frontend, providing a more intuitive and modern operation interface
- **Interaction Experience Optimization** — Improved core workflows including crawler configuration, status monitoring, and log viewing
- **Feature Enhancements & Bug Fixes** — Multiple improvements while preserving the original architecture
- **Continuous Upstream Sync** — Follows upstream feature iterations and platform risk-control fixes, keeping the crawl pipeline aligned with upstream
- **Media & Data Readability** — Each media folder carries a one-line CSV summary of its content, so the owning post is identifiable while browsing files
- **Collection Controllability** — Root and sub-comments share a per-post quota; concurrency, rate limits and all collection switches take effect across the pipeline
- **Export Compatibility** — Fixed write failures on PostgreSQL strict typing for some platforms; every export format is consistently readable across platforms
- **Quality Assurance** — New regression matrices for media acquisition, export format × platform, and rate-limit/switch behavior, covering real database drivers and real audio/video muxing
- **AI-Agent Friendly** — Quick Start offers an end-to-end prompt you can hand to an AI coding assistant, from cloning to output without code changes

> All commits and change records of this branch can be viewed via the [GitHub commit history](https://github.com/Aswellle/WeMediaCrawler/commits/main).

---

## 📖 Project Introduction

A powerful **multi-platform social media data collection tool** that supports crawling public information from mainstream platforms including Xiaohongshu, Douyin, Kuaishou, Bilibili, Weibo, Tieba, Zhihu, and more.

### 🔧 Technical Principles

- **Core Technology**: Based on [Playwright](https://playwright.dev/) browser automation framework for login and maintaining login state
- **No JS Reverse Engineering Required**: Uses browser context environment with preserved login state to obtain signature parameters through JS expressions
- **Advantages**: No need to reverse complex encryption algorithms, significantly lowering the technical barrier

## ✨ Features

| Platform | Keyword Search | Specific Post ID Crawling | Secondary Comments | Specific Creator Homepage | Login State Cache | IP Proxy Pool | Generate Comment Word Cloud |
| ------ | ---------- | -------------- | -------- | -------------- | ---------- | -------- | -------------- |
| Xiaohongshu | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Douyin   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Kuaishou   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Bilibili   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Weibo   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Tieba   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Zhihu   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |

## 🚀 Quick Start

## 📋 Prerequisites

### 🚀 uv Installation (Recommended)

Before proceeding with the next steps, please ensure that uv is installed on your computer:

- **Installation Guide**: [uv Official Installation Guide](https://docs.astral.sh/uv/getting-started/installation)
- **Verify Installation**: Enter the command `uv --version` in the terminal. If the version number is displayed normally, the installation was successful
- **Recommendation Reason**: uv is currently the most powerful Python package management tool, with fast speed and accurate dependency resolution

### 🟢 Node.js Installation

The project depends on Node.js, please download and install from the official website:

- **Download Link**: https://nodejs.org/en/download/
- **Version Requirement**: >= 16.0.0

### 📦 Python Package Installation

```shell
# Enter project directory
cd WeMediaCrawler

# Use uv sync command to ensure consistency of python version and related dependency packages
uv sync
```

### 🌐 Browser Driver Installation (Optional)

> If using the default CDP mode (connecting to an existing Chrome browser), **no browser driver installation is required**. Installation is only needed when using standard Playwright mode.

```shell
# Install browser driver only when in standard Playwright mode
uv run playwright install
```

### 🌍 Chrome Browser Configuration (Recommended)

The project uses CDP mode by default to connect to the user's existing Chrome browser, which can reuse the browser's existing login state, cookies, extensions, etc., **significantly reducing the risk of platform anti-bot detection**.

Before using:

1. **Install the latest version of Chrome browser** (version >= 144), [Download](https://www.google.com/chrome/)
2. **Enable remote debugging**: Type `chrome://inspect/#remote-debugging` in the Chrome address bar and check **"Allow remote debugging for this browser instance"**
3. The page displays `Server running at: 127.0.0.1:9222`, indicating it is ready

> 💡 **Tip**: After running the crawler, a confirmation dialog will appear in Chrome. Click "Accept" to proceed. The program will wait for user confirmation; complete the operation within 60 seconds.
>
> If you do not want to use CDP mode, you can set `ENABLE_CDP_MODE = False` in `config/base_config.py` to switch to standard Playwright mode.

## 🚀 Run Crawler Program

```shell
# View configuration items in config/base_config.py, with English comments available

# Read keywords from configuration file to search related posts and crawl post information and comments
uv run main.py --platform xhs --lt qrcode --type search

# Read specified post ID list from configuration file to get information and comment information of specified posts
uv run main.py --platform xhs --lt qrcode --type detail

# Open corresponding APP to scan QR code for login

# For other platform crawler usage examples, execute the following command to view
uv run main.py --help
```

### 🤖 One-Shot Usage via AI Agent (Recommended)

If you are using an AI coding assistant (Claude Code, Codex, Cursor, etc.), **there is no need to read this document line by line**: paste the prompt below to it (just fill in "local directory" and "collection target"), and the agent will start from scratch and handle the whole flow of "**cloning the repo → installing dependencies → preparing browser login state → (optionally) starting local services → running the crawl → verifying output → reporting**".

```text
You are the data collection engineer of this repository. Deploy and collect from scratch, with single concurrency and small scale, collecting public data only.

[Phase 0: clone the online repo into a local directory]
1. Clone the repository into my specified local directory (create parent dirs if missing):
   git clone https://github.com/Aswellle/WeMediaCrawler.git "<my local directory>"
   cd "<my local directory>"
2. Install Python dependencies (the project uses uv; if uv is missing, first install it per
   https://docs.astral.sh/uv/getting-started/installation):
   uv sync
3. Only if I want the non-CDP Playwright mode, also run uv run playwright install; the default CDP mode skips it.

[Phase 1: prepare browser and login state]
4. The default CDP mode requires Chrome >= 144: open chrome://inspect/#remote-debugging in Chrome,
   enable "Allow remote debugging for this browser instance"; the page shows 127.0.0.1:9222 when ready.
   When the first run needs a QR login, ask me to scan the QR code / accept the browser dialog manually; do not interrupt me otherwise.

[Phase 2: run the collection (no source edits; all via CLI parameters)]
5. First read config/base_config.py (all switches have Chinese comments) and the output of `uv run main.py --help`, then run:
   My collection target: platform=xhs/dy/ks/bili/wb/tieba/zhihu, keyword or content ID="<fill in here>",
   data needed: post content / comments / media files (specify as needed).
   Example (replace parameters with my target):
   uv run main.py --platform xhs --lt qrcode --type search --keywords "food" \
     --crawler_max_notes_count 20 --get_comment true --get_sub_comment true \
     --get_media true --max_comments_count_singlenotes 20 --max_concurrency_num 1 \
     --save_data_option csv --save_data_path ./data
   For specific posts: --type detail --specified_id "<post link or ID>"
   For creators: --type creator --creator_id "<profile link or ID>"

[Phase 3: start local services when a visual UI is needed (only if I want the WebUI)]
6. Terminal 1, start the backend API (the frontend dev server proxies /api to 8083, so use 8083 here):
   uv run uvicorn api.main:app --port 8083 --reload
   Terminal 2, start the frontend:
   cd webui && npm install && npm run dev
   Then open http://localhost:5173 ; backend health check is http://localhost:8083/api/env/check .
   If pure data collection is enough, skip this phase.
7. To let the API server host the built frontend: run cd webui && npm run build (output defaults to gh-pages-dist/),
   then copy the output into api/webui/, and start only uv run uvicorn api.main:app --port 8080 --reload ;
   open http://localhost:8080 .

[Phase 4: report and verify]
8. Report: file list under data/ with row/file counts, and spot-check sanitization
   (creator_hash is a 16-char hash, nicknames are masked).
9. If a captcha, access restriction, or platform risk-control notice appears, stop immediately and tell me; do not retry to bypass it.
```

**Why this saves effort**:

- **One prompt from zero to working**: cloning, dependency install, browser login state, service startup, parameter composition and output verification are all chained by the agent — you only provide the "local directory" and the "collection target";
- Every capability is a CLI flag (`--platform / --type / --keywords / --specified_id / --creator_id / --get_media / --get_comment / --get_sub_comment / --max_comments_count_singlenotes / --max_concurrency_num / --save_data_option / --save_data_path`); the agent can compose any crawl shape without touching code;
- Export format switches via `--save_data_option` (csv/excel/json/jsonl/sqlite/db/postgres/mongodb), and each media folder carries a `summary.csv` note summary for easy browsing;
- After the first QR login, the login state is kept in the browser, so later runs won't interrupt you;
- Pure data collection needs no local service at all; start the API + WebUI only when a UI is needed (Phase 3).

> ⚠️ **Compliance Reminder**: Collect public data at a small scale, and respect the target platform's terms and robots.txt; the project license is for learning and research purposes only.

> ⚠️ **Backend Service Reminder**: The following WebUI visual interface depends on the backend API service to run. Before first use, please **start the backend separately first** (when using the frontend dev server, use port 8083 to match the `/api` proxy target):
>
> ```shell
> uv run uvicorn api.main:app --port 8083 --reload
> ```
>
> After the backend starts successfully, open the WebUI interface (`http://localhost:5173/`). If the backend is not started, the page will call `/api/env/check` for an environment check on first visit and fail. At this point, you can click "Skip Check" to bypass it temporarily, but crawler functionality will be unavailable.

## 🖥️ WebUI Visual Operation Interface

WeMediaCrawler provides a web-based visual operation interface, allowing you to easily use crawler features without the command line.

#### Development (Recommended)

For development, you need to start both the backend API service and the frontend Vite dev server:

```shell
# Terminal 1: start API server (the frontend dev server proxies /api to 8083, so use 8083 here)
uv run uvicorn api.main:app --port 8083 --reload

# Terminal 2: start frontend dev server
cd webui
npm install
npm run dev        # starts on port 5173 and proxies /api to 8083
```

After successful startup, visit `http://localhost:5173/` to open the WebUI interface.

> On first launch, an environment check is performed (calls `/api/env/check`), so make sure the backend service is running. If the check fails, you can click "Skip Check" to bypass it temporarily.

#### Build for Production

If you want the API server to serve the WebUI static assets directly, build the frontend first:

```shell
cd webui
npm install
npm run build      # output goes to gh-pages-dist/
```

After building, copy the output into the directory served by the API server (`api/webui/`), then start the API server:

```shell
uv run uvicorn api.main:app --port 8080 --reload
```

After that, visit `http://localhost:8080`.

#### WebUI Features

- Visualize crawler parameter configuration (platform, login method, crawling type, etc.)
- Real-time view of crawler running status and logs
- Data preview and export

#### Interface Preview

| Overview Panel | Crawler Configuration |
| --- | --- |
| ![Overview Panel](docs/static/images/webui_overview.png) | ![Crawler Configuration](docs/static/images/webui_config.png) |

| Run Logs | <!-- Reserved --> |
| --- | --- |
| ![Run Logs](docs/static/images/webui_logs.png) | — |

## 💾 Data Storage

WeMediaCrawler supports multiple data storage methods, including CSV, JSON, JSONL, Excel, SQLite, and MySQL databases.

📖 **For detailed usage instructions, please see: [Data Storage Guide](docs/data_storage_guide.md)**

## 📚 References

- **Original Project Repository**: [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- **Xiaohongshu Sign Repository**: [Cloxl's xhs sign repository](https://github.com/Cloxl/xhshow)
- **Xiaohongshu Client**: [ReaJason's xhs repository](https://github.com/ReaJason/xhs)
- **SMS Forwarding**: [SmsForwarder reference repository](https://github.com/pppscn/SmsForwarder)
- **Intrusion Penetration Tool**: [ngrok official documentation](https://ngrok.com/docs/)

---
## ⭐ Support This Project

If WeMediaCrawler has been helpful to you, a ⭐️ Star would be much appreciated!

Every bit of support keeps me improving it.

---
# Disclaimer

This repository contains two disclaimers:
1. **Original Project Disclaimer** — Provided by NanmiCoder/relakkes, applicable to the original project code
2. **Fork Branch Disclaimer** — Provided by Aswellle, applicable to modifications in this fork

---

## I. Original Project Disclaimer

> The following disclaimer text is preserved from the [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) original project.
> Original copyright belongs to relakkes@gmail.com, licensed under [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE).

<div id="disclaimer">

### 1. Project Purpose and Nature
This project (hereinafter referred to as "this project") was created as a technical research and learning tool, aiming to explore and learn web data collection technology. This project focuses on data crawling technology research for social media platforms, intended for exchange and use by learners and researchers.

### 2. Legal Compliance Statement
The developer of this project (hereinafter referred to as "the developer") solemnly reminds users to strictly comply with relevant laws and regulations of the People's Republic of China when downloading, installing, and using this project, including but not limited to the "Cybersecurity Law of the People's Republic of China," the "Counter-Espionage Law of the People's Republic of China," and all applicable national laws and policies. Users shall bear all legal liabilities that may arise from the use of this project.

### 3. Intellectual Property Statement
The developer respects and protects the intellectual property rights of all parties. The source code and related content provided by this project are for technical exchange and learning purposes only. Users shall not use this project for any form of commercial activities or infringe upon the legal rights of others.

### 4. Disclaimer
The developer assumes no legal responsibility for any form of direct, indirect, incidental, special, or consequential damages arising from the use of this project. Users assume all risks of using this project.

### 5. User Responsibility
Users shall be responsible for their own actions when using this project and shall ensure that their use of this project complies with local laws and regulations. Users shall not use this project for any illegal activities.

### 6. Final Interpretation Rights
The right to interpret this disclaimer belongs to the original project developer. The disclaimer applies to the version obtained by users from this repository.

</div>

---

## II. Fork Branch Disclaimer

> This fork is maintained by **Aswellle** ([https://github.com/Aswellle/WeMediaCrawler](https://github.com/Aswellle/WeMediaCrawler)).

### 1. Nature of the Branch
This repository is an independent fork of [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler). This fork applies UI/UX improvements and feature enhancements on top of the original project (see the [Branch Contributions](#-branch-contributions) section above).

### 2. Division of Responsibility
- Copyright and responsibility for the **original project code** (crawler core logic, platform crawling implementations, storage layer, proxy/cache infrastructure, etc.) belong to the original author NanmiCoder/relakkes.
- **This fork's modifications** (WebUI redesign, interaction experience optimization, and all code added or modified in this branch) are the corresponding right and responsibility of Aswellle.
- Users of this fork should be aware that these modifications have not been reviewed by the original author, who bears no responsibility for them.

### 3. Usage Notice
- This fork is **for learning and research purposes only**. Commercial use or any illegal purpose is strictly prohibited.
- This fork is licensed under the original project's [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE); the terms of that license remain in effect for the fork as a whole.
- For any legal liability or loss arising from the use of this fork (including both original code and modifications), Aswellle bears responsibility only for the parts they modified and assumes no liability for direct or indirect damages.
- If modifications in this fork change the original project's architecture, users should assess the related risks themselves.

### 4. Intellectual Property Statement
Copyright of code added or modified in this fork belongs to Aswellle; copyright of the original project code remains with relakkes@gmail.com. Using this fork means you acknowledge and agree to all terms of this disclaimer and the original project license.

### 5. Feedback and Issues
- If an issue originates from **original project code**, please report it to [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler/issues).
- If an issue originates from **this fork's modifications** (WebUI, interaction experience, etc.), please report it via this repository's [Issues](https://github.com/Aswellle/WeMediaCrawler/issues).
