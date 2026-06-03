import os
import uuid
import shutil
from fastapi import UploadFile

UPLOAD_ROOT = "media"

USER_PROFILE_DIR = "users/profile"

DEFAULT_USER_IMAGE = "images/user.png"


def save_file(file: UploadFile, folder: str, allowed_extensions=None) -> str:
    if not file:
        return None

    os.makedirs(os.path.join(UPLOAD_ROOT, folder), exist_ok=True)

    ext = file.filename.split(".")[-1].lower()

    if allowed_extensions and ext not in allowed_extensions:
        raise ValueError(f"Invalid file type. Allowed: {allowed_extensions}")

    filename = f"{uuid.uuid4()}.{ext}"
    fs_path = os.path.join(UPLOAD_ROOT, folder, filename)

    file.file.seek(0)

    with open(fs_path, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            f.write(chunk)

    return f"{UPLOAD_ROOT}/{folder}/{filename}"


def save_user_profile(file: UploadFile) -> str:
    return save_file(
        file,
        USER_PROFILE_DIR,
        allowed_extensions=["jpg", "jpeg", "png", "webp"]
    )

def delete_file(path: str):
    if not path or path == DEFAULT_USER_IMAGE:
        return

    fs_path = path.replace("/", os.sep)

    if os.path.exists(fs_path):
        os.remove(fs_path)