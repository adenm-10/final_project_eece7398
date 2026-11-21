#!/usr/bin/env python3
"""Save a Part B figure from a paper PDF as datasets/<dataset>/figures/<paper_id>_fig.png.

  python scripts/extract_figure.py 1004575 1               # list the large images on PDF page 1
  python scripts/extract_figure.py 1004575 1 --index 3     # save image 3 from that list
  python scripts/extract_figure.py icmmt.2012.6230014 5 --crop 1270,2455,1180,190
                                                           # vector figure: crop x,y,w,h of the page at 300 dpi

Embedded images are saved at full resolution. Images stored white-on-black are inverted.
Requires poppler-utils (pdfimages, pdftoppm) and Pillow.
"""
import argparse, glob, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageOps, ImageStat

DATA = Path(__file__).resolve().parent.parent / "datasets"


def large_images(pdf, page):
    """{index: (width, height)} for images on the page at least 400 px wide and 200 px tall."""
    out = subprocess.run(["pdfimages", "-f", str(page), "-l", str(page), "-list", str(pdf)],
                         capture_output=True, text=True).stdout
    images = {}
    for line in out.splitlines()[2:]:  # skip the two header lines
        cols = line.split()
        index, kind, w, h = int(cols[1]), cols[2], int(cols[3]), int(cols[4])
        if kind in ("image", "stencil") and w >= 400 and h >= 200:
            images[index] = (w, h)
    return images


def save_embedded(pdf, page, index, dest, tmp):
    size = large_images(pdf, page).get(index)
    if size is None:
        raise SystemExit(f"--index {index} is not in the list for page {page}")
    subprocess.run(["pdfimages", "-f", str(page), "-l", str(page), "-png", str(pdf), f"{tmp}/img"], check=True)
    # pdfimages numbers its output files differently from its -list output, so find the file by size
    for f in sorted(glob.glob(f"{tmp}/img-*.png")):
        if Image.open(f).size == size:
            shutil.copy(f, dest)
            return
    raise SystemExit(f"no extracted image is {size[0]}x{size[1]}")


def save_crop(pdf, page, crop, dest, tmp):
    x, y, w, h = crop.split(",")
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-f", str(page), "-l", str(page),
                    "-x", x, "-y", y, "-W", w, "-H", h, str(pdf), f"{tmp}/crop"], check=True)
    shutil.copy(glob.glob(f"{tmp}/crop*.png")[0], dest)


def make_black_on_white(path):
    gray = Image.open(path).convert("L")
    if ImageStat.Stat(gray).mean[0] < 128:  # mostly dark -> stored inverted
        ImageOps.invert(gray).save(path)
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper_id")
    ap.add_argument("page", type=int, help="PDF page number, starting at 1")
    ap.add_argument("--index", type=int, help="image number from the list")
    ap.add_argument("--crop", help="x,y,w,h in pixels at 300 dpi")
    ap.add_argument("--dataset", default="full", choices=["full", "intro"])
    a = ap.parse_args()

    pdf = DATA / a.dataset / "pdfs" / f"{a.paper_id}.pdf"
    dest = DATA / a.dataset / "figures" / f"{a.paper_id}_fig.png"

    if a.index is None and a.crop is None:
        images = large_images(pdf, a.page)
        if not images:
            print("no large images on this page: the figure is probably vector, use --crop")
        for index, (w, h) in images.items():
            print(f"  --index {index}   {w}x{h}")
        return

    dest.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        if a.crop:
            save_crop(pdf, a.page, a.crop, dest, tmp)
        else:
            save_embedded(pdf, a.page, a.index, dest, tmp)
    inverted = make_black_on_white(dest)
    print(f"saved {dest.relative_to(DATA.parent)}{'  (inverted to black on white)' if inverted else ''}")


if __name__ == "__main__":
    main()
