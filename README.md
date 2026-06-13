<div align="center">

![Banner](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-banner.svg)

<pre>
██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗███████╗████████╗ ██████╗██╗  ██╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔════╝╚══██╔══╝██╔════╝██║  ██║
██║  ██║███████║██████╔╝█████╔╝     █████╗  █████╗     ██║   ██║     ███████║
██║  ██║██╔══██║██╔══██╗██╔═██╗     ██╔══╝  ██╔══╝     ██║   ██║     ██╔══██║
██████╔╝██║  ██║██║  ██║██║  ██╗    ██║     ███████╗   ██║   ╚██████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
</pre>

<br>

<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&weight=700&size=24&duration=2500&pause=700&color=FF3131&center=true&vCenter=true&width=1000&lines=⚡+SYSTEM+SCAN+INITIALIZED...;🧠+Loading+Hardware+Modules...;🚀+Rendering+Terminal+Interface...;🌌+Welcome+To+DarkFetch" />

<br><br>

<img src="https://img.shields.io/badge/PYTHON-3.6+-FF3131?style=for-the-badge&labelColor=000000&logo=python"/>
<img src="https://img.shields.io/badge/STATUS-STABLE-FF3131?style=for-the-badge&labelColor=000000"/>
<img src="https://img.shields.io/badge/TERMINAL-FUTURISTIC-FF3131?style=for-the-badge&labelColor=000000"/>

<br><br>

<a href="https://github.com/Dark-Vinaal/Dark_Fetch">
  <img src="https://img.shields.io/badge/⚡_OPEN_REPOSITORY-1A0000?style=for-the-badge&logo=github&logoColor=FF3131"/>
</a>

</div>

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🌌 DarkFetch

> A futuristic Python-based system information fetch utility designed with modern terminal aesthetics, real-time hardware insights, and beautifully rendered output.

DarkFetch gathers:
- 🧠 Hardware Information
- ⚡ Resource Utilization
- 🌐 Network Details
- 🖥️ Software Environment Data
- 🚀 System Metrics

and displays them in a sleek cyberpunk-inspired terminal interface.

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## ✨ Features

<div align="center">

| ⚡ Feature | 🌌 Description |
|---|---|
| 🎨 Rich Terminal UI | Beautiful styling powered by `rich` |
| 🧠 Hardware Monitoring | CPU, RAM, Disk, GPU, Battery |
| 🌐 Network Detection | Local IP & system networking |
| 🐍 Python Environment Detection | Detects venv & Conda |
| 🖥️ OS & Shell Detection | Kernel, distro, shell, terminal |
| ⚛️ Dynamic Progress Bars | Modern resource indicators |
| 🚀 Automatic Fallback System | Works even without optional libs |
| 🛰️ Lightweight Architecture | Single optimized Python script |

</div>

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## ⚛️ System Architecture

```mermaid
graph TD

A[🚀 Start DarkFetch] --> B{🔍 Check Local Virtual Environment}

B -->|Found| C[📦 Insert site-packages into sys.path]
B -->|Not Found| D[⚡ Continue Initialization]

C --> E[🧠 Import Optional Libraries]
D --> E

E --> F[📊 Gather System Information]

F --> G[🖥️ CPU Metrics]
F --> H[💾 RAM Usage]
F --> I[🎮 GPU Detection]
F --> J[🌐 Network Information]
F --> K[🐍 Python Environment]
F --> L[⚡ Battery Status]

G --> M{🎨 Is Rich Installed?}

M -->|Yes| N[🌌 Render Futuristic UI]
M -->|No| O[📄 Render Plain Terminal Output]

N --> P[✅ Display Results]
O --> P
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🧠 Information Collected

```mermaid
graph LR

A[🖥️ DarkFetch] --> B[⚡ CPU]
A --> C[💾 RAM]
A --> D[🛰️ GPU]
A --> E[🌐 Network]
A --> F[🐍 Python]
A --> G[🖥️ Shell]
A --> H[🔋 Battery]
A --> I[💽 Disk]
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🎨 Design Philosophy

