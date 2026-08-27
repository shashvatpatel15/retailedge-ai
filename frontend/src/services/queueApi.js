const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"
        ? `http://${window.location.hostname}:8000/api/v1`
        : "http://127.0.0.1:8000/api/v1");


// ============================================
// LIVE QUEUE DATA
// ============================================

export async function getQueueData() {
    const response = await fetch(`${API_BASE_URL}/queue`);

    if (!response.ok) {
        throw new Error("Unable to fetch queue analytics");
    }

    return response.json();
}


// ============================================
// BACKEND / EDGE HEALTH
// ============================================

export async function getHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error("Backend health check failed");
    }

    return response.json();
}


// ============================================
// CLOUD QUEUE HISTORY
// ============================================

export async function getQueueHistory() {
    const response = await fetch(`${API_BASE_URL}/queue/history`);

    if (!response.ok) {
        throw new Error("Unable to fetch queue history");
    }

    return response.json();
}