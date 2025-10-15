/**
 * Dark Mode Implementation
 * Professional dark mode untuk trading platform
 */
class DarkModeManager {
    constructor() {
        this.isDarkMode = this.getStoredTheme() || this.getSystemPreference();
        this.init();
    }

    init() {
        this.applyTheme();
        this.createToggleButton();
        this.setupEventListeners();
        this.initializeCharts();
    }

    getStoredTheme() {
        return localStorage.getItem('darkMode') === 'true';
    }

    getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    applyTheme() {
        const body = document.body;
        const html = document.documentElement;
        
        if (this.isDarkMode) {
            body.classList.add('dark-mode');
            html.setAttribute('data-theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            html.setAttribute('data-theme', 'light');
        }
        
        // Update chart themes
        this.updateChartThemes();
        
        // Update toggle button
        this.updateToggleButton();
    }

    createToggleButton() {
        // Create dark mode toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'dark-mode-toggle';
        toggleButton.className = 'btn btn-outline-secondary position-fixed';
        toggleButton.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        `;
        
        // Add to page
        document.body.appendChild(toggleButton);
    }

    updateToggleButton() {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            toggleButton.innerHTML = this.isDarkMode ? '☀️' : '🌙';
        }
    }

    setupEventListeners() {
        // Toggle button click
        document.addEventListener('click', (e) => {
            if (e.target.id === 'dark-mode-toggle') {
                this.toggle();
            }
        });

        // System preference change
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('darkMode')) {
                this.isDarkMode = e.matches;
                this.applyTheme();
            }
        });

        // Keyboard shortcut (Ctrl/Cmd + D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    toggle() {
        this.isDarkMode = !this.isDarkMode;
        localStorage.setItem('darkMode', this.isDarkMode);
        this.applyTheme();
        
        // Show notification
        this.showThemeChangeNotification();
    }

    showThemeChangeNotification() {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info position-fixed';
        notification.style.cssText = `
            top: 80px;
            right: 20px;
            z-index: 1050;
            min-width: 200px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            ${this.isDarkMode ? 'Dark mode enabled' : 'Light mode enabled'}
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    initializeCharts() {
        // Initialize chart themes
        this.updateChartThemes();
    }

    updateChartThemes() {
        // Update Lightweight Charts themes
        if (window.charts) {
            window.charts.forEach(chart => {
                if (chart && chart.applyOptions) {
                    chart.applyOptions({
                        layout: {
                            background: {
                                type: 'solid',
                                color: this.isDarkMode ? '#1a1a1a' : '#ffffff'
                            },
                            textColor: this.isDarkMode ? '#ffffff' : '#000000'
                        },
                        grid: {
                            vertLines: {
                                color: this.isDarkMode ? '#333333' : '#e1e1e1'
                            },
                            horzLines: {
                                color: this.isDarkMode ? '#333333' : '#e1e1e1'
                            }
                        },
                        crosshair: {
                            mode: 0
                        },
                        rightPriceScale: {
                            borderColor: this.isDarkMode ? '#333333' : '#e1e1e1'
                        },
                        timeScale: {
                            borderColor: this.isDarkMode ? '#333333' : '#e1e1e1'
                        }
                    });
                }
            });
        }
    }

    // Public methods
    enable() {
        this.isDarkMode = true;
        localStorage.setItem('darkMode', 'true');
        this.applyTheme();
    }

    disable() {
        this.isDarkMode = false;
        localStorage.setItem('darkMode', 'false');
        this.applyTheme();
    }

    isEnabled() {
        return this.isDarkMode;
    }
}

// CSS untuk Dark Mode
const darkModeCSS = `
/* Dark Mode Styles */
.dark-mode {
    --bs-body-bg: #1a1a1a;
    --bs-body-color: #ffffff;
    --bs-primary: #0d6efd;
    --bs-secondary: #6c757d;
    --bs-success: #198754;
    --bs-info: #0dcaf0;
    --bs-warning: #ffc107;
    --bs-danger: #dc3545;
    --bs-light: #343a40;
    --bs-dark: #212529;
}

.dark-mode body {
    background-color: var(--bs-body-bg) !important;
    color: var(--bs-body-color) !important;
}

.dark-mode .card {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .card-header {
    background-color: #343a40 !important;
    border-bottom-color: #404040 !important;
}

.dark-mode .table {
    color: #ffffff !important;
}

.dark-mode .table-striped > tbody > tr:nth-of-type(odd) > td,
.dark-mode .table-striped > tbody > tr:nth-of-type(odd) > th {
    background-color: #2d2d2d !important;
}

.dark-mode .table-hover > tbody > tr:hover > td,
.dark-mode .table-hover > tbody > tr:hover > th {
    background-color: #404040 !important;
}

.dark-mode .nav-tabs {
    border-bottom-color: #404040 !important;
}

.dark-mode .nav-tabs .nav-link {
    color: #ffffff !important;
    border-color: transparent !important;
}

.dark-mode .nav-tabs .nav-link:hover {
    border-color: #404040 #404040 transparent !important;
}

.dark-mode .nav-tabs .nav-link.active {
    color: #ffffff !important;
    background-color: #2d2d2d !important;
    border-color: #404040 #404040 transparent !important;
}

.dark-mode .form-control {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .form-control:focus {
    background-color: #2d2d2d !important;
    border-color: #0d6efd !important;
    color: #ffffff !important;
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25) !important;
}

.dark-mode .btn-outline-secondary {
    color: #ffffff !important;
    border-color: #404040 !important;
}

.dark-mode .btn-outline-secondary:hover {
    background-color: #404040 !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .alert {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .modal-content {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .modal-header {
    border-bottom-color: #404040 !important;
}

.dark-mode .modal-footer {
    border-top-color: #404040 !important;
}

.dark-mode .dropdown-menu {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
}

.dark-mode .dropdown-item {
    color: #ffffff !important;
}

.dark-mode .dropdown-item:hover {
    background-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .list-group-item {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
    color: #ffffff !important;
}

.dark-mode .list-group-item:hover {
    background-color: #404040 !important;
}

.dark-mode .badge {
    color: #ffffff !important;
}

/* Chart specific dark mode */
.dark-mode .tradingview-widget-container {
    filter: invert(1) hue-rotate(180deg);
}

.dark-mode .tradingview-widget-container * {
    filter: invert(1) hue-rotate(180deg);
}

/* Custom dark mode styles */
.dark-mode .sidebar {
    background-color: #1a1a1a !important;
    border-right-color: #404040 !important;
}

.dark-mode .main-content {
    background-color: #1a1a1a !important;
}

.dark-mode .navbar {
    background-color: #2d2d2d !important;
    border-bottom-color: #404040 !important;
}

.dark-mode .navbar-brand,
.dark-mode .navbar-nav .nav-link {
    color: #ffffff !important;
}

.dark-mode .navbar-nav .nav-link:hover {
    color: #0d6efd !important;
}

/* Performance metrics dark mode */
.dark-mode .metric-card {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
}

.dark-mode .metric-value {
    color: #ffffff !important;
}

.dark-mode .metric-label {
    color: #cccccc !important;
}

/* Trading interface dark mode */
.dark-mode .trading-panel {
    background-color: #2d2d2d !important;
    border-color: #404040 !important;
}

.dark-mode .order-book {
    background-color: #1a1a1a !important;
}

.dark-mode .order-book .bid {
    background-color: rgba(0, 255, 0, 0.1) !important;
}

.dark-mode .order-book .ask {
    background-color: rgba(255, 0, 0, 0.1) !important;
}

/* Responsive dark mode */
@media (max-width: 768px) {
    .dark-mode #dark-mode-toggle {
        top: 10px;
        right: 10px;
        width: 40px;
        height: 40px;
        font-size: 1rem;
    }
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = darkModeCSS;
document.head.appendChild(style);

// Initialize Dark Mode Manager
const darkModeManager = new DarkModeManager();

// Export for global access
window.darkModeManager = darkModeManager;
