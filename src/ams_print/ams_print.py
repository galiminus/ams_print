#!/usr/bin/env python

from PIL import Image, ImagePalette
from typing_extensions import Annotated

from .layer import Layer
from .threemf import ThreeMF

DEFAULT_SIZE = 70 # mm
DEFAULT_HOLE_SIZE = 0.8 # mm
DEFAULT_HOLE_DENSITY_PERCENT = 40 # %

DEFAULT_COHESION_LAYER_HEIGHT = 1
DEFAULT_COLOR_LAYER_HEIGHT = 0.6

COLOR_CONFIGURATIONS = {
    "black":    [ 0, 0, 0],
    "white":    [ 255, 255, 255 ],
    "blue":     [ 0, 120, 191 ]
}

def ams_print(
    input: Annotated[str, "Path to the image to print"],
    output: Annotated[str, "Path to the output 3MF file"],
    size: Annotated[int, "Size of the print in mm"] = DEFAULT_SIZE,
    hole_size: Annotated[float, "Size of the holes in mm"] = DEFAULT_HOLE_SIZE,
    hole_density_percent: Annotated[int, "Density of the holes as a percentage"] = DEFAULT_HOLE_DENSITY_PERCENT,
    cohesion_layer_height: Annotated[float, "Height of the cohesion layer in mm"] = DEFAULT_COHESION_LAYER_HEIGHT,
    color_layer_height: Annotated[float, "Height of the color layers in mm"] = DEFAULT_COLOR_LAYER_HEIGHT,
    dither: Annotated[bool, "Whether to use dithering"] = False
):
    hole_density = hole_density_percent / 100

    resolution = int(size / hole_size)
    hole_count = int(resolution * hole_density)
    scale = size / resolution

    hole_frequency = round((resolution - hole_size * scale * hole_count) / hole_count)
    hole_offset = int(hole_frequency / 2)

    flat_colors = []
    for rgb in COLOR_CONFIGURATIONS.values():
        flat_colors.append(rgb[0])
        flat_colors.append(rgb[1])
        flat_colors.append(rgb[2])

    palette = ImagePalette.ImagePalette(palette=flat_colors * 32) # Why 32?

    with Image.open(input) as image:
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3]) # remove alpha channel
        else:
            rgb_image = image

        resized_image = rgb_image.resize((resolution, resolution), Image.LANCZOS)

        image_palette = Image.new('P', resized_image.size)
        image_palette.putpalette(palette)

        quantized_image = resized_image.quantize(
            dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE,
            palette=image_palette
        )
        quantized_image_data = quantized_image.load()

        cohesion_layer = Layer(z=0, thickness=cohesion_layer_height, scale=scale, size=(quantized_image.size[0], quantized_image.size[1]))
        color_layers = {}


        for x in range(quantized_image.size[0]):
            for y in range(quantized_image.size[1]):
                # Skip holes
                is_hole = (x + hole_offset) % hole_frequency == 0 and (y + hole_offset) % hole_frequency == 0
                if is_hole:
                    continue

                # Add cohesion layer (ie, a tall pixel under each colored pixel to serve as a platform)
                cohesion_layer.put_pixel(x=x, y=y)

                for index, color in enumerate(COLOR_CONFIGURATIONS.keys()):
                    if quantized_image_data[x, y] != index:
                        continue

                    color_layers.setdefault(
                        color,
                        Layer(z=cohesion_layer_height, thickness=color_layer_height, scale=scale, size=(quantized_image.size[0], quantized_image.size[1]))
                    )
                    color_layers[color].put_pixel(x=x, y=y)

        three_mf = ThreeMF()

        three_mf.add_object(object=cohesion_layer, name="cohesion layer", paint_color="1")

        for index, (color, layer) in enumerate(color_layers.items()):
            three_mf.add_object(object=layer, name=f"{color} layer", paint_color="2")

        three_mf.save(path=output)
