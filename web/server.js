const express = require('express');
const crypto = require('crypto');
const app = express();

const BOT_TOKEN = '7794369165:AAHZxoqFtXfsl6F9B6LrrZxHjGeGZXcJ0k8'; // Replace this

app.use(express.static('.'));

function verifyTelegramAuth(data) {
  const { hash, ...rest } = data;
  const sorted = Object.keys(rest).sort();
  const dataCheckString = sorted.map(k => `${k}=${rest[k]}`).join('\n');
  const secret = crypto.createHash('sha256').update(BOT_TOKEN).digest();
  const hmac = crypto.createHmac('sha256', secret).update(dataCheckString).digest('hex');
  return hmac === hash;
}

app.get('/auth', (req, res) => {
  const data = req.query;
  if (verifyTelegramAuth(data)) {
    res.send(`<h1>✅ Logged in as ${data.first_name} (${data.id})</h1>`);
  } else {
    res.send("<h1>❌ Authentication failed</h1>");
  }
});

app.listen(3000, () => {
  console.log('🌐 Web server running on http://localhost:3000');
});
