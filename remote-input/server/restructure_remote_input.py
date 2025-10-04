#!/usr/bin/env python3
"""
Restructure this repository into the target 'remote-input' layout.

- Creates directories:
  remote-input/client
  remote-input/server
  remote-input/injectors/csharp-hid
  remote-input/injectors/cpp-pad

- Moves files with history preservation when possible:
  Uses `git mv -k` if Git is available, otherwise falls back to shutil.move.

- Move rules:
  *.html  -> remote-input/client/
  *.py    -> remote-input/server/
  *.cs/.csproj -> remote-input/injectors/csharp-hid/
  *.cpp   -> remote-input/injectors/cpp-pad/
  *.bat that mention 'cl' or 'ViGEm' -> remote-input/injectors/cpp-pad/

- Adds minimal scaffolding only if missing (never overwrites):
  - client/index.html
  - server/gateway.py, requirements.txt, config.json
  - injectors/csharp-hid/RemoteInput.HidInjector.csproj, Program.cs, KeyMap.cs
  - injectors/cpp-pad/injector_pad.cpp, build_pad.bat
  - injectors/README.md
  - Appends structure/quick-start to README.md (creates if missing)

Usage
  python restructure_remote_input.py
  python restructure_remote_input.py --branch chore/restructure-remote-input --commit
"""

from __future__ import annotations
import argparse
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple
import shutil as _shutil  # for which()

ROOT = Path.cwd()
EXCLUDE_DIRS = {"remote-input", ".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", "env"}

def run(cmd: List[str]) -> Tuple[bool, str]:
    """Run a command; return (ok, output). Never raise for missing executables."""
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=True)
        return True, (p.stdout or "").strip()
    except FileNotFoundError:
        return False, "executable-not-found"
    except subprocess.CalledProcessError as e:
        return False, (e.stderr or e.stdout or str(e))

def git_available() -> bool:
    return _shutil.which("git") is not None and run(["git", "--version"])[0]

def in_git_repo() -> bool:
    if not git_available():
        return False
    ok, _ = run(["git", "rev-parse", "--is-inside-work-tree"])
    return ok

def ensure_dirs() -> None:
    for p in [
        ROOT / "remote-input" / "client",
        ROOT / "remote-input" / "server",
        ROOT / "remote-input" / "injectors" / "csharp-hid",
        ROOT / "remote-input" / "injectors" / "cpp-pad",
    ]:
        p.mkdir(parents=True, exist_ok=True)

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def under_remote_input(p: Path) -> bool:
    # don't re-process anything already under remote-input
    try:
        (ROOT / "remote-input").resolve().relative_to(ROOT)
    except Exception:
        pass
    return "remote-input" in p.as_posix().split("/")

