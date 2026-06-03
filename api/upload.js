// api/upload.js - Vercel Edge Function
// 前端用SheetJS解析Excel，这里只接收JSON数据+密码验证

export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: { 
        'Access-Control-Allow-Origin': '*', 
        'Access-Control-Allow-Methods': 'POST,OPTIONS', 
        'Access-Control-Allow-Headers': 'Content-Type' 
      }
    });
  }

  if (req.method !== 'POST') {
    return Response.json({ error: '只支持POST' }, { status: 405 });
  }

  try {
    const formData = await req.formData();
    const authToken = formData.get('auth');
    const jsonData = formData.get('data'); // JSON字符串

    if (authToken !== 'ft2024') {
      return Response.json({ error: '密码错误' }, { status: 403 });
    }

    if (!jsonData) {
      return Response.json({ error: '没有数据' }, { status: 400 });
    }

    const parsed = JSON.parse(jsonData);
    
    // 验证数据格式
    if (!parsed.date || !parsed.stores) {
      return Response.json({ error: '数据格式错误' }, { status: 400 });
    }

    const storeCount = Object.keys(parsed.stores).length;
    const total = Object.values(parsed.stores).reduce((sum, s) => sum + (s['总支付金额'] || 0), 0);

    return Response.json({
      ok: true,
      date: parsed.date,
      store_count: storeCount,
      store_order: parsed.store_order || Object.keys(parsed.stores),
      data: parsed.stores,
      total: total
    });

  } catch (err) {
    console.error('Upload error:', err);
    return Response.json({ error: '解析失败: ' + err.message }, { status: 500 });
  }
}
