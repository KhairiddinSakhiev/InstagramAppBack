import secrets
import subprocess
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

MEDIA_DIR = Path("media")


def ensure_media_dir() -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",  
}

MAX_VIDEO_DURATION = 60  
MAX_VIDEO_SIZE = 100 * 1024 * 1024 


FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"

def get_video_duration(file_path: str) -> float:
    try:
        result = subprocess.run(
            [
                FFPROBE_PATH,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to read video metadata: {str(e)}"
        )

    if result.returncode != 0:
        stderr_output = result.stderr.strip() if result.stderr else "Unknown error"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ffprobe failed: {stderr_output}"
        )

    return float(result.stdout.strip())


async def save_uploaded_video(
    file: UploadFile,
    subdirectory: str = "videos",
) -> tuple[str, float]:
    """
    Save uploaded video file and validate duration.
    Returns tuple of (relative_path, duration).
    Deletes file and raises HTTPException if duration > 60 seconds.
    """
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only video files are allowed"
        )

    contents = await file.read()

    if len(contents) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video file is too large"
        )

    file_extension = Path(file.filename).suffix.lower() or ".mp4"
    safe_filename = f"{secrets.token_urlsafe(16)}{file_extension}"

    ensure_media_dir()
    target_dir = MEDIA_DIR / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / safe_filename
    relative_path = f"{subdirectory}/{safe_filename}"

    with open(file_path, "wb") as f:
        f.write(contents)

    duration = get_video_duration(str(file_path))

    if duration > MAX_VIDEO_DURATION:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video duration must be 60 seconds or less"
        )

    return relative_path, duration
