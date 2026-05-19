const API_BASE = '/api';

async function fetchJSON(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function getDigest(page = 1, limit = 10) {
  return fetchJSON(`/digest?page=${page}&limit=${limit}`);
}

export async function getDigestStats() {
  return fetchJSON('/digest/stats');
}

export async function getTopics() {
  return fetchJSON('/topics');
}

export async function getTopicClusters(name) {
  return fetchJSON(`/topic/${encodeURIComponent(name)}`);
}

export async function subscribe(email, topic) {
  return fetchJSON('/subscriptions', {
    method: 'POST',
    body: JSON.stringify({ email, topic }),
  });
}

export async function triggerRefresh() {
  return fetchJSON('/admin/refresh', { method: 'POST' });
}
