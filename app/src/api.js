export  async function uploadFile({ filepath, content }) {
    const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            filepath,
            content,
        }),
    });

    if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

export async function analyze({ filepath, token, model = null }) {
    const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "filepath": filepath,
            "hf_token": token,
            "model": model
        }),
    });

    if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
}
