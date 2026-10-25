"""Validation helpers for user-uploaded raster images."""

from __future__ import annotations

import io
import warnings
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

MAX_IMAGE_SIZE = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000

_FORMATS_BY_EXTENSION = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
}
_MIME_BY_FORMAT = {
    "JPEG": {"image/jpeg", "image/jpg"},
    "PNG": {"image/png"},
    "GIF": {"image/gif"},
}


def validate_image_upload(file: FileStorage) -> tuple[str | None, int]:
    """Validate filename, declared MIME type, image signature, and decoded data.

    Returns an optional client-safe error message and the associated HTTP status.
    On success, the uploaded stream is rewound for the storage provider.
    """
    filename = Path(file.filename or "").name
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    expected_format = _FORMATS_BY_EXTENSION.get(extension)
    if expected_format is None:
        return "Invalid file type. Upload a PNG, JPEG, or GIF image.", 400

    try:
        file.stream.seek(0)
        content = file.stream.read(MAX_IMAGE_SIZE + 1)
        file.stream.seek(0)
    except (OSError, AttributeError):
        return "Unable to read uploaded file.", 400

    if len(content) > MAX_IMAGE_SIZE:
        return "Image exceeds the 8 MiB upload limit.", 413
    if not content:
        return "Uploaded file is empty.", 400

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                image_format = image.format
                if image_format != expected_format:
                    return "File extension does not match image content.", 400
                if file.mimetype.lower() not in _MIME_BY_FORMAT[image_format]:
                    return "MIME type does not match image content.", 400
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    return "Image dimensions exceed the allowed limit.", 400
                if getattr(image, "n_frames", 1) != 1:
                    return "Animated images are not supported.", 400
                image.verify()

            with Image.open(io.BytesIO(content)) as decoded_image:
                decoded_image.load()
                clean_image = Image.new(decoded_image.mode, decoded_image.size)
                clean_image.paste(decoded_image)
                sanitized = io.BytesIO()
                clean_image.save(sanitized, format=expected_format, optimize=True)
                sanitized_content = sanitized.getvalue()
                if len(sanitized_content) > MAX_IMAGE_SIZE:
                    return "Validated image exceeds the 8 MiB upload limit.", 413
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError,
            Image.DecompressionBombWarning):
        return "Uploaded file is not a valid supported image.", 400

    file.stream = io.BytesIO(sanitized_content)
    return None, 0
