# Deployment Guide for Railway

## Quick Deploy

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add FastAPI subtitle burner"
   git push origin main
   ```

2. **Go to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the configuration

3. **Done!** 
   - Railway will install ffmpeg automatically
   - Your API will be live in 2-3 minutes
   - You'll get a URL like: `https://your-app.railway.app`

### Option 2: Deploy with Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Get the URL
railway domain
```

## Environment Variables

Railway automatically sets `PORT` - no manual configuration needed!

## Configuration Files Explained

### `railway.json`
Tells Railway how to build and deploy the app.

### `nixpacks.toml`
Automatically installs ffmpeg during deployment.

### `Procfile`
Backup method for starting the API (Railway uses railway.json first).

### `requirements-api.txt`
Python dependencies for the API.

## Testing Your Deployment

Once deployed, test your API:

```bash
# Replace YOUR_RAILWAY_URL with your actual URL
curl https://your-app.railway.app/health
```

You should see:
```json
{"status": "healthy"}
```

## Using Your Deployed API

### Update test_client.html

Open `test_client.html` and change the API URL:
```javascript
<input type="text" id="apiUrl" value="https://your-app.railway.app">
```

### Call from Code

```python
import requests

url = "https://your-app.railway.app/burn-subtitles"

with open("video.mp4", "rb") as video, open("subs.srt", "rb") as srt:
    files = {"video": video, "srt": srt}
    response = requests.post(url, files=files)
    
    with open("output.mp4", "wb") as f:
        f.write(response.content)
```

## Monitoring

View logs in Railway dashboard:
```bash
railway logs
```

## Troubleshooting

### Build fails
- Check that `nixpacks.toml` exists
- Verify `requirements-api.txt` has correct package versions

### FFmpeg not found
- Ensure `nixpacks.toml` includes ffmpeg in aptPkgs
- Check deployment logs for installation errors

### Timeout errors
- Large videos take time to process
- Railway free tier has request timeouts
- Consider upgrading plan for larger files

### Out of memory
- Railway free tier: 8GB RAM
- Reduce video size or resolution
- Upgrade Railway plan if needed

## Costs

- **Railway Free Tier**: $5 credit/month
  - Plenty for testing and light usage
  - ~100-500 video processing requests/month
  
- **Pro Plan**: $20/month
  - More resources and higher limits
  - Better for production use

## Custom Domain

Add a custom domain in Railway dashboard:
1. Go to your project settings
2. Click "Domains"
3. Add your domain
4. Update DNS records as shown

## Security Tips

1. **Add rate limiting** (optional):
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

2. **Add authentication** (optional):
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

3. **Validate file sizes**:
   The API already validates file types, but you can add size limits:
   ```python
   if video.size > 100 * 1024 * 1024:  # 100MB limit
       raise HTTPException(400, "File too large")
   ```

## Next Steps

- [ ] Deploy to Railway
- [ ] Test with sample video
- [ ] Share your API URL
- [ ] Add to your website/app
- [ ] Monitor usage and costs
- [ ] Consider adding authentication for production

## Support

- Railway docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway GitHub: https://github.com/railwayapp
