using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using VirtualInput;

namespace RemoteInput.HidInjector
{
    internal static class Program
    {
        static UdpClient udp;
        static VirtualKeyboard keyboard;
        static VirtualMouse mouse;

        static void Main(string[] args)
        {
            // Ensure STA for any input edge-cases
            var t = new Thread(Run) { IsBackground = false };
            t.SetApartmentState(ApartmentState.STA);
            t.Start();
            t.Join();
        }

        static void Run()
        {
            keyboard = new VirtualKeyboard();
            mouse = new VirtualMouse();

            udp = new UdpClient(9999);
            var ep = new IPEndPoint(IPAddress.Loopback, 0);
            Console.WriteLine("HID Injector listening on UDP 127.0.0.1:9999 (ver=0x01 packets)");

            while (true)
            {
                byte[] data = udp.Receive(ref ep);
                if (data == null || data.Length < 2) continue;
                if (data[0] != 0x01) continue; // version
                byte type = data[1];

                try
                {
                    switch (type)
                    {
                        case 0x01: // mouse move
                            if (data.Length >= 6)
                            {
                                short dx = BitConverter.ToInt16(data, 2);
                                short dy = BitConverter.ToInt16(data, 4);
                                // VirtualInput 1.0.1 mouse.Move uses relative pixels.
                                // If your build expects absolute, use MoveTo(curX+dx, curY+dy) instead.
                                mouse.Move(dx, dy);
                            }
                            break;

                        case 0x02: // mouse down
                            if (data.Length >= 3)
                            {
                                byte btn = data[2];
                                if (btn == 0) mouse.LeftDown();
                                else if (btn == 1) mouse.MiddleDown();
                                else if (btn == 2) mouse.RightDown();
                            }
                            break;

                        case 0x03: // mouse up
                            if (data.Length >= 3)
                            {
                                byte btn = data[2];
                                if (btn == 0) mouse.LeftUp();
                                else if (btn == 1) mouse.MiddleUp();
                                else if (btn == 2) mouse.RightUp();
                            }
                            break;

                        case 0x06: // mouse wheel
                            if (data.Length >= 4)
                            {
                                short dy = BitConverter.ToInt16(data, 2);
                                mouse.Wheel(dy);
                            }
                            break;

                        case 0x04: // key down
                        case 0x05: // key up
                            if (data.Length >= 3)
                            {
                                byte n = data[2];
                                if (3 + n <= data.Length)
                                {
                                    string code = Encoding.UTF8.GetString(data, 3, n);
                                    Keys k = KeyMap.MapCodeToKey(code);
                                    if (k != Keys.None)
                                    {
                                        if (type == 0x04) keyboard.KeyDown(k);
                                        else keyboard.KeyUp(k);
                                    }
                                }
                            }
                            break;

                        default:
                            // Ignore unknown types
                            break;
                    }
                }
                catch (Exception ex)
                {
                    // Keep injector resilient; log and continue
                    Console.WriteLine($"Inject error: {ex.Message}");
                }
            }
        }
    }
}
