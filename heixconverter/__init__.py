#!/usr/bin/env python3
# -*- python3 -*-

"""
A helper class t converts HEIC, HEIF image formats to jpg and jpeg images
"""

from pathlib import Path
from typing import Final, Tuple, Dict, Any

from PIL import Image
import pyheif

__all__ = ["HEIX"]


class HEIX:
    """
    A thin wrapper over Image.Image to save heic, heif images as other formats.
    """
    SupportedExtensions: Final[Tuple[str]] = (".heic", ".heif")
    SupportedFormats: Final[Dict[str, Any]] = {
        "JPEG": {"transparency": False, },
        "PNG" : {"transparency": True, },
    }
    FormatConvertedMap: Final[Dict[str, str]] = {
        "png" : "as_png",
        "jpg" : "as_jpg",
        "jpeg": "as_jpeg",
    }

    def __init__(self, path: Path):
        """
        Initialize a new HEIX image.

        :param path: path to heic, heif image
        :type path: pathlib.Path
        :raises OSError: If the given image path doesn't exist, or not a file.
        :raises ValueError: If the image's suffix isn't heic or heif.
        """
        self.path: Path = path
        if not self.path.exists():
            raise OSError(f"File {self.path} does not exist")

        if not self.path.is_file():
            raise OSError(f"file {self.path} is not a file")

        if self.path.suffix not in self.SupportedExtensions:
            raise ValueError(
                f"Unsupported image type: {self.path.suffix}. "
                f"Supported formats: {self.SupportedExtensions}"
            )
        heix: pyheif.HeifImage = pyheif.read(self.path)
        self.image = Image.frombytes(
            heix.mode,
            heix.size,
            heix.data,
            "raw",
            heix.mode,
            heix.stride
        )

    def _save_as(self, name: str, fmt: str) -> None:
        """
        save image as a different format (jpg, jpeg, or png).

        :param name: name (or path) of the new image
        :type name: str
        :param fmt: new image format, one of jpg, jpeg, png
        :type fmt: str
        """
        if fmt not in self.SupportedFormats:
            raise ValueError(f"Unsupported format: {fmt}")

        if not self.SupportedFormats[fmt]["transparency"] and self.image.mode == "RGBA":
            img = self.image.convert("RGB")
            img.save(name, fmt)
        else:
            self.image.save(name, fmt)

    def as_jpeg(self, name: str) -> None:
        """Save image as JPEG """
        return self._save_as(name, "JPEG")

    def as_jpg(self, name: str) -> None:
        """Save image as JPG"""
        return self._save_as(name, "JPEG")

    def as_png(self, name: str) -> None:
        """Save image as PNG"""
        return self._save_as(name, "PNG")
