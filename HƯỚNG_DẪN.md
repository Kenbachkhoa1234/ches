# 🎮 Cờ Vua Multiplayer - Người vs Người

Hệ thống chơi cờ vua trực tuyến giữa hai người chơi với tính năng phòng chơi qua mã ID.

## 🌟 Tính Năng

- ♔ **Chơi Người vs Người**: Giao diện đầy đủ cho hai người chơi cùng một bàn cờ
- 🔑 **Phòng Chơi với Mã ID**: Tạo phòng và chia sẻ mã để bạn bè tham gia
- 🌐 **Kết Nối Multiplayer**: Sử dụng WebSocket để truyền tải dữ liệu thời gian thực
- 📱 **Giao Diện Responsive**: Hoạt động tốt trên máy tính để bàn và thiết bị di động
- ⚡ **Đồng Bộ Thời Gian Thực**: Cập nhật bàn cờ tức thì cho cả hai người chơi
- 🎨 **Giao Diện Hiện Đại**: Thiết kế đẹp mắt với màu sắc chuyên nghiệp

## 📋 Yêu Cầu

- Python 3.7+
- Flask
- flask-sock (WebSocket)
- python-chess

## 🚀 Cài Đặt & Chạy

### 1. Cài Đặt Thư Viện

```bash
cd "Chess_game\python-chess-main\python-chess-main"
pip install -r requirements.txt
```

### 2. Chạy Máy Chủ

```bash
cd BE
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 3. Mở Trò Chơi

- **Máy tính 1**: Mở `http://localhost:5000` → Chọn "Tạo Phòng Mới" → Nhận mã phòng
- **Máy tính 2**: Mở `http://localhost:5000` → Chọn "Tham Gia Phòng" → Nhập mã phòng

## 🎯 Cách Chơi

### Tạo Phòng
1. Nhấn "📋 Tạo Phòng Mới"
2. Bạn sẽ nhận được mã phòng 6 chữ số
3. Chia sẻ mã này cho bạn bè
4. Hệ thống chờ bạn bè tham gia

### Tham Gia Phòng
1. Nhấn "🔓 Tham Gia Phòng"
2. Nhập mã phòng từ người tạo phòng
3. Nhấn "Tham Gia"
4. Trò chơi sẽ bắt đầu ngay

### Chơi Cờ
- **Người Trắng (Trắng)**: Đi trước
- **Người Đen (Đen)**: Đi thứ hai
- Nhấn vào quân cờ để chọn → Nhấn vào ô đích để di chuyển
- Ô **sáng xanh lá** = nước đi không bắt quân
- Ô **sáng đỏ** = nước đi bắt quân
- Sử dụng nút **"🏳️ Đầu Hàng"** để kết thúc trò chơi

## 📁 Cấu Trúc Thư Mục

```
python-chess-main/
├── BE/
│   ├── app.py              # Server Flask + WebSocket
│   └── chess_engine.py     # Engine cờ vua (python-chess)
├── FE/
│   ├── multiplayer.html    # Giao diện multiplayer
│   ├── style.css          # CSS chính
│   └── script.js          # JavaScript chính
├── requirements.txt        # Thư viện cần cài
└── main.py                # Entry point
```

## 🔧 Cấu Hình

### Thay Đổi Port

Mở file `BE/app.py` và tìm dòng:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Thay `5000` bằng port bạn muốn sử dụng.

### Cho Phép Kết Nối Từ Xa

Để cho phép người chơi khác từ mạng khác tham gia:
- Thay `host='0.0.0.0'` (mặc định đã hỗ trợ)
- Mở port trong firewall nếu cần

## 🐛 Xử Lý Sự Cố

### "Lỗi kết nối WebSocket"
- Kiểm tra server đang chạy
- Kiểm tra URL đúng: `http://localhost:5000`
- Đóng firewall tạm thời để kiểm tra

### "Phòng không tồn tại"
- Kiểm tra mã phòng nhập đúng
- Phòng đã hết hạn nếu không có người tham gia trong vài phút

### "Không thể di chuyển quân cờ"
- Kiểm tra nước đi hợp lệ (các ô sáng)
- Đợi lượt của bạn (kiểm tra lượt đi ở bên phải)

## 🛠️ Phát Triển Tiếp Theo

- [ ] Lưu lịch sử nước đi
- [ ] Bộ đếm thời gian cho mỗi nước đi
- [ ] Tính năng Undo/Redo
- [ ] Chat giữa hai người chơi
- [ ] Lưu trữ trò chơi đã hoàn thành
- [ ] Thứ hạng người chơi
- [ ] Replay trò chơi

## 📝 Ghi Chú

- Trò chơi sử dụng thư viện **python-chess** để xác nhận nước đi
- Tất cả nước đi được gửi trong định dạng **UCI** (e2e4, a7a8, v.v.)
- WebSocket duy trì kết nối real-time giữa các máy chủ

## 📧 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra console trong DevTools (F12)
2. Xem log server ở terminal
3. Đảm bảo tất cả thư viện đã cài đặt

---

**Tác giả**: Chess Game Development Team  
**Phiên bản**: 1.0.0  
**Cập nhật**: Tháng 12, 2025
