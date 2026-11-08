# CourseHub – Ghi chú thực hành Buổi 5 (Frontend React & Tích hợp API)

## 1. Bản thiết kế giao diện (Figma)

Xem tại [Frame thiết kế](https://www.figma.com/design/4KZyhqdR89ahCspB64yaB3/CourseHub-%E2%80%93-Bu%E1%BB%95i-5?node-id=0-1&t=HQKv6ejl1ywfXBor-1) hoặc bản xem trước bên dưới:

![Frame](./assets/frame.png)

---

## 2. Kết quả hoàn thành các bài tập

### Bài 1. Tách form chọn sinh viên thành `StudentForm.jsx`
- **Component:** [`frontend/src/components/StudentForm.jsx`](file:///d:/Mini%20Project/CourseHub/frontend/src/components/StudentForm.jsx)
- **Kiến trúc State & Props:**
  - Component cha [`App.jsx`](file:///d:/Mini%20Project/CourseHub/frontend/src/App.jsx) giữ Single Source of Truth gồm:
    - `draftId`: Giá trị đang nhập trong ô input.
    - `studentId`: Mã sinh viên chính thức đang xem dữ liệu.
  - Toàn bộ giá trị và hàm xử lý sự kiện được truyền qua props:
    - `draftId`, `studentId`, `busy`, `loading`.
    - `onChangeDraft` (`setDraftId`): Cập nhật giá trị đang gõ.
    - `onSubmit` (`chooseStudent`): Kiểm tra định dạng 8 chữ số và áp dụng mã sinh viên mới.
    - `onRefresh`: Tải lại toàn bộ dữ liệu từ CSDL.
  - **Tuyệt đối không tạo bản sao state sinh viên** bên trong `StudentForm.jsx` để tránh hiện tượng hai vùng hiển thị lệch nhau (dữ liệu hiển thị ở header form và tiêu đề danh sách lớp/nhật ký luôn khớp 100%).

---

### Bài 2. Bộ lọc học phần từ `GET /courses`
- **Giao diện:** Thêm dropdown `<select id="course-filter">` trong vùng lọc của panel *2. Danh sách lớp học phần*.
- **Nguồn dữ liệu:** Lấy danh sách học phần động từ API `GET /courses` (`courses` state gồm `INT2204`, `INT2205`, `INT2206`, ...).
- **Trạng thái rỗng:** Khi bộ lọc kết hợp không có lớp nào phù hợp (`rows.length === 0`), giao diện hiển thị thông báo trạng thái rỗng thân thiện: `<p className="empty-message">Không có lớp phù hợp với bộ lọc.</p>`.
- **An toàn CSDL:** Bộ lọc chỉ áp dụng trên dữ liệu danh sách hiển thị tại client, không thực hiện bất kỳ lệnh sửa đổi dữ liệu nào trong CSDL PostgreSQL.

---

### Bài 3. Màn hình lịch sử thao tác của sinh viên có phân trang (`GET /enrollment-events`)
- **API Endpoint:** `GET /enrollment-events`
- **Mục đích:** Truy vấn nhật ký sự kiện đăng ký (`CREATED`) và hủy đăng ký (`CANCELLED`) do Backend Buổi 4 ghi vào bảng `enrollment_events`.
- **Cô lập tập dữ liệu:**
  - CSDL chứa đồng thời 100.000 bản ghi thử tải `dataset = 'performance'` và các bản ghi thực hành `dataset = 'demo'`.
  - Mặc định tham số `dataset='demo'` để **chỉ tải nhật ký demo**, bảo vệ trình duyệt khỏi nguy cơ tải 100.000 sự kiện gây tràn RAM hay treo tab.
- **Component giao diện:** [`frontend/src/components/EnrollmentHistory.jsx`](file:///d:/Mini%20Project/CourseHub/frontend/src/components/EnrollmentHistory.jsx)
  - Hiển thị bảng nhật ký: Mã sự kiện, thời gian (`occurred_at` định dạng bản địa), lớp/học phần, loại thao tác (badge Xanh cho `CREATED`, Đỏ cho `CANCELLED`), nguồn và dataset.
  - Nút chuyển trang: *Trang trước*, *Trang sau* và chỉ số trang hiện tại.
  - Khi người dùng đăng ký hoặc hủy lớp học phần, bảng lịch sử tự động làm mới để phản ánh ngay sự kiện vừa được Backend ghi nhận.

---

### Bài 4. Thiết kế Tìm kiếm và Phân trang phía Server (Database Pagination)

> [!IMPORTANT]
> **Quy tắc cốt lõi:** Tuyệt đối không gọi việc tải toàn bộ bảng về rồi dùng `array.slice()` hay `array.filter()` trong JavaScript tại trình duyệt là "phân trang CSDL". Phân trang CSDL phải đẩy điều kiện `LIMIT` và `OFFSET` xuống trực tiếp câu lệnh SQL tại PostgreSQL.

#### 1. Bảng so sánh phương pháp

| Đặc điểm | Lọc mảng tại trình duyệt (Client-side slicing) | Phân trang CSDL phía Server (Server-side Pagination) |
| :--- | :--- | :--- |
| **Bản chất** | Kéo toàn bộ dữ liệu (vd: 100.000 dòng) về RAM trình duyệt rồi `.slice()` | Truy vấn chỉ lấy đúng số bản ghi của trang hiện tại (`LIMIT :limit OFFSET :skip`) |
| **Băng thông mạng** | Rất lớn (hàng chục MB), gây nghẽn kết nối | Cực nhỏ (vài KB cho mỗi trang) |
| **Bộ nhớ & CPU client** | Nguy cơ tràn bộ nhớ, đơ UI thread | Hoạt động mượt mà, tài nguyên tiêu thụ tối thiểu |
| **Thời gian phản hồi** | Chậm khi dữ liệu lớn dần | Cực nhanh nhờ chỉ mục B-Tree tại PostgreSQL |

#### 2. Đặc tả các tham số của `GET /enrollment-events`

- `student_id` *(chuỗi, tùy chọn)*: Lọc theo mã sinh viên (ví dụ: `22000004`).
- `class_section_id` *(chuỗi, tùy chọn)*: Lọc theo mã lớp học phần (ví dụ: `WEB-01`).
- `event_type` *(chuỗi, tùy chọn)*: Lọc loại sự kiện (`CREATED` hoặc `CANCELLED`).
- `dataset` *(chuỗi, mặc định: `'demo'`)*: Bắt buộc thuộc `('demo', 'performance')`. Trả về lỗi `HTTP 400` nếu truyền giá trị không hợp lệ.
- `skip` *(số nguyên, mặc định: 0, ge=0)*: Số dòng bỏ qua từ đầu tập kết quả (offset).
- `limit` *(số nguyên, mặc định: 5, ge=1, le=100)*: Kích thước trang tối đa cho phép là 100 dòng.

#### 3. Thứ tự sắp xếp ổn định (Stable Ordering)
- **Câu lệnh SQL:**
  ```sql
  ORDER BY e.occurred_at DESC, e.id DESC
  OFFSET :skip LIMIT :limit
  ```
- **Ý nghĩa kỹ thuật:**
  1. `occurred_at DESC`: Đảm bảo sự kiện mới nhất luôn hiển thị lên trước.
  2. `id DESC` *(Tie-breaker)*: Khóa chính `id` là giá trị đơn điệu tăng dần duy nhất. Trong trường hợp có 2 sự kiện xảy ra trong cùng một microsecond, `id DESC` loại trừ hoàn toàn tính bất định, ngăn chặn hiện tượng nhảy dòng hoặc trùng lặp bản ghi giữa các trang khi phân trang.
  3. **Tận dụng chỉ mục:** Khớp hoàn hảo với Composite Index đã tạo ở Buổi 4:
     ```sql
     CREATE INDEX idx_enrollment_events_dataset_student_time
     ON enrollment_events (dataset, student_id, occurred_at DESC);
     ```
     Giúp câu lệnh chạy trực tiếp qua `Index Scan` với thời gian thực thi cực nhỏ (< 1 ms).

#### 4. Mở rộng cho `GET /sections`
- `available_only` *(boolean, mặc định: `False`)*: Chỉ lấy lớp còn chỗ.
- `course_code` *(chuỗi, tùy chọn)*: Lọc theo mã học phần (ví dụ: `INT2204`).
- `q` *(chuỗi, tùy chọn)*: Tìm kiếm theo mã lớp hoặc mã học phần.
- `skip` *(số nguyên, mặc định: 0, ge=0)*.
- `limit` *(số nguyên, mặc định: 50, ge=1, le=100)*.
- **Thứ tự ổn định:** `ORDER BY class_id OFFSET :skip LIMIT :limit` (khóa chính lớp học phần).

---

## 3. Kiểm thử và Bàn giao

1. **Kiểm thử tự động Backend (FastAPI + PostgreSQL):**
   ```bash
   .venv\Scripts\python backend/tests/test_api_week05.py
   .venv\Scripts\python backend/tests/week04_concurrency_test.py
   ```
   *Kết quả: Toàn bộ kiểm thử 201, 204, 404, 409, phân trang và concurrency test đều đạt 100%.*

2. **Kiểm thử tự động Frontend (Node Test Runner):**
   ```bash
   npm --prefix frontend test
   ```
   *Kết quả: 5/5 bài test xử lý 204 No Content, 200 OK, 404 Not Found, 409 Conflict và Network Error đều đạt.*

3. **Bộ sưu tập Postman Buổi 5:**
   - File cấu hình: [`postman/CourseHub_Buoi_5.postman_collection.json`](file:///d:/Mini%20Project/CourseHub/postman/CourseHub_Buoi_5.postman_collection.json)
   - Chứa đầy đủ các kịch bản kiểm thử: Health check, danh sách học phần, phân trang lớp học phần, xem đăng ký sinh viên, phân trang nhật ký demo, chặn dataset không hợp lệ (400), đăng ký trùng (409), hủy đăng ký không tồn tại (404).
