# src/core.py
import os
import pathlib
import tempfile
import shutil
import subprocess
from typing import Optional
from contextlib import contextmanager

BASE_WORKDIR = pathlib.Path(os.getenv("COG5_WORKDIR", "/srv/cog5/workspace")).resolve()
MAX_UPLOAD_BYTES = int(os.getenv("COG5_MAX_UPLOAD_BYTES", 10 * 1024 * 1024))  # 10 MiB
MAX_PROCESS_SECONDS = int(os.getenv("COG5_MAX_PROCESS_SECONDS", 30))

def ensure_within_base(path: str) -> pathlib.Path:
    p = pathlib.Path(path).resolve()
    base = BASE_WORKDIR
    # ensure base exists
    base.mkdir(parents=True, exist_ok=True)
    if not str(p).startswith(str(base)):
        raise ValueError("path outside allowed workspace")
    return p

def safe_write_bytes(relpath: str, data: bytes) -> pathlib.Path:
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("payload too large")
    dest = ensure_within_base(relpath)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return dest

@contextmanager
def subprocess_timeout(cmd, *, timeout=MAX_PROCESS_SECONDS, cwd: Optional[str]=None, env=None):
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise TimeoutError("process timed out")
    if proc.returncode != 0:
        raise RuntimeError(f"process failed: {proc.returncode}\n{stderr}")
    yield stdout

def run_user_script(script_relpath: str):
    script_path = ensure_within_base(script_relpath)
    if script_path.suffix not in {".py"}:
        raise ValueError("unsupported script type")
    with tempfile.TemporaryDirectory(dir=str(BASE_WORKDIR)) as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)
        shutil.copy(script_path, tmpdir_path / script_path.name)
        cmd = ["python", script_path.name]
        with subprocess_timeout(cmd, cwd=str(tmpdir_path)) as output:
            return output