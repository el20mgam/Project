from PIL import Image


def contains_magenta(image, region):
    # Convert the image to CMYK
    cmyk_image = image.convert('CMYK')

    for x in range(region[0], region[0] + region[2]):
        for y in range(region[1], region[1] + region[3]):
            c, m, y, k = cmyk_image.getpixel((x, y))
            if m > c and m > y:  # Check if magenta is the dominant color
                return True
    return False


# Load your image
image_path = 'LYG61973776.png'
image = Image.open(image_path)

# Define your two regions as (x, y, width, height)
region1 = (x1, y1, width1, height1)
region2 = (x2, y2, width2, height2)

# Check for magenta in the regions
magenta_in_region1 = contains_magenta(image, region1)
magenta_in_region2 = contains_magenta(image, region2)

print(f"Region 1 contains magenta: {magenta_in_region1}")
print(f"Region 2 contains magenta: {magenta_in_region2}")
