import requests

# Quick test with sample URLs
# Using a small test video and SRT

print("🎬 Testing Subtitle Burner API with URLs...")
print()

# Test data
data = {
    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "srt_url": "https://raw.githubusercontent.com/andreyvit/subtitle-tools/master/sample.srt",
    "output_name": "test_output"
}

print(f"Video URL: {data['video_url']}")
print(f"SRT URL: {data['srt_url']}")
print()

try:
    print("📤 Sending request to API...")
    response = requests.post(
        "http://localhost:8000/burn-subtitles-url",
        data=data,
        timeout=300
    )
    
    if response.status_code == 200:
        output_path = "url_test_output.mp4"
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Success! Video saved to: {output_path}")
        print(f"📦 Size: {len(response.content) / 1024 / 1024:.2f} MB")
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ API not running. Start it first with: python -m auto_subtitle.api")
except Exception as e:
    print(f"❌ Error: {e}")
