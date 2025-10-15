@echo off
echo ============================================================
echo TIME LAPSE MODEL SIMULATOR LAUNCHER
echo ============================================================
echo.
echo Starting Time Lapse Model Simulator...
echo Dashboard will be available at: http://localhost:5001
echo.
echo Features:
echo - Visualisasi flow modul real-time
echo - Simulasi 1 hari = 2 detik
echo - Analisis performa 6 bulan dalam 12 menit
echo - Rekomendasi tuning/replacement model
echo.
echo ============================================================
echo.

cd model_evaluation
python run_time_lapse_system.py

pause
