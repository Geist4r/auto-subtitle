import requests
import sys

# File paths
video_path = "😡DEUTSCHRAPPER! ✨Drill erklärt #shorts.mp4"
srt_path = "deutschrapper_test.srt"
output_path = "deutschrapper_subtitled.mp4"

print("🎬 Testing Subtitle Burner API...")
print(f"Video: {video_path}")
print(f"SRT: {srt_path}")
print()

try:
    # Open files
    with open(video_path, "rb") as video_file, open(srt_path, "rb") as srt_file:
        
        files = {
            "video": (video_path, video_file, "video/mp4"),
            "srt": (srt_path, srt_file, "text/plain")
        }
        
        data = {
            "output_name": "deutschrapper_subtitled"
        }
        
        print("📤 Uploading files to API...")
        response = requests.post(
            "http://localhost:8000/burn-subtitles",
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            # Save output
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Success! Subtitled video saved to: {output_path}")
            print(f"📦 File size: {len(response.content) / 1024 / 1024:.2f} MB")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            sys.exit(1)
            
except FileNotFoundError as e:
    print(f"❌ File not found: {e}")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to API. Is it running on http://localhost:8000?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
