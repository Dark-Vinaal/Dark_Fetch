import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
# Check common virtual environment locations
for venv_name in (".venv", "venv", os.path.join(".venv", "darkfetch")):
    _site = os.path.join(
        _here, venv_name, "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages"
    )
    if os.path.exists(_site):
        if _site not in sys.path:
            sys.path.insert(0, _site)
        break

import platform
import socket
import datetime
import subprocess
import shutil
import re

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from rich.console import Console
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"
IS_MACOS = SYSTEM == "Darwin"

BANNER = r"""
  ██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗███████╗████████╗ ██████╗██╗  ██╗
  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔════╝╚══██╔══╝██╔════╝██║  ██║
  ██║  ██║███████║██████╔╝█████╔╝     █████╗  █████╗     ██║   ██║     ███████║
  ██║  ██║██╔══██║██╔══██╗██╔═██╗     ██╔══╝  ██╔══╝     ██║   ██║     ██╔══██║
  ██████╔╝██║  ██║██║  ██║██║  ██╗    ██║     ███████╗   ██║   ╚██████╗██║  ██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
"""

BANNER_COLOR = "bright_red"
LABEL_COLOR  = "cyan"
VALUE_COLOR  = "white"
ACCENT_COLOR = "red"
DIM_COLOR    = "white"


def ascii_bar(used, total, width=20, fill="█", empty="░"):
    if total <= 0:
        return empty * width
    filled = max(0, min(width, int((used / total) * width)))
    return fill * filled + empty * (width - filled)

def format_bytes(n):
    if n <= 0:
        return "0.0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def bar_color(pct):
    if pct < 50:  return "green"
    if pct < 80:  return "yellow"
    return "red"

def get_os():
    if IS_WINDOWS:
        try:
            return f"Windows {platform.release()} {platform.version()}"
        except Exception:
            pass
    elif IS_MACOS:
        try:
            prod_name = subprocess.check_output(["sw_vers", "-productName"], stderr=subprocess.DEVNULL).decode().strip()
            prod_ver = subprocess.check_output(["sw_vers", "-productVersion"], stderr=subprocess.DEVNULL).decode().strip()
            return f"{prod_name} {prod_ver}"
        except Exception:
            try:
                return f"macOS {platform.mac_ver()[0]}"
            except Exception:
                pass
    else:
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        parts = line.split("=", 1)
                        if len(parts) > 1:
                            return parts[1].strip().strip('\'"')
        except Exception:
            pass
        if hasattr(platform, 'freedesktop_os_release'):
            try:
                release_info = platform.freedesktop_os_release()
                if 'PRETTY_NAME' in release_info:
                    return release_info['PRETTY_NAME']
            except Exception:
                pass
        try:
            out = subprocess.check_output(["lsb_release", "-ds"], stderr=subprocess.DEVNULL).decode().strip().strip('\'"')
            if out: return out
        except Exception:
            pass
            
    return f"{platform.system()} {platform.release()}"

def get_kernel():
    return f"{platform.system()} {platform.release()}"

def get_uptime():
    secs = None
    if HAS_PSUTIL:
        try:
            secs = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        except Exception:
            pass
    if secs is None:
        if IS_WINDOWS:
            try:
                import ctypes
                secs = int(getattr(ctypes, "windll").kernel32.GetTickCount64() / 1000)
            except Exception:
                pass
        elif IS_MACOS:
            try:
                out = subprocess.check_output(["sysctl", "-n", "kern.boottime"], stderr=subprocess.DEVNULL).decode()
                if "sec = " in out:
                    match = re.search(r"sec = (\d+)", out)
                    if match:
                        boot_time = int(match.group(1))
                        secs = int(datetime.datetime.now().timestamp() - boot_time)
            except Exception:
                pass
        else:
            try:
                with open("/proc/uptime", "r") as f:
                    secs = int(float(f.readline().split()[0]))
            except Exception:
                pass
                
    if secs is None or secs < 0:
        return "N/A"
    
    days, rem = divmod(secs, 86400)
    hrs,  rem = divmod(rem,  3600)
    mins, _   = divmod(rem,  60)
    parts = []
    if days: parts.append(f"{days}d")
    if hrs:  parts.append(f"{hrs}h")
    parts.append(f"{mins}m")
    return " ".join(parts)

