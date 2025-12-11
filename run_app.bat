@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run streamlit_app.py
pause
