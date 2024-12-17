"""
Compile the site before publishing. Things this script needs to do:

 - Get a list of all the projects in src/projects, so that the javascript can load the previews to the gallery
 - compress photos into the thumbnails folder
 - build html files for each project

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
    project_data = {}
    mypath = "engineering/projects/"
    filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for i in range(len(filenames)):
        filenames[i] = filenames[i]
    project_data["filenames"] = filenames

    all_tags = {}
    for filename in filenames:
        with open(mypath + filename, "r") as file:
            data = json.load(file)

            # modify tags as needed
            data["tags"] = [tag.replace(" ", "_") for tag in data["tags"]]
            try:
                year = datetime.fromisoformat(data["date"]).strftime("%Y")
                if year not in data["tags"]:
                    data["tags"].append(year)
            except:  # if there's no year, don't care
                pass
            with open(mypath + filename, "w") as file:
                json.dump(data, file, indent=4)

            for tag in data["tags"]:
                all_tags[tag] = all_tags.get(tag, 0) + 1

    all_tags = sorted(all_tags.items(), key=lambda x: x[0])
    project_data["tags"] = all_tags  # list(all_tags)
    # Convert the list to JSON format
    json_data = json.dumps(project_data)
    # Specify the file path for the JSON file
    json_file_path = "engineering/project_data.json"
    # Write the JSON data to the file
    with open(json_file_path, "w") as json_file:
        json_file.write(json_data)
    print("Filenames saved as JSON successfully.")


# def compress_photos():
#     photo_dir = "src/photos"
#     thumbnail_dir = "src/thumbnails"
#     max_size = 100 * 1024  # 100kb

#     # Create the thumbnails directory if it doesn't exist
#     if not os.path.exists(thumbnail_dir):
#         os.makedirs(thumbnail_dir)
#     # Iterate through each photo in the photo directory
#     for filename in os.listdir(photo_dir):
#         photo_path = os.path.join(photo_dir, filename)
#         thumbnail_path = os.path.join(thumbnail_dir, filename)

#         # TODO: if there already exists a thumbnail, continue
#         # Check if there already exists a thumbnail, continue
#         if os.path.exists(thumbnail_path):
#             # print(f"Skipped {filename} (thumbnail already exists).")
#             continue

#         # Check if the file is an image
#         if not os.path.isfile(photo_path) or not filename.lower().endswith(
#             (".jpg", ".jpeg", ".png")
#         ):
#             print(f"skipped {filename}, not an image")
#             continue
#         # Open the image
#         image = Image.open(photo_path)
#         # Check if the image size is larger than the maximum size
#         if os.path.getsize(photo_path) > max_size:
#             # Calculate the new dimensions to maintain the aspect ratio
#             width, height = image.size
#             original_size = os.path.getsize(photo_path)
#             # aspect_ratio = width / height
#             new_width = int(width * (max_size / original_size) ** 0.5)
#             new_height = int(height * (max_size / original_size) ** 0.5)
#             # Resize the image
#             resized_image = image.resize((new_width, new_height))
#             # Save the resized image to the thumbnails directory
#             resized_image.save(thumbnail_path)
#             print(f"Compressed {filename} successfully.")
#         else:
#             # Copy the original image to the thumbnails directory
#             shutil.copy(photo_path, thumbnail_path)

#             print(f"Skipped {filename} (already below 100kb).")
#     print("All photos compressed successfully.")


def build_html_files():
    """
    Problems:
     - elements are being placed before the div, rather than inside
     - when gallery page with tag searching is set up, have the tags be links to the gallery page with the tag as a query parameter
     - no css yet
    """

    project_dir = "engineering/projects"
    for filename in os.listdir(project_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(project_dir, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                if data["title"] == "":
                    continue
                template_path = "engineering/template.html"
                output_path =os.path.join("engineering", filename[:-5] + ".html")
                shutil.copy(template_path, output_path)
                # Find the element with id "title" and replace the text with the "title" from the json dictionary
                with open(output_path, "r+") as html_file:
                    # fill in project title
                    html_content = html_file.read()
                    html_content = html_content.replace(
                        '<h1 id="title">title</h1>', f'<h1 id="title">{data["title"]}</h1>'
                    )

                    try:
                        # Get the month and year from the ISO date
                        iso_date = data["date"]
                        date_obj = datetime.fromisoformat(iso_date)
                        month = date_obj.strftime("%B")
                        year = date_obj.strftime("%Y")
                        html_content = html_content.replace(
                            '<p id="date">date</p>', f'<p id="date">Completed {month} {year}</p>'
                        )
                    except:
                        print("ERROR: " + filename + " has no date")

                    # Find the element with id "title" and replace the text with the "title" from the json dictionary
                    html_content = html_content.replace(
                        "<title>Document</title>", f'<title>{data["title"]}</title>'
                    )

                    # fill in project description
                    if not data["long_description"]:
                        description = data["short_description"]
                    else:
                        description = data["long_description"]
                    html_content = html_content.replace(
                        '<p id="description">description</p>',
                        f'<p id="description">{description}</p>',
                    )

                    #list collaborators
                    if data["collaborators"]:
                        text = "Collaborators:"
                        for collaborator in data["collaborators"]:
                            text += f" {collaborator},"
                        html_content = html_content.replace(
                        '<p id="collaborators"></p>',
                        f'<p id="collaborators">{text[:-1]}</p>',
                    )
                
                    # Find the element with id "photos" and add image tags based on the image file paths listed in data["photos"]
                    images_div = html_content.find('<div id="images">') + len(
                        '<div id="images">'
                    )
                    if images_div != -1:
                        image_tags = ""
                        for image in data["images"]:
                            image_tags += f'<img class="carousel-image" src="{os.path.join("files",image)}" alt="photo">'
                        if len(data["images"]) > 1:
                            image_tags += """<button id="carousel-prev" onclick="changeImage(-1)"><</button><button id="carousel-next" onclick="changeImage(1)">></button>"""
                        html_content = (
                            html_content[:(images_div)]
                            + image_tags
                            + html_content[(images_div):]
                        )

                
                    # if there is a video, use the url and embed it in the div with id=video
                    if "youtu" in data["video"]:
                        video_div = html_content.find('<div id="video">') + len(
                            '<div id="video">'
                        )
                        if video_div != -1:
                            html_content = (
                                html_content[:video_div]
                                + f"""<iframe width="560" height="315" src="https://www.youtube.com/embed/{data["video"][27:] if "shorts" in data["video"] else data["video"][17:]}?si=u_yWkDzkLtn0nOf8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>"""
                                + html_content[video_div:]
                            )
                    elif data["video"]:
                        #if not a link, it's a file name that can be found in /files and embedded directly
                        video_div = html_content.find('<div id="video">') + len('<div id="video">')
                        if video_div != -1:
                            html_content = (
                                html_content[:video_div]
                                + f"""<video width="560" height="315" controls>
                                        <source src="files/{data["video"]}" type="video/mp4">
                                        Your browser does not support the video tag.
                                      </video>"""
                                + html_content[video_div:]
                            )

                    if data["pdf"] and type(data["pdf"]) == str:
                        pdf_div = html_content.find('<div id="pdf_wrapper">') + len(
                            '<div id="pdf_wrapper">'
                        )
                        if pdf_div != -1:
                            html_content = (
                                html_content[:pdf_div]+ f"""<div id="pdf"><embed src="files/{data["pdf"]}" type="application/pdf" width="100%" height="600px" /></div>"""+ html_content[pdf_div:]
                            )
                    elif data["pdf"] and type(data["pdf"]) == list:
                        pdf_div = html_content.find('<div id="pdf_wrapper">') + len(
                            '<div id="pdf_wrapper">'
                        )
                        if pdf_div != -1:
                            pdfs = ""
                            for pdf in data["pdf"]:
                                pdfs += f"""<div id="pdf"><embed src="files/{pdf}" type="application/pdf" width="100%" height="600px" /></div>"""
                            html_content = (
                                html_content[:pdf_div]+ pdfs + html_content[pdf_div:]
                            )

                    # fill in tags
                    tags_div = html_content.find('<div id="tags">') + len(
                        '<div id="tags">'
                    )
                    if tags_div != -1:
                        tags = ""
                        for tag in data["tags"]:
                            # tags += f'<span class="tag">{tag+""}</span>'
                            tags += (
                                """<a href="../gallery.html?tag="""
                                + tag
                                + """"><button class="button2 tag">"""
                                + tag
                                + """</button></a>"""
                            )
                        html_content = (
                            html_content[:tags_div]
                            + "<p>Tags: "
                            + tags
                            + "</p>"
                            + html_content[tags_div:]
                        )

                    html_file.seek(0)
                    html_file.write(html_content)
                    html_file.truncate()
    print("All HTML files built successfully.")


if __name__ == "__main__":
    get_filenames()
    # compress_photos()
    build_html_files()
