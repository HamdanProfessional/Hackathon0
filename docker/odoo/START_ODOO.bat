@echo off
REM Start Odoo Community via Docker Compose

echo ============================================
echo Starting Odoo Community 19
echo ============================================
echo.
echo This will start:
echo   - PostgreSQL 15 database
echo   - Odoo 19 Community Edition
echo.
echo Odoo will be available at: http://localhost:8069
echo.
echo Default credentials:
echo   Database: odoo
echo   Email: admin
echo   Password: admin
echo.
echo Press Ctrl+C to stop Odoo
echo ============================================
echo.

cd /d "%~dp0"
docker-compose up

pause
