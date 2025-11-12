# Automatic subtitles in your videos

This repository uses `ffmpeg` and [OpenAI's Whisper](https://openai.com/blog/whisper) to automatically generate and overlay subtitles on any video.

## 🚀 New Features

- **FastAPI REST API**: Deploy as a web service on Railway or any cloud platform
- **Burn SRT Command**: Quickly add existing SRT subtitles to videos without AI processing

## Installation

To get started, you'll need Python 3.7 or newer. Install the binary by running the following command:

    pip install git+https://github.com/m1guelpf/auto-subtitle.git

You'll also need to install [`ffmpeg`](https://ffmpeg.org/), which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg
```

## Usage

The following command will generate a `subtitled/video.mp4` file contained the input video with overlayed subtitles.

    auto_subtitle /path/to/video.mp4 -o subtitled/

The default setting (which selects the `small` model) works well for transcribing English. You can optionally use a bigger model for better results (especially with other languages). The available models are `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large`.

    auto_subtitle /path/to/video.mp4 --model medium

Adding `--task translate` will translate the subtitles into English:

    auto_subtitle /path/to/video.mp4 --task translate

Run the following to view all available options:

    auto_subtitle --help

## Burn Existing SRT Subtitles

If you already have an SRT file and just want to add it to your video (without AI transcription):

    burn_srt video.mp4 subtitles.srt -o output/

See [BURN_SRT_USAGE.md](BURN_SRT_USAGE.md) for more details.

## 🌐 REST API

Deploy this as a web service! Perfect for integrating subtitle burning into your applications.

### Quick Start (Local)

```bash
# Install API dependencies
pip install -r requirements-api.txt

# Run the API
python -m auto_subtitle.api
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Deploy to Railway

1. Click the button below or push to GitHub
2. Railway will automatically detect and deploy the API
3. FFmpeg is automatically installed via `nixpacks.toml`

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

See [API_USAGE.md](API_USAGE.md) for complete API documentation, examples, and deployment guide.

### Test the API

Open `test_client.html` in your browser for a simple web interface to test the API.

## License

This script is open-source and licensed under the MIT License. For more details, check the [LICENSE](LICENSE) file.
