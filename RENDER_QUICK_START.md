# 🚀 Render Deployment Guide - Quick Start

## TL;DR (Too Long; Didn't Read)

Your app is ready to deploy! Just:

1. **Update requirements.txt** - Add gunicorn
2. **Push to GitHub** - Commit and push your code
3. **Create Render account** - Free at render.com
4. **Deploy** - Click "New Web Service" and connect your repo
5. **Add secrets** - GEMINI_API_KEY and MONGODB_URI
6. **Done!** - App runs at `https://cardano-insights.onrender.com`

---

## Detailed Steps

### 📋 Step 1: Prepare Your Code

#### 1.1 Update requirements.txt
Replace the content with:
```
pymongo>=4.6.0
pandas>=2.1.3
python-dotenv>=1.0.0
crewai>=0.34.3
google-generativeai>=0.3.0
flask
gunicorn>=21.2.0
```

#### 1.2 Create/Verify These Files Exist

**Procfile** (no extension):
```
web: gunicorn app:app
```

**runtime.txt**:
```
python-3.12.0
```

**.renderignore**:
```
__pycache__/
*.pyc
.env
.env.local
.env.render
*.egg-info/
.git/
```

#### 1.3 Update .gitignore
Make sure `.env` files are ignored:
```
.env
.env.local
.env.render
```

### 📤 Step 2: Push to GitHub

```bash
cd C:\Users\HP\Desktop\cardano-aiagents-lessgo-new

# Stage all changes
git add .

# Commit
git commit -m "Add deployment files for Render"

# Push to main branch
git push origin main
```

### 🌐 Step 3: Deploy on Render

#### 3.1 Sign Up
1. Go to **https://render.com**
2. Click "Sign up"
3. Click "Continue with GitHub"
4. Authorize Render

#### 3.2 Create Web Service
1. Click **"New"** → **"Web Service"**
2. Click **"Connect your GitHub repository"**
3. Search for `cardano-aiagents-lessgo-new`
4. Click **"Connect"**

#### 3.3 Configure Service

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `cardano-insights` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` (testing) |

#### 3.4 Add Environment Variables
Click **"Advanced"** (or scroll down to "Environment")

Add these variables (click "Add Environment Variable"):

| Key | Value | Source |
|-----|-------|--------|
| `GEMINI_API_KEY` | Your actual API key | https://ai.google.dev/ |
| `MONGODB_URI` | Your MongoDB connection string | https://www.mongodb.com/cloud/atlas |

**How to get these:**

**GEMINI_API_KEY:**
1. Go https://ai.google.dev/
2. Sign in with Google
3. Click "Get API key"
4. Create new API key
5. Copy the key

**MONGODB_URI:**
1. Go https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create free cluster
4. Click "Connect"
5. Select "Drivers"
6. Copy connection string
7. Replace `<password>` with your password

#### 3.5 Deploy
Click **"Create Web Service"**

Render will:
- Build your app
- Install dependencies
- Start the service
- Give you a live URL

**Wait for "Build successful" message** ⏳

### ✅ Step 4: Test Your App

Once deployment is complete, test these URLs:

**Health Check:**
```
https://cardano-insights.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Cardano Insights API",
  "version": "1.0.0"
}
```

**Main App:**
```
https://cardano-insights.onrender.com/
```

You should see the upload interface! 🎉

---

## Important Notes

### ⚠️ Port Configuration
Your app.py has been updated to work with Render's port system. If it still uses the old port, update it:

```python
# At the bottom of app.py
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 📦 Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Limited to 750 free hours per month

### 💰 Upgrade to Production
- Starter plan: $7/month
- No sleep mode
- Always running
- Better performance

---

## Common Issues & Solutions

### ❌ Build Fails
**Error:** "Procfile not found"
- **Fix:** Create `Procfile` (no extension) in root directory
- Content: `web: gunicorn app:app`

### ❌ App Crashes After Deploy
**Error:** "Command exited with code 1"
- **Fix:** Check Render logs
  1. Go to your service in Render
  2. Click "Logs"
  3. Look for error message
  4. Common: Missing environment variables
     - Add GEMINI_API_KEY and MONGODB_URI

### ❌ Module Not Found
**Error:** "No module named 'crewai'"
- **Fix:** Update requirements.txt and redeploy
- ```bash
  git push origin main
  ```
  Render auto-redeploys on push!

### ❌ Can't Connect to MongoDB
**Error:** "Failed to connect to MongoDB"
- **Fix:** 
  1. Check MONGODB_URI is correct
  2. Verify MongoDB cluster is running
  3. Check IP whitelist in MongoDB Atlas
  4. In MongoDB Atlas → Network Access → Add IP Address (use 0.0.0.0/0 for public)

### ❌ Slow Performance
**Cause:** Free tier limitations
- **Fix:** 
  1. Wait for app to "warm up" after sleep
  2. Upgrade to Starter plan ($7/month)
  3. Use caching to reduce AI calls

---

## Auto-Deploy Setup (Optional)

Render automatically redeploys when you push to main branch!

**To verify:**
1. Go to Render dashboard
2. Select your service
3. Settings → Auto-Deploy: Check it's **"On"**

Now every `git push` will trigger a redeploy! 🔄

---

## Monitoring Your App

### View Logs
1. Go to your Render service dashboard
2. Click **"Logs"** tab
3. See real-time logs

### Monitor Resources
1. Go to your Render service dashboard
2. Check **CPU** and **Memory** usage
3. If high, consider upgrading

### View Deployment History
1. Go to **"Deploys"** tab
2. See all deployments
3. Click to see logs of each deployment

---

## What's Next?

### 🎉 App is Live!
Share the URL: `https://cardano-insights.onrender.com`

### 📊 Monitor Performance
- Check logs regularly
- Monitor resource usage
- Watch for errors

### 💾 Backup Data
- MongoDB is backed up automatically
- But download exports regularly
- Keep local copies

### 🔐 Security Checklist
- [ ] Never commit `.env` files
- [ ] Use strong passwords
- [ ] Rotate API keys monthly
- [ ] Monitor logs for errors
- [ ] Set up backup emails

---

## Quick Reference Links

| Resource | Link |
|----------|------|
| Render Docs | https://render.com/docs |
| Flask on Render | https://render.com/docs/deploy-flask |
| Gunicorn | https://gunicorn.org/ |
| Google AI API | https://ai.google.dev/ |
| MongoDB Atlas | https://www.mongodb.com/cloud/atlas |
| GitHub Desktop | https://desktop.github.com/ |

---

## Need Help?

### Render Support
- Docs: https://render.com/docs
- Status: https://status.render.com
- Email: support@render.com

### Common Render Errors
1. **Deploy logs:** Check in Render dashboard
2. **Python errors:** Usually in logs
3. **Module errors:** Update requirements.txt
4. **Port errors:** Already fixed in app.py

---

## Success Indicators ✅

Your deployment is successful when:
- ✅ Build shows "Build successful"
- ✅ Health endpoint returns JSON
- ✅ Main page loads with upload interface
- ✅ Can upload HTML files
- ✅ AI analysis runs (takes 1-2 minutes)
- ✅ Results display properly

---

**You're all set! Deploy with confidence! 🚀**
