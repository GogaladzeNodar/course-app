from django.core.exceptions import ValidationError
import magic


class BaseFileValidator:
    def __init__(self, max_size=None, allowed_types=None):
        self.max_size = max_size  # in bytes
        self.allowed_types = allowed_types

    def __call__(self, file):
        self.validate_size(file)
        self.validate_type(file)

    def validate_size(self, file):
        if self.max_size and file.size > self.max_size:
            raise ValidationError(
                f"file size is bigger then {self.max_size / (1024 * 1024)} MB."
            )

    def validate_type(self, file):
        if self.allowed_types:
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            if mime not in self.allowed_types:
                raise ValidationError(
                    f"Invalid file type: {mime}. Allowed types are: {', '.join(self.allowed_types)}."
                )

    def deconstruct(self):
        path = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        return (
            path,
            [],
            {"max_size": self.max_size, "allowed_types": self.allowed_types},
        )