```txt
Minimal Terminal UI
        +
Cyberpunk Aesthetic
        +
Real-Time System Data
        +
Rich Styling
        +
Lightweight Python Architecture
        =
DARKFETCH
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🚀 Installation

### 📦 Clone Repository

```bash
git clone https://github.com/Dark-Vinaal/Dark_Fetch.git
cd Dark_Fetch
```

### 🐍 Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### ⚡ Install Recommended Dependencies

```bash
pip install rich psutil GPUtil
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 💻 Usage

### 🚀 Run DarkFetch

```bash
python darkfetch.py
```

> For Live preview, checkout the image attached below

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## ⚛️ Dependency Fallback System

- DarkFetch is designed to gracefully degrade functionality depending on installed libraries.

| Dependency | Purpose | Fallback |
|---|---|---|
| `rich` | Styled terminal rendering | Plain text mode |
| `psutil` | Hardware statistics | OS-level checks |
| `GPUtil` | Nvidia GPU detection | `lspci` GPU parsing |

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🛰️ Rendering Pipeline

```mermaid
sequenceDiagram

User->>DarkFetch: Run Program
DarkFetch->>System: Collect Hardware Data
System-->>DarkFetch: Return Metrics
DarkFetch->>Renderer: Format Output
Renderer->>Terminal: Display Futuristic UI
Terminal-->>User: Show System Dashboard
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 📂 Project Structure

```txt
📦 Dark_Fetch/
│
├── 🐍 darkfetch.py
├── 🖼️ assets/
├── 📄 README.md
├── ⚖️ LICENSE
└── 📦 requirements.txt
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🌌 Core Technologies

<div align="center">

<img src="https://skillicons.dev/icons?i=python,linux,bash,git,github,vscode"/>

</div>

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🧠 Supported Platforms

| Platform | Status |
|---|---|
| 🐧 Linux | ✅ Fully Supported |
| 🍎 macOS | ✅ Supported |
| 🪟 Windows | ⚠️ Partial Compatibility |

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 💻 Live Preview

<div align="center">

<img src="https://github.com/Dark-Vinaal/Dark_Fetch/blob/main/assets/darkfetch.png" width="100%"/>

</div>

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🌌 Inspiration

```mermaid
graph LR

A[🌌 Inspired By] --> B[🖥️ Neofetch]
A --> C[⚡ Fastfetch]
A --> D[🤖 Futuristic Terminal UIs]
A --> E[🌃 Cyberpunk Interfaces]
A --> F[🧠 System Monitoring Tools]
```

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🧠 Future Upgrades

- 🌌 Animated terminal rendering
- ⚛️ Better GPU telemetry
- 📊 Real-time monitoring mode
- 🛰️ Plugin architecture
- 🔥 Cross-platform optimization
- 🤖 Interactive dashboard mode

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 👨‍🚀 Developer

<div align="center">

# Vinaal R

### Creative Developer • Terminal UI Enthusiast • Futuristic Interface Explorer

<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&weight=700&size=20&duration=2500&pause=700&color=FF3131&center=true&vCenter=true&width=700&lines=⚡+Always+Building...;🚀+Always+Exploring...;🧠+Always+Optimizing..." />

</div>

![redline](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-line.svg)

## 🌐 Connect

<div align="center">

<a href="https://github.com/Dark-Vinaal">
  <img src="https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=00F7FF"/>
</a>

<a href="https://www.linkedin.com/in/vinaal">
  <img src="https://img.shields.io/badge/LinkedIn-000000?style=for-the-badge&logo=linkedin&logoColor=00F7FF"/>
</a>

![Footer](https://github.com/Dark-Vinaal/Dark-Vinaal/blob/main/Assets/red-footer.svg)

</div>
