import asyncio, shlex
from loguru import logger

FFMPEG_BIN = "ffmpeg"

def build_ffmpeg_cmd(input_url: str, rtmp_url: str, stream_key: str, copy: bool = True) -> list[str]:
    # Compose full destination (Telegram RTMP)
    dst = f"{rtmp_url.rstrip('/')}/{stream_key}"
    if copy:
        # Copy streams if compatible; Telegram requires H.264/AAC in FLV
        return [FFMPEG_BIN, "-re", "-i", input_url, "-c", "copy", "-f", "flv", dst]
    else:
        # Safe re-encode
        return [
            FFMPEG_BIN, "-re", "-i", input_url,
            "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3500k", "-maxrate", "3500k", "-bufsize", "7000k",
            "-g", "50", "-keyint_min", "50",
            "-c:a", "aac", "-b:a", "128k",
            "-f", "flv", dst
        ]

async def run_ffmpeg(cmd: list[str], on_line=None) -> int:
    logger.info("Starting FFmpeg: {}", shlex.join(cmd))
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    if on_line is None:
        on_line = lambda line: None
    assert proc.stdout is not None
    async for raw in proc.stdout:
        line = raw.decode(errors="ignore").rstrip()
        on_line(line)
    rc = await proc.wait()
    logger.info("FFmpeg exited with code {}", rc)
    return rc
