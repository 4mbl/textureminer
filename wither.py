from shutil import copytree, rmtree
from zipfile import ZipFile
import os
import re
from PIL import Image  # py -m pip install Pillow

temp_path = f"{os.path.expanduser('~')}/Downloads/temp-files"
temp_path = temp_path.replace("\\", "/")


def get_latest_version():
    """Get latest installed Minecraft version

    Parameters:
        void

    Returns:
        string: latest stable version, for example: "1.18.1"
    """

    path = f"{os.path.expanduser('~')}/AppData/Roaming/.minecraft/versions"

    versions = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    stable_versions = []
    for version in versions:
        result = re.findall("[0-9]\.[0-9]+\.?[0-9]*", version)
        if result:
            stable_versions.append(result)

    latest_version = max(stable_versions)[0]

    print(
        f"""

Latest stable installed version of Minecraft is {latest_version}, it will be used.
    """
    )

    return latest_version


def extract_textures(version):
    """Extract textures from .jar file located in /.minecraft/ directory

    Parameters:
        version -- the version that the textures will be extracted from, for example: "1.18.2"
    Returns:
        string: path of the directory the files were extracted
    """

    output_path = f"{temp_path}/extracted-textures"

    # %APPDATA%\.minecraft
    copytree(
        f"{os.path.expanduser('~')}/AppData/Roaming/.minecraft/versions/{version}/",
        f"{temp_path}/version-files",
    )

    jar_path = f"{temp_path}/version-files/{version}.jar"

    print(
        f"""
{len(ZipFile(jar_path).namelist())} files are being extracted...
          """
    )

    # extract the .jar file to a different directory
    with ZipFile(f"{temp_path}/version-files/{version}.jar", "r") as zip_object:
        zip_object.extractall(f"{temp_path}/extracted-files/")

    copytree(f"{temp_path}/extracted-files/assets/minecraft/textures", output_path)
    rmtree(f"{temp_path}/version-files/")
    rmtree(f"{temp_path}/extracted-files/")

    return output_path


def remove_non_images(file_path):
    """
    Delete file if it is not an image file

    Parameters:
        file_path (string): path of the file that will be checked

    Returns:
    """

    if (
        not file_path.endswith(".png")
        | file_path.endswith(".jpg")
        | file_path.endswith(".jpeg")
    ):
        os.remove(file_path)


def resize_image(image_path):
    """
    Resize an image

    Parameters:
        image_path (string): full path of the image that will be resized

    Returns:
        void
    """

    remove_non_images(image_path)

    if (
        image_path.endswith(".png")
        | image_path.endswith(".jpg")
        | image_path.endswith(".jpeg")
    ):
        with Image.open(image_path) as image:
            # image = Image.open(image_path)
            resize_multiplier = 100
            image_width, image_height = image.size

            image = image.resize(
                (image_width * resize_multiplier, image_height * resize_multiplier),
                resample=Image.NEAREST,
            )

            image.save(image_path)


def get_item_icons(input_dir):
    """
    Iterate through item icons and delete other files

    Parameters:
        input_dir (string): directory where the files are

    Returns:
        void
    """

    output_dir = f"{os.path.expanduser('~')}/Downloads/mc-textures"

    # TODO merge to both to same dir and override blocks with items if conflicts
    # items are copied last as some assets are in both and they look better as items
    copytree(f"{input_dir}/block", f"{output_dir}/block")
    copytree(f"{input_dir}/item", f"{output_dir}/item")
    rmtree(input_dir)

    for subdir, dirs, files in os.walk(output_dir):

        print(
            f"""
{len(files)} images are being resized...
        """
        )

        for file in files:
            resize_image(f"{os.path.abspath(subdir)}/{file}")

    print(
        f"""
Icons have been extracted and resized.
You can find them on: {os.path.abspath(output_dir)}.
    """
    )


def main():
    """
    Main function

    Parameters:
        void

    Returns:
        void
    """
    get_item_icons(extract_textures(get_latest_version()))


if __name__ == "__main__":
    main()
