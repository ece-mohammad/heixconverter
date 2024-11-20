#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI tool that converts and saves HEIC, HEIF images as png, jpg, jpeg files.
"""

from argparse import ArgumentParser
from concurrent.futures import (
    ProcessPoolExecutor as ExecPool,
    as_completed
)
from pathlib import Path
from typing import List

from tqdm import tqdm

from heixconverter import HEIX


class CLI:
    """
    CLI for HEXIConverter
    """

    def __init__(self):
        self.parser: ArgumentParser = self.make_parser()

    @staticmethod
    def make_parser() -> ArgumentParser:
        """Initialize a new argument parser"""
        parser = ArgumentParser(
            description="Convert and save HEIX (HEIC, HEIF) images as jpeg, jpg or png images"
        )
        parser.add_argument(
            "src",
            help="Path to directory that contains HEIX images to convert",
            type=Path,
            metavar="SOURCE",
        )
        parser.add_argument(
            "format",
            help="format to convert images to, supported formats: jpeg, jpg, png",
            metavar="FORMAT",
        )
        parser.add_argument(
            "-o", "--out",
            help="Path to directory where images will be saved. Default is ./converted_images",
            type=Path,
            default=Path("./converted_images"),
        )
        return parser

    @staticmethod
    def _worker(dst_dir: Path, image_path: Path, fmt: str) -> Path:
        heix_image: HEIX = HEIX(image_path)
        new_image_path: str = str(
            dst_dir / heix_image.path.with_suffix(f".{fmt}").name
        )
        converter = getattr(heix_image, HEIX.FormatConvertedMap[fmt])
        converter(new_image_path)
        return Path(new_image_path)

    def run(self):
        """Run CLI """
        args = vars(self.parser.parse_args())
        src_dir: Path = args["src"].absolute()
        dst_dir: Path = args["out"].absolute()
        fmt: str = args["format"]

        if not src_dir.exists():
            raise OSError(f"Source directory {src_dir} doesn't exist")

        if not src_dir.is_dir():
            raise ValueError(f"Source directory path: {src_dir} is a file")

        if not dst_dir.exists():
            dst_dir.mkdir(parents=True)

        heix_images: List[Path] = [i for i in src_dir.glob("*.hei[cf]")]
        num_images: int = len(heix_images)
        print(f"Found {num_images} images.")
        pbar = tqdm(total=num_images, desc="Progress: ", unit="image")
        errors = list()
        with ExecPool() as pool:
            result_to_image = {
                pool.submit(self._worker, dst_dir, img, fmt): img
                for img in heix_images
            }
            for res in as_completed(result_to_image):
                img = result_to_image[res]
                try:
                    res.result()
                except Exception as exc:
                    errors.append(img)
                else:
                    pbar.update(1)


def main():
    CLI().run()


if __name__ == "__main__":
    main()