def get_shell():
    if IS_WINDOWS:
        shell = os.environ.get("COMSPEC", "")
        if not shell:
            return "N/A"
    else:
        shell = os.environ.get("SHELL", "")
        if not shell:
            return "N/A"
            
    name = os.path.basename(shell).lower().replace('.exe', '')
    
    try:
        if name in ("powershell", "pwsh"):
            result = subprocess.run([shell, "-Command", "$PSVersionTable.PSVersion.ToString()"], capture_output=True, text=True, timeout=2)
            version = result.stdout.strip()
            if version: return f"{name} {version}"
            return name
            
        result = subprocess.run([shell, "--version"], capture_output=True, text=True, timeout=2)
        output = result.stdout or result.stderr
        if not output:
            return name
        first_line = output.splitlines()[0]
        words = first_line.split()
        version = ""
        if "version" in words:
            idx = words.index("version")
            if idx + 1 < len(words):
                version = words[idx + 1].strip("(),;")
        elif len(words) > 1:
            version = words[1].strip("(),;")
        
        return f"{name} {version}" if version else name
    except Exception:
        return name

def get_terminal():
    for term_env in ("WT_SESSION", "TERMINAL_EMULATOR", "TERM_PROGRAM"):
        val = os.environ.get(term_env)
        if val:
            if term_env == "WT_SESSION": return "Windows Terminal"
            return val
            
    for var in ("TERM", "COLORTERM"):
        val = os.environ.get(var)
        if val and val not in ("xterm-256color", "xterm", "linux", "dumb", "screen", "tmux"):
            return val

    if HAS_PSUTIL:
        try:
            parent = psutil.Process().parent()
            while parent:
                pname = parent.name()
                pname_lower = pname.lower()
                ignore_list = ("bash", "zsh", "fish", "sh", "python", "python3", "sudo", "systemd", "init", "cmd.exe", "powershell.exe", "pwsh.exe", "su", "sshd", "tmux", "screen")
                if pname_lower not in ignore_list and "python" not in pname_lower:
                    if pname_lower == "windowsterminal.exe":
                        return "Windows Terminal"
                    if pname_lower == "conhost.exe":
                        return "Command Prompt"
                    if pname_lower == "terminal.app":
                        return "Terminal.app"
                    return pname
                parent = parent.parent()
        except Exception:
            pass
            
    val = os.environ.get("TERM")
    if val: return val
    return "N/A"

def get_packages():
    managers = {}
    if IS_LINUX:
        managers = {
            "pacman": ["pacman", "-Q"],
            "yay": ["yay", "-Q"],
            "paru": ["paru", "-Q"],
            "apt": ["dpkg", "--list"],
            "dpkg": ["dpkg", "--list"],
            "dnf": ["dnf", "list", "installed"],
            "rpm": ["rpm", "-qa"],
            "zypper": ["zypper", "search", "--installed-only"],
            "xbps": ["xbps-query", "-l"],
            "apk": ["apk", "info"],
            "nix": ["nix-env", "-q"],
            "flatpak": ["flatpak", "list"],
            "snap": ["snap", "list"],
            "pip": [sys.executable, "-m", "pip", "list"],
        }
    elif IS_WINDOWS:
        managers = {
            "winget": ["winget", "list"],
            "choco": ["choco", "list", "--local-only"],
            "scoop": ["scoop", "list"],
            "pip": [sys.executable, "-m", "pip", "list"],
        }
    elif IS_MACOS:
        managers = {
            "brew": ["brew", "list"],
            "pip": [sys.executable, "-m", "pip", "list"],
        }

    results = []
    for name, cmd in managers.items():
        if not shutil.which(cmd[0]) and cmd[0] != sys.executable:
            continue
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=5)
            lines = out.decode().strip().splitlines()
            if name in ("apt", "dpkg"):
                count = max(0, len(lines) - 5)
            elif name == "pip":
                count = max(0, len(lines) - 2)
            elif name == "winget":
                count = len([l for l in lines if l.strip() and not l.startswith('-') and not l.startswith('Name') and "==" not in l])
            elif name == "snap":
                count = len([l for l in lines if l.strip() and not l.startswith('Name') and "No snaps" not in l])
            elif name == "flatpak":
                count = len([l for l in lines if l.strip() and not l.startswith('Name') and "No flatpaks" not in l])
            elif name == "brew":
                count = len([l for l in lines if l.strip() and "==" not in l])
            else:
                count = len(lines)
            if count > 0:
                results.append(f"{count} ({name})")
        except Exception:
            pass
    return "  ".join(results) if results else "N/A"

