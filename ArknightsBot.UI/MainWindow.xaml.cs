using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Threading;

namespace ArknightsBot.UI
{
    public partial class MainWindow : HandyControl.Controls.Window
    {
        private Process _botProcess;
        private int _farmCount = 0;

        // Đường dẫn file cài đặt
        private string _settingsPath;

        public MainWindow()
        {
            try
            {
                InitializeComponent();

                // Xác định đường dẫn file settings.json (nằm cùng chỗ với file Python)
                _settingsPath = Path.GetFullPath(@"..\ArknightsBot.Logic\settings.json");

                // Tải cài đặt lên giao diện
                LoadSettings();
            }
            catch (Exception ex)
            {
                MessageBox.Show("LỖI KHỞI ĐỘNG:\n" + ex.ToString());
            }
        }

        // --- CODE XỬ LÝ SETTINGS MỚI ---
        // 1. Sửa hàm LoadSettings
        private void LoadSettings()
        {
            if (File.Exists(_settingsPath))
            {
                try
                {
                    string json = File.ReadAllText(_settingsPath);

                    // Đọc chuỗi ADB (Mới)
                    txtAdbAddress.Text = ParseJsonString(json, "adb_address", "127.0.0.1:7555");

                    // Đọc các số Delay (Cũ)
                    numStart.Value = ParseJsonValue(json, "delay_start", 2.0);
                    numSquad.Value = ParseJsonValue(json, "delay_squad", 5.0);
                    numSettings.Value = ParseJsonValue(json, "delay_settings", 2.0);
                    numRetreat.Value = ParseJsonValue(json, "delay_retreat", 1.5);
                    numConfirm.Value = ParseJsonValue(json, "delay_confirm", 4.0);
                }
                catch { }
            }
        }

        // 2. Sửa hàm BtnSave_Click
        private void BtnSave_Click(object sender, RoutedEventArgs e)
        {
            // Lưu chuỗi JSON (Chú ý cú pháp có dấu ngoặc kép cho chuỗi)
            string json = "{\n";
            json += $"  \"adb_address\": \"{txtAdbAddress.Text}\",\n"; // MỚI
            json += $"  \"delay_start\": {numStart.Value},\n";
            json += $"  \"delay_squad\": {numSquad.Value},\n";
            json += $"  \"delay_settings\": {numSettings.Value},\n";
            json += $"  \"delay_retreat\": {numRetreat.Value},\n";
            json += $"  \"delay_confirm\": {numConfirm.Value}\n";
            json += "}";

            try
            {
                File.WriteAllText(_settingsPath, json);
                HandyControl.Controls.Growl.Success("Đã lưu cấu hình thành công!");
            }
            catch (Exception ex)
            {
                MessageBox.Show("Lỗi lưu file: " + ex.Message);
            }
        }

        // 3. THÊM hàm ParseJsonString (Vì logic đọc chuỗi khác đọc số)
        private string ParseJsonString(string json, string key, string defaultValue)
        {
            try
            {
                int keyIndex = json.IndexOf($"\"{key}\"");
                if (keyIndex == -1) return defaultValue;

                int colonIndex = json.IndexOf(':', keyIndex);

                // Tìm dấu nháy kép mở đầu giá trị
                int startQuote = json.IndexOf('"', colonIndex);
                if (startQuote == -1) return defaultValue;

                // Tìm dấu nháy kép kết thúc
                int endQuote = json.IndexOf('"', startQuote + 1);
                if (endQuote == -1) return defaultValue;

                return json.Substring(startQuote + 1, endQuote - startQuote - 1);
            }
            catch { return defaultValue; }
        }

        private double ParseJsonValue(string json, string key, double defaultValue)
        {
            try
            {
                // Tìm chuỗi: "key": giá_trị
                int keyIndex = json.IndexOf($"\"{key}\"");
                if (keyIndex == -1) return defaultValue;

                int colonIndex = json.IndexOf(':', keyIndex);
                int commaIndex = json.IndexOf(',', colonIndex);
                if (commaIndex == -1) commaIndex = json.IndexOf('}', colonIndex);

                string valueStr = json.Substring(colonIndex + 1, commaIndex - colonIndex - 1).Trim();
                return double.Parse(valueStr, System.Globalization.CultureInfo.InvariantCulture);
            }
            catch { return defaultValue; }
        }

        // ---------------------------------

        private void BtnStart_Click(object sender, RoutedEventArgs e)
        {
            txtLog.AppendText(">>> Đang khởi động Bot...\n");

            // 1. Đường dẫn file .exe Python (Nằm cùng thư mục với file UI)
            string botExePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ArknightsBot.Logic.exe");

            if (!File.Exists(botExePath))
            {
                MessageBox.Show("Không tìm thấy file 'ArknightsBot.Logic.exe'!\nHãy đảm bảo bạn đã copy nó vào cùng thư mục.");
                return;
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = botExePath,      // Gọi thẳng file EXE
                Arguments = "",             // Không cần tham số script nữa
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,      // Ẩn cửa sổ đen console
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                StandardErrorEncoding = System.Text.Encoding.UTF8
            };

            _botProcess = new Process { StartInfo = startInfo };
            // ... (Phần gán sự kiện và Start giữ nguyên) ...
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
            btnStart.IsEnabled = true; btnStop.IsEnabled = false;
        }

        private void Bot_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (string.IsNullOrEmpty(e.Data)) return;
            this.Dispatcher.Invoke(() =>
            {
                if (e.Data.Contains("[STATS]")) { _farmCount++; lblCounter.Text = _farmCount.ToString(); }
                txtLog.AppendText(e.Data + "\n");
                txtLog.ScrollToEnd();
            });
        }

        protected override void OnClosed(EventArgs e)
        {
            if (btnStop.IsEnabled) BtnStop_Click(null, null);
            base.OnClosed(e);
        }
    }
}