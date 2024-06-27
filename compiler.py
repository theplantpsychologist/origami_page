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
from datetime import datetime

def get_filenames():
    model_data = {}
    mypath = "src/models/"
    filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for i in range(len(filenames)):
        filenames[i] =filenames[i]
    model_data["filenames"] = filenames


    all_tags = {}
    for filename in filenames:
        with open(mypath+filename, "r") as file:
            data = json.load(file)

            #modify tags as needed
            data["tags"] = [tag.replace(" ", "_") for tag in data["tags"]]
            if data["cp"] and "has_cp" not in data["tags"]:
                data["tags"].append("has_cp")
            if data["video"] and "has_video" not in data["tags"]:
                data["tags"].append("has_video")
            if data["diagrams"][0] and "has_diagrams" not in data["tags"]:
                data["tags"].append("has_diagrams")
            try:
                year = datetime.fromisoformat(data["date"]).strftime("%Y")
                if year not in data["tags"]:
                    data["tags"].append(year)
            except: #if there's no year, don't care
                pass
            for tag in data["tags"]:
                all_tags[tag] = all_tags.get(tag, 0) + 1
            with open(mypath+filename,'w') as file:
                json.dump(data,file)


    model_data["tags"] = all_tags#list(all_tags)
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

def build_html_files():
    """
    Problems:
     - elements are being placed before the div, rather than inside
     - when gallery page with tag searching is set up, have the tags be links to the gallery page with the tag as a query parameter
     - no css yet 
    """

    model_dir = "src/models"
    for filename in os.listdir(model_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(model_dir, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                if data['name'] == "":
                    continue
                template_path = "src/template.html"
                output_path = os.path.join("gallery", filename[:-5] + ".html")
                shutil.copy(template_path, output_path)
                # Find the element with id "name" and replace the text with the "name" from the json dictionary
                with open(output_path, "r+") as html_file:
                    #fill in model name
                    html_content = html_file.read()
                    html_content = html_content.replace('<h1 id="name">name</h1>', f'<h1 id="name">{data["name"]}</h1>')

                    try:
                        # Get the month and year from the ISO date
                        iso_date = data["date"]
                        date_obj = datetime.fromisoformat(iso_date)
                        month = date_obj.strftime("%B")
                        year = date_obj.strftime("%Y")
                        html_content = html_content.replace('<p id="date">date</p>', f'<p id="date">{month} {year}</p>')
                    except:
                        print("ERROR: "+filename + " has no date")
                    

                    #fill in model description
                    html_content = html_content.replace('<p id="description">description</p>', f'<p id="description">{data["description"]}</p>')

                    #fill in cp description 
                    html_content = html_content.replace('<p id="cpdescription">cp description</p>', f'<p id="cpdescription">{data["cpdescription"]}</p>')

                    # Find the element with id "photos" and add image tags based on the image file paths listed in data["photos"]
                    photos_div = html_content.find('<div id="photos">')
                    if photos_div != -1:
                        image_tags = ""
                        for photo in data["photo"]:
                            image_tags += f'<img src="{os.path.join("../src/photos",photo)}" alt="photo">'
                        html_content = html_content[:photos_div] + image_tags + html_content[photos_div:]

                    # fill in cp
                    cp_div = html_content.find('<div id="cp">')
                    if cp_div != -1:
                        image_tags = ""
                        for cp in data["cp"]:
                            image_tags += f'<img src="{os.path.join("../src/cps",cp)}" alt="crease pattern">'
                        html_content = html_content[:cp_div] + image_tags + html_content[cp_div:]

                    #if there is a video, use the url and embed it in the div with id=video
                    if data["video"]:
                        video_div = html_content.find('<div id="video">')
                        if video_div != -1:
                            html_content = html_content[:video_div] + f"""<iframe width="560" height="315" src="https://www.youtube.com/embed/{data["video"][27:] if "shorts" in data["video"] else data["video"][17:]}?si=u_yWkDzkLtn0nOf8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>""" + html_content[video_div:]

                    #fill in diagrams
                    if data["diagrams"][0]:
                        diagrams_div = html_content.find('<div id="diagrams">')
                        if diagrams_div != -1:
                            html_content = html_content[:diagrams_div] + f'<p>Diagrams are available in: <a href={data["diagrams"][0]}>{data["diagrams"][1]}</a></p>' + html_content[diagrams_div:]

                    #fill in tags
                    tags_div = html_content.find('<div id="tags">')
                    if tags_div != -1:
                        tags = ""
                        for tag in data["tags"]:
                            tags += f'<span>{tag+", "}</span>'
                        html_content = html_content[:tags_div] + "<p>Tags: "+tags +"</p>"+ html_content[tags_div:]

                    html_file.seek(0)
                    html_file.write(html_content)
                    html_file.truncate()
    print("All HTML files built successfully.")

if __name__ == "__main__":
    get_filenames()
    #compress_photos()
    build_html_files()

#right now tags are all weighted same. could have specific categories to put in the json files (like lang) so the user can sort by subject, design style, etc

#TODO: in the photos div, make a carousel for the models with multiple photos

#TODO: add handling for embedding shorts