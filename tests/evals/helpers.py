import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def display_images_mpl(filenames, width=8, height=6):
    for filename in filenames:
        img = mpimg.imread(filename)
        
        # Extracting filename without the suffix using pathlib
        title = Path(filename).stem

        plt.figure(figsize=(width, height))
        plt.imshow(img)
        plt.title(title)  # Setting the title of the image
        plt.axis('off')
        plt.show()