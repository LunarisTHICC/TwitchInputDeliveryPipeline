using System.Windows.Forms;

namespace RemoteInput.HidInjector
{
    internal static class KeyMap
    {
        public static Keys MapCodeToKey(string code) => code switch
        {
            // Letters
            "KeyA" => Keys.A, "KeyB" => Keys.B, "KeyC" => Keys.C, "KeyD" => Keys.D,
            "KeyE" => Keys.E, "KeyF" => Keys.F, "KeyG" => Keys.G, "KeyH" => Keys.H,
            "KeyI" => Keys.I, "KeyJ" => Keys.J, "KeyK" => Keys.K, "KeyL" => Keys.L,
            "KeyM" => Keys.M, "KeyN" => Keys.N, "KeyO" => Keys.O, "KeyP" => Keys.P,
            "KeyQ" => Keys.Q, "KeyR" => Keys.R, "KeyS" => Keys.S, "KeyT" => Keys.T,
            "KeyU" => Keys.U, "KeyV" => Keys.V, "KeyW" => Keys.W, "KeyX" => Keys.X,
            "KeyY" => Keys.Y, "KeyZ" => Keys.Z,

            // Top-row digits
            "Digit0" => Keys.D0, "Digit1" => Keys.D1, "Digit2" => Keys.D2,
            "Digit3" => Keys.D3, "Digit4" => Keys.D4, "Digit5" => Keys.D5,
            "Digit6" => Keys.D6, "Digit7" => Keys.D7, "Digit8" => Keys.D8,
            "Digit9" => Keys.D9,

            // Function keys
            "F1" => Keys.F1, "F2" => Keys.F2, "F3" => Keys.F3, "F4" => Keys.F4,
            "F5" => Keys.F5, "F6" => Keys.F6, "F7" => Keys.F7, "F8" => Keys.F8,
            "F9" => Keys.F9, "F10" => Keys.F10, "F11" => Keys.F11, "F12" => Keys.F12,
            "F13" => Keys.F13, "F14" => Keys.F14, "F15" => Keys.F15, "F16" => Keys.F16,
            "F17" => Keys.F17, "F18" => Keys.F18, "F19" => Keys.F19, "F20" => Keys.F20,
            "F21" => Keys.F21, "F22" => Keys.F22, "F23" => Keys.F23, "F24" => Keys.F24,

            // Modifiers
            "ShiftLeft" => Keys.LShiftKey, "ShiftRight" => Keys.RShiftKey,
            "ControlLeft" => Keys.LControlKey, "ControlRight" => Keys.RControlKey,
            "AltLeft" => Keys.LMenu, "AltRight" => Keys.RMenu,
            "MetaLeft" => Keys.LWin, "MetaRight" => Keys.RWin,

            // Navigation
            "ArrowUp" => Keys.Up, "ArrowDown" => Keys.Down,
            "ArrowLeft" => Keys.Left, "ArrowRight" => Keys.Right,
            "Home" => Keys.Home, "End" => Keys.End,
            "PageUp" => Keys.PageUp, "PageDown" => Keys.PageDown,
            "Insert" => Keys.Insert, "Delete" => Keys.Delete,

            // Editing
            "Backspace" => Keys.Back, "Tab" => Keys.Tab, "Enter" => Keys.Enter,
            "Escape" => Keys.Escape, "CapsLock" => Keys.CapsLock,

            // Symbols (US OEM)
            "Space" => Keys.Space,
            "Minus" => Keys.OemMinus, "Equal" => Keys.Oemplus,
            "BracketLeft" => Keys.OemOpenBrackets, "BracketRight" => Keys.Oem6,
            "Backslash" => Keys.Oem5, "Semicolon" => Keys.Oem1,
            "Quote" => Keys.Oem7, "Backquote" => Keys.Oem3,
            "Comma" => Keys.Oemcomma, "Period" => Keys.OemPeriod,
            "Slash" => Keys.OemQuestion,

            // Numpad
            "Numpad0" => Keys.NumPad0, "Numpad1" => Keys.NumPad1,
            "Numpad2" => Keys.NumPad2, "Numpad3" => Keys.NumPad3,
            "Numpad4" => Keys.NumPad4, "Numpad5" => Keys.NumPad5,
            "Numpad6" => Keys.NumPad6, "Numpad7" => Keys.NumPad7,
            "Numpad8" => Keys.NumPad8, "Numpad9" => Keys.NumPad9,
            "NumpadAdd" => Keys.Add, "NumpadSubtract" => Keys.Subtract,
            "NumpadMultiply" => Keys.Multiply, "NumpadDivide" => Keys.Divide,
            "NumpadDecimal" => Keys.Decimal, "NumpadEnter" => Keys.Enter,

            // Locks & misc
            "NumLock" => Keys.NumLock, "ScrollLock" => Keys.Scroll,
            "PrintScreen" => Keys.PrintScreen, "Pause" => Keys.Pause,

            // International (optional, best-effort)
            "IntlBackslash" => Keys.Oem5,      // often near Enter
            "IntlRo" => Keys.None,             // JP Ro key (no direct Keys mapping)
            "IntlYen" => Keys.None,            // JP Yen key (no direct Keys mapping)
            "KanaMode" => Keys.None,           // IME toggle (handled by IME)
            "NonConvert" => Keys.None,         // JP Muhenkan
            "Convert" => Keys.None,            // JP Henkan
            "HangulMode" => Keys.None, "Hanja" => Keys.None,

            _ => Keys.None
        };
    }
}
