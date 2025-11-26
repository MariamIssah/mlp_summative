# Streamlit Cloud Deployment Guide

## Option 1: Deploy to Streamlit Cloud (Recommended - Free & Easy)

### Steps:

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push
   ```

2. **Go to Streamlit Cloud**:
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

3. **Deploy your app**:
   - Click "New app"
   - Select your repository: `MariamIssah/mlp_summative`
   - Main file path: `streamlit_app.py`
   - Branch: `main`
   - Click "Deploy"

4. **Configure Environment Variables** (Optional):
   - In Streamlit Cloud dashboard → Settings → Secrets
   - Add if needed:
     ```
     API_URL = "https://mlpsummative-production.up.railway.app"
     ```
   - Or the app will auto-detect and use the Railway URL

5. **Wait for deployment**:
   - Streamlit Cloud will build and deploy your app
   - You'll get a URL like: `https://your-app-name.streamlit.app`

### Notes:
- Streamlit Cloud automatically detects `requirements.txt` and installs dependencies
- The app will automatically use the Railway API URL when deployed
- Free tier includes 1GB RAM and reasonable usage limits

## Option 2: Deploy Streamlit to Railway (Alternative)

### Steps:

1. **Create a new Railway service for Streamlit**:
   - In Railway dashboard, click "New" → "Empty Service"
   - Or add a new service to your existing project

2. **Configure the service**:
   - **Build Command**: Leave blank (Railway will auto-detect)
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - **Root Directory**: Leave blank (or set if needed)

3. **Set Environment Variables**:
   - `API_URL`: `https://mlpsummative-production.up.railway.app`
   - `STREAMLIT_CLOUD`: `true` (optional, to trigger cloud mode)

4. **Connect to GitHub**:
   - Settings → Source → Connect GitHub
   - Select your repository
   - Railway will auto-deploy

5. **Generate Domain**:
   - Settings → Networking → Generate Domain

### Notes:
- Railway free tier may have resource limits
- Streamlit Cloud is generally easier for Streamlit apps
- Both options will work, but Streamlit Cloud is optimized for Streamlit

## Testing After Deployment

1. **Check API Connection**:
   - Open your deployed Streamlit app
   - Go to "Home" page
   - Should show "Online" status if API is reachable

2. **Test Prediction**:
   - Go to "Predict" page
   - Upload a test image
   - Should get predictions from Railway API

3. **Test Retrain** (if using local API):
   - Note: Retrain may timeout on Railway, so this is best demonstrated locally

## Troubleshooting

- **API not connecting**: Check that Railway API is running and accessible
- **Import errors**: Ensure all dependencies are in `requirements.txt`
- **Timeout errors**: Railway free tier has limits; consider using local API for retraining demos

