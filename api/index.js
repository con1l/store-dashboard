// 处理 CORS
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type,Authorization',
};

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') {
    res.status(200).setHeader('Set-Cookie', '').end();
    return;
  }
  res.status(404).json({ error: 'not found' });
};
