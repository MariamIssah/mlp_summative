# Railway Deployment Guide

## Option 1: Deploy from Railway Website

1. Go to: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select: `MariamIssah/mlp_summative`
4. Railway will automatically:
   - Detect your Dockerfile
   - Build and deploy your service
   - Generate a public URL

## Option 2: Use Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Deploy:
   ```bash
   railway up
   ```

## Option 3: Direct GitHub Integration

1. Go to your GitHub repository: https://github.com/MariamIssah/mlp_summative
2. Look for Railway integration (if installed)
3. Or go to Railway dashboard and connect the repo from there

## After Deployment

1. Go to your service in Railway
2. Settings → Variables → Add `DATA_VARIANT=mini`
3. Settings → Networking → Generate Domain
4. Test: `https://your-service.up.railway.app/docs`

