# Panduan Fitur Trading - Time Lapse Simulator

## 🚀 **Fitur Trading Baru**

### 1. **Informasi Tanggal**
- **Start Date:** Tanggal mulai simulasi
- **Current Date:** Tanggal sedang diproses
- **End Date:** Tanggal akhir simulasi
- **Progress:** Persentase simulasi yang sudah selesai

### 2. **Informasi Modal & P&L**
- **Initial Capital:** Modal awal ($100,000)
- **Current Capital:** Modal saat ini
- **Total P&L:** Total untung/rugi
- **Return %:** Persentase return

### 3. **Pengambilan Keputusan Trading**
- **Symbol:** Saham yang diperdagangkan (AAPL, GOOGL, MSFT, TSLA, AMZN)
- **Action:** BUY, SELL, atau HOLD
- **Quantity:** Jumlah saham
- **Price:** Harga per saham
- **Reason:** Alasan keputusan trading
- **Confidence:** Tingkat kepercayaan (60-95%)

### 4. **History Trading**
- **Total Trades:** Jumlah total transaksi
- **Win Rate:** Persentase transaksi yang menguntungkan
- **Winning Trades:** Jumlah transaksi menguntungkan
- **Losing Trades:** Jumlah transaksi merugikan

## 📊 **Cara Menggunakan**

### **1. Start Simulasi**
1. Buka `http://localhost:5001`
2. Set tanggal mulai dan jumlah hari
3. Klik "Start Simulation"
4. Lihat informasi trading real-time

### **2. Monitor Trading Performance**
- **Trading Performance Card:** Menampilkan modal dan P&L
- **Recent Trading Decisions:** Keputusan trading terbaru
- **Trading History Summary:** Statistik trading

### **3. Analisis Data**
- **Date Information:** Track progress simulasi
- **Trading Decisions:** Detail setiap keputusan
- **Performance Metrics:** Win rate, total trades, dll

## 🎯 **Fitur Utama**

### **Real-time Updates**
- Informasi trading terupdate otomatis
- Status modal berubah setiap sesi
- P&L dihitung real-time

### **Trading Decisions**
- 3-7 keputusan per sesi trading
- Alasan keputusan yang realistis
- Confidence level untuk setiap keputusan

### **Performance Tracking**
- Modal awal: $100,000
- Simulasi P&L dengan volatilitas realistis
- Win rate calculation otomatis

## 📈 **Contoh Data Trading**

### **Trading Decision:**
```json
{
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": 50,
  "price": 150.25,
  "reason": "Technical signal: RSI oversold, MACD bullish crossover",
  "confidence": 0.85
}
```

### **Trading History:**
```json
{
  "total_capital": 100000,
  "current_capital": 102500,
  "total_pnl": 2500,
  "win_rate": 0.68,
  "total_trades": 150,
  "winning_trades": 102,
  "losing_trades": 48
}
```

## 🔧 **API Endpoints**

### **Simulation Status**
```bash
GET /api/simulation-status
```
Response:
```json
{
  "running": true,
  "start_date": "2024-01-01T00:00:00",
  "current_date": "2024-01-15T00:00:00",
  "end_date": "2024-01-30T00:00:00",
  "initial_capital": 100000,
  "current_capital": 102500,
  "total_pnl": 2500
}
```

### **Trading History**
```bash
GET /api/trading-history
```
Response:
```json
{
  "trades": [...],
  "total_trades": 150,
  "initial_capital": 100000,
  "current_capital": 102500,
  "total_pnl": 2500,
  "return_percentage": 2.5
}
```

### **Session Details**
```bash
GET /api/session/{session_id}
```
Response:
```json
{
  "session_id": "session_20240115",
  "date": "2024-01-15",
  "trading_decisions": [...],
  "trading_history": {...}
}
```

## 🎨 **UI Components**

### **Date Information**
- Grid layout dengan 3 kolom
- Start Date, Current Date, End Date
- Warna berbeda untuk current date

### **Trading Performance**
- 4 kolom: Initial Capital, Current Capital, Total P&L, Return %
- Warna hijau untuk profit, merah untuk loss
- Format currency dengan separator

### **Trading Decisions**
- List dengan border kiri berwarna
- BUY: hijau, SELL: merah, HOLD: kuning
- Informasi lengkap: symbol, action, quantity, price, reason, confidence

### **Trading History Summary**
- Grid 2x2: Total Trades, Win Rate, Winning Trades, Losing Trades
- Warna berbeda untuk setiap metric
- Font size besar untuk emphasis

## 🚀 **Cara Test**

### **1. Start Simulasi**
```bash
# Buka browser
http://localhost:5001

# Start simulasi 30 hari
# Klik "Start Simulation"
```

### **2. Monitor Real-time**
- Lihat date information terupdate
- Monitor trading performance
- Lihat trading decisions muncul
- Track trading history summary

### **3. Analisis Data**
- Klik session untuk detail
- Lihat trading decisions per session
- Analisis win rate dan performance

## 📋 **Checklist Fitur**

- [x] **Date Information:** Start, Current, End dates
- [x] **Capital Tracking:** Initial, Current, P&L
- [x] **Trading Decisions:** BUY/SELL/HOLD dengan reason
- [x] **Trading History:** Total trades, win rate, dll
- [x] **Real-time Updates:** SocketIO integration
- [x] **API Endpoints:** REST API untuk data
- [x] **UI Components:** Responsive design
- [x] **Performance Metrics:** Win rate, return %, dll

## 🎉 **Hasil Akhir**

Sekarang Time Lapse Simulator menampilkan:

1. **📅 Informasi Tanggal:** Start, Current, End dates
2. **💰 Modal & P&L:** Initial capital, current capital, total P&L
3. **📊 Trading Decisions:** Keputusan trading dengan reason dan confidence
4. **📈 Trading History:** Statistik lengkap trading performance
5. **🔄 Real-time Updates:** Semua informasi terupdate otomatis

**Sistem trading sudah lengkap dan siap digunakan!** 🚀
