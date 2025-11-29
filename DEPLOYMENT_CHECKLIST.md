# Quick Deployment Checklist for Render

## Pre-Deployment Checklist

- [ ] All code is committed to Git
- [ ] `Procfile` created in root directory
- [ ] `runtime.txt` created with Python 3.12.0
- [ ] `.renderignore` created
- [ ] `requirements.txt` updated with gunicorn
- [ ] `.gitignore` includes `.env` files
- [ ] All secrets moved to environment variables (not in code)

## Files You Need to Create/Update

### 1. Procfile (Already created)
Location: `/root/Procfile`
```
web: gunicorn app:app
```

### 2. runtime.txt (Already created)
Location: `/root/runtime.txt`
```
python-3.12.0
```

### 3. requirements.txt (Update needed)
Add `gunicorn>=21.2.0` to your existing requirements.txt

### 4. .renderignore (Already created)
Location: `/root/.renderignore`
Prevents large files from uploading

## Render Deployment Steps

### Step 1: Push Code to GitHub
```bash
cd C:\Users\HP\Desktop\cardano-aiagents-lessgo-new
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account
- Go to https://render.com
- Sign up with GitHub

### Step 3: Create New Web Service
1. Click "New" → "Web Service"
2. Select your repository
3. Configure as follows:

| Setting | Value |
|---------|-------|
| Name | `cardano-insights` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | `Free` (test) or `Starter` (production) |

### Step 4: Add Environment Variables
In Render dashboard, add these variables:

```
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=your_mongodb_connection_string
```

Where to get these:
- **GEMINI_API_KEY**: https://ai.google.dev/
- **MONGODB_URI**: https://www.mongodb.com/cloud/atlas (free tier available)

### Step 5: Deploy
Click "Create Web Service"
- Render will build and deploy automatically
- Wait for "Build successful"
- Your app will be live at `https://cardano-insights.onrender.com`

## Post-Deployment

### Test Your App
```bash
# Health check
https://cardano-insights.onrender.com/health

# Main app
https://cardano-insights.onrender.com/
```

### Monitor
- Go to Render Dashboard
- Select your service
- Check Logs for any errors
- Monitor CPU/Memory usage

## Troubleshooting

**Build fails?**
- Check if `Procfile` is correct
- Verify `requirements.txt` exists
- Check Render logs for specific error

**App won't start?**
- Ensure environment variables are set
- Check MongoDB URI is valid
- Look at Render logs for errors

**Slow performance?**
- Free tier apps sleep after 15 mins
- First request takes ~30 seconds
- Upgrade to Starter ($7/month) for better performance

## Important: Port Configuration

⚠️ **IMPORTANT**: Don't specify port in Flask app for Render!

Your current `app.py` has:
```python
port = int(os.getenv('INSIGHTS_API_PORT', 5002))
app.run(debug=True, host='0.0.0.0', port=port)
```

For Render, change to:
```python
port = int(os.getenv('PORT', 5000))
app.run(debug=False, host='0.0.0.0', port=port)
```

Or Render will auto-assign port 10000.

## Update requirements.txt

Replace old requirements.txt with this:

```
pymongo>=4.6.0
pandas>=2.1.3
python-dotenv>=1.0.0
crewai>=0.34.3
google-generativeai>=0.3.0
flask
gunicorn>=21.2.0
```

## Security Notes

1. **Never commit `.env` file**
   - Add to `.gitignore`
   - Use Render's environment variables

2. **Use strong API keys**
   - Don't reuse local keys
   - Rotate keys periodically

3. **Monitor logs**
   - Watch for errors
   - Check for suspicious activity

## Support

- Render Docs: https://render.com/docs
- Flask on Render: https://render.com/docs/deploy-flask
- Gunicorn: https://gunicorn.org/

---

**Ready to deploy?** Follow the "Render Deployment Steps" above!
