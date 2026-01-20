@echo off
set API_KEY=c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM
set BASE_URL=https://api.z.ai/api/coding/paas/v4

echo Creating update script...
(
echo import re
echo config_path = "/root/AI_EMPLOYEE_APP/process-manager/pm2.cloud.config.js"
echo with open^(config_path, 'r'^) as f:
echo     content = f.read^(^)
echo content = re.sub^(r"process\.env\.ANTHROPIC_API_KEY", "'%API_KEY%'", content^)
echo with open^(config_path, 'w'^) as f:
echo     f.write^(content^)
echo print^("Config updated"^)
) > temp_update.py

echo Uploading to Cloud VM...
powershell -Command "Get-Content temp_update.py | ssh -o StrictHostKeyChecking=no root@143.244.143.143 'cat > /tmp/update_api.py'"

echo Running update...
powershell -Command "ssh -o StrictHostKeyChecking=no root@143.244.143.143 'python3 /tmp/update_api.py && pm2 restart auto-approver && pm2 status'"

del temp_update.py
echo Done!
pause
