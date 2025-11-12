import os
import ffmpeg
import tempfile
import shutil
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
from pathlib import Path
import time

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

# Create output directory for downloadable files
OUTPUT_DIR = TEMP_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Store file metadata (job_id -> {filename, created_at, path})
file_registry = {}


@app.get("/")
async def root():
    return {
        "message": "Subtitle Burner API",
        "version": "2.0.0",
        "endpoints": {
            "POST /burn-subtitles": "Upload files OR provide URLs. Returns download URL (file stored until server restart)",
            "POST /burn-subtitles-url": "Legacy URL-only endpoint (deprecated, use /burn-subtitles instead)",
            "GET /download/{job_id}": "Download a processed video by job ID",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/burn-subtitles")
async def burn_subtitles(
    request: Request,
    video: Optional[UploadFile] = File(None, description="Video file (mp4, avi, mov, etc.)"),
    srt: Optional[UploadFile] = File(None, description="SRT subtitle file"),
    video_url: Optional[str] = Form(None, description="URL to video file (alternative to upload)"),
    srt_url: Optional[str] = Form(None, description="URL to SRT file (alternative to upload)"),
    style: Optional[str] = Form(
        "OutlineColour=&H40000000,BorderStyle=3",
        description="FFmpeg subtitle style options"
    ),
    output_name: Optional[str] = Form(None, description="Custom output filename (without extension)")
):
    """
    Burn SRT subtitles into a video file. Returns a download URL.
    
    - **video**: Video file to upload OR
    - **video_url**: URL to video file
    - **srt**: SRT subtitle file to upload OR
    - **srt_url**: URL to SRT file
    - **style**: Optional FFmpeg style string for subtitle appearance
    - **output_name**: Optional custom name for output file
    
    Returns JSON with download URL. File will be deleted on server restart.
    You can mix and match: e.g., upload video + provide SRT URL
    """
    
    # Validate that we have both video and srt (either as file or URL)
    if not video and not video_url:
        raise HTTPException(status_code=400, detail="Either 'video' file or 'video_url' is required")
    if not srt and not srt_url:
        raise HTTPException(status_code=400, detail="Either 'srt' file or 'srt_url' is required")
    
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    video_path = None
    srt_path = None
    output_path = None
    
    try:
        # Handle video (file or URL)
        if video:
            # Upload from file
            if not video.filename:
                raise HTTPException(status_code=400, detail="Video filename is required")
            
            video_ext = Path(video.filename).suffix
            video_path = job_dir / f"input{video_ext}"
            
            with open(video_path, "wb") as f:
                content = await video.read()
                f.write(content)
        else:
            # Download from URL
            print(f"Downloading video from {video_url}...")
            async with httpx.AsyncClient(timeout=300.0) as client:
                video_response = await client.get(video_url)
                video_response.raise_for_status()
                
                # Determine file extension from URL
                video_ext = ".mp4"  # default
                if "." in video_url.split("/")[-1]:
                    video_ext = "." + video_url.split(".")[-1].split("?")[0]
                
                video_path = job_dir / f"input{video_ext}"
                with open(video_path, "wb") as f:
                    f.write(video_response.content)
        
        # Handle SRT (file or URL)
        if srt:
            # Upload from file
            if not srt.filename:
                raise HTTPException(status_code=400, detail="SRT filename is required")
            
            if not srt.filename.lower().endswith('.srt'):
                raise HTTPException(status_code=400, detail="Subtitle file must be .srt format")
            
            srt_path = job_dir / "subtitles.srt"
            
            with open(srt_path, "wb") as f:
                content = await srt.read()
                f.write(content)
        else:
            # Download from URL
            print(f"Downloading SRT from {srt_url}...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                srt_response = await client.get(srt_url)
                srt_response.raise_for_status()
                
                srt_path = job_dir / "subtitles.srt"
                with open(srt_path, "wb") as f:
                    f.write(srt_response.content)
        
        # Determine output filename
        if output_name:
            output_filename = f"{output_name}.mp4"
        else:
            # Use video filename if available, otherwise generate one
            if video and video.filename:
                output_filename = f"{Path(video.filename).stem}_subtitled.mp4"
            else:
                output_filename = f"subtitled_{job_id[:8]}.mp4"
        
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
        
        # Always return URL - Move file to output directory
        final_path = OUTPUT_DIR / output_filename
        shutil.move(str(output_path), str(final_path))
        
        # Store in registry
        file_registry[job_id] = {
            "filename": output_filename,
            "created_at": time.time(),
            "path": final_path
        }
        
        # Build download URL
        base_url = str(request.base_url).rstrip('/')
        download_url = f"{base_url}/download/{job_id}"
        
        # Clean up temp files (keep only output)
        shutil.rmtree(job_dir, ignore_errors=True)
        
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "download_url": download_url,
            "filename": output_filename,
            "message": "Video processed successfully. File will be deleted on server restart."
        })
        
    except httpx.HTTPError as e:
        # Clean up on error
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download file from URL: {str(e)}"
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


@app.get("/download/{job_id}")
async def download_file(job_id: str):
    """
    Download a processed video file by job ID.
    Files are temporary and will be deleted on server restart.
    """
    if job_id not in file_registry:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = file_registry[job_id]
    file_path = file_info["path"]
    
    if not file_path.exists():
        # Clean up registry if file is missing
        del file_registry[job_id]
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=file_info["filename"]
    )


@app.post("/burn-subtitles-url")
async def burn_subtitles_url(
    video_url: str = Form(..., description="URL to video file"),
    srt_url: str = Form(..., description="URL to SRT subtitle file"),
    style: Optional[str] = Form(
        "OutlineColour=&H40000000,BorderStyle=3",
        description="FFmpeg subtitle style options"
    ),
    output_name: Optional[str] = Form(None, description="Custom output filename (without extension)")
):
    """
    Burn SRT subtitles into a video file using URLs.
    
    - **video_url**: Direct URL to video file
    - **srt_url**: Direct URL to SRT subtitle file
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
        # Download video from URL
        print(f"Downloading video from {video_url}...")
        async with httpx.AsyncClient(timeout=300.0) as client:
            video_response = await client.get(video_url)
            video_response.raise_for_status()
            
            # Determine file extension from URL or content-type
            video_ext = ".mp4"  # default
            if "." in video_url.split("/")[-1]:
                video_ext = "." + video_url.split(".")[-1].split("?")[0]
            
            video_path = job_dir / f"input{video_ext}"
            with open(video_path, "wb") as f:
                f.write(video_response.content)
        
        # Download SRT from URL
        print(f"Downloading SRT from {srt_url}...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            srt_response = await client.get(srt_url)
            srt_response.raise_for_status()
            
            srt_path = job_dir / "subtitles.srt"
            with open(srt_path, "wb") as f:
                f.write(srt_response.content)
        
        # Determine output filename
        if output_name:
            output_filename = f"{output_name}.mp4"
        else:
            output_filename = f"subtitled_{job_id[:8]}.mp4"
        
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
            background=None
        )
        
    except httpx.HTTPError as e:
        # Clean up on error
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download file: {str(e)}"
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
