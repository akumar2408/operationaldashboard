// web/src/lib/api.ts
export const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function authHeaders() {
  const t = localStorage.getItem("OD_TOKEN");
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function rawFetch(path: string, init: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: "include",
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.headers || {}),
      ...authHeaders(),
    },
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${txt ? ` — ${txt}` : ""}`);
  }
  return res;
}

export async function get<T>(path: string): Promise<T> {
  const res = await rawFetch(path);
  return res.json();
}

export async function post<T>(
  path: string,
  body: any,
  headers: Record<string, string> = {}
): Promise<T> {
  const res = await rawFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  return res.json();
}

/* S3 presigned upload helper */
export async function uploadToPresignedS3(file: File) {
  const presign = await get<{ url: string; fields: Record<string, string> }>(
    "/sales/presign-upload"
  );

  const form = new FormData();
  Object.entries(presign.fields).forEach(([k, v]) => form.append(k, v));
  form.append("file", file);

  const s3Res = await fetch(presign.url, { method: "POST", body: form });
  if (!s3Res.ok) throw new Error(`S3 upload failed: ${s3Res.statusText}`);

  // now tell API to ingest from S3 event
  await post("/sales/ingest-s3", { key: presign.fields.key });
}
