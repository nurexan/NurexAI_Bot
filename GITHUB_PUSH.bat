@echo off
chcp 65001 >nul
echo.
echo  ==========================================
echo   NurexAI Bot - GitHubga yuklash...
echo  ==========================================
echo.

git add -A
git commit -m "v12.3: UI yangilandi, auto-cleanup, temp storage"
git push origin main

echo.
echo  ==========================================
echo   ✅ BOʼLDI JIGAR! GitHub yangilandi!
echo   Railway endi avtomatik deploy qiladi!
echo  ==========================================
echo.
pause
