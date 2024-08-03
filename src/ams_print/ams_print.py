from PIL import Image
from typing_extensions import Annotated

from .layer import Layer
from .threemf import ThreeMF

DEFAULT_SIZE = 70 # mm
DEFAULT_PIXEL_SIZE = 0.8 # mm
DEFAULT_GRID_DENSITY_PERCENT = 40 # %

DEFAULT_COHESION_LAYER_HEIGHT = 1
DEFAULT_COLOR_LAYER_HEIGHT = 0.6

def ams_print(
    input: Annotated[str, "Path to the image to print"],
    output: Annotated[str, "Path to the output 3MF file"],

    size: Annotated[int, "Size of the print in mm"] = DEFAULT_SIZE,
    pixel_size: Annotated[float, "Size of the pixels in mm"] = DEFAULT_PIXEL_SIZE,

    grid: Annotated[bool, "Whether to add holes"] = False,
    grid_density_percent: Annotated[int, "Density of the holes as a percentage"] = DEFAULT_GRID_DENSITY_PERCENT,

    cohesion_layer_height: Annotated[float, "Height of the cohesion layer in mm"] = DEFAULT_COHESION_LAYER_HEIGHT,
    color_layer_height: Annotated[float, "Height of the color layers in mm"] = DEFAULT_COLOR_LAYER_HEIGHT,

    layered: Annotated[bool, "Whether to use multiple layers (each color on top of the previous color)"] = False,

    dither: Annotated[bool, "Whether to dither the image"] = False,
    colors: Annotated[int, "Number of colors to use in the image quantization"] = 4,
):
    hole_density = grid_density_percent / 100

    resolution = int(size / pixel_size)
    hole_count = int(resolution * hole_density)
    scale = size / resolution

    hole_frequency = round((resolution - pixel_size * scale * hole_count) / hole_count)
    hole_offset = int(hole_frequency / 2)

    with Image.open(input) as image:
        if image.mode != "P":
            image = image.convert(
                "P",
                palette=Image.ADAPTIVE,
                colors=colors,
                dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
            )

        print(resolution)
        resized_image = image.resize((resolution, resolution), Image.LANCZOS)
        resized_image_data = resized_image.load()

        palette = resized_image.getpalette()

        # Compute color configuration from the image palette
        color_mapping = []
        for index in range(0, len(palette), 3):
            color = tuple(palette[index:index + 3])
            color_mapping.append('#%02X%02X%02X' % color)

        cohesion_layer = Layer(size=(resized_image.size[0], resized_image.size[1]))

        color_layers = {}
        for index, color in enumerate(color_mapping):
            color_layers[color] = Layer(size=(resized_image.size[0], resized_image.size[1]))

        for x in range(resized_image.size[0]):
            for y in range(resized_image.size[1]):
                # Skip holes in the grid (ie, empty pixels) if grid is enabled
                is_hole = (x + hole_offset) % hole_frequency == 0 and (y + hole_offset) % hole_frequency == 0
                if grid and is_hole:
                    continue

                # Add cohesion layer (ie, a tall pixel under each colored pixel to serve as a platform)
                cohesion_layer.plot(x=x, y=y)

                for index, color in enumerate(color_mapping):
                    # Since the image is quantized, we can compare the pixel value to the index
                    if resized_image_data[x, y] != index:
                        continue

                    color_layers[color].plot(x=x, y=y)

                    if layered:
                        # We must also add the previous color layers to sit on top of them.
                        for previous_index in range(index):
                            color_layers[color_mapping[previous_index]].plot(x=x, y=y)

        three_mf = ThreeMF()

        three_mf.add_object(
            object=cohesion_layer,
            name="cohesion layer",
            z=0,
            thickness=cohesion_layer_height,
            scale=scale
        )

        for index, (color, layer) in enumerate(color_layers.items()):
            # Start at the top of the cohesion layer
            z = cohesion_layer_height

            # Add the height of the previous color layers
            if layered:
                z += index * color_layer_height

            three_mf.add_object(
                object=layer,
                name=f"{color} layer",
                z=z,
                thickness=color_layer_height,
                scale=scale
            )

        three_mf.save(path=output)
