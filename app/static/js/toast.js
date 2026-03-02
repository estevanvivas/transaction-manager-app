/* ═══════════════════════════════════════════════════════
   Toast Notification System
   ═══════════════════════════════════════════════════════ */

const Toast = (() => {
    function _createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed top-6 right-6 z-[9999] flex flex-col gap-3';
            document.body.appendChild(container);
        }
        return container;
    }

    const icons = {
        success: `<svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`,
        error:   `<svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
        info:    `<svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z"/></svg>`,
        warning: `<svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86l-8.58 14.86A1 1 0 002.59 20h18.82a1 1 0 00.88-1.28L13.71 3.86a1 1 0 00-1.42 0z"/></svg>`
    };

    const bgColors = {
        success: 'border-emerald-500/30',
        error:   'border-red-500/30',
        info:    'border-blue-500/30',
        warning: 'border-amber-500/30'
    };

    function show(message, type = 'info', duration = 4000) {
        const container = _createContainer();

        const toast = document.createElement('div');
        toast.className = `glass border ${bgColors[type]} rounded-xl px-5 py-4 flex items-center gap-3 min-w-[320px] max-w-[420px] shadow-2xl transform translate-x-[120%] transition-transform duration-500`;
        toast.style.transitionTimingFunction = 'cubic-bezier(.34,1.56,.64,1)';

        toast.innerHTML = `
            <div class="flex-shrink-0">${icons[type]}</div>
            <p class="text-sm text-white/90 flex-1">${message}</p>
            <button onclick="this.closest('div').remove()" class="text-white/40 hover:text-white/80 transition-colors ml-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        `;

        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
        });

        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 500);
        }, duration);
    }

    return {
        success: (msg, dur) => show(msg, 'success', dur),
        error:   (msg, dur) => show(msg, 'error', dur),
        info:    (msg, dur) => show(msg, 'info', dur),
        warning: (msg, dur) => show(msg, 'warning', dur),
    };
})();

