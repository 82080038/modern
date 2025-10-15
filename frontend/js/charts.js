/**
 * Lightweight Charts Integration dengan Technical Indicators
 * Trading Platform Modern
 */
class TradingCharts {
    constructor() {
        this.charts = new Map();
        this.indicators = new Map();
        this.symbols = new Map();
        this.timeframes = ['1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M'];
        this.availableIndicators = [
            'SMA', 'EMA', 'WMA', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic',
            'Williams %R', 'CCI', 'ATR', 'ADX', 'Parabolic SAR', 'Ichimoku',
            'Volume Profile', 'Pivot Points', 'Fibonacci Retracement'
        ];
        this.init();
    }
    
    init() {
        this.loadLightweightCharts();
        this.setupEventListeners();
        this.initializeIndicators();
    }
    
    async loadLightweightCharts() {
        // Load Lightweight Charts library
        if (typeof LightweightCharts === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js';
            script.onload = () => {
                console.log('Lightweight Charts loaded');
                this.initializeCharts();
            };
            document.head.appendChild(script);
        } else {
            this.initializeCharts();
        }
    }
    
    initializeCharts() {
        // Initialize main chart container
        const chartContainer = document.getElementById('main-chart');
        if (chartContainer) {
            this.createMainChart(chartContainer);
        }
        
        // Initialize multi-chart layout
        this.createMultiChartLayout();
    }
    
