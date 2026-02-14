# 🚀 Deploying Streamlit Dashboard to Render

## Prerequisites
- ✅ API already deployed at: `https://csqa-cnn-api.onrender.com`
- ✅ Supabase database configured and accessible
- ✅ Gemini API key available
- ✅ GitHub repository with the code

---

## 📋 Step-by-Step Deployment Guide

### **Step 1: Prepare Your Repository**

Ensure these files are in your repository:
```bash
.streamlit/
  └── config.toml          # Streamlit configuration
render-dashboard.yaml      # Render deployment config
Procfile                   # Process file for Render
requirements.txt           # Python dependencies
src/
  ├── dashboard.py         # Main dashboard file
  └── reporting/           # Supporting modules
```

### **Step 2: Create Render Web Service**

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Sign in or create an account

2. **Create New Web Service**
   - Click "New +" button → "Web Service"
   - Connect your GitHub repository
   - Select the `csqa-cnn` repository

3. **Configure Service Settings**
   ```
   Name: csqa-cnn-dashboard
   Runtime: Python 3
   Branch: main (or your default branch)
   Root Directory: (leave blank or specify if needed)
   ```

### **Step 3: Configure Build & Start Commands**

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
streamlit run src/dashboard.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

### **Step 4: Set Environment Variables**

In the Render dashboard, add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DB_API` | `https://your-project.supabase.co` | Your Supabase project URL |
| `DB_SERVICE_ROLE_KEY` | `your-service-role-key` | From Supabase Settings → API |
| `GEMINI_API_KEY` | `your-gemini-api-key` | From Google AI Studio |
| `PYTHON_VERSION` | `3.11.14` | Python version |

**To add environment variables:**
1. Click on "Environment" tab in your service
2. Click "Add Environment Variable"
3. Enter Key and Value
4. Click "Save Changes"

### **Step 5: Deploy**

1. **Automatic Deployment**
   - Render will automatically start deploying after you create the service
   - Watch the logs in the "Logs" tab

2. **Monitor Deployment**
   - Build process will install dependencies (~2-3 minutes)
   - Service will start and begin running
   - Look for: `✅ Streamlit app running on port...`

3. **Access Your Dashboard**
   - Once deployed, Render provides a URL like:
   - `https://csqa-cnn-dashboard.onrender.com`
   - Click the URL to access your dashboard

### **Step 6: Verify Deployment**

1. **Check Service Status**
   - Should show "Live" with green indicator
   - If failed, check logs for errors

2. **Test Dashboard**
   - Open the provided URL
   - Check sidebar shows: ✅ Database Connected
   - Check sidebar shows: ✅ Gemini AI Connected
   - Test time range filters
   - Try generating a report

---

## 🔧 Alternative: Deploy Using YAML File

If you prefer automated deployment:

1. **Use the render-dashboard.yaml file**
   ```bash
   # From Render Dashboard:
   # New + → Blueprint → Connect Repository
   # It will detect render-dashboard.yaml automatically
   ```

2. **Set Environment Variables**
   - Even with YAML, you'll need to manually set the environment variables
   - Go to service → Environment tab
   - Add the three required variables

---

## 📊 Service Configuration Details

### Instance Type
- **Free Tier** (recommended for testing)
  - 512 MB RAM
  - 0.1 CPU
  - Spins down after inactivity
  - First request after spin-down takes ~30 seconds

- **Starter** ($7/month)
  - 512 MB RAM
  - 0.5 CPU
  - Never spins down
  - Always fast response

### Auto-Deploy
- Enable "Auto-Deploy" to automatically deploy on git push
- Go to Settings → Build & Deploy → Enable Auto-Deploy

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution:** 
- Ensure `requirements.txt` includes all dependencies
- Check Python version matches (3.11.14)

### Issue: "Port already in use"
**Solution:**
- Render automatically assigns `$PORT` variable
- Ensure start command uses `$PORT`

### Issue: "Database connection failed"
**Solution:**
- Verify `DB_API` and `DB_SERVICE_ROLE_KEY` are set correctly
- Check Supabase project is accessible
- Test connection locally first

### Issue: "Gemini AI not configured"
**Solution:**
- Verify `GEMINI_API_KEY` is set
- Ensure API key is valid and not expired
- Check key has proper permissions

### Issue: Service keeps spinning down
**Solution:**
- Free tier spins down after 15 minutes of inactivity
- Upgrade to Starter plan for always-on service
- Or use a service like UptimeRobot to ping periodically

### Issue: Slow first load after inactivity
**Solution:**
- This is normal for free tier
- Service spins down after inactivity
- First request "wakes up" the service (~30 seconds)
- Subsequent requests are fast

---

## 🔄 Updating Your Dashboard

1. **Push Changes to GitHub**
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push origin main
   ```

2. **Automatic Deployment**
   - If Auto-Deploy is enabled, Render will automatically redeploy
   - Otherwise, click "Manual Deploy" → "Deploy latest commit"

3. **Monitor Deployment**
   - Watch logs for any errors
   - Service will be temporarily unavailable during deployment
   - Usually takes 1-2 minutes

---

## 📱 Custom Domain (Optional)

To use a custom domain:

1. **Add Custom Domain**
   - Go to Settings → Custom Domain
   - Enter your domain (e.g., dashboard.yourdomain.com)

2. **Configure DNS**
   - Add CNAME record pointing to your .onrender.com URL
   - Wait for DNS propagation (~5-60 minutes)

3. **SSL Certificate**
   - Render automatically provisions SSL certificate
   - Your dashboard will be available over HTTPS

---

## 🎯 Best Practices

### Security
- ✅ Never commit environment variables to git
- ✅ Use Supabase service role key (not anon key)
- ✅ Rotate API keys periodically
- ✅ Enable CORS only for specific domains in production

### Performance
- ✅ Use caching in Streamlit (`@st.cache_data`)
- ✅ Optimize database queries
- ✅ Consider upgrading to Starter plan for production
- ✅ Monitor resource usage in Render dashboard

### Monitoring
- ✅ Check logs regularly for errors
- ✅ Set up UptimeRobot for uptime monitoring
- ✅ Monitor Supabase usage and limits
- ✅ Track Gemini API usage

---

## 📞 Support

### Render Documentation
- https://render.com/docs

### Streamlit Documentation
- https://docs.streamlit.io/

### If Deployment Fails
1. Check logs in Render dashboard
2. Verify all environment variables are set
3. Ensure requirements.txt is complete
4. Test locally with same environment variables
5. Check GitHub repository permissions

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] All environment variables set in Render
- [ ] Database connection working
- [ ] Gemini API key working
- [ ] Dashboard loads without errors
- [ ] Time range filters working
- [ ] Report generation working
- [ ] PDF download working
- [ ] Dark theme displaying correctly
- [ ] Mobile responsive (test on phone)
- [ ] Custom domain configured (if applicable)

---

## 🎉 Success!

Your dashboard should now be live at:
```
https://csqa-cnn-dashboard.onrender.com
```

**Next Steps:**
1. Share the URL with your team
2. Monitor usage and performance
3. Consider upgrading plan if needed
4. Add custom domain for professional look

Enjoy your deployed Quality Control Dashboard! 🚀
