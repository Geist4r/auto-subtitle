import requests
import sys

# Test with public URLs
# You can replace these with your own URLs
video_url = input("Enter video URL (or press Enter to skip): ").strip()
srt_url = input("Enter SRT URL (or press Enter to skip): ").strip()

if not video_url or not srt_url:
    print("❌ Skipping test - no URLs provided")
    print("\nTo test, provide:")
    print("- A direct link to a video file (e.g., .mp4)")
    print("- A direct link to an SRT file")
    sys.exit(0)

output_path = "url_test_output.mp4"

print("\n🎬 Testing Subtitle Burner API with URLs...")
print(f"Video URL: {video_url}")
print(f"SRT URL: {srt_url}")
print()

try:
    data = {
        "video_url": video_url,
        "srt_url": srt_url,
        "output_name": "url_test"
    }
    
    print("📤 Sending request to API...")
    response = requests.post(
        "http://localhost:8000/burn-subtitles-url",
        data=data,
        timeout=300
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
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to API. Is it running on http://localhost:8000?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
