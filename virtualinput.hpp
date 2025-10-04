// injectors/virtualinput.hpp
#pragma once
#include <cstdint>
#include <string>

// Replace these stubs with actual VirtualInput API calls and initialization.
// Make sure your VirtualInput driver is installed and the virtual devices are present.

inline bool vi_init() {
  // TODO: Initialize VirtualInput keyboard and mouse devices.
  return true;
}

inline void vi_mouse_move(int dx, int dy) {
  // TODO: Inject relative mouse movement via VirtualInput.
}

inline void vi_mouse_down(uint8_t button) {
  // TODO: Inject mouse button down (0=left,1=middle,2=right).
}

inline void vi_mouse_up(uint8_t button) {
  // TODO: Inject mouse button up (0=left,1=middle,2=right).
}

inline void vi_mouse_wheel(int dy) {
  // TODO: Inject vertical wheel delta.
}

inline void vi_key_down(uint16_t usage) {
  // TODO: Inject HID keyboard usage down.
}

inline void vi_key_up(uint16_t usage) {
  // TODO: Inject HID keyboard usage up.
}
