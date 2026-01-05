const API_BASE = import.meta.env.VITE_API_URL;

export async function runClipForge(file) {
  const formData = new FormData();
  formData.append("video", file);

  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    body: formData,
  });

  console.log("API status:", res.status);

  const text = await res.text();
  console.log("API raw response:", text);

  if (!res.ok) {
    throw new Error(`Backend error ${res.status}: ${text}`);
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Backend did not return valid JSON");
  }
}
