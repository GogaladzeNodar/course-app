from .base import BaseFileValidator
from django.core.exceptions import ValidationError
from PIL import Image


class ImageValidator(BaseFileValidator):
    def __init__(
        self, max_size=None, allowed_types=None, max_width=None, max_height=None
    ):
        super().__init__(
            max_size, allowed_types or ["image/jpeg", "image/png", "image/gif"]
        )
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, file):
        super().__call__(file)
        self.validate_dimensions(file)

    def validate_dimensions(self, file):
        img = Image.open(file)
        width, height = img.size
        if self.max_width and width > self.max_width:
            raise ValidationError(
                f"Image width {width}px exceeds maximum of {self.max_width}px."
            )
        if self.max_height and height > self.max_height:
            raise ValidationError(
                f"Image height {height}px exceeds maximum of {self.max_height}px."
            )
        file.seek(0)

    def deconstruct(self):
        path = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        return (
            path,
            [],
            {
                "max_size": self.max_size,
                "allowed_types": self.allowed_types,
                "max_width": self.max_width,
                "max_height": self.max_height,
            },
        )
