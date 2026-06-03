try {
    $url = "https://tolerant-lobster-100130.upstash.io/set/test"
    $body = [System.Text.Encoding]::UTF8.GetBytes('"hello"')
    $headers = @{
        "Authorization" = "Bearer gQAAAAAAAYciAAIgcDJhMzAwYzJlZDMyM2E0YzNmOTAxMTdlMzAxZWU0MmRlZA"
        "Content-Type" = "application/json"
    }
    $result = Invoke-RestMethod -Uri $url -Method POST -Headers $headers -Body $body -ErrorAction Stop
    Write-Host "OK:" $result
} catch {
    Write-Host "Error:" $_.Exception.Message
    if ($_.Exception.Response) {
        Write-Host "Status:" $_.Exception.Response.StatusCode.value__
    }
}
