# 🚀 Quick Deployment to Render

## TL;DR - Deploy in 5 Minutes

### 1. Go to Render
Visit: https://dashboard.render.com/ → New + → Web Service

### 2. Connect GitHub Repository
Select your `csqa-cnn` repository

### 3. Configure Service
```
Name: csqa-cnn-dashboard
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run src/dashboard.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

### 4. Add Environment Variables
```
DB_API = https://your-project.supabase.co
DB_SERVICE_ROLE_KEY = your-service-role-key
GEMINI_API_KEY = your-gemini-api-key
```

### 5. Deploy!
Click "Create Web Service" → Wait 2-3 minutes → Access your dashboard!

---

## Your Dashboard URLs

- **API**: https://csqa-cnn-api.onrender.com ✅ (Already deployed)
- **Dashboard**: https://csqa-cnn-dashboard.onrender.com 🚀 (After deployment)

---

## Need Help?
See full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
