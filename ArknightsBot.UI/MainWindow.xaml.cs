using System;
using System.Diagnostics;
using System.IO;
using System.Windows;

namespace ArknightsBot.UI
{
    public partial class MainWindow : HandyControl.Controls.Window
    {
        private Process _botProcess;
        private int _farmCount = 0;

        // Đường dẫn settings.json (nằm cùng thư mục với UI.exe)
        private readonly string _settingsPath;

        // Cờ phân biệt Manual Stop hay Bot tự sập
        private bool _isManualStop = false;

        public MainWindow()
        {
            try
            {
                InitializeComponent();

                _settingsPath = Path.Combine(
                    AppDomain.CurrentDomain.BaseDirectory,
                    "settings.json"
                );

                LoadSettings();
            }
            catch (Exception ex)
            {
                MessageBox.Show("LỖI KHỞI ĐỘNG UI:\n" + ex);
            }
        }

        #region SETTINGS (LOAD / SAVE)

        private void LoadSettings()
        {
            if (!File.Exists(_settingsPath)) return;

            try
            {
                string json = File.ReadAllText(_settingsPath);

                txtAdbAddress.Text = ParseJsonString(json, "adb_address", "127.0.0.1:7555");

                numStart.Value = ParseJsonValue(json, "delay_start", 2.0);
                numSquad.Value = ParseJsonValue(json, "delay_squad", 5.0);
                numSettings.Value = ParseJsonValue(json, "delay_settings", 2.0);
                numRetreat.Value = ParseJsonValue(json, "delay_retreat", 1.5);
                numConfirm.Value = ParseJsonValue(json, "delay_confirm", 4.0);
            }
            catch
            {
                // Bỏ qua nếu file lỗi format
            }
        }

        private void BtnSave_Click(object sender, RoutedEventArgs e)
        {
            string json =
$@"{{
  ""adb_address"": ""{txtAdbAddress.Text}"",
  ""delay_start"": {numStart.Value},
  ""delay_squad"": {numSquad.Value},
  ""delay_settings"": {numSettings.Value},
  ""delay_retreat"": {numRetreat.Value},
  ""delay_confirm"": {numConfirm.Value}
}}";

            try
            {
                File.WriteAllText(_settingsPath, json);
                HandyControl.Controls.Growl.Success("Đã lưu cấu hình!");
            }
            catch (Exception ex)
            {
                MessageBox.Show("Lỗi lưu settings.json:\n" + ex.Message);
            }
        }

        private string ParseJsonString(string json, string key, string defaultValue)
        {
            try
            {
                int keyIndex = json.IndexOf($"\"{key}\"");
                if (keyIndex < 0) return defaultValue;

                int start = json.IndexOf('"', json.IndexOf(':', keyIndex)) + 1;
                int end = json.IndexOf('"', start);

                return json.Substring(start, end - start);
            }
            catch { return defaultValue; }
        }

        private double ParseJsonValue(string json, string key, double defaultValue)
        {
            try
            {
                int keyIndex = json.IndexOf($"\"{key}\"");
                if (keyIndex < 0) return defaultValue;

                int colon = json.IndexOf(':', keyIndex);
                int comma = json.IndexOf(',', colon);
                if (comma < 0) comma = json.IndexOf('}', colon);

                string value = json.Substring(colon + 1, comma - colon - 1).Trim();
                return double.Parse(value, System.Globalization.CultureInfo.InvariantCulture);
            }
            catch { return defaultValue; }
        }

        #endregion

        #region START / STOP BOT (ĐÃ FIX)

        private void BtnStart_Click(object sender, RoutedEventArgs e)
        {
            _isManualStop = false;

            txtLog.AppendText(">>> Đang khởi động Bot...\n");

            string botExePath = Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                "ArknightsBot.Logic.exe"
            );

            if (!File.Exists(botExePath))
            {
                MessageBox.Show("Không tìm thấy ArknightsBot.Logic.exe");
                return;
            }

            _botProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = botExePath,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8
                },
                EnableRaisingEvents = true
            };

            _botProcess.OutputDataReceived += Bot_OutputDataReceived;
            _botProcess.ErrorDataReceived += Bot_OutputDataReceived;
            _botProcess.Exited += Bot_Exited;

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
                MessageBox.Show("Lỗi Start Bot:\n" + ex.Message);
            }
        }

        private void BtnStop_Click(object sender, RoutedEventArgs e)
        {
            _isManualStop = true;

            KillBotProcess();

            txtLog.AppendText(">>> ĐÃ DỪNG BOT (MANUAL STOP)\n");
            txtLog.ScrollToEnd();

            btnStart.IsEnabled = true;
            btnStop.IsEnabled = false;
        }

        private void Bot_Exited(object sender, EventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                if (_isManualStop) return;

                txtLog.AppendText("!!! BOT ĐÃ TẮT ĐỘT NGỘT !!!\n");
                txtLog.ScrollToEnd();

                btnStart.IsEnabled = true;
                btnStop.IsEnabled = false;
            });
        }

        private void KillBotProcess()
        {
            if (_botProcess == null || _botProcess.HasExited) return;

            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = "taskkill",
                    Arguments = $"/F /T /PID {_botProcess.Id}",
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
            }
            catch { }
            finally
            {
                _botProcess.Dispose();
                _botProcess = null;
            }
        }

        #endregion

        private void Bot_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (string.IsNullOrEmpty(e.Data)) return;

            Dispatcher.Invoke(() =>
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
            _isManualStop = true;
            KillBotProcess();
            base.OnClosed(e);
            Application.Current.Shutdown();
        }
    }
}
