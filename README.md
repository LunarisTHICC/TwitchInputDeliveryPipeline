# TwitchInputDeliveryPipeline
# 🎮 Remote Input System (Keyboard + Mouse + Gamepad)

A low-latency system for injecting remote keyboard, mouse, and gamepad input into a host machine.  
Viewers interact via a browser, their inputs are sent over WebRTC, and the host injects them using **VirtualInput** (keyboard + mouse) and **ViGEm** (gamepad).

---

## 🧩 Components

### 1. `client/index.html`
- Captures **mouse**, **keyboard**, and **gamepad** input from viewers.
- Sends inputs over a **WebRTC DataChannel** (`unordered`, `unreliable`).
- Receives **capability updates** from the host (e.g., disable mouse).

### 2. `server/gateway.py`
- Handles **WebRTC signaling** and **input routing**.
- Forwards packets to:
  - **HID injector (C#)** → UDP `127.0.0.1:9999`
  - **Gamepad injector (C++)** → UDP `127.0.0.1:9998`
- Provides a **toggle API** (`/toggle`) to enable/disable input types live.

### 3. `injectors/csharp-hid`
- C# console app using [VirtualInput 1.0.1](https://github.com/SaqibS/VirtualInput).
- Injects **keyboard** and **mouse** input via `VirtualKeyboard` and `VirtualMouse`.
- Listens on UDP port **9999**.

### 4. `injectors/cpp-pad`
- C++ injector using **ViGEmClient**.
- Emulates an **Xbox 360 controller** via ViGEmBus.
- Listens on UDP port **9998**.

---

## 🚀 Setup Instructions

### Prerequisites
- **Windows 10/11**
- **Python 3.10+**
- **ViGEmBus installed** → [vigem.org](https://vigem.org)
- **.NET Framework 4.8 SDK** (for HID injector)
- **VirtualInput 1.0.1 NuGet package**

---

### 1. Install Python server
```bash
cd server
pip install -r requirements.txt
python gateway.py
