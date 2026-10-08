const TOKEN_KEY = "smartmark_access_token";
const REFRESH_KEY = "smartmark_refresh_token";

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(TOKEN_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

async function request(path, { method = "GET", body, headers = {}, isForm = false } = {}) {
  const token = getAccessToken();
  const finalHeaders = { ...headers };
  if (!isForm) finalHeaders["Content-Type"] = "application/json";
  if (token) finalHeaders["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, {
    method,
    headers: finalHeaders,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : await res.blob();

  if (!res.ok) {
    const message = (isJson && data.error) || "Something went wrong. Please try again.";
    const error = new Error(message);
    error.status = res.status;
    error.details = isJson ? data.details : null;
    throw error;
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  del: (path) => request(path, { method: "DELETE" }),
  postForm: (path, formData) => request(path, { method: "POST", body: formData, isForm: true }),
  downloadUrl: (path) => `/api${path}`,
};
