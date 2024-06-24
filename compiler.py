"""
Compile the site before publishing. Things this script needs to do:

 - Get a list of all the models in src/models, so that the javascript can load the previews to the gallery
 - compress photos into the thumbnails folder
 - build html files for each model

Another cool feature would be to generate .svg and .png for .cp files...? or an option to download it in multiple formats
"""

from os import listdir
from os.path import isfile, join
import json
from PIL import Image
import os
import shutil

def get_filenames():
    model_data = {}

    mypath = "models"
    filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for i in range(len(filenames)):
        filenames[i] = "models/" + filenames[i]

    model_data["filenames"] = filenames
    all_tags = set()
    for filename in filenames:
        with open(filename, "r") as file:
            data = json.load(file)
            if "tags" in data:
                all_tags.update(data["tags"])
            else:
                data["tags"] = []
    model_data["tags"] = list(all_tags)
    # Convert the list to JSON format
    json_data = json.dumps(model_data)

    # Specify the file path for the JSON file
    json_file_path = "/Users/brandonwong/Desktop/portfolio/model_data.json"

    # Write the JSON data to the file
    with open(json_file_path, "w") as json_file:
        json_file.write(json_data)

    print("Filenames saved as JSON successfully.")

def compress_photos():
    photo_dir = "src/photos"
    thumbnail_dir = "src/thumbnails"
    max_size = 100 * 1024  # 100kb

    # Create the thumbnails directory if it doesn't exist
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)
    # Iterate through each photo in the photo directory
    for filename in os.listdir(photo_dir):
        photo_path = os.path.join(photo_dir, filename)
        thumbnail_path = os.path.join(thumbnail_dir, filename)

        # Check if the file is an image
        if not os.path.isfile(photo_path) or not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"skipped {filename}, not an image")
            continue
        # Open the image
        image = Image.open(photo_path)
        # Check if the image size is larger than the maximum size
        if os.path.getsize(photo_path) > max_size:
            # Calculate the new dimensions to maintain the aspect ratio
            width, height = image.size
            original_size = os.path.getsize(photo_path)
            # aspect_ratio = width / height
            new_width = int(width * (max_size / original_size)**0.5)
            new_height = int(height * (max_size / original_size)**0.5)
            # Resize the image
            resized_image = image.resize((new_width, new_height))
            # Save the resized image to the thumbnails directory
            resized_image.save(thumbnail_path)
            print(f"Compressed {filename} successfully.")
        else:
            # Copy the original image to the thumbnails directory
            shutil.copy(photo_path, thumbnail_path)

            print(f"Skipped {filename} (already below 100kb).")
    print("All photos compressed successfully.")
if __name__ == "__main__":
    compress_photos()

#right now tags are all weighted same. could have specific categories to put in the json files (like lang) so the user can sort by subject, design style, etc