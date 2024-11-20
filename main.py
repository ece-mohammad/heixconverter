#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from pathlib import Path

from tqdm import tqdm

from heixconverter import HEIX


class CLI:
    def __init__(self):
        self.parser: ArgumentParser = self.make_parser()

    @staticmethod
    def make_parser() -> ArgumentParser:
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

    def run(self):
        args = vars(self.parser.parse_args())
        src_dir: Path = args["src"].absolute()
        dst_dir: Path = args["out"].absolute()
        fmt: str = args["format"]

        if not src_dir.exists():
            raise OSError(f"Source directory {src_dir} doesn't exist")

        if not src_dir.is_dir():
            raise ValueError(f"Source directory path: {src_dir} is a file")

        if not dst_dir.exists():
            dst_dir.mkdir()

        heix_images = [i for i in src_dir.glob("*.hei[cf]")]
        print(f"Found {len(heix_images)} images.")
        pbar = tqdm(heix_images)
        for img_path in pbar:
            img_path = img_path
            img_name = img_path.stem
            dst_img = dst_dir / img_name
            img = HEIX(Path(img_path))
            pbar.set_description(f"Converting image: {img_name}")
            if fmt == "png":
                img.as_png(f"{dst_img.with_suffix('.png')}")

            elif fmt == "jpeg":
                img.as_jpeg(f"{dst_img.with_suffix('.jpeg')}")

            else:
                img.as_jpg(f"{dst_img.with_suffix('.jpg')}")


def main():
    CLI().run()


if __name__ == "__main__":
    main()
