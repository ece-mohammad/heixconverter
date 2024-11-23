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
    SupportedFormats: Final[Dict[str, Dict[str, Any]]] = {
        "png" : {"codec": "PNG", "transparency": True},
        "jpg" : {"codec": "JPEG", "transparency": False},
        "jpeg": {"codec": "JPEG", "transparency": False},
    }

    def __init__(self, path: Path):
        """
        Initialize a new HEIX image.

        :param path: path to heic, heif image
        :type path: pathlib.Path
        :raises OSError: If the given image path doesn't exist, or not a file.
        :raises ValueError: If the image's suffix isn't heic or heif.
        """
        if not path.exists():
            raise OSError(f"File {path} does not exist")

        if not path.is_file():
            raise OSError(f"file {path} is not a file")

        self.path: Path = path
        heix: pyheif.HeifImage = pyheif.read(self.path)
        self.image = Image.frombytes(
            heix.mode,
            heix.size,
            heix.data,
            "raw",
            heix.mode,
            heix.stride
        )

    def save_as(self, dst_dir: Path, fmt: str) -> Path:
        """
        save image as a different format (jpg, jpeg, or png).

        :param dst_dir: directory to save image to
        :type dst_dir: Path
        :param fmt: format to save image as (jpg, jpeg, png)
        :type fmt: str
        """
        if not fmt in self.SupportedFormats:
            raise ValueError(f"Unsupported conversion format: {fmt}")

        codec = self.SupportedFormats[fmt]["codec"]
        alpha_support = self.SupportedFormats[fmt]["transparency"]
        new_name = dst_dir / self.path.with_suffix(f".{fmt}").name
        if self.image.mode == "RGBA" and not alpha_support:
            img = self.image.convert("RGB")
            img.save(str(new_name), codec)
        else:
            self.image.save(str(new_name), codec)
        return new_name
