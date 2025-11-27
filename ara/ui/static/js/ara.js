/* Copyright (c) 2025 The ARA Records Ansible authors
GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) */

(function() {
    'use strict';

    // =========================================================================
    // Theme Management (dark/light)
    // =========================================================================
    /* Inspired by https://getbootstrap.com/docs/5.3/customize/color-modes/#javascript */
    /*!
     * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
     * Copyright 2011-2023 The Bootstrap Authors
     * Licensed under the Creative Commons Attribution 3.0 Unported License.
     */

    var getStoredTheme = function() {
        return localStorage.getItem('theme');
    };

    var setStoredTheme = function(theme) {
        localStorage.setItem('theme', theme);
    };

    var getPreferredTheme = function() {
        var storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    var setTheme = function(theme) {
        var toggleBtn = document.getElementById('dark-light-toggle-btn');
        var pygmentsDark = document.getElementById('pygments-dark-css');
        var pygmentsLight = document.getElementById('pygments-light-css');

        if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme);
            if (toggleBtn) toggleBtn.setAttribute('checked', 'true');
        }

        if (theme === 'light') {
            if (toggleBtn) toggleBtn.removeAttribute('checked');
            if (pygmentsDark) pygmentsDark.disabled = true;
            if (pygmentsLight) pygmentsLight.disabled = false;
        } else {
            if (toggleBtn) toggleBtn.setAttribute('checked', 'true');
            if (pygmentsDark) pygmentsDark.disabled = false;
            if (pygmentsLight) pygmentsLight.disabled = true;
        }
    };

    // Set theme immediately (before DOMContentLoaded)
    setTheme(getPreferredTheme());

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
        var storedTheme = getStoredTheme();
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
            setTheme(getPreferredTheme());
        }
    });

    // =========================================================================
    // Auto-Refresh Feature
    // =========================================================================

    function AutoRefresh() {
        this.timeoutId = null;
        this.countdownId = null;
        this.badge = document.getElementById('refresh-badge');
        this.icon = document.getElementById('refresh-icon');
        this.dropdown = document.getElementById('auto-refresh');
        this.timeRemaining = 0;

        if (!this.dropdown) return;
        this.init();
    }

    AutoRefresh.prototype.init = function() {
        var self = this;

        this.dropdown.addEventListener('click', function(event) {
            var button = event.target.closest('[data-refresh-interval]');
            if (button) {
                var interval = parseInt(button.dataset.refreshInterval, 10);
                self.setRefreshInterval(interval);
                self.updateActiveState(button);
                self.updateBadge(interval);
            }
        });

        var savedInterval = localStorage.getItem('araRefreshInterval');
        if (savedInterval) {
            var interval = parseInt(savedInterval, 10);
            this.setRefreshInterval(interval);
            var btn = this.dropdown.querySelector('[data-refresh-interval="' + interval + '"]');
            if (btn) this.updateActiveState(btn);
            this.updateBadge(interval);
        }
    };

    AutoRefresh.prototype.setRefreshInterval = function(seconds) {
        var self = this;

        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        if (this.countdownId) {
            clearInterval(this.countdownId);
        }

        if (this.icon) this.icon.classList.remove('refresh-spin');
        localStorage.setItem('araRefreshInterval', seconds);

        if (seconds > 0) {
            this.timeRemaining = seconds;
            this.startCountdown();

            this.timeoutId = setInterval(function() {
                window.location.reload();
            }, seconds * 1000);
        }
    };

    AutoRefresh.prototype.startCountdown = function() {
        var self = this;

        this.countdownId = setInterval(function() {
            self.timeRemaining--;

            if (self.timeRemaining === 3 && self.icon) {
                self.icon.classList.add('refresh-spin');
            }

            if (self.timeRemaining <= 0) {
                clearInterval(self.countdownId);
                self.setRefreshInterval(parseInt(localStorage.getItem('araRefreshInterval'), 10));
            }
        }, 1000);
    };

    AutoRefresh.prototype.updateActiveState = function(activeButton) {
        var buttons = this.dropdown.querySelectorAll('[data-refresh-interval]');
        buttons.forEach(function(button) {
            button.classList.remove('active');
        });
        activeButton.classList.add('active');
    };

    AutoRefresh.prototype.updateBadge = function(seconds) {
        if (!this.badge) return;

        if (seconds === 0) {
            this.badge.textContent = '';
            this.badge.classList.add('d-none');
        } else {
            this.badge.classList.remove('d-none');
            this.badge.textContent = seconds < 60 ? seconds + 's' : (seconds / 60) + 'm';
        }
    };

    // =========================================================================
    // Copy to Clipboard
    // =========================================================================

    window.copyToClipboard = function(text) {
        var textToCopy = typeof text === 'string' ? text : JSON.stringify(text);

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy).then(function() {
                showCopyToast();
            }).catch(function(err) {
                console.error('Failed to copy:', err);
            });
        } else {
            var textArea = document.createElement('textarea');
            textArea.value = textToCopy;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showCopyToast();
            } catch (err) {
                console.error('Failed to copy:', err);
            }
            textArea.remove();
        }
    };

    function showCopyToast() {
        var toastEl = document.getElementById('copyToast');
        if (toastEl && typeof bootstrap !== 'undefined') {
            var toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 2000
            });
            toast.show();
        }
    }

    // =========================================================================
    // Tooltips
    // =========================================================================

    function initTooltips() {
        var tooltipTriggerList = document.querySelectorAll('[title]');
        tooltipTriggerList.forEach(function(el) {
            if (el.scrollWidth > el.clientWidth || el.hasAttribute('title')) {
                new bootstrap.Tooltip(el, {
                    placement: 'top',
                    trigger: 'hover'
                });
            }
        });
    }

    // =========================================================================
    // Host Facts Dashboard
    // =========================================================================

    function initHostFacts() {
        var searchInput = document.getElementById('factSearch');
        var clearButton = document.getElementById('clearSearch');
        var tableBody = document.getElementById('factsTableBody');
        var noResults = document.getElementById('noResults');
        var expandIcon = document.getElementById('expandIcon');
        var allFactsCollapse = document.getElementById('allFactsCollapse');
        var allInterfaces = document.getElementById('allInterfaces');
        var interfaceExpandIcon = document.getElementById('interfaceExpandIcon');

        // Handle interface expansion
        if (allInterfaces) {
            allInterfaces.addEventListener('show.bs.collapse', function() {
                if (interfaceExpandIcon) interfaceExpandIcon.className = 'bi bi-chevron-down';
            });

            allInterfaces.addEventListener('hide.bs.collapse', function() {
                if (interfaceExpandIcon) interfaceExpandIcon.className = 'bi bi-chevron-right';
            });
        }

        // Check for fact anchor in URL
        function checkForFactAnchor() {
            var hash = window.location.hash;

            var previousHighlighted = document.querySelectorAll('.fact-row-highlighted');
            previousHighlighted.forEach(function(row) {
                row.classList.remove('fact-row-highlighted');
            });

            if (hash && hash.length > 1) {
                var factId = hash.substring(1);
                var factElement = document.getElementById(factId);

                if (factElement && allFactsCollapse) {
                    if (!allFactsCollapse.classList.contains('show')) {
                        new bootstrap.Collapse(allFactsCollapse, { show: true });
                    }

                    setTimeout(function() {
                        factElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        var row = factElement.closest('tr');
                        if (row) {
                            row.classList.add('fact-row-highlighted');
                        }
                    }, 350);
                }
            }
        }

        checkForFactAnchor();
        window.addEventListener('hashchange', checkForFactAnchor);

        // Toggle icon when collapse opens/closes
        if (allFactsCollapse) {
            allFactsCollapse.addEventListener('show.bs.collapse', function() {
                expandIcon.className = 'bi bi-chevron-up';
                expandIcon.parentElement.querySelector('span').textContent = 'Hide All Facts';
            });

            allFactsCollapse.addEventListener('hide.bs.collapse', function() {
                expandIcon.className = 'bi bi-chevron-down';
                expandIcon.parentElement.querySelector('span').textContent = 'Show All Facts';
                var highlighted = document.querySelectorAll('.fact-row-highlighted');
                highlighted.forEach(function(row) {
                    row.classList.remove('fact-row-highlighted');
                });
            });
        }

        // Search functionality
        if (searchInput && tableBody) {
            function filterFacts() {
                var searchTerm = searchInput.value.toLowerCase().trim();
                var rows = tableBody.querySelectorAll('.fact-row-item');
                var visibleCount = 0;

                rows.forEach(function(row) {
                    var factName = row.dataset.factName;
                    var factContent = row.querySelector('.fact-name').textContent.toLowerCase();
                    var valueContent = row.querySelector('.fact-raw-value').textContent.toLowerCase();

                    if (searchTerm === '' ||
                        factName.indexOf(searchTerm) > -1 ||
                        factContent.indexOf(searchTerm) > -1 ||
                        valueContent.indexOf(searchTerm) > -1) {
                        row.style.display = '';
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });

                if (visibleCount === 0 && searchTerm !== '') {
                    noResults.style.display = 'block';
                    tableBody.style.display = 'none';
                } else {
                    noResults.style.display = 'none';
                    tableBody.style.display = '';
                }
            }

            searchInput.addEventListener('input', filterFacts);

            if (clearButton) {
                clearButton.addEventListener('click', function() {
                    searchInput.value = '';
                    filterFacts();
                    searchInput.focus();
                });
            }

            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    filterFacts();
                }
            });
        }
    }

    // =========================================================================
    // Single DOMContentLoaded listener
    // =========================================================================

    document.addEventListener('DOMContentLoaded', function() {
        // Theme toggle button
        var toggleBtn = document.getElementById('dark-light-toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
                    setTheme('light');
                    setStoredTheme('light');
                } else {
                    setTheme('dark');
                    setStoredTheme('dark');
                }
            });
        }

        new AutoRefresh();
        initTooltips();
        initHostFacts();
    });
})();
