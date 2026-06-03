$resp = Invoke-WebRequest -Uri "https://tolerant-lobster-100130.upstash.io" -Method GET -Headers @{"Authorization"="Bearer gQAAAAAAAYciAAIgcDJhMzAwYzJlZDMyM2E0YzNmOTAxMTdlMzAxZWU0MmRlZA"}
Write-Host "Status:" $resp.StatusCode
Write-Host "Body:" $resp.Content.Substring(0, [Math]::Min(200, $resp.Content.Length))
