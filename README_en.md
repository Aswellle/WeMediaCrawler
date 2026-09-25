# 🔥 MeitiCrawler - Social Media Platform Crawler 🕷️

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/Aswellle/MeitiCrawler?style=social)](https://github.com/Aswellle/MeitiCrawler/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Aswellle/MeitiCrawler?style=social)](https://github.com/Aswellle/MeitiCrawler/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Aswellle/MeitiCrawler)](https://github.com/Aswellle/MeitiCrawler/issues)
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

> All commits and change records of this branch can be viewed via [GitHub Compare View](https://github.com/NanmiCoder/MediaCrawler/compare...Aswellle:MeitiCrawler:main).

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
cd MeitiCrawler

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

> ⚠️ **Backend Service Reminder**: The following WebUI visual interface depends on the backend API service to run. Before first use, please **start the backend separately first**:
>
> ```shell
> uv run uvicorn api.main:app --port 8080 --reload
> ```
>
> After the backend starts successfully, open the WebUI interface (`http://localhost:5173/` or `http://localhost:8080`). If the backend is not started, the page will call `/api/env/check` for an environment check on first visit and fail. At this point, you can click "Skip Check" to bypass it temporarily, but crawler functionality will be unavailable.

## 🖥️ WebUI Visual Operation Interface

MeitiCrawler provides a web-based visual operation interface, allowing you to easily use crawler features without the command line.

#### Development (Recommended)

For development, you need to start both the backend API service and the frontend Vite dev server:

```shell
# Terminal 1: start API server (default port 8080)
uv run uvicorn api.main:app --port 8080 --reload

# Terminal 2: start frontend dev server
cd webui
npm install
npm run dev        # starts on port 5173 by default and proxies /api to 8080
```

After successful startup, visit `http://localhost:5173/` to open the WebUI interface.

> On first launch, an environment check is performed (calls `/api/env/check`), so make sure the backend service is running. If the check fails, you can click "Skip Check" to bypass it temporarily.

#### Build for Production

If you want the API server to serve the WebUI static assets directly, build the frontend first:

```shell
cd webui
npm install
npm run build      # outputs to api/webui/
```

Then start only the API server:

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


## 🔗 Using Python Native venv Environment Management (Not Recommended)

#### Create and activate Python virtual environment

> If crawling Douyin and Zhihu, you need to install nodejs environment in advance, version greater than or equal to: `16`

```shell
# Enter project root directory
cd MeitiCrawler

# Create virtual environment
# The libraries in requirements.txt are based on python 3.11
# If using other python versions, the libraries in requirements.txt may not be compatible, please resolve on your own
python -m venv venv

# macOS & Linux activate virtual environment
source venv/bin/activate

# Windows activate virtual environment
venv\Scripts\activate
```

#### Install dependency libraries

```shell
pip install -r requirements.txt
```

#### Install playwright browser driver

```shell
playwright install
```

#### Run crawler program (native environment)

```shell
# The project does not enable comment crawling mode by default. If you need comments, please modify the ENABLE_GET_COMMENTS variable in config/base_config.py
# Other supported options can also be viewed in config/base_config.py with comments

# Read keywords from configuration file to search related posts and crawl post information and comments
python main.py --platform xhs --lt qrcode --type search

# Read specified post ID list from configuration file to get information and comment information of specified posts
python main.py --platform xhs --lt qrcode --type detail

# Open corresponding APP to scan QR code for login

# For other platform crawler usage examples, execute the following command to view
python main.py --help
```



## 💾 Data Storage

MeitiCrawler supports multiple data storage methods, including CSV, JSON, JSONL, Excel, SQLite, and MySQL databases.

📖 **For detailed usage instructions, please see: [Data Storage Guide](docs/data_storage_guide.md)**


## 📚 References

- **Original Project Repository**: [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- **Xiaohongshu Sign Repository**: [Cloxl's xhs sign repository](https://github.com/Cloxl/xhshow)
- **Xiaohongshu Client**: [ReaJason's xhs repository](https://github.com/ReaJason/xhs)
- **SMS Forwarding**: [SmsForwarder reference repository](https://github.com/pppscn/SmsForwarder)
- **Intrusion Penetration Tool**: [ngrok official documentation](https://ngrok.com/docs/)


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

> The following disclaimer is provided by Aswellle for the modifications made in this fork branch (including but not limited to WebUI, interactive experience, etc.).

### 1. Scope of Modifications
This fork branch is modified by Aswellle based on the original project code. The scope of modifications includes the WebUI frontend, API backend logic, project structure optimization, and more.

### 2. Disclaimer for Modifications
Issues arising from modifications in this fork branch (including but not limited to code defects, functional abnormalities, data loss, etc.) are the responsibility of Aswellle. Users should evaluate the risks themselves when using this fork branch.

### 3. Copyright Notice
The copyright of the original project belongs to NanmiCoder/relakkes. The copyright of modifications made in this fork branch belongs to Aswellle. When distributing or using this fork branch, users shall retain the original project's copyright and modification copyright notices at the same time.

### 4. Issue Feedback
If you find issues originating from **modifications in this fork** (WebUI, interactive experience, etc.), please provide feedback via this repository's [Issues](https://github.com/Aswellle/MeitiCrawler/issues).
