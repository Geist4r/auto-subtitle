import os
import ffmpeg
import tempfile
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
from pathlib import Path

app = FastAPI(
    title="Subtitle Burner API",
    description="API to burn SRT subtitles into videos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory for processing
TEMP_DIR = Path(tempfile.gettempdir()) / "subtitle_api"
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "Subtitle Burner API",
        "version": "1.0.0",
        "endpoints": {
            "POST /burn-subtitles": "Upload video and SRT file to create subtitled video",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/burn-subtitles")
async def burn_subtitles(
    video: UploadFile = File(..., description="Video file (mp4, avi, mov, etc.)"),
    srt: UploadFile = File(..., description="SRT subtitle file"),
    style: Optional[str] = Form(
        "OutlineColour=&H40000000,BorderStyle=3",
        description="FFmpeg subtitle style options"
    ),
    output_name: Optional[str] = Form(None, description="Custom output filename (without extension)")
):
    """
    Burn SRT subtitles into a video file.
    
    - **video**: Video file to add subtitles to
    - **srt**: SRT subtitle file
    - **style**: Optional FFmpeg style string for subtitle appearance
    - **output_name**: Optional custom name for output file
    """
    
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    video_path = None
    srt_path = None
    output_path = None
    
    try:
        # Validate file types
        if not video.filename:
            raise HTTPException(status_code=400, detail="Video filename is required")
        if not srt.filename:
            raise HTTPException(status_code=400, detail="SRT filename is required")
        
        if not srt.filename.lower().endswith('.srt'):
            raise HTTPException(status_code=400, detail="Subtitle file must be .srt format")
        
        # Save uploaded files
        video_ext = Path(video.filename).suffix
        video_path = job_dir / f"input{video_ext}"
        srt_path = job_dir / "subtitles.srt"
        
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        with open(srt_path, "wb") as f:
            content = await srt.read()
            f.write(content)
        
        # Determine output filename
        if output_name:
            output_filename = f"{output_name}.mp4"
        else:
            output_filename = f"{Path(video.filename).stem}_subtitled.mp4"
        
        output_path = job_dir / output_filename
        
        # Process video with ffmpeg
        try:
            # Use absolute paths - ffmpeg on Windows needs proper path format
            video_path_str = str(video_path.absolute())
            srt_path_str = str(srt_path.absolute())
            output_path_str = str(output_path.absolute())
            
            video_input = ffmpeg.input(video_path_str)
            audio = video_input.audio
            
            # Use filename= parameter for subtitles filter on Windows
            ffmpeg.concat(
                video_input.filter('subtitles', filename=srt_path_str, force_style=style),
                audio,
                v=1,
                a=1
            ).output(output_path_str).run(quiet=True, overwrite_output=True)
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg processing failed: {error_msg}"
            )
        
        # Return the processed video
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=output_filename,
            background=None  # We'll clean up manually after response
        )
        
    except HTTPException:
        # Clean up on error
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
        raise
        
    except Exception as e:
        # Clean up on error
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Clean up old temp files on startup"""
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up temp directory on shutdown"""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