def get_cpu():
    name = "Unknown"
    try:
        if IS_MACOS:
            try:
                name = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL).decode().strip()
            except Exception:
                try:
                    name = subprocess.check_output(["sysctl", "-n", "hw.model"], stderr=subprocess.DEVNULL).decode().strip()
                except Exception:
                    name = platform.processor() or platform.machine()
        elif IS_WINDOWS:
            name = platform.processor()
            if not name:
                try:
                    out = subprocess.check_output(["powershell", "-Command", "(Get-CimInstance Win32_Processor).Name"], stderr=subprocess.DEVNULL, text=True, timeout=3).strip()
                    if out: name = out.splitlines()[0]
                except Exception:
                    pass
        else:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        name = line.split(":")[1].strip()
                        break
    except Exception:
        name = platform.processor() or platform.machine()
        
    if not HAS_PSUTIL:
        return name, "?", "?", 0.0
    cores   = psutil.cpu_count(logical=False) or "?"
    threads = psutil.cpu_count(logical=True)  or "?"
    try:
        usage = psutil.cpu_percent(interval=0.4)
    except Exception:
        usage = 0.0
    return name, cores, threads, usage

def get_ram():
    if HAS_PSUTIL:
        try:
            vm = psutil.virtual_memory()
            return vm.used, vm.total, vm.percent
        except Exception:
            pass
            
    if IS_WINDOWS:
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            getattr(ctypes, "windll").kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total = stat.ullTotalPhys
            available = stat.ullAvailPhys
            used = total - available
            percent = (used / total) * 100 if total > 0 else 0
            return used, total, percent
        except Exception:
            pass
    elif IS_MACOS:
        try:
            total = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
            return 0, total, 0.0
        except Exception:
            pass
    else:
        try:
            meminfo = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(":")] = int(parts[1]) * 1024
            total = meminfo.get("MemTotal", 0)
            if total > 0:
                available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
                used = max(0, total - available)
                percent = (used / total) * 100
                return used, total, percent
        except Exception:
            pass
    return 0, 0, 0

def get_swap():
    if HAS_PSUTIL:
        try:
            sw = psutil.swap_memory()
            return sw.used, sw.total, sw.percent
        except Exception:
            pass
            
    if IS_WINDOWS:
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            getattr(ctypes, "windll").kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total = max(0, stat.ullTotalPageFile - stat.ullTotalPhys)
            available = max(0, stat.ullAvailPageFile - stat.ullAvailPhys)
            used = total - available
            percent = (used / total) * 100 if total > 0 else 0
            return used, total, percent
        except Exception:
            pass
    elif IS_MACOS:
        try:
            out = subprocess.check_output(["sysctl", "-n", "vm.swapusage"]).decode()
            m_total = re.search(r"total = ([\d.]+)M", out)
            m_used = re.search(r"used = ([\d.]+)M", out)
            if m_total and m_used:
                total = float(m_total.group(1)) * 1024 * 1024
                used = float(m_used.group(1)) * 1024 * 1024
                percent = (used / total) * 100 if total > 0 else 0
                return used, total, percent
        except Exception:
            pass
    else:
        try:
            meminfo = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(":")] = int(parts[1]) * 1024
            total = meminfo.get("SwapTotal", 0)
            if total > 0:
                free = meminfo.get("SwapFree", 0)
                used = max(0, total - free)
                percent = (used / total) * 100
                return used, total, percent
        except Exception:
            pass
    return 0, 0, 0

def get_disk_root():
    if IS_WINDOWS:
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"

def get_disk_label():
    if IS_WINDOWS:
        return f"Disk ({os.environ.get('SystemDrive', 'C:')}\\)"
    return "Disk (/)"

