from fortext import style, Fg

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

COMMAND_SYNTAX = "\n\tpy -m textureminer <version> <edition>\n\te.g.\n\tpy -m textureminer 1.17 java\n\tpt -m textureminer 1.17 bedrock\n\tdefaults to java if no edition is specified, and defaults to latest version if no version is specified"
EDITION_INVALID = "Invalid edition"
EDITION_USING_DEFAULT = "Using default edition (Java Edition)"
EDITION_USING_X = "Using {edition} Edition"
ERROR_COMMAND_FAILED = "The command failed with return code {error_code}: {error_msg}"
FILE_DOWNLOADING = "Downloading assets..."
FILES_EXTRACTING = "Extracting {file_amount} files..."
CLEARING_TEMP = "Clearing temporary files..."
INVALID_COMBINATION = "Invalid combination of version and edition"
TEXTURES_FILTERING = "Filtering textures..."
TEXTURES_MERGING = "Merging block and item textures to a single directory..."
TEXTURES_RESISING_AMOUNT_IN_DIR = "Resizing {texture_amount} {dir_name} textures..."
TEXTURES_RESIZING_AMOUNT = "Resizing {texture_amount} textures..."
VERSION_INVALID = "Invalid version ({version})"
VERSION_LATEST_FINDING = "Finding latest {version_type} version..."
VERSION_LATEST_IS = "Latest {version_type} is {latest_version}."
VERSION_USING_X = "Using {version} version"
