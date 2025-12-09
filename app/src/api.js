export async function uploadFile({ filename, content }) {
  const response = await fetch("http://localhost:8000/upload", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      filename,
      content,
    }),
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}


export async function analyze({ filename, token, model = null }) {
  const response = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "filepath": filename,
      "hf_token": token,
      "model": model
    }),
  });

  if (!response.ok) {
    throw new Error(`Analyze failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
