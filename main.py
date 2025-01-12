# -*- coding: utf-8 -*-


from PIL import Image
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Braille Unicode offset
BRAILLE_OFFSET = 0x2800

# Map for pixel positions in a Braille character
# [1] [4]   <- (0, 0), (1, 0)
# [2] [5]   <- (0, 1), (1, 1)
# [3] [6]   <- (0, 2), (1, 2)
# [7] [8]   <- (0, 3), (1, 3)
BRAILLE_MAP = [
    (0, 0), (0, 1), (0, 2), (1, 0),
    (1, 1), (1, 2), (0, 3), (1, 3)
]

def image_to_ascii_braille(image_path, max_height=200, output_width=100):
    # Load the image and convert to grayscale
    image = Image.open(image_path).convert("L")

    # Get the current dimensions of the image
    img_width, img_height = image.size

    # Rognage pour avoir une taille multiple de 2x4
    new_width = (img_width // 2) * 2  # Largeur multiple de 2
    new_height = (img_height // 4) * 4  # Hauteur multiple de 4

    # Calcul de la boîte de découpe pour centrer l'image
    left = (img_width - new_width) // 2
    top = (img_height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    # Rogner l'image
    image = image.crop((left, top, right, bottom))

    # Maintenant, redimensionner l'image pour que la hauteur soit <= max_height
    img_width, img_height = image.size  # Mise à jour des dimensions après rognage

    # Si l'image est plus haute que max_height, on redimensionne
    if img_height > max_height:
        aspect_ratio = img_width / img_height
        new_height = max_height
        new_width = int(aspect_ratio * new_height)
        image = image.resize((new_width, new_height))

    # Convert image to NumPy array
    pixel_data = np.array(image)

    # Normalize pixel values to binary (0 or 1)
    threshold = 0.7*np.mean(pixel_data) # Vous pouvez ajuster ce seuil
    binary_data = (pixel_data < threshold).astype(int)

    # Build the ASCII art line by line
    ascii_art = []
    for y in range(0, binary_data.shape[0], 4):
        line = []
        for x in range(0, binary_data.shape[1], 2):
            # Déterminer le caractère Braille pour le bloc actuel de 2x4 pixels
            braille_char = 0
            for bit, (dx, dy) in enumerate(BRAILLE_MAP):
                if y + dy < binary_data.shape[0] and x + dx < binary_data.shape[1]:
                    braille_char |= binary_data[y + dy, x + dx] << bit
            line.append(chr(BRAILLE_OFFSET + braille_char))
        ascii_art.append("".join(line))

    return "\n".join(ascii_art)


if __name__ == "__main__":
    # Launch a file dialog to select the image
    Tk().withdraw()  # Hide the root tkinter window
    image_path = askopenfilename(
        title="Select an Image File",
        filetypes=[("All Files", "*.*")]
    )
    
    if not image_path:
        print("No file selected. Exiting.")
    else:
        # Convert the selected image to Braille ASCII art
        ascii_braille = image_to_ascii_braille(image_path, max_height=80)

        # Print the result
        print(ascii_braille)

        # Optionally save to a file
        with open("output_braille.txt", "w", encoding="utf-8") as f:
            f.write(ascii_braille)