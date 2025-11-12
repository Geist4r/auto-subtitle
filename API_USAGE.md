# Subtitle Burner API

FastAPI-based API for burning SRT subtitles into videos. Ready to deploy on Railway!

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

Make sure you have `ffmpeg` installed on your system.

### 2. Run the API

```bash
python -m auto_subtitle.api
```

Or using uvicorn directly:

```bash
uvicorn auto_subtitle.api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 3. View API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### `GET /`
Get API information and available endpoints.

**Response:**
```json
{
  "message": "Subtitle Burner API",
  "version": "1.0.0",
  "endpoints": {
    "POST /burn-subtitles": "Upload video and SRT file to create subtitled video",
    "GET /health": "Health check endpoint"
  }
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /burn-subtitles`
Upload a video and SRT file to create a subtitled video.

**Parameters:**
- `video` (file, required): Video file (mp4, avi, mov, etc.)
- `srt` (file, required): SRT subtitle file
- `style` (string, optional): FFmpeg subtitle style options
  - Default: `"OutlineColour=&H40000000,BorderStyle=3"`
- `output_name` (string, optional): Custom output filename (without extension)

**Response:**
Returns the subtitled video file as a download.

## Usage Examples

### Using cURL

```bash
# Basic usage
curl -X POST "http://localhost:8000/burn-subtitles" \
  -F "video=@video.mp4" \
  -F "srt=@subtitles.srt" \
  -o output_video.mp4

# With custom style
curl -X POST "http://localhost:8000/burn-subtitles" \
  -F "video=@video.mp4" \
  -F "srt=@subtitles.srt" \
  -F "style=FontSize=24,PrimaryColour=&H00FFFF" \
  -o output_video.mp4

# With custom output name
curl -X POST "http://localhost:8000/burn-subtitles" \
  -F "video=@video.mp4" \
  -F "srt=@subtitles.srt" \
  -F "output_name=my_final_video" \
  -o my_final_video.mp4
```

### Using Python (requests)

```python
import requests

url = "http://localhost:8000/burn-subtitles"

with open("video.mp4", "rb") as video_file, \
     open("subtitles.srt", "rb") as srt_file:
    
    files = {
        "video": ("video.mp4", video_file, "video/mp4"),
        "srt": ("subtitles.srt", srt_file, "text/plain")
    }
    
    data = {
        "style": "OutlineColour=&H40000000,BorderStyle=3",
        "output_name": "output_video"
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        with open("output_video.mp4", "wb") as f:
            f.write(response.content)
        print("Video processed successfully!")
    else:
        print(f"Error: {response.json()}")
```

### Using JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('video', videoFile);
formData.append('srt', srtFile);
formData.append('style', 'FontSize=24,PrimaryColour=&H00FFFF');
formData.append('output_name', 'my_video');

fetch('http://localhost:8000/burn-subtitles', {
  method: 'POST',
  body: formData
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'output_video.mp4';
  a.click();
})
.catch(error => console.error('Error:', error));
```

## Deploy to Railway

### Method 1: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Initialize and deploy:
   ```bash
   railway init
   railway up
   ```

### Method 2: Using Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Railway will automatically detect the configuration from `railway.json` and `nixpacks.toml`
5. Click "Deploy"

### Environment Variables (Optional)

You can set these in Railway dashboard:
- `PORT`: Port to run the API (Railway sets this automatically)

## Subtitle Styling

You can customize subtitle appearance using FFmpeg style options:

Common options:
- `FontSize=24` - Text size
- `PrimaryColour=&HFFFFFF` - Text color (BGR format)
- `OutlineColour=&H000000` - Outline color
- `BorderStyle=1` - Border style (1=outline, 3=opaque box)
- `Alignment=2` - Position (2=bottom center, 8=top center)
- `MarginV=20` - Vertical margin from edge

Example combined style:
```
FontSize=28,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Alignment=2,MarginV=30
```

## Troubleshooting

### FFmpeg not found
Make sure ffmpeg is installed:
- **Railway**: Automatically installed via `nixpacks.toml`
- **Local**: Install via package manager (see main README)

### Large file uploads
For very large videos, you may need to adjust timeouts:
```python
# In api.py, modify uvicorn.run()
uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
```

### Memory issues
Railway provides 8GB RAM on the free tier. For very large videos, consider:
- Using smaller input videos
- Upgrading Railway plan
- Implementing chunked processing

## API Limits

- **Max file size**: Depends on Railway plan (typically 100MB on free tier)
- **Processing time**: Limited by Railway's timeout settings
- **Concurrent requests**: Handled asynchronously

## Development

Run with auto-reload for development:
```bash
uvicorn auto_subtitle.api:app --reload --port 8000
```

Run tests:
```bash
pytest tests/
```

## License

MIT License (see LICENSE file)
