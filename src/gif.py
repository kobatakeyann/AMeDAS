import glob
import os
from PIL import Image

def convert_jpg_to_gif(parent_path,dir_out,gif_name):
    img_array = []
    for filename in sorted(glob.glob(f"{parent_path}/*.jpg")):
        img = Image.open(filename)
        img.thumbnail((1200,800))
        img_array.append(img)

        out_path = os.path.join(dir_out,gif_name)

    img_array[0].save(out_path ,save_all=True, append_images=img_array[1:], optimize=True, duration=1000, loop=0)
