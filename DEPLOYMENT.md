# Deployment Guide - Get Your Live Website

Follow these steps to deploy your Wedding Venue Finder to the web for free!

## Option 1: Deploy to Render (Recommended - Easiest)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `wedding-venue-finder`
3. Make it **Public** (required for free Render tier)
4. Click "Create repository"

### Step 2: Push Your Code to GitHub

Run these commands in your terminal:

```bash
cd /Users/jackieeicholz/wedding-venue-finder

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wedding-venue-finder.git

# Push code
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render

1. Go to https://render.com and sign up (free account)
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select the `wedding-venue-finder` repository
5. Configure the service:
   - **Name**: `wedding-venue-finder` (or anything you want)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && python seed_data.py`
   - **Start Command**: `gunicorn web:app`
   - **Instance Type**: `Free`
6. Click "Create Web Service"

### Step 4: Get Your Live URL

After 2-3 minutes, Render will give you a URL like:
```
https://wedding-venue-finder.onrender.com
```

Share this link with anyone!

---

## Option 2: Deploy to Railway

### Step 1: Push to GitHub (same as above)

Follow steps 1-2 from Option 1.

### Step 2: Deploy to Railway

1. Go to https://railway.app and sign up (free account)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `wedding-venue-finder`
5. Railway will auto-detect it's a Python app
6. Add these settings:
   - Build Command: `pip install -r requirements.txt && python seed_data.py`
   - Start Command: `gunicorn web:app`
7. Click "Deploy"

### Step 3: Generate Domain

1. Go to Settings → Networking
2. Click "Generate Domain"
3. You'll get a URL like: `wedding-venue-finder.up.railway.app`

---

## Option 3: Quick Deploy (No GitHub needed) - Replit

1. Go to https://replit.com
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. Paste: `https://github.com/YOUR_USERNAME/wedding-venue-finder`
5. Click "Import from GitHub"
6. Replit will automatically run your app
7. Click the "Share" button to get your public URL

---

## Important Notes

### Database Persistence

**Warning**: Free hosting platforms may reset the database on each deployment. This means:
- Initial 14 venues will always be there
- Any venues you add or Reddit data you scrape may be lost on redeployment

**Solutions**:
1. Use the CSV export regularly to backup your data
2. For persistent storage, upgrade to paid tier on Render/Railway
3. Or switch to PostgreSQL (I can help with this if needed)

### Rate Limiting

The Reddit scraper has a 2.5-second delay between requests. This is intentional to be respectful to servers. Be patient when scraping multiple venues.

### Custom Domain (Optional)

If you want a custom domain like `wedding.yourdomain.com`:
1. Buy a domain from Namecheap, Google Domains, etc.
2. In Render/Railway settings, add your custom domain
3. Update your DNS records as instructed

---

## Troubleshooting

**Build Failed**
- Check that all files are committed: `git status`
- Verify requirements.txt includes all dependencies
- Check Render/Railway logs for specific errors

**Site loads but no venues**
- Build command must include: `python seed_data.py`
- Check deployment logs to see if seeding ran

**500 Error**
- Check application logs in Render/Railway dashboard
- Verify all template files were uploaded

**Need Help?**
Open an issue on GitHub or check Render/Railway documentation.

---

## Next Steps After Deployment

1. Share your live URL with your partner/family
2. Add new venues as you discover them
3. Use the "Search Reddit" feature to gather reviews
4. Export to CSV regularly to backup your research
5. Filter venues to create your shortlist

Enjoy planning your wedding!
