const express = require('express');
const router = express.Router();
const User = require('../models/User');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'love_memory_secret_key';

router.post('/register', async (req, res) => {
  try {
    const { username, password, email } = req.body;

    if (!username || !password) {
      return res.json({ code: -1, msg: '用户名和密码不能为空' });
    }

    const existingUser = await User.findByUsername(username);
    if (existingUser) {
      return res.json({ code: -1, msg: '用户名已存在' });
    }

    const userId = await User.create(username, password, email);
    res.json({ code: 0, msg: '注册成功', data: { userId } });
  } catch (error) {
    console.error('注册失败:', error);
    res.json({ code: -1, msg: '注册失败，请稍后重试' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.json({ code: -1, msg: '用户名和密码不能为空' });
    }

    const user = await User.findByUsername(username);
    if (!user) {
      return res.json({ code: -1, msg: '用户名或密码错误' });
    }

    const isPasswordValid = await User.verifyPassword(password, user.password);
    if (!isPasswordValid) {
      return res.json({ code: -1, msg: '用户名或密码错误' });
    }

    const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
    
    res.json({ 
      code: 0, 
      msg: '登录成功', 
      data: { 
        token,
        user: { id: user.id, username: user.username, email: user.email }
      } 
    });
  } catch (error) {
    console.error('登录失败:', error);
    res.json({ code: -1, msg: '登录失败，请稍后重试' });
  }
});

router.get('/user', async (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.json({ code: -1, msg: '未登录' });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(decoded.userId);
    
    if (!user) {
      return res.json({ code: -1, msg: '用户不存在' });
    }

    res.json({ code: 0, data: user });
  } catch (error) {
    console.error('获取用户信息失败:', error);
    res.json({ code: -1, msg: '获取用户信息失败' });
  }
});

module.exports = router;