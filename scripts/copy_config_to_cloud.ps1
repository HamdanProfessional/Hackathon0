# Copy PM2 config to Cloud VM
$Password = "NooBNooBl0l!"
$ConfigPath = "C:\Users\User\Desktop\AI_EMPLOYEE_APP\process-manager\pm2.cloud.config.js"

# Read file content
$Content = Get-Content $ConfigPath -Raw

# Create SSH command to write file
$Command = "cat > /root/AI_EMPLOYEE_APP/process-manager/pm2.cloud.config.js << 'EOFFILE'$Content$([char]10)EOFFILE"

# Execute via SSH
echo $Password | ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@143.244.143.143 $Command
