from PIL import Image


def contains_magenta(image, region):
    # Convert the image to CMYK
    cmyk_image = image.convert('CMYK')

    max_magenta_percentage = 0
    for x in range(region[0], region[0] + region[2]):
        for y in range(region[1], region[1] + region[3]):
            c, m, y, k = cmyk_image.getpixel((x, y))
            magenta_percentage = m / 255 * 100
            max_magenta_percentage = max(max_magenta_percentage, magenta_percentage)
            if magenta_percentage > 50:
                return True, max_magenta_percentage
    return False, max_magenta_percentage


# Load your image
image_path = 'LYG61973776.png'
image = Image.open(image_path)

# Define your two regions as (x, y, width, height)
control = (1414, 733, 39, 13)
test = (1424, 788, 30, 8)

# Check for magenta above 50% in the regions
magenta_in_control, control_max_magenta = contains_magenta(image, control)
magenta_in_test, test_max_magenta = contains_magenta(image, test)

# Output results
if not magenta_in_control and not magenta_in_test:
    print("Invalid")
elif not magenta_in_test and magenta_in_control:
    print("Negative")
elif magenta_in_test and magenta_in_control:
    print("Positive")

print(f"Control magenta percentage: {control_max_magenta:.2f}%")
print(f"Test magenta percentage: {test_max_magenta:.2f}%")