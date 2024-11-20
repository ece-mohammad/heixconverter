# HEIXConverter

Convert and save `HEIC`, `HEIF` images as other formats (`jpg`, `jpeg`, `png`).

## Usage

```commandline
Usage: main.py [-h] [-o OUT] SOURCE FORMAT

Convert and save HEIX (HEIC, HEIF) images as jpeg, jpg or png images

positional arguments:
  SOURCE             Path to directory that contains HEIX images to convert
  FORMAT             format to convert images to, supported formats: jpeg, jpg, png

options:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  Path to directory where images will be saved. Default is ./converted_images
```

## Example

```commandline
python main.py /home/user/Pictures/my_images png 
```

Will save all `heic`, and `heif` images from `/home/user/Pictures/my_images` as
`png` images into a subdirectory `converted_images` in the current working 
directory.
