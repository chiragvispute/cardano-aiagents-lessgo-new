# Deploying to Render - Step by Step Guide

## Prerequisites
- Render account (free at https://render.com)
- GitHub account with your code pushed
- All files committed to git

## Step 1: Prepare Your Repository

### 1.1 Create a `Procfile` (Required)
Create a file named `Procfile` in the root of your project (no extension):

```
web: gunicorn app:app
```

### 1.2 Update `requirements.txt`
Make sure your `requirements.txt` includes all dependencies. Add gunicorn:

```bash
pip freeze > requirements.txt
```

Or manually ensure these are included:
```
pymongo>=4.6.0
pandas>=2.1.3
python-dotenv>=1.0.0
crewai>=0.34.3
google-generativeai>=0.3.0
flask
gunicorn
```

### 1.3 Create `.renderignore` (Optional)
Create a `.renderignore` file to exclude unnecessary files:

```
__pycache__/
*.pyc
.env.local
.git/
*.csv
*.html (optional - only if you don't want to include sample files)
```

### 1.4 Create `runtime.txt` (Optional but Recommended)
Specify Python version:

```
python-3.12.0
```

## Step 2: Prepare Environment Variables

### 2.1 Create Environment Variables on Render
You'll add these in the Render dashboard. Create a `.env.render` file locally (do NOT commit this):

```
GEMINI_API_KEY=your_actual_key_here
MONGODB_URI=your_mongodb_connection_string
INSIGHTS_API_PORT=10000
```

**Important:** Never commit `.env.render` to GitHub. Add to `.gitignore`:

```
.env
.env.local
.env.render
*.env
```

## Step 3: Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 4: Deploy on Render

### 4.1 Sign In to Render
1. Go to https://render.com
2. Sign in with GitHub account
3. Click "New" → "Web Service"

### 4.2 Connect Repository
1. Click "Connect your GitHub repository"
2. Authorize Render to access your GitHub
3. Select your repository `cardano-aiagents-lessgo-new`
4. Click "Connect"

### 4.3 Configure Service
Fill in the following details:

| Field | Value |
|-------|-------|
| **Name** | `cardano-insights` (or your preferred name) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` (for testing) or `Starter` (for production) |

### 4.4 Add Environment Variables
1. Scroll down to "Environment" section
2. Click "Add Environment Variable"
3. Add each variable:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your actual Gemini API key |
| `MONGODB_URI` | Your MongoDB connection string |
| `INSIGHTS_API_PORT` | `10000` |

4. Click "Create Web Service"

### 4.5 Monitor Deployment
1. Render will automatically build and deploy
2. Wait for the build logs to show "Build successful"
3. Your app will be live at: `https://cardano-insights.onrender.com`

## Step 5: Test Your Deployment

Once deployment is complete:

```bash
# Test health endpoint
curl https://cardano-insights.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "service": "Cardano Insights API",
  "version": "1.0.0"
}
```

Visit the dashboard:
```
https://cardano-insights.onrender.com/
```

## Step 6: Set Up Auto-Deploy (Optional)

Render will automatically redeploy when you push to main branch.

To control deployments:
1. Go to your Render dashboard
2. Select your service
3. Settings → Auto-Deploy → On/Off

## Important Notes

### Free Tier Limitations
- App goes to sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Limited to 1GB RAM

### For Production
- Upgrade to Starter plan ($7/month)
- Get dedicated resources
- No sleep mode
- Better performance for AI analysis

### Troubleshooting

**Build fails - Python version error:**
- Ensure `runtime.txt` exists with correct version
- Try `python-3.11.0` if 3.12 causes issues

**Module not found errors:**
- Run `pip freeze > requirements.txt` locally
- Commit and push again

**App crashes on startup:**
- Check Render logs: Dashboard → Your Service → Logs
- Ensure all environment variables are set
- Verify MongoDB connection string is correct

**Slow performance:**
- AI analysis is resource-intensive
- Consider caching results
- Use background jobs for large analyses

### Environment Variables Checklist

Before deploying, ensure you have:
- [ ] GEMINI_API_KEY (from Google AI Studio)
- [ ] MONGODB_URI (from MongoDB Atlas)
- [ ] All other required API keys

## Additional Tips

### 1. Use MongoDB Atlas
For free MongoDB hosting:
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Add to Render environment variables

### 2. Monitor Your App
In Render dashboard:
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history

### 3. Update Code
Simply push to main branch:
```bash
git push origin main
```
Render automatically redeploys!

### 4. Custom Domain (Optional)
In Render service settings:
1. Go to Settings
2. Add custom domain
3. Update DNS records
4. Enable HTTPS

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Update `requirements.txt` and redeploy |
| `App crashes after deploy` | Check Render logs for specific error |
| `Port not working` | Render uses port 10000, don't specify port in Flask |
| `Environment vars not loading` | Restart service in Render dashboard |
| `Slow first request` | Normal on free tier (app sleep) |

## Next Steps

After successful deployment:
1. Share the URL: `https://cardano-insights.onrender.com`
2. Users can upload HTML files and get insights
3. Monitor logs for any issues
4. Upgrade plan if needed for production use

---

**Questions?** Check Render documentation: https://render.com/docs
