from aiohttp import web
from aiortc import RTCPeerConnection
import asyncio, json, os, socket
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
UDP_KEYMOUSE_ADDR = ("127.0.0.1", 41234)
UDP_GAMEPAD_ADDR = ("127.0.0.1", 41235)

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"keyboard": True, "mouse": True, "gamepad": False}

def udp_sender(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    async def send(msg: dict):
        data = (json.dumps(msg) + "\n").encode("utf-8")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, sock.sendto, data, addr)
    return send

async def negotiate(request):
    pc = RTCPeerConnection()
    config = load_config()
    send_hid = udp_sender(UDP_KEYMOUSE_ADDR)
    send_pad = udp_sender(UDP_GAMEPAD_ADDR)
    @pc.on("datachannel")
    def on_datachannel(channel):
        async def handle(message):
            try:
                if isinstance(message, (bytes, bytearray)):
                    return
                evt = json.loads(message)
                t = evt.get("t")
                if t == "key" and config.get("keyboard"): await send_hid(evt)
                elif t == "mouse" and config.get("mouse"): await send_hid(evt)
                elif t == "pad" and config.get("gamepad"): await send_pad(evt)
            except Exception:
                pass
        @channel.on("message")
        def on_message(m): asyncio.create_task(handle(m))
    offer = await request.json()
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

def make_app():
    app = web.Application()
    app.add_routes([web.post("/offer", negotiate)])
    return app

if __name__ == "__main__":
    web.run_app(make_app(), host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8080")))
