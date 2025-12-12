# 🚀 SaarLM - Render Deployment Guide

## Current Version: 1.0 (December 12, 2024)

### ✅ Pre-Deployment Checklist

- [x] Security filters for contact info (commit 6368c5c)
- [x] UTF-8 encoding for Windows
- [x] Backup system in place
- [x] All features tested locally
- [x] Documentation complete
- [x] .env.example file ready
- [x] .gitignore configured

---

## 📋 Render Setup Instructions

### 1. Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `binaryninja437/commute-learn`
4. Select the repository

### 2. Configure Service Settings

**Basic Settings:**
```
Name: saarlm-backend
Region: Singapore (or closest to India)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
- Start with **Free** tier (test)
- Upgrade to **Starter ($7/month)** for production

### 3. Environment Variables

Click **"Environment"** and add these variables:

```
GEMINI_API_KEY = [Your Gemini API Key]
PORT = 8000
PYTHONIOENCODING = utf-8
```

**Important:** Don't commit the actual API key! Add it only in Render's environment variables.

### 4. Advanced Settings (Optional)

**Auto-Deploy:**
- [x] Enable Auto-Deploy from main branch

**Health Check Path:**
```
/
```

**Persistent Storage (if needed):**
- Mount path: `/opt/render/project/src/uploads`
- Mount path: `/opt/render/project/src/outputs`
- Mount path: `/opt/render/project/src/metadata`

**Note:** Render free tier doesn't have persistent storage. Files will be lost on restart. Consider using cloud storage (S3, Cloudinary) for production.

---

## 🔧 Backend Requirements

File: `backend/requirements.txt`

Make sure it contains:
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
httpx>=0.25.0
python-dotenv>=1.0.0
gtts>=2.5.0
pydub>=0.25.1
pypdf>=3.17.0
```

---

## 🌐 Frontend Deployment (Separate Service)

### Option 1: Render Static Site

1. Create **"Static Site"**
2. Configure:
   ```
   Name: saarlm-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

3. Environment Variables:
   ```
   VITE_API_URL = https://saarlm-backend.onrender.com
   ```

### Option 2: Vercel (Recommended for Frontend)

1. Go to https://vercel.com
2. Import repository
3. Configure:
   ```
   Framework: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. Environment Variables:
   ```
   VITE_API_URL = https://saarlm-backend.onrender.com
   ```

---

## 🔒 Security Configuration

### CORS Settings (Already in main.py)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For Production:** Update `allow_origins` to your frontend URL:
```python
allow_origins=[
    "https://saarlm-frontend.vercel.app",
    "https://your-custom-domain.com"
]
```

---

## 📊 Post-Deployment Testing

### 1. Test Backend Health
```bash
curl https://saarlm-backend.onrender.com/
```

Expected response:
```json
{
  "status": "online",
  "app": "SaarLM",
  "version": "1.0.0",
  "api_key_loaded": true
}
```

### 2. Test API Key
```bash
curl -X POST https://saarlm-backend.onrender.com/api/test-ocr
```

Expected: `{"works": true}`

### 3. Test Upload Flow
1. Open frontend URL
2. Upload test image
3. Verify OCR extraction
4. Check script generation (should have NO contact info)
5. Confirm audio playback

---

## ⚠️ Known Issues & Solutions

### Issue 1: Port Binding
**Problem:** "Address already in use"
**Solution:** Render automatically assigns $PORT, don't hardcode 8000

### Issue 2: Build Timeout
**Problem:** Build takes too long
**Solution:** Optimize requirements.txt, remove unused packages

### Issue 3: Memory Issues
**Problem:** Process killed (out of memory)
**Solution:**
- Upgrade to Starter plan (512MB)
- Reduce concurrent requests
- Optimize audio processing

### Issue 4: File Persistence
**Problem:** Uploaded files disappear after restart
**Solution:**
- Use Render's Disk storage (paid)
- Or integrate cloud storage (S3, Cloudinary)

### Issue 5: Cold Starts
**Problem:** First request takes 30+ seconds
**Solution:**
- Keep service awake with cron job
- Or upgrade to always-on instance

---

## 🔄 CI/CD Pipeline

Render auto-deploys when you push to `main` branch:

```bash
git add .
git commit -m "Update: [your changes]"
git push origin main
```

Render will:
1. Pull latest code
2. Run `pip install -r requirements.txt`
3. Start service with new code
4. Health check → Live!

---

## 📈 Monitoring

### Render Dashboard
- View logs in real-time
- Check CPU/Memory usage
- Monitor request counts
- Set up alerts

### Log Viewing
```bash
# In Render dashboard, click "Logs" tab
# You'll see all print() statements from main.py
```

Look for:
- `[STARTUP] SaarLM Backend Starting...`
- `[UPLOAD] New file: ...`
- `[STEP 1] OCR...`
- `[STEP 2] Generating script...`
- `[STEP 2] After safety filter: ...` ← Confirms security is active
- `[STEP 3] Generating audio...`

---

## 🌍 Custom Domain (Optional)

### Add Custom Domain in Render

1. Go to service → Settings → Custom Domain
2. Add your domain: `api.saarlm.com`
3. Point DNS to Render:
   ```
   Type: CNAME
   Name: api
   Value: [provided by Render]
   ```

### Update Frontend API URL
```javascript
// In frontend/src/App.jsx
const API_BASE = 'https://api.saarlm.com/api';
```

---

## 💰 Cost Estimation

### Free Tier
- **Backend:** Free (sleeps after 15 min inactivity)
- **Frontend:** Free on Vercel
- **Total:** $0/month
- **Limitations:**
  - 750 hours/month
  - No persistent storage
  - Cold starts

### Production Tier
- **Backend:** $7/month (Starter)
- **Frontend:** $0/month (Vercel free)
- **Disk Storage:** $1/GB/month (if needed)
- **Total:** ~$7-10/month
- **Benefits:**
  - Always online
  - 512MB RAM
  - Persistent storage available

---

## 🚀 Deployment Steps (Final)

### 1. Verify Code Locally
```bash
cd backend
set PYTHONIOENCODING=utf-8
python -m uvicorn main:app --reload --port 8000
```

Test at http://localhost:8000

### 2. Commit & Push
```bash
git add .
git commit -m "Fresh deploy - SaarLM v1.0 with safety filters"
git push origin main
```

### 3. Create Render Service
- Follow "Render Setup Instructions" above
- Add environment variables (GEMINI_API_KEY, PORT, PYTHONIOENCODING)
- Wait for initial deploy (3-5 minutes)

### 4. Test Deployed Backend
```bash
curl https://saarlm-backend.onrender.com/
```

### 5. Deploy Frontend
- Use Vercel or Render Static Site
- Set VITE_API_URL to backend URL
- Test upload flow

### 6. Done! 🎉

---

## 📞 Support

Issues? Check:
- Render logs for errors
- Backend health endpoint: `/`
- Test OCR endpoint: `/api/test-ocr`
- GitHub repo: https://github.com/binaryninja437/commute-learn
- QUICK_START.md for local setup
- SECURITY_UPDATE.md for security info

---

## 🔖 Quick Reference

**Backend URL:** `https://saarlm-backend.onrender.com`
**Frontend URL:** `https://saarlm-frontend.vercel.app` (or your Vercel URL)
**Repository:** `https://github.com/binaryninja437/commute-learn`
**Branch:** `main`
**Python Version:** 3.11
**Node Version:** 18+ (for frontend)

---

**Last Updated:** December 12, 2024
**Status:** Ready for Deployment ✅
