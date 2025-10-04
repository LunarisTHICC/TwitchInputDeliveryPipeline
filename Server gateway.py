# server/gateway.py
import asyncio, json, socket
from aiohttp import web
from aiortc import RTCPeerConnection

caps = {"keyboard": True, "mouse": True, "gamepad": True}
datachannels = []

HID_ADDR = ("127.0.0.1", 9999)
PAD_ADDR = ("127.0.0.1", 9998)
hid_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pad_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_caps(dc, caps_obj):
    blob = json.dumps({"type": "caps", "caps": caps_obj}).encode("utf-8")
    hdr = bytes([1, 0x20]) + len(blob).to_bytes(2, "little")
    try:
        dc.send(hdr + blob)
    except Exception:
        pass

def forward_hid(b: bytes):
    hid_sock.sendto(b, HID_ADDR)

def forward_pad(b: bytes):
    pad_sock.sendto(b, PAD_ADDR)

def handle_binary(b: bytes):
    if len(b) < 2 or b[0] != 1:
        return
    t = b[1]
    # Keyboard/mouse types
    if t in (0x01, 0x02, 0x03, 0x04, 0x05, 0x06):
        if (t in (0x04, 0x05) and not caps["keyboard"]) or (t in (0x01, 0x02, 0x03, 0x06) and not caps["mouse"]):
            return
        forward_hid(b)
    # Gamepad types
    elif t in (0x10, 0x11, 0x12):
        if not caps["gamepad"]:
            return
        forward_pad(b)

async def handle_offer(request):
    sdp = await request.text()
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_dc(dc):
        datachannels.append(dc)
        dc.on("open", lambda: send_caps(dc, caps))
        dc.on("message", lambda m: isinstance(m, bytes) and handle_binary(m))

    await pc.setRemoteDescription({"type": "offer", "sdp": sdp})
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.Response(text=pc.localDescription.sdp, content_type="application/sdp")

async def toggle_handler(request):
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)
    for k in ("keyboard", "mouse", "gamepad"):
        if k in body:
            caps[k] = bool(body[k])
    for dc in datachannels:
        if dc.readyState == "open":
            send_caps(dc, caps)
    return web.json_response(caps)

app = web.Application()
app.router.add_post("/signal/offer", handle_offer)
app.router.add_post("/toggle", toggle_handler)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