    createMainChart(container) {
        const chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 400,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#333',
            },
            grid: {
                vertLines: {
                    color: '#f0f0f0',
                },
                horzLines: {
                    color: '#f0f0f0',
                },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#cccccc',
            },
            timeScale: {
                borderColor: '#cccccc',
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        // Create candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderDownColor: '#ef5350',
            borderUpColor: '#26a69a',
            wickDownColor: '#ef5350',
            wickUpColor: '#26a69a',
        });
        
        // Create volume series
        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        });
        
        this.charts.set('main', {
            chart: chart,
            candlestickSeries: candlestickSeries,
            volumeSeries: volumeSeries,
            indicators: new Map()
        });
        
        return chart;
    }
    
    createMultiChartLayout() {
        const layouts = [
            { id: 'layout-1', name: 'Single Chart', charts: 1 },
            { id: 'layout-2', name: '2 Charts', charts: 2 },
            { id: 'layout-4', name: '4 Charts', charts: 4 },
            { id: 'layout-6', name: '6 Charts', charts: 6 }
        ];
        
        layouts.forEach(layout => {
            this.createLayout(layout);
        });
    }
    
    createLayout(layout) {
        const container = document.getElementById(`chart-layout-${layout.charts}`);
        if (!container) return;
        
        const charts = [];
        for (let i = 0; i < layout.charts; i++) {
            const chartContainer = document.createElement('div');
            chartContainer.id = `chart-${layout.id}-${i}`;
            chartContainer.style.width = '100%';
            chartContainer.style.height = '300px';
            chartContainer.style.marginBottom = '10px';
            container.appendChild(chartContainer);
            
            const chart = this.createMainChart(chartContainer);
            charts.push(chart);
        }
        
        this.charts.set(layout.id, charts);
    }
    
    async loadChartData(symbol, timeframe = '1D', period = 100) {
        try {
            const response = await fetch(`/api/v1/market-data/candlestick/${symbol}?timeframe=${timeframe}&limit=${period}`);
            const data = await response.json();
            
            if (data && data.length > 0) {
                this.updateChartData('main', data);
                this.symbols.set('main', { symbol, timeframe, data });
                return data;
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
        return null;
    }
    
    updateChartData(chartId, data) {
        const chartInfo = this.charts.get(chartId);
        if (!chartInfo) return;
        
        // Convert data to Lightweight Charts format
        const candlestickData = data.map(item => ({
            time: new Date(item.timestamp).getTime() / 1000,
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close
        }));
        
        const volumeData = data.map(item => ({
            time: new Date(item.timestamp).getTime() / 1000,
            value: item.volume,
            color: item.close >= item.open ? '#26a69a' : '#ef5350'
        }));
        
        // Update series
        chartInfo.candlestickSeries.setData(candlestickData);
        chartInfo.volumeSeries.setData(volumeData);
        
        // Fit content
        chartInfo.chart.timeScale().fitContent();
    }
    
    addIndicator(chartId, indicatorType, params = {}) {
        const chartInfo = this.charts.get(chartId);
        if (!chartInfo) return;
        
        const indicatorId = `${indicatorType}_${Date.now()}`;
        
        switch (indicatorType) {
            case 'SMA':
                this.addSMA(chartInfo, indicatorId, params);
                break;
            case 'EMA':
                this.addEMA(chartInfo, indicatorId, params);
                break;
            case 'RSI':
                this.addRSI(chartInfo, indicatorId, params);
                break;
            case 'MACD':
                this.addMACD(chartInfo, indicatorId, params);
                break;
            case 'Bollinger Bands':
                this.addBollingerBands(chartInfo, indicatorId, params);
                break;
            case 'Volume Profile':
                this.addVolumeProfile(chartInfo, indicatorId, params);
                break;
            default:
                console.warn(`Indicator ${indicatorType} not implemented`);
        }
        
        return indicatorId;
    }
    
    addSMA(chartInfo, indicatorId, params) {
        const period = params.period || 20;
        const color = params.color || '#ff6b6b';
        
        const smaSeries = chartInfo.chart.addLineSeries({
            color: color,
            lineWidth: 2,
            title: `SMA(${period})`
        });
        
        // Calculate SMA
        const data = this.symbols.get('main')?.data || [];
        const smaData = this.calculateSMA(data, period);
        
        smaSeries.setData(smaData);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'SMA',
            series: smaSeries,
            params: params
        });
    }
    
    addEMA(chartInfo, indicatorId, params) {
        const period = params.period || 20;
        const color = params.color || '#4ecdc4';
        
        const emaSeries = chartInfo.chart.addLineSeries({
            color: color,
            lineWidth: 2,
            title: `EMA(${period})`
        });
        
        const data = this.symbols.get('main')?.data || [];
        const emaData = this.calculateEMA(data, period);
        
        emaSeries.setData(emaData);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'EMA',
            series: emaSeries,
            params: params
        });
    }
    
    addRSI(chartInfo, indicatorId, params) {
        const period = params.period || 14;
        const color = params.color || '#ff9f43';
        
        // Create RSI chart in separate pane
        const rsiChart = LightweightCharts.createChart(document.createElement('div'), {
            width: 400,
            height: 150,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#333',
            },
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
            rightPriceScale: {
                borderColor: '#cccccc',
            },
            timeScale: {
                borderColor: '#cccccc',
            },
        });
        
        const rsiSeries = rsiChart.addLineSeries({
            color: color,
            lineWidth: 2,
            title: `RSI(${period})`
        });
        
        const data = this.symbols.get('main')?.data || [];
        const rsiData = this.calculateRSI(data, period);
        
        rsiSeries.setData(rsiData);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'RSI',
            chart: rsiChart,
            series: rsiSeries,
            params: params
        });
    }
    
    addMACD(chartInfo, indicatorId, params) {
        const fastPeriod = params.fastPeriod || 12;
        const slowPeriod = params.slowPeriod || 26;
        const signalPeriod = params.signalPeriod || 9;
        
        const macdSeries = chartInfo.chart.addLineSeries({
            color: '#ff6b6b',
            lineWidth: 2,
            title: 'MACD'
        });
        
        const signalSeries = chartInfo.chart.addLineSeries({
            color: '#4ecdc4',
            lineWidth: 2,
            title: 'Signal'
        });
        
        const data = this.symbols.get('main')?.data || [];
        const macdData = this.calculateMACD(data, fastPeriod, slowPeriod, signalPeriod);
        
        macdSeries.setData(macdData.macd);
        signalSeries.setData(macdData.signal);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'MACD',
            series: [macdSeries, signalSeries],
            params: params
        });
    }
    
    addBollingerBands(chartInfo, indicatorId, params) {
        const period = params.period || 20;
        const stdDev = params.stdDev || 2;
        
        const upperBand = chartInfo.chart.addLineSeries({
            color: '#ff6b6b',
            lineWidth: 1,
            title: 'Upper Band'
        });
        
        const middleBand = chartInfo.chart.addLineSeries({
            color: '#4ecdc4',
            lineWidth: 1,
            title: 'Middle Band'
        });
        
        const lowerBand = chartInfo.chart.addLineSeries({
            color: '#ff6b6b',
            lineWidth: 1,
            title: 'Lower Band'
        });
        
        const data = this.symbols.get('main')?.data || [];
        const bbData = this.calculateBollingerBands(data, period, stdDev);
        
        upperBand.setData(bbData.upper);
        middleBand.setData(bbData.middle);
        lowerBand.setData(bbData.lower);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'Bollinger Bands',
            series: [upperBand, middleBand, lowerBand],
            params: params
        });
    }
    
    addVolumeProfile(chartInfo, indicatorId, params) {
        const bins = params.bins || 20;
        const data = this.symbols.get('main')?.data || [];
        const vpData = this.calculateVolumeProfile(data, bins);
        
        // Create volume profile visualization
        const vpSeries = chartInfo.chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: 'volume-profile',
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
        });
        
        vpSeries.setData(vpData);
        
        chartInfo.indicators.set(indicatorId, {
            type: 'Volume Profile',
            series: vpSeries,
            params: params
        });
    }
    
    // Technical Analysis Calculations
    calculateSMA(data, period) {
        const sma = [];
        for (let i = period - 1; i < data.length; i++) {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j].close;
            }
            sma.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: sum / period
            });
        }
        return sma;
    }
    
    calculateEMA(data, period) {
        const ema = [];
        const multiplier = 2 / (period + 1);
        
        // First EMA is SMA
        let sum = 0;
        for (let i = 0; i < period; i++) {
            sum += data[i].close;
        }
        ema.push({
            time: new Date(data[period - 1].timestamp).getTime() / 1000,
            value: sum / period
        });
        
        // Calculate EMA for remaining data
        for (let i = period; i < data.length; i++) {
            const emaValue = (data[i].close * multiplier) + (ema[ema.length - 1].value * (1 - multiplier));
            ema.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: emaValue
            });
        }
        return ema;
    }
    
    calculateRSI(data, period) {
        const rsi = [];
        const gains = [];
        const losses = [];
        
        // Calculate price changes
        for (let i = 1; i < data.length; i++) {
            const change = data[i].close - data[i - 1].close;
            gains.push(change > 0 ? change : 0);
            losses.push(change < 0 ? Math.abs(change) : 0);
        }
        
        // Calculate initial average gain and loss
        let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
        let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;
        
        for (let i = period; i < data.length; i++) {
            avgGain = ((avgGain * (period - 1)) + gains[i - 1]) / period;
            avgLoss = ((avgLoss * (period - 1)) + losses[i - 1]) / period;
            
            const rs = avgGain / avgLoss;
            const rsiValue = 100 - (100 / (1 + rs));
            
            rsi.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: rsiValue
            });
        }
        return rsi;
    }
    
    calculateMACD(data, fastPeriod, slowPeriod, signalPeriod) {
        const fastEMA = this.calculateEMA(data, fastPeriod);
        const slowEMA = this.calculateEMA(data, slowPeriod);
        
        const macd = [];
        const signal = [];
        
        // Calculate MACD line
        for (let i = 0; i < fastEMA.length; i++) {
            if (i < slowEMA.length) {
                macd.push({
                    time: fastEMA[i].time,
                    value: fastEMA[i].value - slowEMA[i].value
                });
            }
        }
        
        // Calculate signal line (EMA of MACD)
        const signalEMA = this.calculateEMA(macd, signalPeriod);
        
        return {
            macd: macd,
            signal: signalEMA
        };
    }
    
    calculateBollingerBands(data, period, stdDev) {
        const sma = this.calculateSMA(data, period);
        const upper = [];
        const middle = [];
        const lower = [];
        
        for (let i = period - 1; i < data.length; i++) {
            const smaValue = sma[i - period + 1].value;
            let sum = 0;
            
            for (let j = 0; j < period; j++) {
                sum += Math.pow(data[i - j].close - smaValue, 2);
            }
            
            const std = Math.sqrt(sum / period);
            const upperValue = smaValue + (std * stdDev);
            const lowerValue = smaValue - (std * stdDev);
            
            upper.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: upperValue
            });
            
            middle.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: smaValue
            });
            
            lower.push({
                time: new Date(data[i].timestamp).getTime() / 1000,
                value: lowerValue
            });
        }
        
        return { upper, middle, lower };
    }
    
    calculateVolumeProfile(data, bins) {
        const prices = data.map(d => d.close);
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const priceRange = maxPrice - minPrice;
        const binSize = priceRange / bins;
        
        const vp = [];
        for (let i = 0; i < bins; i++) {
            const priceLevel = minPrice + (i * binSize);
            let volume = 0;
            
            data.forEach(d => {
                if (d.close >= priceLevel && d.close < priceLevel + binSize) {
                    volume += d.volume;
                }
            });
            
            if (volume > 0) {
                vp.push({
                    time: new Date(data[0].timestamp).getTime() / 1000,
                    value: volume,
                    color: volume > 0 ? '#26a69a' : '#ef5350'
                });
            }
        }
        
        return vp;
    }
    
    removeIndicator(chartId, indicatorId) {
        const chartInfo = this.charts.get(chartId);
        if (!chartInfo) return;
        
        const indicator = chartInfo.indicators.get(indicatorId);
        if (!indicator) return;
        
        if (indicator.series) {
            if (Array.isArray(indicator.series)) {
                indicator.series.forEach(series => series.remove());
            } else {
                indicator.series.remove();
            }
        }
        
        if (indicator.chart) {
            indicator.chart.remove();
        }
        
        chartInfo.indicators.delete(indicatorId);
    }
    
    setupEventListeners() {
        // Chart interaction events
        document.addEventListener('chart-click', (event) => {
            console.log('Chart clicked:', event.detail);
        });
        
        // Indicator management
        document.addEventListener('add-indicator', (event) => {
            const { chartId, indicatorType, params } = event.detail;
            this.addIndicator(chartId, indicatorType, params);
        });
        
        document.addEventListener('remove-indicator', (event) => {
            const { chartId, indicatorId } = event.detail;
            this.removeIndicator(chartId, indicatorId);
        });
    }
    
    initializeIndicators() {
        // Initialize default indicators
        this.indicators.set('default', [
            { type: 'SMA', period: 20, color: '#ff6b6b' },
            { type: 'EMA', period: 20, color: '#4ecdc4' },
            { type: 'RSI', period: 14, color: '#ff9f43' }
        ]);
    }
    
    getAvailableIndicators() {
        return this.availableIndicators;
    }
    
    getChartInfo(chartId) {
        return this.charts.get(chartId);
    }
    
    resizeChart(chartId) {
        const chartInfo = this.charts.get(chartId);
        if (chartInfo && chartInfo.chart) {
            chartInfo.chart.applyOptions({
                width: chartInfo.chart.container().clientWidth,
                height: chartInfo.chart.container().clientHeight
            });
        }
    }
    
    // Pattern Recognition
    detectPatterns(data) {
        const patterns = [];
        
        // Simple pattern detection
        for (let i = 2; i < data.length - 2; i++) {
            const current = data[i];
            const prev = data[i - 1];
            const next = data[i + 1];
            
            // Doji pattern
            if (Math.abs(current.open - current.close) < (current.high - current.low) * 0.1) {
                patterns.push({
                    type: 'Doji',
                    index: i,
                    timestamp: current.timestamp,
                    confidence: 0.8
                });
            }
            
            // Hammer pattern
            if (current.close > current.open && 
                (current.close - current.open) > (current.high - current.close) * 2) {
                patterns.push({
                    type: 'Hammer',
                    index: i,
                    timestamp: current.timestamp,
                    confidence: 0.7
                });
            }
        }
        
        return patterns;
    }
    
    // Drawing Tools
    addDrawingTool(chartId, toolType, params) {
        const chartInfo = this.charts.get(chartId);
        if (!chartInfo) return;
        
        switch (toolType) {
            case 'trendline':
                this.addTrendline(chartInfo, params);
                break;
            case 'horizontal':
                this.addHorizontalLine(chartInfo, params);
                break;
            case 'fibonacci':
                this.addFibonacciRetracement(chartInfo, params);
                break;
        }
    }
    
    addTrendline(chartInfo, params) {
        const { startTime, endTime, startPrice, endPrice, color = '#ff6b6b' } = params;
        
        const trendline = chartInfo.chart.addLineSeries({
            color: color,
            lineWidth: 2,
            title: 'Trendline'
        });
        
        trendline.setData([
            { time: startTime, value: startPrice },
            { time: endTime, value: endPrice }
        ]);
        
        return trendline;
    }
    
    addHorizontalLine(chartInfo, params) {
        const { price, color = '#4ecdc4' } = params;
        
        const hline = chartInfo.chart.addLineSeries({
            color: color,
            lineWidth: 1,
            title: 'Horizontal Line'
        });
        
        const data = this.symbols.get('main')?.data || [];
        if (data.length > 0) {
            hline.setData([
                { time: new Date(data[0].timestamp).getTime() / 1000, value: price },
                { time: new Date(data[data.length - 1].timestamp).getTime() / 1000, value: price }
            ]);
        }
        
        return hline;
    }
    
    addFibonacciRetracement(chartInfo, params) {
        const { startTime, endTime, startPrice, endPrice } = params;
        const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
        const priceRange = endPrice - startPrice;
        
        const fibLines = [];
        levels.forEach(level => {
            const price = startPrice + (priceRange * level);
            const fibLine = chartInfo.chart.addLineSeries({
                color: '#ff6b6b',
                lineWidth: 1,
                title: `Fib ${(level * 100).toFixed(1)}%`
            });
            
            fibLine.setData([
                { time: startTime, value: price },
                { time: endTime, value: price }
            ]);
            
            fibLines.push(fibLine);
        });
        
        return fibLines;
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tradingCharts = new TradingCharts();
});

// Export for global use
window.TradingCharts = TradingCharts;
