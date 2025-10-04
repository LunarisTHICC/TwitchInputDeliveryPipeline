// injectors/injector_hid.cpp
// Build: see build_hid.bat
#include <winsock2.h>
#include <windows.h>
#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>
#include "virtualinput.hpp"

#pragma comment(lib, "ws2_32.lib")

static std::unordered_map<std::string, uint16_t> kCodeToUsage = {
  {"KeyA", 0x04}, {"KeyB", 0x05}, {"KeyC", 0x06}, {"KeyD", 0x07},
  {"KeyE", 0x08}, {"KeyF", 0x09}, {"KeyG", 0x0A}, {"KeyH", 0x0B},
  {"KeyI", 0x0C}, {"KeyJ", 0x0D}, {"KeyK", 0x0E}, {"KeyL", 0x0F},
  {"KeyM", 0x10}, {"KeyN", 0x11}, {"KeyO", 0x12}, {"KeyP", 0x13},
  {"KeyQ", 0x14}, {"KeyR", 0x15}, {"KeyS", 0x16}, {"KeyT", 0x17},
  {"KeyU", 0x18}, {"KeyV", 0x19}, {"KeyW", 0x1A}, {"KeyX", 0x1B},
  {"KeyY", 0x1C}, {"KeyZ", 0x1D},
  {"Digit1", 0x1E}, {"Digit2", 0x1F}, {"Digit3", 0x20}, {"Digit4", 0x21},
  {"Digit5", 0x22}, {"Digit6", 0x23}, {"Digit7", 0x24}, {"Digit8", 0x25},
  {"Digit9", 0x26}, {"Digit0", 0x27},
  {"Enter", 0x28}, {"Escape", 0x29}, {"Backspace", 0x2A}, {"Tab", 0x2B},
  {"Space", 0x2C},
  {"Minus", 0x2D}, {"Equal", 0x2E}, {"BracketLeft", 0x2F}, {"BracketRight", 0x30},
  {"Backslash", 0x31}, {"Semicolon", 0x33}, {"Quote", 0x34}, {"Backquote", 0x35},
  {"Comma", 0x36}, {"Period", 0x37}, {"Slash", 0x38},
  {"CapsLock", 0x39},
  {"F1", 0x3A}, {"F2", 0x3B}, {"F3", 0x3C}, {"F4", 0x3D}, {"F5", 0x3E}, {"F6", 0x3F},
  {"F7", 0x40}, {"F8", 0x41}, {"F9", 0x42}, {"F10", 0x43}, {"F11", 0x44}, {"F12", 0x45},
  {"PrintScreen", 0x46}, {"ScrollLock", 0x47}, {"Pause", 0x48},
  {"Insert", 0x49}, {"Home", 0x4A}, {"PageUp", 0x4B},
  {"Delete", 0x4C}, {"End", 0x4D}, {"PageDown", 0x4E},
  {"ArrowRight", 0x4F}, {"ArrowLeft", 0x50}, {"ArrowDown", 0x51}, {"ArrowUp", 0x52},
  {"ControlLeft", 0xE0}, {"ShiftLeft", 0xE1}, {"AltLeft", 0xE2}, {"MetaLeft", 0xE3},
  {"ControlRight", 0xE4}, {"ShiftRight", 0xE5}, {"AltRight", 0xE6}, {"MetaRight", 0xE7}
};

static uint16_t map_code(const std::string& code) {
  auto it = kCodeToUsage.find(code);
  return it == kCodeToUsage.end() ? 0 : it->second;
}

int main() {
  WSADATA wsa; WSAStartup(MAKEWORD(2,2), &wsa);
  SOCKET s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK); addr.sin_port = htons(9999);
  bind(s, (sockaddr*)&addr, sizeof(addr));

  if (!vi_init()) {
    OutputDebugStringA("VirtualInput init failed\n");
    // continue anyway to observe traffic; replace with exit(1) if you prefer
  }

  std::vector<uint8_t> buf(1024);
  for (;;) {
    int len = recv(s, (char*)buf.data(), (int)buf.size(), 0);
    if (len < 2 || buf[0] != 1) continue;
    uint8_t t = buf[1];
    if (t == 0x01 && len >= 6) {
      int16_t dx = *(int16_t*)&buf[2], dy = *(int16_t*)&buf[4];
      vi_mouse_move(dx, dy);
    } else if ((t == 0x02 || t == 0x03) && len >= 3) {
      uint8_t b = buf[2];
      if (t == 0x02) vi_mouse_down(b); else vi_mouse_up(b);
    } else if (t == 0x06 && len >= 4) {
      int16_t dy = *(int16_t*)&buf[2];
      vi_mouse_wheel(dy);
    } else if (t == 0x04 || t == 0x05) {
      if (len < 3) continue;
      uint8_t n = buf[2];
      if (3 + n > len) continue;
      std::string code((char*)&buf[3], n);
      uint16_t usage = map_code(code);
      if (usage) {
        if (t == 0x04) vi_key_down(usage);
        else vi_key_up(usage);
      }
    }
  }

  closesocket(s);
  WSACleanup();
  return 0;
}
