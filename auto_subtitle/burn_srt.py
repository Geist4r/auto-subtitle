import os
import ffmpeg
import argparse
from .utils import filename


def main():
    parser = argparse.ArgumentParser(
        description="Burn existing SRT subtitles into a video file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", type=str,
                        help="path to video file")
    parser.add_argument("srt", type=str,
                        help="path to SRT subtitle file")
    parser.add_argument("--output_dir", "-o", type=str,
                        default=".", help="directory to save the output video")
    parser.add_argument("--output_name", "-n", type=str,
                        default=None, help="name for output file (without extension)")
    parser.add_argument("--style", type=str,
                        default="OutlineColour=&H40000000,BorderStyle=3",
                        help="FFmpeg subtitle style override")

    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        return

    if not os.path.exists(args.srt):
        print(f"Error: SRT file not found: {args.srt}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine output filename
    if args.output_name:
        output_filename = f"{args.output_name}.mp4"
    else:
        output_filename = f"{filename(args.video)}_subtitled.mp4"
    
    out_path = os.path.join(args.output_dir, output_filename)

    print(f"Adding subtitles from {os.path.basename(args.srt)} to {os.path.basename(args.video)}...")

    try:
        # Load video and audio
        video = ffmpeg.input(args.video)
        audio = video.audio

        # Apply subtitles and combine with audio
        ffmpeg.concat(
            video.filter('subtitles', args.srt, force_style=args.style),
            audio,
            v=1,
            a=1
        ).output(out_path).run(quiet=True, overwrite_output=True)

        print(f"✓ Successfully created subtitled video: {os.path.abspath(out_path)}")

    except ffmpeg.Error as e:
        print(f"Error: Failed to process video. Make sure ffmpeg is installed.")
        print(f"Details: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()
