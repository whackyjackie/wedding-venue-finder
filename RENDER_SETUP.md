# Render Deployment Setup Guide

## Quick Setup Steps

### 1. Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `wedding-venue-db`
   - **Database**: `wedding_venues`
   - **User**: (auto-generated)
   - **Region**: `Oregon (US West)`
   - **Instance Type**: **Free**
4. Click **"Create Database"**
5. **IMPORTANT**: Copy the **Internal Database URL** (starts with `postgresql://`)

### 2. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect to GitHub and select `whackyjackie/wedding-venue-finder`
3. Configure:
   - **Name**: `wedding-venue-finder`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed_data.py`
   - **Start Command**: `gunicorn web:app`
   - **Instance Type**: **Free**

### 3. Add Environment Variable

1. In your web service, go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the **Internal Database URL** from step 1
4. Click **"Save Changes"**

### 4. Deploy

Render will automatically build and deploy. Watch the logs for:
```
Seeding database with venues...
✓ Added: Carmel Valley Ranch (ID: 1)
...
Your service is live at https://wedding-venue-finder.onrender.com
```

## How It Works

- **Local Development**: Uses SQLite (`data/venues.db`)
- **Production (Render)**: Automatically detects `DATABASE_URL` and uses PostgreSQL
- **Database Persistence**: PostgreSQL data persists across deployments (unlike SQLite on free hosting)

## Troubleshooting

### Build Fails

**Check**: Build logs for specific error
**Fix**: Ensure `psycopg2-binary` is in `requirements.txt`

### Can't Connect to Database

**Check**: Environment variable `DATABASE_URL` is set correctly
**Fix**: Copy **Internal Database URL** (not External) from PostgreSQL service

### Seeding Fails

**Check**: Database is created and accessible
**Fix**: Ensure PostgreSQL instance is running before deploying web service

### Site Loads But No Venues

**Check**: Build logs - did seeding complete?
**Fix**: Manually run seed: Go to **Shell** tab and run `python seed_data.py`

## Updating Your Live Site

When you make changes locally:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render auto-deploys on every push to `main`.

## Free Tier Limits

- PostgreSQL: 90-day free database (1GB storage)
- Web Service: Spins down after 15 min of inactivity (first request may be slow)
- Both services: Free forever if within limits

## Connecting to Production Database (Optional)

If you need to access the production database directly:

1. Install PostgreSQL locally: `brew install postgresql`
2. Get **External Database URL** from Render PostgreSQL dashboard
3. Connect:
```bash
psql "postgresql://user:password@host/database"
```

## Environment Variables Reference

- `DATABASE_URL`: PostgreSQL connection string (set automatically on Render)
- No other environment variables needed

## Next Steps

1. Share your live URL: `https://wedding-venue-finder.onrender.com`
2. Add venues through the web interface
3. Use "Search Reddit" and "Search Reviews" buttons
4. Export to CSV regularly to backup research