def get_disk():
    root = get_disk_root()
    if HAS_PSUTIL:
        try:
            du = psutil.disk_usage(root)
            return du.used, du.total, du.percent
        except Exception:
            pass
    if IS_WINDOWS:
        try:
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            getattr(ctypes, "windll").kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(root), None, ctypes.byref(total_bytes), ctypes.byref(free_bytes))
            total = total_bytes.value
            free = free_bytes.value
            used = total - free
            percent = (used / total) * 100 if total > 0 else 0
            return used, total, percent
        except Exception:
            pass
    else:
        try:
            st = os.statvfs(root)
            total = st.f_blocks * st.f_frsize
            free = st.f_bfree * st.f_frsize
            used = total - free
            percent = (used / total) * 100 if total > 0 else 0
            return used, total, percent
        except Exception:
            pass
    return 0, 0, 0

def get_gpu():
    if HAS_GPUTIL:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                g   = gpus[0]
                pct = round((g.memoryUsed / g.memoryTotal) * 100) if g.memoryTotal else 0
                bar = ascii_bar(g.memoryUsed, g.memoryTotal)
                return g.name, f"{g.name}  [{bar}]  {g.memoryUsed:.0f} MB / {g.memoryTotal:.0f} MB  ({pct}%)"
        except Exception:
            pass
            
    gpus = []
    if IS_WINDOWS:
        try:
            out = subprocess.check_output(["powershell", "-Command", "(Get-CimInstance Win32_VideoController).Name"], text=True, timeout=5).strip()
            if out:
                gpus = [line.strip() for line in out.splitlines() if line.strip()]
        except Exception:
            pass
        if not gpus:
            try:
                out = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"], text=True, timeout=5).strip()
                lines = out.splitlines()
                if len(lines) > 1:
                    gpus = [line.strip() for line in lines[1:] if line.strip()]
            except Exception:
                pass
    elif IS_MACOS:
        try:
            out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True, timeout=5)
            for line in out.splitlines():
                if "Chipset Model:" in line:
                    gpus.append(line.split(":", 1)[1].strip())
        except Exception:
            pass
    else:
        if shutil.which("lspci"):
            try:
                result = subprocess.check_output(["lspci"], stderr=subprocess.DEVNULL, timeout=3).decode()
                for line in result.splitlines():
                    if "VGA" in line or "3D" in line or "Display" in line:
                        gpus.append(line.split(":")[-1].strip()[:70])
            except Exception:
                pass

    if gpus:
        return None, "  │  ".join(gpus)
    return None, "N/A"

def get_battery():
    if HAS_PSUTIL:
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                status = "Charging" if batt.power_plugged else "Discharging"
                bar    = ascii_bar(batt.percent, 100)
                return batt.percent, f"[{bar}]  {batt.percent:.0f}%  [{status}]"
        except Exception:
            pass
            
    if IS_MACOS:
        try:
            out = subprocess.check_output(["pmset", "-g", "batt"], text=True, timeout=2)
            m = re.search(r"(\d+)%;\s*(\w+)", out)
            if m:
                percent = float(m.group(1))
                status_raw = m.group(2).lower()
                status = "Charging" if "charg" in status_raw else "Discharging"
                bar = ascii_bar(percent, 100)
                return percent, f"[{bar}]  {percent:.0f}%  [{status}]"
        except Exception:
            pass
    elif IS_LINUX:
        try:
            batt_dir = None
            base_dir = "/sys/class/power_supply"
            if os.path.exists(base_dir):
                for d in os.listdir(base_dir):
                    if d.startswith("BAT"):
                        batt_dir = os.path.join(base_dir, d)
                        break
            if batt_dir and os.path.exists(batt_dir):
                with open(os.path.join(batt_dir, "capacity")) as f:
                    percent = float(f.read().strip())
                with open(os.path.join(batt_dir, "status")) as f:
                    status = f.read().strip()
                bar = ascii_bar(percent, 100)
                return percent, f"[{bar}]  {percent:.0f}%  [{status}]"
        except Exception:
            pass
            
    return None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"

def get_venv():
    venv  = os.environ.get("VIRTUAL_ENV")
    conda = os.environ.get("CONDA_DEFAULT_ENV")
    if venv:  return os.path.basename(venv)
    if conda: return conda
    return None

