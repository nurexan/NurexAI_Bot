@echo off
echo ==========================================
echo GITHUBGA YUKLASH BOSHLANDI... (v12.3)
echo ==========================================

:: Eski git ulanishini tozalash va toza boshlash (xatolar oldini olish uchun)
if exist .\.git\ (
    rmdir /s /q .\.git
)

git init
git add .
git commit -m "NurexAI v12.3 Super Clean + Auto Cleanup"
git branch -M main
git remote add origin https://github.com/nurexan/NurexAI_Bot.git
git push -u origin main -f

echo.
echo ==========================================
echo 🚀 BO'LDI JIGAR! HAMMASI GITHUBGA KETDI! (va eskilari tozalandi)
echo ==========================================
echo Endi Railway.app ga kiring, tepada o'ngda "Deploy" yoki "Restart" tugmasini bosing!
pause
