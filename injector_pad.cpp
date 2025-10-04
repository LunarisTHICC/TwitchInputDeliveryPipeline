// injectors/injector_pad.cpp
// Build: see build_pad.bat (requires ViGEmClient)
#include <winsock2.h>
#include <windows.h>
#include <cstdint>
#include <vector>
#include <ViGEm/Client.h>

#pragma comment(lib, "ws2_32.lib")

int main() {
  WSADATA wsa; WSAStartup(MAKEWORD(2,2), &wsa);
  SOCKET s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK); addr.sin_port = htons(9998);
  bind(s, (sockaddr*)&addr, sizeof(addr));

  PVIGEM_CLIENT client = vigem_alloc();
  if (vigem_connect(client) != VIGEM_ERROR_NONE) return 1;
  PVIGEM_TARGET pad = vigem_target_x360_alloc();
  if (vigem_target_add(client, pad) != VIGEM_ERROR_NONE) return 2;

  XUSB_REPORT rep{}; // zero

  std::vector<uint8_t> buf(64);
  for (;;) {
    int len = recv(s, (char*)buf.data(), (int)buf.size(), 0);
    if (len < 2 || buf[0] != 1) continue;
    uint8_t t = buf[1];
    if (t == 0x10 && len >= (2 + 2*4 + 2 + 4)) {
      int16_t lx = *(int16_t*)&buf[2];
      int16_t ly = *(int16_t*)&buf[4];
      int16_t rx = *(int16_t*)&buf[6];
      int16_t ry = *(int16_t*)&buf[8];
      uint8_t lt = buf[10];
      uint8_t rt = buf[11];
      uint32_t buttons = *(uint32_t*)&buf[12];

      rep.sThumbLX = lx;
      rep.sThumbLY = ly;
      rep.sThumbRX = rx;
      rep.sThumbRY = ry;
      rep.bLeftTrigger = lt;
      rep.bRightTrigger = rt;

      rep.wButtons = 0;
      auto set = [&](int bit, WORD flag) { if (buttons & (1u<<bit)) rep.wButtons |= flag; };
      set(0, XUSB_GAMEPAD_A);
      set(1, XUSB_GAMEPAD_B);
      set(2, XUSB_GAMEPAD_X);
      set(3, XUSB_GAMEPAD_Y);
      set(4, XUSB_GAMEPAD_LEFT_SHOULDER);
      set(5, XUSB_GAMEPAD_RIGHT_SHOULDER);
      set(6, XUSB_GAMEPAD_BACK);
      set(7, XUSB_GAMEPAD_START);
      set(8, XUSB_GAMEPAD_LEFT_THUMB);
      set(9, XUSB_GAMEPAD_RIGHT_THUMB);
      set(10, XUSB_GAMEPAD_DPAD_UP);
      set(11, XUSB_GAMEPAD_DPAD_DOWN);
      set(12, XUSB_GAMEPAD_DPAD_LEFT);
      set(13, XUSB_GAMEPAD_DPAD_RIGHT);

      vigem_target_x360_update(client, pad, rep);
    }
  }

  // Cleanup (unreachable in this loop)
  // vigem_target_remove(client, pad);
  // vigem_target_free(pad);
  // vigem_disconnect(client);

  closesocket(s);
  WSACleanup();
  return 0;
}
