"""
Cloudinary storage that shrinks large photos before upload.

Cloudinary's plan rejects images over 10 MB, and full-size camera photos
(15–25 MB) are far bigger than a website needs anyway. Any image that is
larger than MAX_BYTES or MAX_DIMENSION is resized and re-saved as WebP,
which keeps quality high and usually lands well under 1–2 MB.
"""
import os
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from cloudinary_storage.storage import MediaCloudinaryStorage

MAX_BYTES = 2 * 1024 * 1024        # optimise anything above 2 MB
MAX_DIMENSION = 2560               # longest side in pixels (enough for full-width hero images)
QUALITY = 85
CLOUDINARY_LIMIT = 10 * 1024 * 1024


def optimise_image(name, content):
    """Return (name, content), resized/compressed when the image is too big."""
    size = getattr(content, 'size', None)
    try:
        content.seek(0)
        img = Image.open(content)
        img.load()
    except Exception:
        content.seek(0)
        return name, content  # not an image Pillow can read (e.g. SVG/ICO) -> upload as is

    too_big = size is None or size > MAX_BYTES or max(img.size) > MAX_DIMENSION
    if not too_big:
        content.seek(0)
        return name, content

    img = ImageOps.exif_transpose(img)          # keep phone photos the right way up
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=QUALITY, method=6)

    if buffer.tell() > CLOUDINARY_LIMIT:
        raise ValidationError("Image is still larger than 10 MB after compression. Please use a smaller image.")

    new_name = os.path.splitext(name)[0] + '.webp'
    return new_name, ContentFile(buffer.getvalue(), name=os.path.basename(new_name))


class OptimizedMediaCloudinaryStorage(MediaCloudinaryStorage):
    def _save(self, name, content):
        name, content = optimise_image(name, content)
        return super()._save(name, content)
