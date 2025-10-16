# Module Testing Framework

Framework komprehensif untuk testing dan evaluasi setiap modul dalam aplikasi trading, dengan tujuan menentukan apakah modul tersebut perlu dipertahankan, dihapus, atau diperbaiki.

## 🎯 Tujuan

Framework ini dirancang untuk:
- **Evaluasi Modul**: Menganalisis setiap modul berdasarkan berbagai kriteria
- **Testing Komprehensif**: Menjalankan unit, integration, dan performance testing
- **Keputusan Cerdas**: Membantu mengambil keputusan KEEP/FIX/REMOVE
- **Laporan Detail**: Menghasilkan laporan komprehensif dengan rekomendasi

## 📁 Struktur Folder

```
module_testing/
├── module_evaluator.py      # Evaluator utama untuk analisis modul
├── test_runner.py          # Runner untuk berbagai jenis testing
├── decision_framework.py    # Framework untuk keputusan modul
├── report_generator.py     # Generator laporan komprehensif
├── run_all_tests.py        # Script utama untuk menjalankan semua testing
└── README.md              # Dokumentasi ini
```

## 🚀 Cara Penggunaan

### 1. Jalankan Semua Testing (Recommended)

```bash
cd module_testing
python run_all_tests.py
```

Script ini akan menjalankan semua komponen secara berurutan:
1. Module Evaluator
2. Test Runner  
3. Decision Framework
4. Report Generator

### 2. Jalankan Komponen Individual

#### Module Evaluator
```bash
python module_evaluator.py
```
- Menganalisis setiap modul
- Mengevaluasi syntax, import, complexity
- Menghasilkan rekomendasi awal

#### Test Runner
```bash
python test_runner.py
```
- Menjalankan unit testing
- Menjalankan integration testing
- Menjalankan performance testing

#### Decision Framework
```bash
python decision_framework.py
```
- Menganalisis hasil evaluasi
- Membuat keputusan KEEP/FIX/REMOVE
- Menghasilkan action plan

#### Report Generator
```bash
python report_generator.py
```
- Menghasilkan laporan komprehensif
- Executive summary
- Detailed analysis
- Recommendations

## 📊 Output Files

Framework ini menghasilkan berbagai file output:

### JSON Files
- `module_evaluation_results_*.json` - Hasil evaluasi modul
- `test_results_*.json` - Hasil testing
- `module_decisions_*.json` - Keputusan untuk setiap modul

### Markdown Reports
- `module_evaluation_report_*.md` - Laporan evaluasi
- `decision_summary_*.md` - Ringkasan keputusan
- `action_plan_*.md` - Rencana aksi
- `complete_evaluation_report_*.md` - Laporan lengkap

## 🔍 Kriteria Evaluasi

### File Analysis
- ✅ File exists
- ✅ File size
- ✅ Last modified date
- ✅ Line count

### Code Quality
- ✅ Syntax validation
- ✅ Import success
- ✅ Function count
- ✅ Class count
- ✅ Docstring presence
- ✅ Complexity score

### Error Analysis
- ✅ Error messages
- ✅ Warning messages
- ✅ Import failures
- ✅ Syntax errors

## 🤔 Decision Framework

### KEEP (Pertahankan)
- File exists dan valid
- Import berhasil
- Syntax benar
- Tidak ada error
- Complexity rendah-medium
- Memiliki fungsi/class

### FIX (Perbaiki)
- Ada error yang bisa diperbaiki
- Import gagal tapi syntax benar
- Complexity tinggi
- Missing functions/classes
- Warning messages

### REMOVE (Hapus)
- File tidak ada
- Syntax error parah
- Terlalu banyak error
- File kosong/terlalu kecil
- Tidak ada fungsi/class

## 📈 Priority Levels

### HIGH Priority
- Modules dengan banyak error
- Modules yang tidak bisa diimport
- Modules dengan syntax error
- Modules yang tidak ada

### MEDIUM Priority
- Modules dengan complexity tinggi
- Modules dengan beberapa error
- Modules yang perlu refactoring

### LOW Priority
- Modules yang berfungsi dengan baik
- Modules dengan minor issues
- Modules yang sudah optimal

## 🛠️ Customization

### Mengubah Kriteria Evaluasi
Edit `module_evaluator.py` untuk menyesuaikan kriteria evaluasi:

```python
# Ubah weights untuk kriteria
self.criteria_weights = {
    'file_exists': 0.15,
    'syntax_valid': 0.20,
    'import_success': 0.20,
    # ... tambah kriteria lain
}
```

### Mengubah Decision Thresholds
Edit `decision_framework.py` untuk menyesuaikan threshold keputusan:

```python
self.thresholds = {
    'KEEP': {
        'min_score': 0.7,
        'max_errors': 0,
        # ... ubah threshold
    }
}
```

## 📋 Action Plan Template

Framework menghasilkan action plan dengan timeline:

### Phase 1: Immediate (Week 1)
- Remove unnecessary modules
- Fix critical issues
- Address high priority problems

### Phase 2: Short-term (Weeks 2-4)
- Fix medium priority issues
- Improve code quality
- Add documentation

### Phase 3: Long-term (Months 2-6)
- Architecture improvements
- Performance optimization
- Security enhancements

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   - Pastikan semua dependencies terinstall
   - Check Python path
   - Verify module structure

2. **File Not Found**
   - Check file paths
   - Verify base_path setting
   - Ensure modules exist

3. **Permission Errors**
   - Check file permissions
   - Run with appropriate privileges
   - Verify write access

### Debug Mode

Untuk debugging, tambahkan logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

Jika mengalami masalah:
1. Check error messages di console
2. Verify file permissions
3. Check Python dependencies
4. Review generated logs

## 🔄 Maintenance

### Regular Cleanup
Framework otomatis membersihkan file lama (>7 hari) saat dijalankan.

### Manual Cleanup
```bash
# Hapus file lama manual
find module_testing/ -name "*.json" -mtime +7 -delete
find module_testing/ -name "*.md" -mtime +7 -delete
```

## 📝 Notes

- Framework ini dirancang untuk aplikasi trading
- Dapat disesuaikan untuk proyek lain
- Menggunakan Python 3.6+
- Memerlukan dependencies: pandas, matplotlib (optional)

---

**Author**: AI Assistant  
**Date**: 2025-01-16  
**Version**: 1.0.0
