# Panduan Tombol Stop - Time Lapse Simulator

## 🛑 Cara Menggunakan Tombol Stop

### 1. **Tombol Stop di Web Interface**
- Buka `http://localhost:5001` di browser
- Klik tombol **"Stop"** (merah) untuk menghentikan simulasi
- Simulasi akan berhenti dengan aman di tengah-tengah proses

### 2. **API Endpoint untuk Stop**
```bash
curl -X POST http://localhost:5001/api/stop-simulation
```

### 3. **Cara Kerja Tombol Stop**

#### **Sebelum Perbaikan:**
- Tombol stop hanya mengatur flag `simulation_running = False`
- Simulasi di background thread tidak memeriksa flag ini
- Simulasi tetap berjalan sampai selesai

#### **Setelah Perbaikan:**
- Tombol stop mengatur flag `simulation_running = False`
- Simulasi memeriksa flag ini di setiap iterasi
- Simulasi berhenti segera setelah flag diatur

### 4. **Pengecekan Flag di Kode**

#### **Di Loop Utama:**
```python
for day in range(days):
    # Check if simulation should stop
    if not self.simulation_running:
        print(f"\nSimulation stopped by user at day {day + 1}")
        break
```

#### **Di Loop Modul:**
```python
for module_name in execution_order:
    # Check if simulation should stop
    if not self.simulation_running:
        print(f"\nSimulation stopped during {module_name}")
        break
```

### 5. **Status Simulasi**

#### **Mengecek Status:**
```bash
curl http://localhost:5001/api/simulation-status
```

#### **Response:**
```json
{
    "running": false,
    "sessions_count": 5,
    "current_session": null
}
```

### 6. **Test Tombol Stop**

#### **Manual Test:**
1. Start simulasi dengan 30 hari
2. Tunggu beberapa detik
3. Klik tombol "Stop"
4. Simulasi harus berhenti segera

#### **Programmatic Test:**
```python
# Test script
python test_stop_button.py
```

### 7. **Troubleshooting**

#### **Jika Tombol Stop Tidak Berfungsi:**
1. **Cek Status Server:**
   ```bash
   netstat -an | findstr :5001
   ```

2. **Restart Server:**
   ```bash
   # Stop server (Ctrl+C)
   python run_time_lapse_system.py
   ```

3. **Cek Log Console:**
   - Lihat pesan "Simulation stopped by user"
   - Pastikan flag `simulation_running` berubah ke `False`

### 8. **Fitur Tambahan**

#### **Graceful Shutdown:**
- Simulasi berhenti di tengah-tengah sesi dengan aman
- Data yang sudah diproses tetap tersimpan
- Tidak ada data corruption

#### **Real-time Updates:**
- Status simulasi terupdate real-time
- Web interface menampilkan status terkini
- SocketIO mengirim update otomatis

### 9. **Contoh Penggunaan**

#### **Scenario 1: Stop di Tengah Sesi**
```
Day 1: Processing market_data... COMPLETED
Day 1: Processing technical_analysis... COMPLETED
Day 1: Processing fundamental_analysis... COMPLETED
[USER CLICKS STOP]
Simulation stopped during sentiment_analysis
```

#### **Scenario 2: Stop di Antara Hari**
```
Day 1: All modules completed
Day 2: Processing market_data... COMPLETED
[USER CLICKS STOP]
Simulation stopped by user at day 3
```

### 10. **Best Practices**

#### **Untuk Developer:**
- Selalu cek flag `simulation_running` di loop
- Gunakan `break` untuk keluar dari loop
- Simpan data yang sudah diproses

#### **Untuk User:**
- Tunggu beberapa detik setelah klik stop
- Cek status di web interface
- Restart jika diperlukan

## ✅ **Verifikasi Tombol Stop Berfungsi**

### **Test Checklist:**
- [ ] Tombol stop terlihat di web interface
- [ ] Klik tombol stop menghentikan simulasi
- [ ] Status berubah dari "Running" ke "Stopped"
- [ ] Simulasi berhenti di tengah-tengah proses
- [ ] Data yang sudah diproses tersimpan
- [ ] Bisa start simulasi baru setelah stop

### **Expected Behavior:**
1. **Start Simulation** → Status: "Running"
2. **Click Stop** → Status: "Stopped"
3. **Simulation Stops** → Pesan: "Simulation stopped by user"
4. **Data Saved** → Sesi yang sudah selesai tersimpan
5. **Can Restart** → Bisa start simulasi baru

---

**Tombol stop sekarang berfungsi dengan baik!** 🎉

Simulasi akan berhenti segera setelah tombol stop diklik, dan semua data yang sudah diproses akan tersimpan dengan aman.
