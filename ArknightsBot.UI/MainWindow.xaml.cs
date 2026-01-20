using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json; // Dùng để lưu file cấu hình xịn
using System.Windows;
using System.Windows.Forms; // Dùng cho FolderBrowserDialog
using Application = System.Windows.Application;
using MessageBox = System.Windows.MessageBox; // Fix lỗi xung đột MessageBox

namespace ArknightsBot.UI
{
    public partial class MainWindow : System.Windows.Window // Hoặc HandyControl.Controls.Window tùy project của bạn
    {
        private Process? _botProcess;
        private readonly string _settingsPath;
        private bool _isManualStop = false;

        public MainWindow()
        {
            InitializeComponent();

            // Đường dẫn file settings.json nằm cùng thư mục file exe
            _settingsPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "settings.json");

            LoadSettings();
        }

        #region 1. XỬ LÝ CẤU HÌNH (LOAD / SAVE)

        private void LoadSettings()
        {
            if (!File.Exists(_settingsPath)) return;

            try
            {
                string json = File.ReadAllText(_settingsPath);
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

                // Cách parse thủ công đơn giản (giữ nguyên logic của bạn để tránh lỗi thư viện)
                txtAdbAddress.Text = ParseJsonString(json, "adb_address", "127.0.0.1:7555");
                txtMumuPath.Text = ParseJsonString(json, "mumu_path", "");
                chkEnhancedMode.IsChecked = ParseJsonValue(json, "enhanced_mode", 0.0) == 1.0;

                numStart.Text = ParseJsonValue(json, "delay_start", 2.0).ToString();
                numSquad.Text = ParseJsonValue(json, "delay_squad", 5.0).ToString();
                numSettings.Text = ParseJsonValue(json, "delay_settings", 2.0).ToString();
                numRetreat.Text = ParseJsonValue(json, "delay_retreat", 1.5).ToString();
                numConfirm.Text = ParseJsonValue(json, "delay_confirm", 4.0).ToString();
            }
            catch { /* Bỏ qua lỗi nếu file chưa có */ }
        }

        private void BtnSave_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Parse dữ liệu từ TextBox số sang double an toàn
                double.TryParse(numStart.Text, out double dStart);
                double.TryParse(numSquad.Text, out double dSquad);
                double.TryParse(numSettings.Text, out double dSettings);
                double.TryParse(numRetreat.Text, out double dRetreat);
                double.TryParse(numConfirm.Text, out double dConfirm);

                // Tạo object dữ liệu
                var settingsData = new
                {
                    adb_address = txtAdbAddress.Text,
                    mumu_path = txtMumuPath.Text, // Tự động escape ký tự đặc biệt
                    enhanced_mode = (chkEnhancedMode.IsChecked == true ? 1 : 0),
                    delay_start = dStart,
                    delay_squad = dSquad,
                    delay_settings = dSettings,
                    delay_retreat = dRetreat,
                    delay_confirm = dConfirm
                };

                // Lưu JSON
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(settingsData, options);

                File.WriteAllText(_settingsPath, json);
                HandyControl.Controls.Growl.Success("Đã lưu cấu hình thành công!");
            }
            catch (Exception ex)
            {
                MessageBox.Show("Lỗi lưu settings:\n" + ex.Message);
            }
        }

        // Helper: Parse chuỗi JSON thủ công (cho LoadSettings)
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
                string val = json.Substring(colon + 1, comma - colon - 1).Trim();
                return double.Parse(val, System.Globalization.CultureInfo.InvariantCulture);
            }
            catch { return defaultValue; }
        }

        #endregion

        #region 2. XỬ LÝ MUMU PATH (CODE MỚI)

        private void BtnBrowseMumu_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new FolderBrowserDialog();
            dialog.Description = "Chọn thư mục gốc cài đặt MuMu (VD: MuMuPlayer-12.0)";
            dialog.UseDescriptionForTitle = true;
            dialog.ShowNewFolderButton = false;

            // Gợi ý đường dẫn mặc định
            string programFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
            string mumuDefault = Path.Combine(programFiles, "Netease", "MuMuPlayer-12.0");
            if (Directory.Exists(mumuDefault)) dialog.SelectedPath = mumuDefault;

            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                string selectedPath = dialog.SelectedPath;

                // Kiểm tra xem có phải folder MuMu chuẩn không
                if (AutoFindMuMuExe(selectedPath) != null)
                {
                    txtMumuPath.Text = selectedPath;
                    HandyControl.Controls.Growl.Success("Đã nhận diện đúng thư mục MuMu!");
                }
                else
                {
                    txtMumuPath.Text = selectedPath;
                    HandyControl.Controls.Growl.Warning("Cảnh báo: Không tìm thấy file chạy trong thư mục này. Hãy kiểm tra lại!");
                }
            }
        }

        private string? AutoFindMuMuExe(string folderPath)
        {
            string[] targetExes = { "MuMuPlayer.exe", "NemuPlayer.exe" };
            string[] subFolders = { "", "shell", "vmonitor/bin", "emulator/nemu/vmonitor/bin" };

            foreach (string sub in subFolders)
            {
                foreach (string exeName in targetExes)
                {
                    string tryPath = Path.Combine(folderPath, sub, exeName);
                    if (File.Exists(tryPath)) return tryPath;
                }
            }
            return null;
        }

        #endregion

        #region 3. START / STOP BOT

        private void BtnStart_Click(object sender, RoutedEventArgs e)
        {
            _isManualStop = false;
            LogToUI(">>> Đang khởi động Bot...", "#22c55e"); // Màu xanh lá

            string botExePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ArknightsBot.Logic.exe");

            if (!File.Exists(botExePath))
            {
                MessageBox.Show("Không tìm thấy file ArknightsBot.Logic.exe!");
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
                    // Quan trọng: Đọc tiếng Việt không lỗi font
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
            LogToUI(">>> ĐÃ DỪNG BOT (MANUAL STOP)", "#ef4444"); // Màu đỏ

            btnStart.IsEnabled = true;
            btnStop.IsEnabled = false;
        }

        private void Bot_Exited(object sender, EventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                if (!_isManualStop)
                {
                    LogToUI("!!! BOT ĐÃ TẮT ĐỘT NGỘT !!!", "#ef4444");
                    btnStart.IsEnabled = true;
                    btnStop.IsEnabled = false;
                }
            });
        }

        private void KillBotProcess()
        {
            if (_botProcess == null || _botProcess.HasExited) return;
            try
            {
                // Dùng taskkill để giết sạch cả process con (adb...)
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

        #region 4. XỬ LÝ LOGS

        private void Bot_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (string.IsNullOrEmpty(e.Data)) return;

            Dispatcher.Invoke(() =>
            {
                // Lọc bỏ bớt log rác nếu cần
                LogToUI(e.Data);
            });
        }

        private void LogToUI(string message, string colorHex = "#a3a3a3") // Màu mặc định xám
        {
            // Thêm log vào TextBlock (Dùng Run để có thể chỉnh màu sau này nếu muốn)
            txtLogs.Text += $"[{DateTime.Now:HH:mm:ss}] {message}\n";

            // Tự động cuộn xuống cuối
            scrollViewerLogs.ScrollToBottom();
        }

        protected override void OnClosed(EventArgs e)
        {
            _isManualStop = true;
            KillBotProcess();
            base.OnClosed(e);
            Application.Current.Shutdown();
        }

        #endregion
    }
}