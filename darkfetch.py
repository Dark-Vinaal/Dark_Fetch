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
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    parts = line.split("=", 1)
                    if len(parts) > 1:
                        return parts[1].strip().strip('\'"')
    except Exception:
        pass
    if platform.system() == "Darwin":
        try:
            prod_name = subprocess.check_output(["sw_vers", "-productName"], stderr=subprocess.DEVNULL).decode().strip()
            prod_ver = subprocess.check_output(["sw_vers", "-productVersion"], stderr=subprocess.DEVNULL).decode().strip()
            return f"{prod_name} {prod_ver}"
        except Exception:
            try:
                return f"macOS {platform.mac_ver()[0]}"
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
    shell = os.environ.get("SHELL", "")
    if not shell:
        return "N/A"
    name = os.path.basename(shell)
    try:
        result = subprocess.run(
            [shell, "--version"], capture_output=True, text=True, timeout=2
        )
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
    # 1. Try TERM_PROGRAM first
    term_program = os.environ.get("TERM_PROGRAM")
    if term_program:
        return term_program
    # 2. Try inspecting parent process using psutil
    if HAS_PSUTIL:
        try:
            parent = psutil.Process().parent()
            while parent:
                pname = parent.name()
                if pname.lower() not in ("bash", "zsh", "fish", "sh", "python", "python3", "sudo", "systemd", "init"):
                    return pname
                parent = parent.parent()
        except Exception:
            pass
    # 3. Fallback to TERM or COLORTERM
    for var in ("TERM", "COLORTERM"):
        val = os.environ.get(var)
        if val:
            return val
    return "N/A"

def get_packages():
    managers = {
        "pacman": ["pacman", "-Q"],
        "apt":    ["dpkg", "--list"],
        "pip":    [sys.executable, "-m", "pip", "list"],
    }
    results = []
    for name, cmd in managers.items():
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=3)
            lines = out.decode().strip().splitlines()
            if name == "apt":
                count = max(0, len(lines) - 5)
            elif name == "pip":
                count = max(0, len(lines) - 2)
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
        if platform.system() == "Darwin":
            name = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL).decode().strip()
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
    usage   = psutil.cpu_percent(interval=0.4)
    return name, cores, threads, usage

def get_ram():
    if HAS_PSUTIL:
        vm = psutil.virtual_memory()
        return vm.used, vm.total, vm.percent
    # Fallback for Linux
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
        sw = psutil.swap_memory()
        return sw.used, sw.total, sw.percent
    # Fallback for Linux
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

def get_disk():
    if HAS_PSUTIL:
        du = psutil.disk_usage("/")
        return du.used, du.total, du.percent
    # Fallback for Unix/Linux
    try:
        st = os.statvfs("/")
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
    try:
        result = subprocess.check_output(
            ["lspci"], stderr=subprocess.DEVNULL, timeout=3
        ).decode()
        gpus = []
        for line in result.splitlines():
            if "VGA" in line or "3D" in line or "Display" in line:
                gpus.append(line.split(":")[-1].strip()[:70])
        if gpus:
            return None, "  │  ".join(gpus)
    except Exception:
        pass
    return None, "N/A  (install GPUtil for NVIDIA details)"

def get_battery():
    if not HAS_PSUTIL:
        return None
    try:
        batt = psutil.sensors_battery()
        if batt is None:
            return None
        status = "Charging" if batt.power_plugged else "Discharging"
        bar    = ascii_bar(batt.percent, 100)
        return batt.percent, f"[{bar}]  {batt.percent:.0f}%  [{status}]"
    except Exception:
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
        
    if disk_total > 0:
        info["Disk (/)"] = (disk_pct, f"[{ascii_bar(disk_used, disk_total)}]  {format_bytes(disk_used)} / {format_bytes(disk_total)}  ({disk_pct:.0f}%)")
    else:
        info["Disk (/)"] = "N/A"
        
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