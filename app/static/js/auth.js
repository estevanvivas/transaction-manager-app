/* ═══════════════════════════════════════════════════════
   Auth Page – Login & Register Logic
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // Si ya está autenticado, redirigir al dashboard
    if (API.isAuthenticated()) {
        window.location.href = '/dashboard';
        return;
    }

    const loginTab    = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm   = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    /* ── Tab switching ───────────────────────────────── */
    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    });

    registerTab.addEventListener('click', () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    });

    /* ── Login handler ───────────────────────────────── */
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = loginForm.querySelector('button[type="submit"]');
        const email    = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;

        if (!email || !password) {
            Toast.warning('Por favor completa todos los campos.');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner mx-auto"></div>';

        try {
            await API.login(email, password);
            Toast.success('¡Bienvenido de vuelta!');
            setTimeout(() => window.location.href = '/dashboard', 800);
        } catch (err) {
            Toast.error(err.message || 'Error al iniciar sesión.');
            btn.disabled = false;
            btn.textContent = 'Iniciar Sesión';
        }
    });

    /* ── Register handler ────────────────────────────── */
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = registerForm.querySelector('button[type="submit"]');
        const username = document.getElementById('reg-username').value.trim();
        const email    = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;
        const confirm  = document.getElementById('reg-confirm').value;

        if (!username || !email || !password || !confirm) {
            Toast.warning('Por favor completa todos los campos.');
            return;
        }

        if (password !== confirm) {
            Toast.error('Las contraseñas no coinciden.');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner mx-auto"></div>';

        try {
            await API.register(username, email, password);
            Toast.success('¡Cuenta creada exitosamente! Inicia sesión.');
            // Switch to login tab
            loginTab.click();
            document.getElementById('login-email').value = email;
        } catch (err) {
            const msg = err.details
                ? Object.values(err.details).flat().join(' ')
                : err.message;
            Toast.error(msg || 'Error al registrarse.');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Crear Cuenta';
        }
    });

    /* ── Password visibility toggles ─────────────────── */
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            btn.innerHTML = isPassword
                ? '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9.27-3.11-11-7.5a11.72 11.72 0 014.57-5.39M9.88 9.88a3 3 0 104.24 4.24M1 1l22 22"/></svg>'
                : '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>';
        });
    });

    // Check URL params for auto-tab
    const params = new URLSearchParams(window.location.search);
    if (params.get('tab') === 'register') {
        registerTab.click();
    }
});

