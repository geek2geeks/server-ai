# Location: E:/justica/scripts/setup/create_auth.ps1

# Ensure we're running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    Exit 1
}

# Create nginx directory if it doesn't exist
$nginxDir = "E:\justica\config\services\nginx"
New-Item -ItemType Directory -Force -Path $nginxDir | Out-Null

# Create a temporary container to generate the htpasswd file
$containerName = "nginx-htpasswd-generator"
docker run --name $containerName --rm -i nginx:alpine htpasswd -nb fixola "As!101010" > "$nginxDir\.htpasswd" 2>$null

# Set proper permissions
$htpasswdPath = Join-Path $nginxDir ".htpasswd"
$acl = Get-Acl $htpasswdPath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Users","FullControl","Allow")
$acl.SetAccessRule($rule)
Set-Acl $htpasswdPath $acl

Write-Host "Auth file created successfully at: $htpasswdPath"
Get-Content $htpasswdPath