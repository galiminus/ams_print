#!/usr/bin/env python

from PIL import Image, ImagePalette
from sys import argv


from datetime import datetime

from layer import Layer
from threemf import ThreeMF

## Configuration

SIZE = 70 # mm
HOLE_SIZE = 0.8 # mm
HOLE_DENSITY_PERCENT = 100 # %

COHESION_LAYER_HEIGHT = 1
COLOR_LAYER_HEIGHT = 0.6

## End configuration

INPUT_IMAGE_PATH = argv[1]

HOLE_DENSITY = HOLE_DENSITY_PERCENT * 0.4 / 100

RESOLUTION = int(SIZE / HOLE_SIZE)
HOLE_COUNT = int(RESOLUTION * HOLE_DENSITY)
SCALE = SIZE / RESOLUTION

HOLE_FREQUENCY = round((RESOLUTION - HOLE_SIZE * SCALE * HOLE_COUNT) / HOLE_COUNT)
HOLE_OFFSET = int(HOLE_FREQUENCY / 2)
DITHER = False

COLOR_CONFIGURATIONS = {
    "black":    [ 0, 0, 0],
    "white":    [ 255, 255, 255 ],
    "blue":     [ 0, 120, 191 ]
}

def ams_print():
    flat_colors = []
    for rgb in COLOR_CONFIGURATIONS.values():
        flat_colors.append(rgb[0])
        flat_colors.append(rgb[1])
        flat_colors.append(rgb[2])

    palette = ImagePalette.ImagePalette(palette=flat_colors * 32) # Why 32?

    with Image.open(INPUT_IMAGE_PATH) as image:
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3]) # remove alpha channel
        else:
            rgb_image = image

        resized_image = rgb_image.resize((RESOLUTION, RESOLUTION), Image.LANCZOS)

        image_palette = Image.new('P', resized_image.size)
        image_palette.putpalette(palette)

        quantized_image = resized_image.quantize(
            dither=Image.Dither.FLOYDSTEINBERG if DITHER else Image.Dither.NONE,
            palette=image_palette
        )
        quantized_image_data = quantized_image.load()

        cohesion_layer = Layer(z=0, thickness=COHESION_LAYER_HEIGHT, scale=SCALE, size=(quantized_image.size[0], quantized_image.size[1]))
        color_layers = {}


        for x in range(quantized_image.size[0]):
            for y in range(quantized_image.size[1]):
                # Skip holes
                is_hole = (x + HOLE_OFFSET) % HOLE_FREQUENCY == 0 and (y + HOLE_OFFSET) % HOLE_FREQUENCY == 0
                if is_hole:
                    continue

                # Add cohesion layer (ie, a tall pixel under each colored pixel to serve as a platform)
                cohesion_layer.put_pixel(x=x, y=y)

                for index, color in enumerate(COLOR_CONFIGURATIONS.keys()):
                    if quantized_image_data[x, y] != index:
                        continue

                    color_layers.setdefault(
                        color,
                        Layer(z=COHESION_LAYER_HEIGHT, thickness=COLOR_LAYER_HEIGHT, scale=SCALE, size=(quantized_image.size[0], quantized_image.size[1]))
                    )
                    color_layers[color].put_pixel(x=x, y=y)

        three_mf = ThreeMF()

        three_mf.add_object(object=cohesion_layer, id="1", paint_color="1")

        # for index, (color, layer) in enumerate(color_layers.items()):
        #     add_layer_to_model(document=model_document, layer=layer, id=str(index + 2), paint_color="2")

        now = datetime.now().strftime("%m%d%Y%H%M%S")
        output_file_path = f"output-{now}.3mf"

        three_mf.save(path=output_file_path)
