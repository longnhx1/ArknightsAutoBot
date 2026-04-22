# 🤖 Arknights Auto Bot

![Build Status](https://github.com/longnhx1/ArknightsAutoBot/actions/workflows/build.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/longnhx1/ArknightsAutoBot)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

Công cụ hỗ trợ Arknights hiệu suất cao với giao diện WPF hiện đại, tích hợp engine nhận diện hình ảnh C++ và chế độ chụp màn hình siêu tốc (Enhanced Mode) dành cho MuMu Player.

## ✨ Tính năng nổi bật

* **⚡ Enhanced Mode (Siêu tốc):** Chụp ảnh màn hình trực tiếp qua Window API dành riêng cho MuMu Player, giảm độ trễ từ ~500ms (ADB) xuống còn ~15ms.
* **👁️ Engine Vision C++:** Sử dụng OpenCV C++ DLL để nhận diện hình ảnh tốc độ cao, đảm bảo độ chính xác và tiết kiệm tài nguyên.
* **🔄 Auto Retreat (Instant Win Helper):** Tự động thực hiện quy trình Cài đặt -> Rút lui -> Xác nhận. Đặc biệt hiệu quả khi sử dụng cùng các bản Mod Instant Win để clear map siêu tốc.
* **🌍 Đa ngôn ngữ (Region Support):** Hỗ trợ nhận diện hình ảnh trên cả server Global (EN) và Nhật Bản (JP).
* **🚀 Giao diện hiện đại (Rhodes Island Style):** Được xây dựng bằng WPF và HandyControl, mang lại trải nghiệm chuyên nghiệp và mượt mà.

## 🛠️ Yêu cầu hệ thống

* **Giả lập:** MuMu Player 12 (khuyên dùng để bật Enhanced Mode), LDPlayer, Nox...
* **Độ phân giải:** `1280 x 720` (DPI 240).
* **ADB:** Đã bật (Root/Debug).

## 📥 Hướng dẫn sử dụng

1.  Tải về từ mục **[Releases](https://github.com/longnhx1/ArknightsAutoBot/releases)**.
2.  Giải nén và chạy file **`ArknightsBot.UI.exe`**.
3.  Nhấn nút **Auto** để tự động tìm cổng ADB hoặc nhập thủ công (VD: `127.0.0.1:16384` cho MuMu).
4.  Bấm **SAVE CONFIGURATION** và sau đó **START OPERATION**.

## 🚀 Lộ trình phát triển (Roadmap)

- [ ] **Auto Recruit:** Tự động tuyển dụng công khai.
- [ ] **Auto I.S:** Tự động chạy chế độ Integrated Strategies.
- [ ] **Auto Update:** Tự động cập nhật phiên bản mới từ GitHub.

## 🏗️ Công nghệ sử dụng

* **Frontend:** C# (WPF), HandyControl.
* **Logic Engine:** Python 3.10.
* **Vision Core:** C++ (OpenCV).
* **CI/CD:** GitHub Actions.

---
Developed by **longnhx1** | 2026
