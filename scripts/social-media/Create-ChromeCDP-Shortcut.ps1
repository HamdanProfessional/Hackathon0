# Create a desktop shortcut for Chrome with CDP
$WshShell = New-Object -ComObject WScript.Shell
$Desktop = $WshShell.SpecialFolders("Desktop")
$Shortcut = $WshShell.CreateShortcut("$Desktop\Chrome with CDP.lnk")
$Shortcut.TargetPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$Shortcut.Arguments = '--remote-debugging-port=9222 --user-data-dir="C:\Users\User\AppData\Local\Google\Chrome\User Data"'
$Shortcut.WorkingDirectory = "C:\Program Files\Google\Chrome\Application"
$Shortcut.Description = "Chrome with CDP for AI automation"
$Shortcut.Save()

Write-Host "Shortcut created on desktop: 'Chrome with CDP.lnk'" -ForegroundColor Green
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Yellow
Write-Host "1. Close ALL Chrome windows" -ForegroundColor White
Write-Host "2. Double-click the 'Chrome with CDP' shortcut on your desktop" -ForegroundColor White
Write-Host "3. Log in to LinkedIn, Twitter, and Meta in this Chrome window" -ForegroundColor White
Write-Host "4. Keep this Chrome window open for automation" -ForegroundColor White
Write-Host ""
Write-Host "After logging in, run the posters and they will use this Chrome session!" -ForegroundColor Cyan
