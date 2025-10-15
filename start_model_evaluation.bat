@echo off
echo ============================================================
echo MODEL EVALUATION SYSTEM LAUNCHER
echo ============================================================
echo.
echo Starting Model Evaluation System...
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the system
echo.
echo ============================================================
echo.

cd model_evaluation
python run_evaluation_system.py

pause
