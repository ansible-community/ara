class AutoRefresh {
    constructor() {
        this.timeoutId = null;
        this.countdownId = null;
        this.badge = document.getElementById('refresh-badge');
        this.icon = document.getElementById('refresh-icon');
        this.dropdown = document.getElementById('auto-refresh');
        this.timeRemaining = 0;
        this.init();
    }

    init() {
        this.dropdown.addEventListener('click', (event) => {
            const button = event.target.closest('[data-refresh-interval]');
            if (button) {
                const interval = parseInt(button.dataset.refreshInterval);
                this.setRefreshInterval(interval);
                this.updateActiveState(button);
                this.updateBadge(interval);
            }
        });

        const savedInterval = localStorage.getItem('araRefreshInterval');
        if (savedInterval) {
            const interval = parseInt(savedInterval);
            this.setRefreshInterval(interval);
            this.updateActiveState(this.dropdown.querySelector(`[data-refresh-interval="${interval}"]`));
            this.updateBadge(interval);
        }
    }

    setRefreshInterval(seconds) {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        if (this.countdownId) {
            clearInterval(this.countdownId);
        }

        this.icon.classList.remove('refresh-spin');
        localStorage.setItem('araRefreshInterval', seconds);

        if (seconds > 0) {
            this.timeRemaining = seconds;
            this.startCountdown();

            this.timeoutId = setInterval(() => {
                window.location.reload();
            }, seconds * 1000);
        }
    }

    startCountdown() {
        this.countdownId = setInterval(() => {
            this.timeRemaining--;

            if (this.timeRemaining === 3) {
                this.icon.classList.add('refresh-spin');
            }

            if (this.timeRemaining <= 0) {
                clearInterval(this.countdownId);
                this.setRefreshInterval(parseInt(localStorage.getItem('araRefreshInterval')));
            }
        }, 1000);
    }

    updateActiveState(activeButton) {
        const buttons = this.dropdown.querySelectorAll('[data-refresh-interval]');
        buttons.forEach(button => button.classList.remove('active'));
        activeButton.classList.add('active');
    }

    updateBadge(seconds) {
        if (seconds === 0) {
            this.badge.textContent = '';
            this.badge.classList.add('d-none');
        } else {
            this.badge.classList.remove('d-none');
            this.badge.textContent = seconds < 60 ? `${seconds}s` : `${seconds/60}m`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AutoRefresh();
});
