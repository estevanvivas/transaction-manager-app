/* ═══════════════════════════════════════════════════════
   API Client – Comunicación con el backend
   ═══════════════════════════════════════════════════════ */

const API = (() => {
    const BASE = '';

    /* ── Token management ────────────────────────────── */
    function getAccessToken()  { return localStorage.getItem('access_token'); }
    function getRefreshToken() { return localStorage.getItem('refresh_token'); }

    function saveTokens({ access_token, refresh_token }) {
        if (access_token)  localStorage.setItem('access_token', access_token);
        if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
    }

    function clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    function isAuthenticated() {
        return !!getAccessToken();
    }

    /* ── Core fetch wrapper ──────────────────────────── */
    async function request(method, path, body = null, retry = true) {
        const headers = { 'Content-Type': 'application/json' };
        const token = getAccessToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const opts = { method, headers };
        if (body) opts.body = JSON.stringify(body);

        let res = await fetch(`${BASE}${path}`, opts);

        // Si el token expiró, intentar refresh
        if (res.status === 401 && retry && getRefreshToken()) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                return request(method, path, body, false);
            } else {
                clearTokens();
                window.location.href = '/login';
                return null;
            }
        }

        const data = await res.json();
        if (!res.ok) {
            const error = new Error(data.message || 'Error desconocido');
            error.status = res.status;
            error.details = data.errors || null;
            throw error;
        }
        return data;
    }

    async function refreshAccessToken() {
        try {
            const res = await fetch(`${BASE}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getRefreshToken()}`
                }
            });
            if (!res.ok) return false;
            const data = await res.json();
            saveTokens(data.data);
            return true;
        } catch {
            return false;
        }
    }

    /* ── Auth endpoints ──────────────────────────────── */
    async function login(email, password) {
        const res = await request('POST', '/auth/login', { email, password });
        saveTokens(res.data);
        return res;
    }

    async function register(username, email, password) {
        return request('POST', '/auth/register', { username, email, password });
    }

    async function logout() {
        const accessToken  = getAccessToken();
        const refreshToken = getRefreshToken();

        if (accessToken) {
            try {
                await fetch(`${BASE}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
            } catch (_) { }
        }

        if (refreshToken) {
            try {
                await fetch(`${BASE}/auth/logout/refresh`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${refreshToken}`
                    }
                });
            } catch (_) { }
        }

        clearTokens();
        window.location.href = '/';
    }

    /* ── User endpoints ──────────────────────────────── */
    async function getProfile() {
        return request('GET', '/users/me');
    }

    /* ── Transaction endpoints ───────────────────────── */
    async function getTransactions() {
        return request('GET', '/transactions/');
    }

    async function deposit(amount) {
        return request('POST', '/transactions/deposit', { amount: amount.toString() });
    }

    async function withdraw(amount) {
        return request('POST', '/transactions/withdrawal', { amount: amount.toString() });
    }

    async function transfer(recipientUsername, amount) {
        return request('POST', '/transactions/transfer', {
            recipient_username: recipientUsername,
            amount: amount.toString()
        });
    }

    return {
        login, register, logout,
        getProfile, getTransactions,
        deposit, withdraw, transfer,
        isAuthenticated, clearTokens
    };
})();

