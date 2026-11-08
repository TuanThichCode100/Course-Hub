export default function EnrollmentHistory({
  events,
  page,
  pageSize,
  loading,
  onPrevPage,
  onNextPage,
  studentId,
}) {
  return (
    <section className="panel">
      <div className="section-header">
        <h2>4. Lịch sử thao tác (Nhật ký demo)</h2>
        <span className="chip chip-subtle">
          Phân trang CSDL (limit={pageSize}) · Sinh viên {studentId}
        </span>
      </div>
      <p className="muted">
        Chỉ truy vấn nhật ký <code>demo</code> theo từng trang trực tiếp từ PostgreSQL qua API,
        không tải 100.000 sự kiện <code>performance</code> về trình duyệt.
      </p>

      {events.length === 0 ? (
        <p className="empty-message">
          Chưa có nhật ký thao tác nào cho sinh viên <strong>{studentId}</strong> trong tập dữ liệu demo.
        </p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Nhật ký thao tác của sinh viên">
            <thead>
              <tr>
                <th>Mã SK</th>
                <th>Thời gian</th>
                <th>Lớp / Học phần</th>
                <th>Thao tác</th>
                <th>Nguồn / Tập DL</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt) => {
                const isCreated = evt.event_type === "CREATED";
                const dateStr = evt.occurred_at
                  ? new Date(evt.occurred_at).toLocaleString("vi-VN")
                  : "-";
                return (
                  <tr key={evt.id} data-testid={`event-${evt.id}`}>
                    <td>
                      <code>#{evt.id}</code>
                    </td>
                    <td>
                      <span className="timestamp">{dateStr}</span>
                    </td>
                    <td>
                      <strong>{evt.class_section_id}</strong>
                      {evt.course_name && (
                        <span className="subtext">{evt.course_name}</span>
                      )}
                      {evt.course_code && <small>{evt.course_code}</small>}
                    </td>
                    <td>
                      <span className={isCreated ? "badge badge-success" : "badge badge-danger"}>
                        {isCreated ? "Đăng ký" : "Hủy đăng ký"}
                      </span>
                    </td>
                    <td>
                      <span className="muted">
                        {evt.source} · <code>{evt.dataset}</code>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <span className="pagination-info">
          Trang <strong>{page + 1}</strong>
          {events.length > 0 && ` (${events.length} bản ghi hiển thị)`}
        </span>
        <div className="pagination-actions">
          <button
            type="button"
            className="secondary"
            disabled={page === 0 || loading}
            onClick={onPrevPage}
          >
            ◀ Trang trước
          </button>
          <button
            type="button"
            className="secondary"
            disabled={events.length < pageSize || loading}
            onClick={onNextPage}
          >
            Trang sau ▶
          </button>
        </div>
      </div>
    </section>
  );
}
