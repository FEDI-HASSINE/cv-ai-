import express from 'express';
import multer from 'multer';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';
import fs from 'fs';

dotenv.config();

const app = express();
const upload = multer({ dest: 'uploads/' });

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';
const API_TOKEN = process.env.API_TOKEN || '';
const API_EMAIL = process.env.API_EMAIL || '';
const API_PASSWORD = process.env.API_PASSWORD || '';

// CORS for local React dev
const PROXY_CORS_ORIGINS = (process.env.PROXY_CORS_ORIGINS || 'http://localhost:3000,http://localhost:5173')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

app.use(cors({ origin: PROXY_CORS_ORIGINS }));
app.use(express.json());

async function getToken() {
  if (API_TOKEN) return API_TOKEN;
  if (!API_EMAIL || !API_PASSWORD) {
    throw new Error('No API_TOKEN provided and missing API_EMAIL/API_PASSWORD to login');
  }
  const res = await axios.post(`${FASTAPI_URL}/api/v1/auth/login`, {
    email: API_EMAIL,
    password: API_PASSWORD,
  });
  return res.data.access_token;
}

// Health check
app.get('/healthz', (req, res) => res.json({ ok: true }));

// Proxy: Analyze resume
app.post('/api/resume/analyze', upload.single('file'), async (req, res) => {
  const filePath = req.file?.path;
  if (!filePath) return res.status(400).json({ error: 'Missing file' });
  let token;
  try {
    token = await getToken();
    const formData = new (await import('form-data')).default();
    formData.append('file', fs.createReadStream(filePath), req.file.originalname);

    const apiRes = await axios.post(`${FASTAPI_URL}/api/v1/resume/analyze`, formData, {
      headers: {
        ...formData.getHeaders(),
        Authorization: `Bearer ${token}`,
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
    });

    return res.json(apiRes.data);
  } catch (err) {
    const status = err.response?.status || 500;
    const detail = err.response?.data || { error: err.message };
    return res.status(status).json(detail);
  } finally {
    if (filePath) fs.unlink(filePath, () => {});
  }
});

// Proxy: Rewrite resume
app.post('/api/resume/rewrite', upload.single('file'), async (req, res) => {
  const filePath = req.file?.path;
  const useAi = (req.query.use_ai || 'false') === 'true';
  if (!filePath) return res.status(400).json({ error: 'Missing file' });
  let token;
  try {
    token = await getToken();
    const formData = new (await import('form-data')).default();
    formData.append('file', fs.createReadStream(filePath), req.file.originalname);
    formData.append('use_ai', String(useAi));

    const apiRes = await axios.post(`${FASTAPI_URL}/api/v1/resume/rewrite?use_ai=${useAi}`, formData, {
      headers: {
        ...formData.getHeaders(),
        Authorization: `Bearer ${token}`,
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
    });

    return res.json(apiRes.data);
  } catch (err) {
    const status = err.response?.status || 500;
    const detail = err.response?.data || { error: err.message };
    return res.status(status).json(detail);
  } finally {
    if (filePath) fs.unlink(filePath, () => {});
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Node proxy listening on http://localhost:${PORT}`);
});
