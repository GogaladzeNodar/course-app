from django.core.exceptions import ValidationError
import magic
import zipfile
from .base import BaseFileValidator


class AdvancedFileValidator(BaseFileValidator):
    def __init__(self, max_size=None, allowed_types=None, allowed_inner_types=None):
        super().__init__(max_size, allowed_types)
        self.allowed_inner_types = allowed_inner_types or []

    def validate_zip_contents(self, file):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as zf:
                for name in zf.namelist():
                    if name.endswith("/"):
                        continue

                    with zf.open(name) as inner_file:
                        sample = inner_file.read(2048)
                        mime = magic.from_buffer(sample, mime=True)

                        if self.allowed_inner_types and not any(
                            mime.startswith(t) for t in self.allowed_inner_types
                        ):
                            raise ValidationError(
                                f"Invalid file inside zip: {name} "
                                f"(MIME: {mime}). Allowed types are: {', '.join(self.allowed_inner_types)}"
                            )
            file.seek(0)

    def __call__(self, file):
        super().__call__(file)
        self.validate_zip_contents(file)

    def deconstruct(self):
        path = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        return (
            path,
            [],
            {
                "max_size": self.max_size,
                "allowed_types": self.allowed_types,
                "allowed_inner_types": self.allowed_inner_types,
            },
        )
