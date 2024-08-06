import json
import os
from shutil import copyfile
import subprocess
from typing import Any, override

import requests  # type: ignore

from .. import texts
from ..file import rm_if_exists
from ..edition.Edition import BlockShape, Edition, TextureOptions
from ..options import DEFAULTS, EditionType, VersionType
from ..texts import tabbed_print


class Bedrock(Edition):
    """
    Represents the Bedrock Edition of Minecraft.

    Attributes:
        REPO_URL (str): The URL of the Bedrock Edition repository.
        REPLICATE_MAP (dict): A dictionary mapping texture names to their replication counterparts.

    """

    REPO_URL = 'https://github.com/Mojang/bedrock-samples'

    REPLICATE_MAP: dict[str, str] = {
        'glass_pane_top': 'glass_pane',
        'glass_pane_top_red': 'red_glass_pane',
        'glass_pane_top_orange': 'orange_glass_pane',
        'glass_pane_top_yellow': 'yellow_glass_pane',
        'glass_pane_top_lime': 'lime_glass_pane',
        'glass_pane_top_green': 'green_glass_pane',
        'glass_pane_top_cyan': 'cyan_glass_pane',
        'glass_pane_top_light_blue': 'light_blue_glass_pane',
        'glass_pane_top_blue': 'blue_glass_pane',
        'glass_pane_top_purple': 'purple_glass_pane',
        'glass_pane_top_magenta': 'magenta_glass_pane',
        'glass_pane_top_pink': 'pink_glass_pane',
        'glass_pane_top_black': 'black_glass_pane',
        'glass_pane_top_brown': 'brown_glass_pane',
    }

    blocks_cache: dict[str, Any] | None = None
    terrain_texture_cache: dict[str, Any] | None = None

    def __init__(self):
        self.repo_dir: str | None = None
        super().__init__()

    @override
    def get_textures(
        self,
        version_or_type: VersionType | str,
        output_dir: str = DEFAULTS['OUTPUT_DIR'],
        options: TextureOptions | None = None,
    ) -> str | None:

        if options is None:
            options = DEFAULTS['TEXTURE_OPTIONS']

        if isinstance(version_or_type, str) and not Edition.validate_version(
                version_or_type, edition=EditionType.BEDROCK):
            tabbed_print(
                texts.ERROR_VERSION_INVALID.format(version=version_or_type))
            return None

        version_type = version_or_type if isinstance(
            version_or_type, VersionType) else VersionType.ALL
        version = None

        self.repo_dir = self.temp_dir + '/bedrock-samples/'
        self._clone_repo(self.repo_dir)

        if isinstance(version_or_type, str):
            version = version_or_type
        else:
            version = self.get_latest_version(version_type)

        self._change_repo_version(version)

        filtered = Edition.filter_unwanted(self.repo_dir,
                                           output_dir + '/bedrock/' + version,
                                           edition=EditionType.BEDROCK)

        if options['DO_PARTIALS']:
            self._create_partial_textures(filtered, version_type)

        if options['DO_REPLICATE']:
            Edition.replicate_textures(filtered, self.REPLICATE_MAP)

        Edition.scale_textures(filtered, options['SCALE_FACTOR'],
                               options['DO_MERGE'])

        output_dir = os.path.abspath(filtered).replace('\\', '/')
        return output_dir

    @override
    def get_version_type(self, version: str) -> VersionType | None:
        if version[0] != 'v':
            version = f'v{version}'
        if Edition.validate_version(version=version,
                                    version_type=VersionType.STABLE,
                                    edition=EditionType.BEDROCK):
            return VersionType.STABLE
        if Edition.validate_version(version=version,
                                    version_type=VersionType.EXPERIMENTAL,
                                    edition=EditionType.BEDROCK):
            return VersionType.EXPERIMENTAL
        return None

    @override
    def get_latest_version(self, version_type: VersionType) -> str:
        if self.repo_dir is None:
            raise OSError(
                'Repository not found. Please clone the repository first.')

        subprocess.run('git fetch --tags', check=False, cwd=self.repo_dir)

        out = subprocess.run('git tag --list',
                             check=False,
                             cwd=self.repo_dir,
                             capture_output=True)

        tags = out.stdout.decode('utf-8').splitlines()

        tag = None

        for tag in reversed(tags):
            if Edition.validate_version(
                    version=tag,
                    version_type=version_type
                    if version_type != VersionType.ALL else None,
                    edition=EditionType.BEDROCK):
                break

        return tag

    def _clone_repo(self, clone_dir: str, repo_url: str = REPO_URL):
        """Clones a git repository.

        Args:
            clone_dir (str): directory to clone the repository to
            repo_url (str): URL of the repo to clone
        """

        tabbed_print(texts.FILES_DOWNLOADING)

        self.repo_dir = clone_dir

        rm_if_exists(self.repo_dir)

        command_1 = f'git clone --filter=blob:none --sparse {repo_url} {self.repo_dir}'
        command_2 = 'git config core.sparsecheckout true && echo "resource_pack" >> .git/info/sparse-checkout && git sparse-checkout init --cone && git sparse-checkout set resource_pack'

        try:
            subprocess.run(command_1,
                           check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)
            subprocess.run(command_2,
                           check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT,
                           cwd=self.repo_dir,
                           shell=True)

        except subprocess.CalledProcessError as err:
            print(
                texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode,
                                                  error_msg=err.stderr))

    def _change_repo_version(self, version: str, fetch_tags: bool = True):
        """Changes the version of the repository.

        Args:
            version (str): version to change the repository to
            fetch_tags (bool, optional): whether to fetch tags from the repository
        """
        if fetch_tags:
            subprocess.run('git fetch --tags', check=False, cwd=self.repo_dir)
        try:
            subprocess.run(f'git checkout tags/v{version}',
                           check=False,
                           cwd=self.repo_dir,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print(
                texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode,
                                                  error_msg=err.stderr))

    def _create_partial_textures(self, texture_dir: str,
                                 version_type: VersionType):
        """Creates partial textures for the Bedrock Edition.

        Args:
            texture_dir (str): directory where the textures are
            version_type (VersionType): type of version to create partials for
        """
        UNUSED_TEXTURES: list[str] = ['carpet']

        tabbed_print(texts.CREATING_PARTIALS)
        texture_dict = self._get_blocks_json(version_type=version_type)

        for texture_name in texture_dict:
            if texture_name in UNUSED_TEXTURES:
                continue

            if 'slab' in texture_name and 'double_slab' not in texture_name:
                identifier = texture_dict[texture_name]["textures"]
                base_texture = self._identifier_to_filename(
                    identifier, version_type)
                sub_dir = base_texture.split('/').pop(
                    0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.SLAB, out_path)
            elif 'stairs' in texture_name:
                identifier = texture_dict[texture_name]["textures"]
                base_texture = self._identifier_to_filename(
                    identifier, version_type)
                sub_dir = base_texture.split('/').pop(
                    0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.STAIR, out_path)
            elif 'carpet' in texture_name and 'moss' not in texture_name:
                if 'moss' in texture_name:
                    base_texture = 'moss_block'
                else:
                    base_texture = 'wool_colored_' + texture_name.replace(
                        '_carpet', '').replace('light_gray', 'silver')
                sub_dir = base_texture.split('/').pop(
                    0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.CARPET, out_path)

            # waxed copper blocks use same texture as the base variant
            elif 'copper' in texture_name and 'waxed' in texture_name:
                base_texture = texture_name.replace('waxed_', '')
                sub_dir = texture_name.split('/').pop(
                    0) if '/' in texture_name else ''

                if '_door' in texture_name:
                    base_texture_top = base_texture + '_top'
                    base_texture_bottom = base_texture + '_bottom'
                    in_path_top = f'{texture_dir}/blocks/{base_texture_top}.png'
                    in_path_bottom = f'{texture_dir}/blocks/{base_texture_bottom}.png'
                    out_path_top = f'{texture_dir}/blocks/{sub_dir}/{texture_name}_top.png'
                    out_path_bottom = f'{texture_dir}/blocks/{sub_dir}/{texture_name}_bottom.png'
                    copyfile(in_path_top, out_path_top)
                    copyfile(in_path_bottom, out_path_bottom)
                    continue

                base_texture = base_texture.replace(
                    'copper', 'copper_block'
                ) if base_texture == 'copper' else base_texture
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                copyfile(in_path, out_path)

    def _get_blocks_json(self, version_type: VersionType) -> dict[str, Any]:
        """Fetches the blocks dictionary.

        Args:
            version_type (VersionType): type of version to fetch the blocks dictionary for

        Returns:
            dict[str, Any]: blocks dictionary
        """

        if self.blocks_cache is not None:
            return self.blocks_cache

        branch = 'main' if version_type == VersionType.STABLE else 'preview'

        file = requests.get(
            f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{branch}/resource_pack/blocks.json',
            timeout=10)

        data = file.json()

        self.blocks_cache = data
        return data

    def _identifier_to_filename(self, identifier: str,
                                version_type: VersionType) -> str:
        """Converts a block identifier to a texture filename.

        Args:
            identifier (str): block identifier
            version_type (VersionType): type of version to convert the identifier for

        Returns:
            str: texture filename
        """

        if isinstance(identifier, dict):
            if 'side' in identifier:
                identifier = identifier['side']

        data = self._get_terrain_texture_json(version_type=version_type)
        textures = data["texture_data"][identifier]["textures"]

        if isinstance(textures, list):
            return textures[0].replace('textures/blocks/', '')

        return textures.replace('textures/blocks/', '')

    def _get_terrain_texture_json(self,
                                  version_type: VersionType) -> dict[str, Any]:
        """Fetches the terrain texture dictionary.

        Args:
            version_type (VersionType): type of version to fetch the terrain texture dictionary for

        Returns:
            dict[str, Any]: terrain texture dictionary
        """

        if self.terrain_texture_cache is not None:
            return self.terrain_texture_cache

        branch = 'main' if version_type == VersionType.STABLE else 'preview'

        file = requests.get(
            f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{branch}/resource_pack/textures/terrain_texture.json',
            timeout=10)
        text = file.text

        json_text = ""
        for line in text.splitlines():
            if line.startswith('//'):
                continue
            json_text += line + '\n'

        data = json.loads(json_text)

        self.terrain_texture_cache = data
        return data
