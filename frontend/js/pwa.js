/**
 * PWA Helper untuk Trading Platform Modern
 * Development-friendly dengan cache control
 */
class PWAHelper {
    constructor() {
        this.isDevelopment = true; // Set to false in production
        this.registration = null;
        this.updateAvailable = false;
        this.init();
    }
    
    async init() {
        // Check if service worker is supported
        if ('serviceWorker' in navigator) {
            await this.registerServiceWorker();
            this.setupEventListeners();
        } else {
            console.log('Service Worker not supported');
        }
        
        // Check for updates
        this.checkForUpdates();
    }
    
    async registerServiceWorker() {
        try {
            this.registration = await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registered successfully');
            
            // Handle updates
            this.registration.addEventListener('updatefound', () => {
                const newWorker = this.registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.updateAvailable = true;
                        this.showUpdateNotification();
                    }
                });
            });
            
        } catch (error) {
            console.error('Service Worker registration failed:', error);
        }
    }
    
    setupEventListeners() {
        // Listen for service worker messages
        navigator.serviceWorker.addEventListener('message', (event) => {
            this.handleServiceWorkerMessage(event);
        });
        
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.showNotification('Connection restored', 'success');
            this.syncData();
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('You are offline', 'warning');
        });
        
        // Listen for beforeunload to save state
        window.addEventListener('beforeunload', () => {
            this.saveAppState();
        });
        
        // Listen for visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.onAppVisible();
            } else {
                this.onAppHidden();
            }
        });
    }
    
    handleServiceWorkerMessage(event) {
        const { type, data } = event.data;
        
        switch (type) {
            case 'CACHE_UPDATED':
                console.log('Cache updated:', data);
                break;
            case 'CACHE_ERROR':
                console.error('Cache error:', data);
                break;
            case 'UPDATE_AVAILABLE':
                this.updateAvailable = true;
                this.showUpdateNotification();
                break;
            default:
                console.log('Service Worker message:', type, data);
        }
    }
    
    async checkForUpdates() {
        if (this.registration) {
            try {
                await this.registration.update();
            } catch (error) {
                console.error('Update check failed:', error);
            }
        }
    }
    
    showUpdateNotification() {
        if (this.isDevelopment) {
            // In development, show console message
            console.log('Update available - refreshing page');
            this.applyUpdate();
        } else {
            // In production, show user notification
            if (confirm('A new version is available. Update now?')) {
                this.applyUpdate();
            }
        }
    }
    
    applyUpdate() {
        if (this.registration && this.registration.waiting) {
            this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
        }
    }
    
    async clearCache() {
        if (this.registration) {
            try {
                // Send message to service worker
                navigator.serviceWorker.controller.postMessage({
                    type: 'CLEAR_CACHE'
                });
                
                // Clear application cache
                if ('caches' in window) {
                    const cacheNames = await caches.keys();
                    await Promise.all(
                        cacheNames.map(cacheName => caches.delete(cacheName))
                    );
                }
                
                this.showNotification('Cache cleared', 'success');
            } catch (error) {
                console.error('Cache clear failed:', error);
                this.showNotification('Cache clear failed', 'error');
            }
        }
    }
    
    async updateCache() {
        if (this.registration) {
            try {
                navigator.serviceWorker.controller.postMessage({
                    type: 'UPDATE_CACHE'
                });
                this.showNotification('Cache updated', 'success');
            } catch (error) {
                console.error('Cache update failed:', error);
                this.showNotification('Cache update failed', 'error');
            }
        }
    }
    
    async getCacheStatus() {
        if (this.registration) {
            try {
                return new Promise((resolve) => {
                    const messageChannel = new MessageChannel();
                    messageChannel.port1.onmessage = (event) => {
                        resolve(event.data);
                    };
                    
                    navigator.serviceWorker.controller.postMessage({
                        type: 'GET_CACHE_STATUS'
                    }, [messageChannel.port2]);
                });
            } catch (error) {
                console.error('Get cache status failed:', error);
                return null;
            }
        }
    }
    
    async syncData() {
        // Sync data when coming back online
        try {
            // Sync trading data
            if (window.syncTradingData) {
                await window.syncTradingData();
            }
            
            // Sync notifications
            if (window.syncNotifications) {
                await window.syncNotifications();
            }
            
            console.log('Data sync completed');
        } catch (error) {
            console.error('Data sync failed:', error);
        }
    }
    
    saveAppState() {
        // Save current app state
        const appState = {
            currentPage: window.location.pathname,
            timestamp: Date.now(),
            userData: this.getUserData()
        };
        
        localStorage.setItem('appState', JSON.stringify(appState));
    }
    
    restoreAppState() {
        try {
            const appState = JSON.parse(localStorage.getItem('appState'));
            if (appState && Date.now() - appState.timestamp < 24 * 60 * 60 * 1000) { // 24 hours
                return appState;
            }
        } catch (error) {
            console.error('Failed to restore app state:', error);
        }
        return null;
    }
    
    getUserData() {
        // Get user data from localStorage or sessionStorage
        return {
            sessionId: localStorage.getItem('sessionId'),
            userId: localStorage.getItem('userId'),
            preferences: JSON.parse(localStorage.getItem('preferences') || '{}')
        };
    }
    
    onAppVisible() {
        // App became visible
        console.log('App visible');
        this.checkForUpdates();
        this.syncData();
    }
    
    onAppHidden() {
        // App became hidden
        console.log('App hidden');
        this.saveAppState();
    }
    
    showNotification(message, type = 'info') {
        // Show notification to user
        if (this.isDevelopment) {
            console.log(`[${type.toUpperCase()}] ${message}`);
        } else {
            // In production, show actual notification
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('Trading Platform', {
                    body: message,
                    icon: '/icons/icon-192x192.png'
                });
            }
        }
    }
    
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return false;
    }
    
    async installApp() {
        // Trigger app installation
        if (window.deferredPrompt) {
            window.deferredPrompt.prompt();
            const { outcome } = await window.deferredPrompt.userChoice;
            window.deferredPrompt = null;
            return outcome === 'accepted';
        }
        return false;
    }
    
    isAppInstalled() {
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone === true;
    }
    
    getAppInfo() {
        return {
            isInstalled: this.isAppInstalled(),
            isOnline: navigator.onLine,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            serviceWorkerSupported: 'serviceWorker' in navigator,
            notificationSupported: 'Notification' in window,
            pushSupported: 'PushManager' in window
        };
    }
    
    // Development helpers
    enableDevelopmentMode() {
        this.isDevelopment = true;
        console.log('PWA Development mode enabled');
        
        // Add development controls to console
        window.pwaDev = {
            clearCache: () => this.clearCache(),
            updateCache: () => this.updateCache(),
            getCacheStatus: () => this.getCacheStatus(),
            checkUpdates: () => this.checkForUpdates(),
            getAppInfo: () => this.getAppInfo()
        };
    }
    
    disableDevelopmentMode() {
        this.isDevelopment = false;
        console.log('PWA Development mode disabled');
    }
}

// Initialize PWA helper
const pwaHelper = new PWAHelper();

// Handle app installation
window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    window.deferredPrompt = event;
    
    // Show install button or notification
    if (pwaHelper.isDevelopment) {
        console.log('App installation available');
    }
});

// Handle app installed
window.addEventListener('appinstalled', () => {
    console.log('App installed successfully');
    pwaHelper.showNotification('App installed successfully', 'success');
});

// Export for global use
window.PWAHelper = PWAHelper;
window.pwaHelper = pwaHelper;

// Development mode detection
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    pwaHelper.enableDevelopmentMode();
}
