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

#right now tags are all weighted same. could have specific categories to put in the json files (like lang) so the user can sort by subject, design style, etc