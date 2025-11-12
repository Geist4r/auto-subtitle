# Burn SRT - Add Existing Subtitles to Videos

This tool allows you to burn existing SRT subtitle files into your videos.

## Installation

First, install the package (if not already installed):

```bash
pip install git+https://github.com/Geist4r/auto-subtitle.git
```

Make sure you have `ffmpeg` installed (see main README for installation instructions).

## Usage

### Basic Usage

The simplest way to use it:

```bash
burn_srt video.mp4 subtitles.srt
```

This will create a file named `video_subtitled.mp4` in the current directory.

### Specify Output Directory

```bash
burn_srt video.mp4 subtitles.srt -o output/
```

### Custom Output Name

```bash
burn_srt video.mp4 subtitles.srt -n my_final_video
```

This creates `my_final_video.mp4`.

### Custom Subtitle Style

You can customize the subtitle appearance using FFmpeg style options:

```bash
burn_srt video.mp4 subtitles.srt --style "FontSize=24,PrimaryColour=&H00FF00"
```

Common style options:
- `FontSize=24` - Set font size
- `PrimaryColour=&H00FFFF` - Set text color (in BGR format)
- `OutlineColour=&H40000000` - Set outline color
- `BorderStyle=3` - Set border style (1=outline, 3=opaque box)
- `Alignment=2` - Set alignment (2=bottom center, 8=top center)

### View All Options

```bash
burn_srt --help
```

## Examples

```bash
# Basic usage
burn_srt my_video.mp4 my_subtitles.srt

# Save to specific folder with custom name
burn_srt my_video.mp4 my_subtitles.srt -o final_videos/ -n presentation_final

# Larger subtitles with yellow text
burn_srt my_video.mp4 my_subtitles.srt --style "FontSize=28,PrimaryColour=&H00FFFF"
```

## Differences from auto_subtitle

- **burn_srt**: Takes an existing SRT file and burns it into the video (fast, no AI needed)
- **auto_subtitle**: Uses Whisper AI to automatically generate subtitles from the video's audio (slower, requires AI processing)

Use `burn_srt` when you already have subtitles and just need to add them to your video!
