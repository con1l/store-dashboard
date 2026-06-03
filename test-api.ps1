try {
    $result = Invoke-RestMethod -Uri "https://store-dashboard-gamma-five.vercel.app/api/data?key=ft2024" -ErrorAction Stop
    Write-Host "API OK:"
    $result | ConvertTo-Json -Depth 3
} catch {
    Write-Host "API Error:" $_.Exception.Message
}
