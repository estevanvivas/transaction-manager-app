/* ═══════════════════════════════════════════════════════
   Dashboard – Main Application Logic
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // Guard: redirigir si no está autenticado
    if (!API.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    /* ── State ───────────────────────────────────────── */
    let currentUser = null;
    let transactions = [];

    /* ── DOM refs ─────────────────────────────────────── */
    const userNameEl       = document.getElementById('user-name');
    const userEmailEl      = document.getElementById('user-email');
    const userAvatarEl     = document.getElementById('user-avatar');
    const balanceEl        = document.getElementById('balance-amount');
    const transactionsList = document.getElementById('transactions-list');
    const transactionsEmpty = document.getElementById('transactions-empty');
    const logoutBtn        = document.getElementById('logout-btn');
    const refreshBtn       = document.getElementById('refresh-btn');

    /* ── Modal refs ───────────────────────────────────── */
    const modal           = document.getElementById('transaction-modal');
    const modalTitle      = document.getElementById('modal-title');
    const modalForm       = document.getElementById('modal-form');
    const modalAmount     = document.getElementById('modal-amount');
    const modalRecipient  = document.getElementById('modal-recipient');
    const recipientGroup  = document.getElementById('recipient-group');
    const modalSubmitBtn  = document.getElementById('modal-submit');
    const modalCancelBtn  = document.getElementById('modal-cancel');
    const modalCloseBtn   = document.getElementById('modal-close');

    let currentAction = '';

    /* ── Init ────────────────────────────────────────── */
    loadDashboard();

    /* ── Load all data ───────────────────────────────── */
    async function loadDashboard() {
        try {
            const [profileRes, txRes] = await Promise.all([
                API.getProfile(),
                API.getTransactions()
            ]);

            currentUser = profileRes.data;
            transactions = txRes.data || [];

            renderProfile();
            renderTransactions();
        } catch (err) {
            Toast.error('Error al cargar los datos. Intenta de nuevo.');
            if (err.status === 401) {
                API.clearTokens();
                window.location.href = '/login';
            }
        }
    }

    /* ── Render profile ──────────────────────────────── */
    function renderProfile() {
        if (!currentUser) return;
        userNameEl.textContent = currentUser.username;
        userEmailEl.textContent = currentUser.email;
        userAvatarEl.textContent = currentUser.username.charAt(0).toUpperCase();

        const balance = parseFloat(currentUser.balance);
        balanceEl.textContent = formatCurrency(balance);

        // Update balance color
        balanceEl.className = balance >= 0
            ? 'text-4xl md:text-5xl font-bold text-emerald-400 tracking-tight'
            : 'text-4xl md:text-5xl font-bold text-red-400 tracking-tight';
    }

    /* ── Render transactions ─────────────────────────── */
    function renderTransactions() {
        transactionsList.innerHTML = '';

        if (!transactions.length) {
            transactionsEmpty.classList.remove('hidden');
            return;
        }
        transactionsEmpty.classList.add('hidden');

        // Sort by date desc
        const sorted = [...transactions].sort((a, b) =>
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        sorted.forEach((tx, i) => {
            const el = createTransactionItem(tx, i);
            transactionsList.appendChild(el);
        });
    }

    function createTransactionItem(tx, index) {
        const div = document.createElement('div');
        div.className = `transaction-item flex items-center justify-between p-4 rounded-xl border border-white/5 animate-fade-in-up`;
        div.style.animationDelay = `${index * 0.05}s`;

        const config = getTransactionConfig(tx.type);
        const amount = parseFloat(tx.amount);
        const commission = parseFloat(tx.commission || 0);
        const date = new Date(tx.timestamp);

        let details = '';
        if (tx.type === 'transfer_send' && tx.recipient_username) {
            details = `<span class="text-xs text-white/40">→ ${tx.recipient_username}</span>`;
        } else if (tx.type === 'transfer_receive' && tx.sender_username) {
            details = `<span class="text-xs text-white/40">← ${tx.sender_username}</span>`;
        }

        div.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl ${config.bg} flex items-center justify-center flex-shrink-0">
                    ${config.icon}
                </div>
                <div>
                    <p class="text-sm font-medium text-white/90">${config.label}</p>
                    ${details}
                    <p class="text-xs text-white/40 mt-0.5">${formatDate(date)}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-sm font-semibold ${config.color}">
                    ${config.sign} ${formatCurrency(amount)}
                </p>
                ${commission > 0 ? `<p class="text-xs text-white/30">Comisión: ${formatCurrency(commission)}</p>` : ''}
                <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full ${tx.status === 'completed' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'}">${tx.status}</span>
            </div>
        `;

        return div;
    }

    function getTransactionConfig(type) {
        const configs = {
            deposit: {
                label: 'Depósito',
                icon: '<svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m0 0l-4-4m4 4l4-4"/></svg>',
                bg: 'bg-emerald-500/15',
                color: 'text-emerald-400',
                sign: '+'
            },
            withdrawal: {
                label: 'Retiro',
                icon: '<svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20V4m0 0l-4 4m4-4l4 4"/></svg>',
                bg: 'bg-red-500/15',
                color: 'text-red-400',
                sign: '-'
            },
            transfer_send: {
                label: 'Transferencia Enviada',
                icon: '<svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>',
                bg: 'bg-orange-500/15',
                color: 'text-orange-400',
                sign: '-'
            },
            transfer_receive: {
                label: 'Transferencia Recibida',
                icon: '<svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16l-4-4m0 0l4-4m-4 4h18"/></svg>',
                bg: 'bg-blue-500/15',
                color: 'text-blue-400',
                sign: '+'
            }
        };
        return configs[type] || configs.deposit;
    }

    /* ── Modal controls ──────────────────────────────── */
    document.getElementById('btn-deposit').addEventListener('click', () => openModal('deposit'));
    document.getElementById('btn-withdraw').addEventListener('click', () => openModal('withdraw'));
    document.getElementById('btn-transfer').addEventListener('click', () => openModal('transfer'));

    function openModal(action) {
        currentAction = action;
        modalAmount.value = '';
        modalRecipient.value = '';

        const titles = {
            deposit:  'Realizar Depósito',
            withdraw: 'Realizar Retiro',
            transfer: 'Realizar Transferencia'
        };

        const btnTexts = {
            deposit:  'Depositar',
            withdraw: 'Retirar',
            transfer: 'Transferir'
        };

        modalTitle.textContent = titles[action];
        modalSubmitBtn.textContent = btnTexts[action];

        if (action === 'transfer') {
            recipientGroup.classList.remove('hidden');
            modalRecipient.required = true;
        } else {
            recipientGroup.classList.add('hidden');
            modalRecipient.required = false;
        }

        modal.classList.add('active');
        setTimeout(() => modalAmount.focus(), 300);
    }

    function closeModal() {
        modal.classList.remove('active');
        currentAction = '';
    }

    modalCancelBtn.addEventListener('click', closeModal);
    modalCloseBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    /* ── Transaction form submit ─────────────────────── */
    modalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const amount = parseFloat(modalAmount.value);

        if (!amount || amount <= 0) {
            Toast.warning('Ingresa un monto válido.');
            return;
        }

        modalSubmitBtn.disabled = true;
        modalSubmitBtn.innerHTML = '<div class="spinner mx-auto"></div>';

        try {
            let res;
            switch (currentAction) {
                case 'deposit':
                    res = await API.deposit(amount);
                    break;
                case 'withdraw':
                    res = await API.withdraw(amount);
                    break;
                case 'transfer':
                    const recipient = modalRecipient.value.trim();
                    if (!recipient) {
                        Toast.warning('Ingresa el usuario destinatario.');
                        return;
                    }
                    res = await API.transfer(recipient, amount);
                    break;
            }

            Toast.success(res.message || 'Operación exitosa.');
            closeModal();
        } catch (err) {
            const msg = err.details
                ? Object.values(err.details).flat().join(' ')
                : err.message;
            Toast.error(msg || 'Error en la operación.');
        } finally {
            modalSubmitBtn.disabled = false;
            const btnTexts = { deposit: 'Depositar', withdraw: 'Retirar', transfer: 'Transferir' };
            modalSubmitBtn.textContent = btnTexts[currentAction] || 'Confirmar';
            await loadDashboard();
        }
    });

    /* ── Logout ──────────────────────────────────────── */
    logoutBtn.addEventListener('click', async () => {
        logoutBtn.disabled = true;
        const originalHTML = logoutBtn.innerHTML;
        logoutBtn.innerHTML = '<div class="spinner mx-auto"></div>';

        try {
            await API.logout();
        } catch (_) {
            // En caso de error inesperado, limpiar igual y redirigir
            API.clearTokens();
            window.location.href = '/';
        } finally {
            logoutBtn.disabled = false;
            logoutBtn.innerHTML = originalHTML;
        }
    });

    /* ── Refresh ─────────────────────────────────────── */
    refreshBtn.addEventListener('click', async () => {
        refreshBtn.classList.add('animate-spin');
        await loadDashboard();
        setTimeout(() => refreshBtn.classList.remove('animate-spin'), 600);
        Toast.info('Datos actualizados.');
    });

    /* ── Helpers ──────────────────────────────────────── */
    function formatCurrency(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2
        }).format(amount);
    }

    function formatDate(date) {
        return new Intl.DateTimeFormat('es-CO', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    /* ── Keyboard shortcut ───────────────────────────── */
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
});

