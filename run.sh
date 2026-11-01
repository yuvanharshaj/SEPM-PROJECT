#!/usr/bin/env bash
set -e

echo "===================================================================="
echo " ProcessCompass: VTU 24CS51 SEPM Decision Support System"
echo "===================================================================="

if [ ! -f "venv/bin/activate" ]; then
    echo "[INFO] Virtual environment not found. Creating venv..."
    python3 -m venv venv || python -m venv venv
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Verifying requirements..."
python -m pip install -r requirements.txt --quiet

echo "[INFO] Launching ProcessCompass on http://localhost:8501 ..."
streamlit run app.py
