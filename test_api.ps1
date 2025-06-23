# Get auth token from environment
$authToken = (Get-Content .env | Where-Object { $_ -match 'SUNBIRD_API_KEY=' } | ForEach-Object { $_.Split('=')[1] })

# Test root endpoint
Write-Host "Testing root endpoint..."
Invoke-WebRequest -Uri "https://api.sunbird.ai/" -Method Get -Headers @{
    "Authorization" = $authToken
    "accept" = "application/json"
} -SkipCertificateCheck | Select-Object -ExpandProperty Content

# Test STT endpoint with POST
Write-Host "`nTesting STT endpoint with POST..."
Invoke-WebRequest -Uri "https://api.sunbird.ai/tasks/stt" -Method Post -Headers @{
    "Authorization" = $authToken
    "accept" = "application/json"
} -Form @{
    "language" = "lug"
    "adapter" = "lug"
    "whisper" = "true"
} -SkipCertificateCheck | Select-Object -ExpandProperty Content