def get_locale():
    for var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        val = os.environ.get(var)
        if val:
            return val
    return "N/A"

def gather():
    cpu_name, cores, threads, cpu_pct = get_cpu()
    ram_used,  ram_total,  ram_pct    = get_ram()
    swap_used, swap_total, swap_pct   = get_swap()
    disk_used, disk_total, disk_pct   = get_disk()
    _, gpu_display                    = get_gpu()
    battery                           = get_battery()
    venv                              = get_venv()

    info: dict[str, str | tuple[float, str]] = {}
    info["OS"]        = get_os()
    info["Host"]      = platform.node()
    info["Kernel"]    = get_kernel()
    info["Arch"]      = platform.machine()
    info["Uptime"]    = get_uptime()
    info["Packages"]  = get_packages()
    info["Shell"]     = get_shell()
    info["Terminal"]  = get_terminal()
    info["Locale"]    = get_locale()
    info["CPU"]       = f"{cpu_name}  ({cores}c / {threads}t)"
    info["CPU Usage"] = (cpu_pct,  f"[{ascii_bar(cpu_pct, 100)}]  {cpu_pct:.1f}%")
    
    if ram_total > 0:
        info["RAM"]   = (ram_pct,  f"[{ascii_bar(ram_used, ram_total)}]  {format_bytes(ram_used)} / {format_bytes(ram_total)}  ({ram_pct:.0f}%)")
    else:
        info["RAM"]   = "N/A"
        
    if swap_total > 0:
        info["Swap"]  = (swap_pct, f"[{ascii_bar(swap_used, swap_total)}]  {format_bytes(swap_used)} / {format_bytes(swap_total)}  ({swap_pct:.0f}%)")
    else:
        info["Swap"]  = "N/A"
        
    disk_label = get_disk_label()
    if disk_total > 0:
        info[disk_label] = (disk_pct, f"[{ascii_bar(disk_used, disk_total)}]  {format_bytes(disk_used)} / {format_bytes(disk_total)}  ({disk_pct:.0f}%)")
    else:
        info[disk_label] = "N/A"
        
    info["GPU"]       = gpu_display
    if battery:
        info["Battery"] = battery
    info["Local IP"]  = get_local_ip()
    info["Python"]    = platform.python_version() + (f"  (venv: {venv})" if venv else "")

    return info

def render_rich(info):
    console   = Console()
    key_width = max(len(k) for k in info) + 2

    console.print(Text(BANNER, style=BANNER_COLOR))
    console.print(f"  [{DIM_COLOR}]{'─' * 72}[/{DIM_COLOR}]")
    console.print(
        f"  [{ACCENT_COLOR}]system information fetcher[/{ACCENT_COLOR}]"
        f"  [{DIM_COLOR}]│  DarkFetch v1.1  │  {platform.node()}[/{DIM_COLOR}]"
    )
    console.print(f"  [{DIM_COLOR}]{'─' * 72}[/{DIM_COLOR}]")
    console.print()

    for key, val in info.items():
        label = Text(f"  {key:<{key_width}}", style=LABEL_COLOR)
        sep   = Text("  ", style=DIM_COLOR)
        if isinstance(val, tuple):
            pct, display = val
            value = Text(display, style=bar_color(pct))
        else:
            value = Text(str(val), style=VALUE_COLOR)
        console.print(label + sep + value)

    console.print()
    console.print(f"  [{DIM_COLOR}]{'─' * 72}[/{DIM_COLOR}]")
    console.print()

def render_plain(info):
    print(BANNER)
    print("  " + "─" * 72)
    print(f"  system information fetcher  |  DarkFetch v1.1  |  {platform.node()}")
    print("  " + "─" * 72)
    print()
    key_width = max(len(k) for k in info) + 2
    for key, val in info.items():
        display = val[1] if isinstance(val, tuple) else str(val)
        print(f"  {key:<{key_width}}  {display}")
    print()
    print("  " + "─" * 72)
    print()

def main():
    info = gather()
    if HAS_RICH:
        render_rich(info)
    else:
        render_plain(info)
        print("  tip: pip install rich  →  enables colors")

if __name__ == "__main__":
    main()