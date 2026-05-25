$ws = New-Object -ComObject WScript.Shell

$s1 = $ws.CreateShortcut("$env:USERPROFILE\Desktop\AI Movie Studio Start.lnk")
$s1.TargetPath = 'd:\ai-moive-studio\start.bat'
$s1.WorkingDirectory = 'd:\ai-moive-studio'
$s1.Description = 'AI Movie Studio Start'
$s1.IconLocation = 'shell32.dll,13'
$s1.Save()

$s2 = $ws.CreateShortcut("$env:USERPROFILE\Desktop\AI Movie Studio Stop.lnk")
$s2.TargetPath = 'd:\ai-moive-studio\stop.bat'
$s2.WorkingDirectory = 'd:\ai-moive-studio'
$s2.Description = 'AI Movie Studio Stop'
$s2.IconLocation = 'shell32.dll,28'
$s2.Save()

Write-Host 'Desktop shortcuts created successfully'
