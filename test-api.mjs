const r = await fetch('https://store-dashboard-gamma-five.vercel.app/api/data?key=ft2024');
const t = await r.text();
console.log('Status:', r.status);
console.log('Body:', t.substring(0, 300));
