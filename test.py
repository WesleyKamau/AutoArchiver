from PIL import Image

def crop_image(image_path ):
    """Crops an image to a specific aspect ratio.

    Args:
        image_path: The path to the image file.
        aspect_ratio: The desired aspect ratio of the cropped image.

    Returns:
        A PIL Image object of the cropped image.
    """
    aspect_ratio = 16 / 9

    image = Image.open(image_path)
    width, height = image.size

    # Calculate the new width and height of the cropped image.
    new_width = width
    new_height = int(width / aspect_ratio)

    # Calculate the cropping coordinates to crop equally from the top and bottom.
    top = (height - new_height) // 2
    bottom = top + new_height

    # Crop the image to the new width and height.
    cropped_image = image.crop((0, top, new_width, bottom))

    return cropped_image

# Example usage:

image_path = 'thumbnails/test.jpg'
aspect_ratio = 16 / 9

cropped_image = crop_image(image_path)

# Save the cropped image.
cropped_image.save("thumbnails/test.jpg")
