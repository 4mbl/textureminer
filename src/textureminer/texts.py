from fortext import style, Fg  # type: ignore

TITLE = style(r"""

 _______ ________   _________ _    _ _____  ______   __  __ _____ _   _ ______ _____
|__   __|  ____\ \ / /__   __| |  | |  __ \|  ____| |  \/  |_   _| \ | |  ____|  __ \
   | |  | |__   \ V /   | |  | |  | | |__) | |__    | \  / | | | |  \| | |__  | |__) |
   | |  |  __|   > <    | |  | |  | |  _  /|  __|   | |\/| | | | | . ` |  __| |  _  /
   | |  | |____ / . \   | |  | |__| | | \ \| |____  | |  | |_| |_| |\  | |____| | \ \
   |_|  |______/_/ \_\  |_|   \____/|_|  \_\______| |_|  |_|_____|_| \_|______|_|  \_\

""",
              fg=Fg.CYAN)
STYLED_TAB = style(f"{' '*4}* ", fg=Fg.CYAN)

COMPLETED = style("Completed. You can find the textures on:\n{output_dir}\n",
                  fg=Fg.GREEN)
CLEARING_TEMP = "Clearing temporary files..."
CREATING_PARTIALS = "Creating partial textures..."
EDITION_USING_X = "Using {edition} Edition."
ERROR_COMMAND_FAILED = "The command failed with return code {error_code}: {error_msg}!"
ERROR_EDITION_INVALID = "Invalid edition!"
ERROR_INVALID_COMBINATION = "Invalid combination of version and edition!"
ERROR_VERSION_INVALID = "Invalid version ({version})!"
FILES_DOWNLOADING = "Downloading assets..."
FILES_EXTRACTING_N = "Extracting {file_amount} files..."
TEXTURES_FILTERING = "Filtering textures..."
TEXTURES_MERGING = "Merging block and item textures to a single directory..."
TEXTURES_REPLICATING = "Replicating textures..."
TEXTURES_RESISING_AMOUNT_IN_DIR = "Resizing {texture_amount} {dir_name} textures..."
TEXTURES_RESIZING_AMOUNT = "Resizing {texture_amount} textures..."
VERSION_LATEST_FINDING = "Finding latest version from {version_type} releases channel..."
VERSION_LATEST_IS = "Latest version from {version_type} releases channel is {latest_version}."
VERSION_USING_X = "Using {version} version."


def tabbed_print(text: str):
    """Prints text with a tab at the beginning.

    Args:
        text (str): text that will be printed
    """
    print(f"{STYLED_TAB}{text}")
