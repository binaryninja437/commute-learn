# 🚀 SaarLM v1.0 - Deployment Checklist

## ✅ Pre-Deployment Verification (COMPLETED)

### Code Quality
- [x] All features tested locally
- [x] Security filters active (no phone numbers/emails/URLs)
- [x] UTF-8 encoding configured
- [x] Error handling in place
- [x] Backup system created

### Documentation
- [x] QUICK_START.md - Local setup guide
- [x] RENDER_DEPLOY.md - Render deployment guide
- [x] SECURITY_UPDATE.md - Security fix documentation
- [x] backend/backups/README.md - Backup system guide
- [x] backend/backups/BACKUP_INFO.txt - Detailed backup info

### Configuration Files
- [x] backend/.env.example - Environment template
- [x] .gitignore - Properly configured (excludes .env, uploads, outputs)
- [x] backend/requirements.txt - All dependencies listed

### Git Repository
- [x] All changes committed
- [x] Pushed to GitHub (main branch)
- [x] No sensitive data in commits
- [x] API keys excluded (.env in .gitignore)

### Security
- [x] Contact info filters (commit 6368c5c)
- [x] Prompt engineering for safe content
- [x] Regex safety filters
- [x] No hardcoded API keys
- [x] CORS configured (allow_origins to be updated for production)

---

## 📋 Render Deployment Steps

### 1. Create Backend Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub: `binaryninja437/commute-learn`
4. Configure:
   ```
   Name: saarlm-backend
   Region: Singapore
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free (test) or Starter (production)
   ```

### 2. Add Environment Variables in Render

**Required:**
```
GEMINI_API_KEY = [Your actual Gemini API key from .env file]
PORT = 8000
PYTHONIOENCODING = utf-8
```

**How to add:**
- Click "Environment" tab in Render dashboard
- Click "Add Environment Variable"
- Paste key-value pairs
- Click "Save Changes"

### 3. Deploy Backend

- Click "Create Web Service"
- Wait 3-5 minutes for initial build
- Watch logs for: `[STARTUP] SaarLM Backend Starting...`
- Verify health: https://saarlm-backend.onrender.com/

### 4. Test Backend Endpoints

```bash
# Health check
curl https://saarlm-backend.onrender.com/

# API key test
curl -X POST https://saarlm-backend.onrender.com/api/test-ocr

# Library endpoint
curl https://saarlm-backend.onrender.com/api/library
```

### 5. Deploy Frontend (Vercel Recommended)

1. Go to https://vercel.com
2. Import `binaryninja437/commute-learn`
3. Configure:
   ```
   Framework: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. Add environment variable:
   ```
   VITE_API_URL = https://saarlm-backend.onrender.com
   ```

5. Deploy and test upload flow

### 6. Update CORS for Production

In `backend/main.py`, update:
```python
allow_origins=[
    "https://your-frontend-url.vercel.app",
    "https://your-custom-domain.com"  # if you have one
]
```

Commit and push to trigger redeploy.

---

## ✅ Post-Deployment Testing

### Backend Tests
- [ ] Health endpoint responds: `/`
- [ ] API key test passes: `/api/test-ocr`
- [ ] Library endpoint works: `/api/library`
- [ ] Logs show startup message

### Frontend Tests
- [ ] Home page loads
- [ ] Upload form visible
- [ ] Drag-and-drop works

### Full Flow Test
- [ ] Upload test image (e.g., Physics notes)
- [ ] OCR extracts text (check logs)
- [ ] Script generates (20-30 seconds)
- [ ] **CRITICAL:** Script has NO phone numbers/emails/URLs
- [ ] Audio generates (60-90 seconds)
- [ ] Player shows podcast
- [ ] Audio plays correctly
- [ ] Download works
- [ ] Library shows uploaded podcast

### Security Verification
- [ ] Check generated script for contact info
- [ ] Verify logs show: `[STEP 2] After safety filter: ...`
- [ ] Confirm no WhatsApp/phone numbers in output
- [ ] Test with multiple uploads

---

## 🐛 Common Issues & Solutions

### Issue: Build Fails
**Check:**
- requirements.txt is correct
- Python version is 3.11
- Build command is correct

**Solution:**
```bash
# Locally test:
cd backend
pip install -r requirements.txt
python -m uvicorn main:app
```

### Issue: "API key not loaded"
**Check:**
- Environment variable name: `GEMINI_API_KEY` (exact match)
- Value is correct (copy from your .env file)
- No extra spaces in key

**Solution:**
- Re-add environment variable in Render
- Trigger manual deploy

### Issue: CORS Error in Browser
**Check:**
- Frontend URL is in allow_origins list
- CORS middleware is configured

**Solution:**
```python
# Temporarily allow all (testing only):
allow_origins=["*"]

