from PIL import Image

def contains_red(image, region):
    for x in range(region[0], region[0] + region[2]):
        for y in range(region[1], region[1] + region[3]):
            r, g, b = image.getpixel((x, y))
            if r > g and r > b:  # Check if red is the dominant color
                return True
    return False

# Load your image
image_path = 'LYG61973776.png'
image = Image.open(image_path)

# Define your two regions as (x, y, width, height)
region1 = (x1, y1, width1, height1)
region2 = (x2, y2, width2, height2)

# Check for red in the regions
red_in_region1 = contains_red(image, region1)
red_in_region2 = contains_red(image, region2)

print(f"Region 1 contains red: {red_in_region1}")
print(f"Region 2 contains red: {red_in_region2}")
