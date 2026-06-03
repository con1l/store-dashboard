# Test KV with SET and GET
$url = "https://tolerant-lobster-100130.upstash.io/set/test"
$resp = Invoke-WebRequest -Uri $url -Method POST -ContentType "application/json" -Headers @{"Authorization"="Bearer gQAAAAAAAYciAAIgcDJhMzAwYzJlZDMyM2E0YzNmOTAxMTdlMzAxZWU0MmRlZA"} -Body '"hello"'
Write-Host "Status:" $resp.StatusCode
Write-Host "Body:" $resp.Content
