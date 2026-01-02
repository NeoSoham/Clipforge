export async function runClipForge(file) {
  const formData = new FormData();
  formData.append("video", file);

  const res = await fetch("http://127.0.0.1:8000/run", {
    method: "POST",
    body: formData,
  });

  // 👇 LOG STATUS
  console.log("API status:", res.status);

  const text = await res.text(); // read raw response first
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
