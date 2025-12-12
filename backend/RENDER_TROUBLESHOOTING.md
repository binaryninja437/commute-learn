# Render Deployment Troubleshooting

## Common Render Build Failures & Solutions

### Issue 1: Build Command Failed

**Error:** `pip install -r requirements.txt` fails

**Solutions:**

#### Option A: Use render-build.sh (Recommended)
```
Build Command: ./render-build.sh
```

#### Option B: Simple pip install
```
Build Command: pip install -r requirements.txt
```

#### Option C: Upgrade pip first
```
Build Command: pip install --upgrade pip && pip install -r requirements.txt
```

### Issue 2: ffmpeg Not Found (for pydub)

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solutions:**

#### Option A: Install ffmpeg in build script
Use `render-build.sh` which installs ffmpeg automatically

#### Option B: Add ffmpeg as system dependency
In Render dashboard:
1. Go to "Native Environment"
2. Add: `ffmpeg`

#### Option C: Use simpler audio (remove pydub dependency)
This requires code changes to use only gTTS without concatenation.

### Issue 3: Python Version Mismatch

**Error:** `Package requires Python >=3.11`

**Solution:**
In Render dashboard:
1. Go to "Environment"
2. Set `PYTHON_VERSION = 3.11.0`

Or use runtime.txt:
```
python-3.11.0
```

### Issue 4: Missing Environment Variables

**Error:** `API key not loaded` or `KeyError: 'GEMINI_API_KEY'`

**Solution:**
1. Go to Render dashboard → Environment
2. Add these variables:
   ```
   GEMINI_API_KEY = your_actual_key_here
   PORT = 8000  
   PYTHONIOENCODING = utf-8
   ```
3. Click "Save Changes"
4. Wait for automatic redeploy

### Issue 5: Start Command Failed

**Error:** `bash: uvicorn: command not found`

**Solutions:**

#### Option A: Use python -m
```
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Option B: Full path (if using venv)
```
Start Command: python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Issue 6: Import Errors

**Error:** `ModuleNotFoundError: No module named 'services'`

**Solution:**
Make sure Root Directory is set to: `backend`

### Issue 7: Port Binding Failed

**Error:** `[Errno 98] Address already in use`

**Solution:**
Always use `$PORT` variable, not hardcoded 8000:
```
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Issue 8: Memory Exceeded

**Error:** `Killed` or `Out of memory`

**Solutions:**
1. Upgrade from Free to Starter plan ($7/month, 512MB RAM)
2. Optimize code to use less memory
3. Reduce concurrent requests

## Recommended Render Configuration

```yaml
Name: saarlm-backend
Region: Singapore (or closest to India)
Branch: main
Root Directory: backend
Runtime: Python 3

# Option A: With ffmpeg (full audio features)
Build Command: ./render-build.sh
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT

# Option B: Simple (no ffmpeg, basic features)
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT

Instance Type: Free (testing) or Starter (production)

Environment Variables:
GEMINI_API_KEY = [your key]
PORT = 8000
PYTHONIOENCODING = utf-8
PYTHON_VERSION = 3.11.0 (optional)
```

## Check Render Logs

In Render dashboard:
1. Click on your service
2. Go to "Logs" tab
3. Look for errors in:
   - Build logs (during deployment)
   - Runtime logs (after deployment)

## Test After Deployment

```bash
# 1. Health check
curl https://your-service.onrender.com/

# 2. API key test
curl -X POST https://your-service.onrender.com/api/test-ocr

# 3. Check specific error endpoint
curl https://your-service.onrender.com/api/library
```

## Still Having Issues?

1. **Check Render Status:** https://status.render.com
2. **Review Logs:** Render Dashboard → Logs tab
3. **Test Locally:** Make sure it works with:
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. **Verify Environment Variables:** Double-check spelling and values
5. **Try Free Plan First:** Test with free tier before upgrading

## Quick Fix Checklist

- [ ] Root Directory set to `backend`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables added (GEMINI_API_KEY, PORT, PYTHONIOENCODING)
- [ ] Python version 3.11
- [ ] requirements.txt has no syntax errors
- [ ] All imports in main.py are available in requirements.txt

## Contact Support

If issue persists:
- Render Support: https://render.com/docs/support
- Check this repo: https://github.com/binaryninja437/commute-learn/issues