def discover(patterns: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for pat in patterns:
        for p in ROOT.rglob(pat):
            if not p.is_file():
                continue
            if any(d in p.parts for d in EXCLUDE_DIRS):
                continue
            out.append(p)
    return out

def git_mv(src: Path, dest: Path, allow_legacy_html: bool = False) -> Tuple[bool, str]:
    """Try git mv first (if available), otherwise shutil.move. Avoid overwrite; can rename *.html to *.legacy.html."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if allow_legacy_html and dest.suffix.lower() == ".html":
            # generate a unique .legacy.html name
            i = 0
            while True:
                candidate = dest.with_name(f"{dest.stem}.legacy{'' if i==0 else i}{dest.suffix}")
                if not candidate.exists():
                    dest = candidate
                    break
                i += 1
        else:
            return False, f"Conflict (exists): {rel(dest)}"

    if git_available():
        ok, _ = run(["git", "mv", "-k", str(src), str(dest)])
        if ok:
            return True, f"git mv {rel(src)} -> {rel(dest)}"
        # fall through if git mv failed

    # fallback: plain move (no history preservation)
    try:
        shutil.move(str(src), str(dest))
        return True, f"shutil.move {rel(src)} -> {rel(dest)}"
    except Exception as e:
        return False, f"Move failed {rel(src)} -> {rel(dest)}: {e}"

def write_if_missing(path: Path, content: str) -> Tuple[bool, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False, f"Skip (exists): {rel(path)}"
    path.write_text(content, encoding="utf-8", newline="\n")
    return True, f"Created: {rel(path)}"

# ---------- Minimal scaffolding (short strings to avoid quoting issues) ----------
INDEX_HTML = (
    "<!doctype html>\n"
    "<html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Remote Input Client</title></head>"
    "<body><h1>Remote Input Client</h1>"
    "<p>Keyboard/mouse/gamepad capture via WebRTC data channel.</p>"
    "<p>This is a minimal placeholder. Replace with your real UI.</p>"
    "</body></html>\n"
)

GATEWAY_PY = (
    'from aiohttp import web\n'
    'from aiortc import RTCPeerConnection\n'
    'import asyncio, json, os, socket\n'
    'from pathlib import Path\n\n'
    'ROOT = Path(__file__).resolve().parent\n'
    'CONFIG_PATH = ROOT / "config.json"\n'
    'UDP_KEYMOUSE_ADDR = ("127.0.0.1", 41234)\n'
    'UDP_GAMEPAD_ADDR = ("127.0.0.1", 41235)\n\n'
    'def load_config():\n'
    '    if CONFIG_PATH.exists():\n'
    '        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))\n'
    '    return {"keyboard": True, "mouse": True, "gamepad": False}\n\n'
    'def udp_sender(addr):\n'
    '    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n'
    '    sock.setblocking(False)\n'
    '    async def send(msg: dict):\n'
    '        data = (json.dumps(msg) + "\\n").encode("utf-8")\n'
    '        loop = asyncio.get_running_loop()\n'
    '        await loop.run_in_executor(None, sock.sendto, data, addr)\n'
    '    return send\n\n'
    'async def negotiate(request):\n'
    '    pc = RTCPeerConnection()\n'
    '    config = load_config()\n'
    '    send_hid = udp_sender(UDP_KEYMOUSE_ADDR)\n'
    '    send_pad = udp_sender(UDP_GAMEPAD_ADDR)\n'
    '    @pc.on("datachannel")\n'
    '    def on_datachannel(channel):\n'
    '        async def handle(message):\n'
    '            try:\n'
    '                if isinstance(message, (bytes, bytearray)):\n'
    '                    return\n'
    '                evt = json.loads(message)\n'
    '                t = evt.get("t")\n'
    '                if t == "key" and config.get("keyboard"): await send_hid(evt)\n'
    '                elif t == "mouse" and config.get("mouse"): await send_hid(evt)\n'
    '                elif t == "pad" and config.get("gamepad"): await send_pad(evt)\n'
    '            except Exception:\n'
    '                pass\n'
    '        @channel.on("message")\n'
    '        def on_message(m): asyncio.create_task(handle(m))\n'
    '    offer = await request.json()\n'
    '    await pc.setRemoteDescription(offer)\n'
    '    answer = await pc.createAnswer()\n'
    '    await pc.setLocalDescription(answer)\n'
    '    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})\n\n'
    'def make_app():\n'
    '    app = web.Application()\n'
    '    app.add_routes([web.post("/offer", negotiate)])\n'
    '    return app\n\n'
    'if __name__ == "__main__":\n'
    '    web.run_app(make_app(), host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8080")))\n'
)

SERVER_REQUIREMENTS = "aiortc==1.7.0\naiohttp==3.9.5\n"
SERVER_CONFIG = '{\n  "keyboard": true,\n  "mouse": true,\n  "gamepad": false\n}\n'

CS_PROJ = (
    '<Project Sdk="Microsoft.NET.Sdk">\n'
    '  <PropertyGroup>\n'
    '    <OutputType>Exe</OutputType>\n'
    '    <TargetFramework>net8.0</TargetFramework>\n'
    '    <ImplicitUsings>enable</ImplicitUsings>\n'
    '    <Nullable>enable</Nullable>\n'
    '  </PropertyGroup>\n'
    '  <ItemGroup>\n'
    '    <PackageReference Include="VirtualInput" Version="1.0.1" />\n'
    '  </ItemGroup>\n'
    '</Project>\n'
)

CS_PROGRAM = (
    'using System.Net.Sockets;\n'
    'using System.Text.Json;\n'
    'class Program{\n'
    '  static async Task Main(){\n'
    '    const int port=41234; using var udp=new UdpClient(port);\n'
    '    Console.WriteLine($"[HID] UDP {port}");\n'
    '    while(true){ var r=await udp.ReceiveAsync(); var txt=System.Text.Encoding.UTF8.GetString(r.Buffer).Trim();\n'
    '      foreach(var line in txt.Split("\\n", StringSplitOptions.RemoveEmptyEntries)){\n'
    '        try{ var root=JsonDocument.Parse(line).RootElement; var t=root.GetProperty("t").GetString();\n'
    '          if(t=="key") Console.WriteLine($"key {root.GetProperty("a").GetString()}");\n'
    '          else if(t=="mouse") Console.WriteLine($"mouse {root.GetProperty("a").GetString()}");\n'
    '        }catch{}\n'
    '      }\n'
    '    }\n'
    '  }\n'
    '}\n'
)

CS_KEYMAP = (
    "using System.Collections.Generic;\n"
    "public static class KeyMap{ public static readonly Dictionary<string,int> CodeToKey=new(){ /* fill */ }; }\n"
)

CPP_INJECTOR = (
    "#include <iostream>\n#include <winsock2.h>\n#include <ws2tcpip.h>\n"
    "#pragma comment(lib, \"ws2_32.lib\")\n"
    "int main(){\n"
    "  WSADATA w; if(WSAStartup(MAKEWORD(2,2), &w)!=0){std::cerr<<\"WSAStartup failed\\n\"; return 1;}\n"
    "  SOCKET s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP); if(s==INVALID_SOCKET){std::cerr<<\"socket failed\\n\";return 1;}\n"
    "  sockaddr_in a{}; a.sin_family=AF_INET; a.sin_port=htons(41235); a.sin_addr.s_addr=htonl(INADDR_ANY);\n"
    "  if(bind(s,(sockaddr*)&a,sizeof(a))==SOCKET_ERROR){std::cerr<<\"bind failed\\n\";return 1;}\n"
    "  std::cout<<\"[PAD] UDP 41235\"<<std::endl; char buf[8192];\n"
    "  while(true){int n=recv(s,buf,sizeof(buf),0); if(n>0){ std::string j(buf,n); std::cout<<\"[PAD] \"<<j<<std::endl; }}\n"
    "}\n"
)

CPP_BUILD = (
    "@echo off\r\n"
    "setlocal\r\n"
    "set VIGEM_INC=C:\\Vendors\\ViGEm\\include\r\n"
    "set VIGEM_LIB=C:\\Vendors\\ViGEm\\lib\r\n"
    "cl /std:c++20 /EHsc ^\r\n"
    "  /I \"%VIGEM_INC%\" ^\r\n"
    "  injector_pad.cpp ^\r\n"
    "  /link /LIBPATH:\"%VIGEM_LIB\" ViGEmClient.lib Ws2_32.lib\r\n"
    "endlocal\r\n"
)

INJECTORS_MD = (
    "# Injectors\n\n"
    "- csharp-hid: UDP 41234 (keyboard/mouse)\n"
    "- cpp-pad: UDP 41235 (gamepad via ViGEm; placeholder)\n"
)

README_SNIPPET = (
    "\n## Remote Input Delivery Pipeline structure\n\n"
    "remote-input/\n"
    "  client/index.html\n"
    "  server/{gateway.py, requirements.txt, config.json}\n"
    "  injectors/\n"
    "    csharp-hid/{RemoteInput.HidInjector.csproj, Program.cs, KeyMap.cs}\n"
    "    cpp-pad/{injector_pad.cpp, build_pad.bat}\n"
)

def append_or_create_readme() -> str:
    p = ROOT / "README.md"
    if p.exists():
        t = p.read_text(encoding="utf-8")
        if "Remote Input Delivery Pipeline structure" in t:
            return "README already contains structure section"
        p.write_text(t.rstrip() + "\n" + README_SNIPPET, encoding="utf-8")
        return "Appended structure/quick-start to README.md"
    else:
        p.write_text("# Remote Input Delivery Pipeline\n" + README_SNIPPET, encoding="utf-8")
        return "Created README.md"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="", help="Create/switch to branch before changes")
    ap.add_argument("--commit", action="store_true", help="Commit changes after restructuring")
    args = ap.parse_args()

    if args.branch and in_git_repo():
        ok, _ = run(["git", "checkout", "-b", args.branch])
        if not ok:
            run(["git", "checkout", args.branch])

    ensure_dirs()

    report, conflicts = [], []

    # Discover and move
    html = [p for p in discover(["*.html"]) if not under_remote_input(p)]
    py   = [p for p in discover(["*.py"])   if not under_remote_input(p)]
    cs   = [p for p in discover(["*.cs", "*.csproj"]) if not under_remote_input(p)]
    cpp  = [p for p in discover(["*.cpp"])  if not under_remote_input(p)]
    bats = []
    for p in discover(["*.bat"]):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            txt = ""
        if re.search(r"\bcl\b", txt, re.I) or re.search(r"ViGEm", txt, re.I):
            if not under_remote_input(p):
                bats.append(p)

    for f in html:
        ok, msg = git_mv(f, ROOT/"remote-input"/"client"/f.name, allow_legacy_html=True)
        (report if ok else conflicts).append(msg)
    for f in py:
        ok, msg = git_mv(f, ROOT/"remote-input"/"server"/f.name)
        (report if ok else conflicts).append(msg)
    for f in cs:
        ok, msg = git_mv(f, ROOT/"remote-input"/"injectors"/"csharp-hid"/f.name)
        (report if ok else conflicts).append(msg)
    for f in cpp:
        ok, msg = git_mv(f, ROOT/"remote-input"/"injectors"/"cpp-pad"/f.name)
        (report if ok else conflicts).append(msg)
    for f in bats:
        ok, msg = git_mv(f, ROOT/"remote-input"/"injectors"/"cpp-pad"/f.name)
        (report if ok else conflicts).append(msg)

    # Scaffolding
    files = {
        ROOT/"remote-input"/"client"/"index.html": INDEX_HTML,
        ROOT/"remote-input"/"server"/"gateway.py": GATEWAY_PY,
        ROOT/"remote-input"/"server"/"requirements.txt": SERVER_REQUIREMENTS,
        ROOT/"remote-input"/"server"/"config.json": SERVER_CONFIG,
        ROOT/"remote-input"/"injectors"/"csharp-hid"/"RemoteInput.HidInjector.csproj": CS_PROJ,
        ROOT/"remote-input"/"injectors"/"csharp-hid"/"Program.cs": CS_PROGRAM,
        ROOT/"remote-input"/"injectors"/"csharp-hid"/"KeyMap.cs": CS_KEYMAP,
        ROOT/"remote-input"/"injectors"/"cpp-pad"/"injector_pad.cpp": CPP_INJECTOR,
        ROOT/"remote-input"/"injectors"/"cpp-pad"/"build_pad.bat": CPP_BUILD,
        ROOT/"remote-input"/"injectors"/"README.md": INJECTORS_MD,
    }
    for path, content in files.items():
        _, msg = write_if_missing(path, content)
        report.append(msg)

    report.append(append_or_create_readme())

    if args.commit and in_git_repo():
        run(["git", "add", "-A"])
        ok, out = run(["git", "status", "--porcelain"])
        if ok and out.strip():
            run(["git", "commit", "-m", "chore: restructure into remote-input layout"])

    print("=== Restructure Summary ===")
    for m in report:
        print("-", m)
    if conflicts:
        print("\n=== Conflicts/Manual follow-ups ===")
        for m in conflicts:
            print("-", m)

if __name__ == "__main__":
    main()