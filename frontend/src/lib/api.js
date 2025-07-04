const API_BASE = "http://localhost:8000";

export async function fetchSearchResults(query, topK = 10) {
  const res = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}&top_k=${topK}`);
  const data = await res.json();
  return data.results || [];
}
