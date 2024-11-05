from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image as PilImage

def validate_image_size(image):
    """Validate that the uploaded image is at least 450x350 pixels."""
    with PilImage.open(image) as img:
        width, height = img.size
        if width < 450 or height < 350:
            raise ValidationError(
                _('Image must be at least 450x350 pixels.')
            )
