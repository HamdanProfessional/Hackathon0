# Setup Git Sync Scheduled Task for AI Employee
# Runs git_sync_pull.bat every 5 minutes

$TaskName = "AI Employee Git Sync"
$ScriptPath = "C:\Users\User\Desktop\AI_EMPLOYEE_APP\scripts\git_sync_pull.bat"

Write-Host "Creating scheduled task: $TaskName" -ForegroundColor Green

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c $ScriptPath"

# Create trigger - every 5 minutes for 1 year (effectively indefinitely)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)

# Create principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId 'S-1-5-32-544' -LogonType ServiceAccount -RunLevel Highest

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Description "Pulls vault changes from Git repository every 5 minutes" -Force

Write-Host "Scheduled task created successfully!" -ForegroundColor Green
Write-Host "Task will run every 5 minutes starting now." -ForegroundColor Cyan

# Show task info
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, LastRunTime | Format-List
