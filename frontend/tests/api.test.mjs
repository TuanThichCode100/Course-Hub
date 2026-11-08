import test from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";

// Mock global fetch
const originalFetch = globalThis.fetch;

test.afterEach(() => {
  globalThis.fetch = originalFetch;
});

test("api() returns null for 204 No Content", async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });
  const result = await api("/enrollments/22000004/WEB-01", { method: "DELETE" });
  assert.equal(result, null);
});

test("api() returns parsed JSON for 200 OK", async () => {
  const mockData = [{ code: "INT2204", name: "CSDL Web", credits: 3 }];
  globalThis.fetch = async () =>
    new Response(JSON.stringify(mockData), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  const result = await api("/courses");
  assert.deepEqual(result, mockData);
});

test("api() handles 404 error detail properly", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Khong tim thay sinh vien" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  await assert.rejects(
    async () => api("/students/99999999/enrollments"),
    (err) => {
      assert.equal(err.status, 404);
      assert.match(err.message, /Khong tim thay sinh vien/);
      return true;
    },
  );
});

test("api() handles 409 Conflict properly", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Lop hoc phan da het cho" }), {
      status: 409,
      headers: { "Content-Type": "application/json" },
    });
  await assert.rejects(
    async () =>
      api("/enrollments", {
        method: "POST",
        body: { student_id: "22000004", class_section_id: "RACE-01" },
      }),
    (err) => {
      assert.equal(err.status, 409);
      assert.match(err.message, /Lop hoc phan da het cho/);
      return true;
    },
  );
});

test("api() throws network error on fetch failure", async () => {
  globalThis.fetch = async () => {
    throw new TypeError("Failed to fetch");
  };
  await assert.rejects(
    async () => api("/sections"),
    (err) => {
      assert.match(err.message, /Không nhận được phản hồi API/);
      return true;
    },
  );
});
