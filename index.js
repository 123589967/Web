const express = require('express');
const cors = require('cors');
require('dotenv').config();

const { initDatabase } = require('./config/db');
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

app.use('/api', authRoutes);

app.get('/', (req, res) => {
  res.send('Love Memory Backend Service');
});

async function startServer() {
  try {
    await initDatabase();
    app.listen(PORT, () => {
      console.log(`服务器运行在 http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('启动服务器失败:', error);
    process.exit(1);
  }
}

startServer();