# Then update to specific domain:
allow_origins=["https://your-frontend.vercel.app"]
```

### Issue: Upload Fails
**Check:**
- Backend logs for errors
- File size (keep under 10MB)
- API quota not exhausted

**Solution:**
- Check Render logs
- Test with smaller image
- Verify Gemini API key has quota

### Issue: Audio Not Playing
**Check:**
- Audio file generated (check logs: `[STEP 3] SUCCESS`)
- File accessible: https://backend-url/audio/[job_id].mp3
- Browser console for errors

**Solution:**
- Check if TTS service ran
- Verify pydub is installed
- Test audio URL directly

---

## 📊 Monitoring

### Render Dashboard
- **Logs:** Real-time log viewing
- **Metrics:** CPU, Memory, Request count
- **Events:** Deploys, Restarts, Errors

### Log Keywords to Watch
```
✅ Good:
[STARTUP] SaarLM Backend Starting...
[UPLOAD] New file: ...
[STEP 1] SUCCESS! Extracted X chars
[STEP 2] After safety filter: X chars  ← Security active!
[STEP 3] SUCCESS! Audio duration: Xs
[COMPLETE] Job X finished successfully!

⚠️  Errors:
[ERROR] Job X failed: ...
[OCR] API ERROR: ...
[SCRIPT] API ERROR: ...
```

### Set Up Alerts (Optional)
- Render can send emails for:
  - Deploy failures
  - Service downtime
  - High error rates

---

## 💰 Cost Breakdown

### Free Tier (Testing)
- Backend: Free (750 hours/month, sleeps after 15 min)
- Frontend: Free (Vercel)
- Total: $0/month

**Limitations:**
- Cold starts (30+ seconds)
- No persistent storage
- Sleeps when inactive

### Production Tier (Recommended)
- Backend: $7/month (Starter - 512MB, always on)
- Frontend: $0/month (Vercel free tier)
- Disk Storage: $1/GB/month (optional)
- Total: ~$7-10/month

**Benefits:**
- Always online
- No cold starts
- Persistent storage (if added)
- Better performance

---

## 🎯 Success Criteria

Your deployment is successful when:

1. **Backend Health:** https://backend-url/ returns status "online"
2. **API Working:** test-ocr endpoint returns works: true
3. **Frontend Loads:** Home page accessible
4. **Upload Works:** File upload succeeds
5. **OCR Extracts:** Text extracted from image
6. **Script Safe:** NO contact info in generated scripts
7. **Audio Plays:** Podcast plays in browser
8. **Library Shows:** All podcasts visible

---

## 📞 Support Resources

- **Deployment Guide:** `RENDER_DEPLOY.md`
- **Local Setup:** `QUICK_START.md`
- **Security Info:** `SECURITY_UPDATE.md`
- **Backup System:** `backend/backups/README.md`
- **GitHub:** https://github.com/binaryninja437/commute-learn
- **Render Docs:** https://render.com/docs

---

## 🔄 Next Steps After Deployment

1. **Monitor Logs:** Watch for errors in first 24 hours
2. **Test Thoroughly:** Upload various file types
3. **Check Security:** Verify no contact info in scripts
4. **Get Feedback:** Have users test the system
5. **Optimize:** Based on usage patterns
6. **Scale:** Upgrade instance type if needed

---

## 🎉 Deployment Complete!

Once all checkboxes are ticked, your SaarLM app is:
- ✅ Deployed to Render
- ✅ Secure (no contact info leaks)
- ✅ Tested and working
- ✅ Ready for users!

**Congratulations!** 🎊

---

**Last Updated:** December 12, 2024
**Version:** 1.0
**Status:** Ready for Deployment
