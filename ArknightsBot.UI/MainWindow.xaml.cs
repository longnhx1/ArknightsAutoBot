using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Threading;

namespace ArknightsBot.UI
{
    // FIX QUAN TRỌNG 1: Phải kế thừa từ HandyControl.Controls.Window
    public partial class MainWindow : HandyControl.Controls.Window
    {
        private Process _botProcess;
        private int _farmCount = 0;

        public MainWindow()
        {
            try
            {
                InitializeComponent();
            }
            catch (Exception ex)
            {
                MessageBox.Show("LỖI KHỞI ĐỘNG:\n" + ex.ToString());
            }
        }

        private void BtnStart_Click(object sender, RoutedEventArgs e)
        {
            txtLog.AppendText(">>> Đang khởi động Bot...\n");

            string scriptPath = Path.GetFullPath(@"D:\Auto\Arknights\Project\ArknightsAutoBot\ArknightsBot.Logic\ArknightsBot.Logic.py");

            if (!File.Exists(scriptPath))
            {
                MessageBox.Show("Không tìm thấy file Python!");
                return;
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                StandardErrorEncoding = System.Text.Encoding.UTF8
            };

            _botProcess = new Process { StartInfo = startInfo };
            _botProcess.OutputDataReceived += Bot_OutputDataReceived;
            _botProcess.ErrorDataReceived += Bot_OutputDataReceived;

            try
            {
                _botProcess.Start();
                _botProcess.BeginOutputReadLine();
                _botProcess.BeginErrorReadLine();

                btnStart.IsEnabled = false;
                btnStop.IsEnabled = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi khởi động: {ex.Message}");
            }
        }

        private void BtnStop_Click(object sender, RoutedEventArgs e)
        {
            if (_botProcess != null && !_botProcess.HasExited)
            {
                _botProcess.Kill();
                txtLog.AppendText(">>> ĐÃ DỪNG BOT.\n");
                txtLog.ScrollToEnd();
            }

            btnStart.IsEnabled = true;
            btnStop.IsEnabled = false;
        }

        private void Bot_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (string.IsNullOrEmpty(e.Data)) return;

            // FIX QUAN TRỌNG 2: Dùng this.Dispatcher thay vì Dispatcher class
            // Dispatcher là một thuộc tính của cửa sổ hiện tại
            this.Dispatcher.Invoke(() =>
            {
                if (e.Data.Contains("[STATS]"))
                {
                    _farmCount++;
                    lblCounter.Text = _farmCount.ToString();
                }

                txtLog.AppendText(e.Data + "\n");
                txtLog.ScrollToEnd();
            });
        }

        protected override void OnClosed(EventArgs e)
        {
            if (btnStop.IsEnabled)
            {
                BtnStop_Click(null, null);
            }
            base.OnClosed(e);
        }
    }
}