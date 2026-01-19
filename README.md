# 🤖 Arknights Auto Bot

![Build Status](https://github.com/longnhx1/ArknightsAutoBot/actions/workflows/build.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/longnhx1/ArknightsAutoBot)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

Tool hỗ trợ tự động cày cuốc (Auto Farm) game Arknights trên giả lập, được xây dựng với kiến trúc đa ngôn ngữ (C# UI + Python Logic + C++ Vision) nhằm tối ưu hiệu suất và trải nghiệm người dùng.

## ✨ Tính năng nổi bật

* **🎯 Auto Farm thông minh:** Tự động lặp lại các màn chơi (1-7, LS-6, CE-6...), tự cắn thuốc (Sanity Potion) hoặc Originite Prime.
* **🚀 Chạy nền (System Tray):** Tắt cửa sổ chính tool vẫn chạy ngầm dưới khay hệ thống, không chiếm chỗ trên Taskbar.
* **⚡ Siêu nhẹ & Portable:** Không cần cài đặt Python/VS, tải về giải nén là chạy.
* **👁️ Xử lý ảnh chính xác:** Sử dụng OpenCV C++ để nhận diện hình ảnh tốc độ cao.
* **🔄 Auto Reconnect:** Tự động kết nối lại ADB nếu giả lập bị lag/dis.

## 🤝 Combo Tối Ưu (Recommended Setup)

Tool được thiết kế để hoạt động hoàn hảo khi kết hợp với:

1.  **Arknights BLACKMOD:** Dùng bản Mod (High Damage) để clear map siêu tốc.
2.  **MaaAssistantArknights (MAA):** Dùng để Auto chế độ **Integrated Strategies (I.S)**.
3.  **Arknights Auto Bot (Tool này):** Quản lý quy trình farm tài nguyên cơ bản, giữ kết nối ADB và chạy nền nhẹ nhàng khi bạn treo máy làm việc khác.

## 🛠️ Yêu cầu hệ thống

* **Giả lập:** MuMu Player, LDPlayer, Nox...
* **Độ phân giải:** `1280 x 720` (DPI 240).
* **ADB:** Đã bật (Root/Debug).

## 📥 Hướng dẫn sử dụng

1.  Tải về từ mục **[Releases](https://github.com/longnhx1/ArknightsAutoBot/releases)**.
2.  Giải nén và chạy file **`ArknightsBot.UI.exe`**.
3.  Nhập địa chỉ ADB (VD: `127.0.0.1:7555`) và bấm **Start**.

## 🚀 Lộ trình phát triển (Roadmap)

- [ ] **Auto Update:** Tự động tải bản mới từ GitHub.
- [ ] **Scheduler:** Hẹn giờ tắt máy/dừng farm.
- [ ] **Webhook:** Gửi thông báo về Discord/Telegram khi hoàn thành.
- [ ] **Deep Integration:** Tích hợp Core MAA để chạy I.S trực tiếp trên giao diện này.

## 🏗️ Công nghệ

* **Frontend:** C# (WPF), HandyControl.
* **Backend:** Python 3.10.
* **Vision:** C++ (OpenCV).
* **CI/CD:** GitHub Actions.

---
Developed by **longnhx1** | 2026
