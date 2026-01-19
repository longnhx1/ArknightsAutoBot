using System.Diagnostics;
using System.IO;
using System.Windows;

namespace ArknightsBot.UI
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void btnTest_Click(object sender, RoutedEventArgs e)
        {
            txtLog.Text = "Đang khởi động Python...\n";

            // Đường dẫn đến file Python (Tính từ thư mục bin lùi về src)
            string scriptPath = Path.GetFullPath(@"..\..\src\ArknightsBot.Logic\main.py");

            if (!File.Exists(scriptPath))
            {
                txtLog.Text += $"LỖI: Không tìm thấy file tại {scriptPath}";
                return;
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = "python", // Đảm bảo máy đã cài Python và add Path
                Arguments = $"\"{scriptPath}\"", // Dùng ngoặc kép đề phòng đường dẫn có dấu cách
                UseShellExecute = false,
                RedirectStandardOutput = true, // Quan trọng: Để đọc log từ Python
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using (var process = new Process { StartInfo = startInfo })
            {
                process.Start();

                // Đọc toàn bộ output trả về từ Python
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                process.WaitForExit();

                txtLog.Text += output;
                if (!string.IsNullOrEmpty(error))
                {
                    txtLog.Text += "\n[LỖI PYTHON]: " + error;
                }
            }
        }
    }
}