import json
import os
import subprocess
from typing import Any, Dict, List

import requests  # type: ignore


from .. import texts
from ..file import rm_if_exists
from ..edition.Edition import BlockShape, Edition
from ..options import DEFAULTS, EditionType, VersionType
from ..texts import tabbed_print


class Bedrock(Edition):
    """A class representing the Bedrock Edition of Minecraft.

    This class provides methods for retrieving information about versions, downloading textures, and more.

    Attributes:
        REPO_URL (str): The URL of the Bedrock Edition repository.

    """

    REPO_URL = 'https://github.com/Mojang/bedrock-samples'

    _blocks: Dict[str, Any] | None = None
    _terrain_texture: Dict[str, Any] | None = None

    def __init__(self):
        self.repo_dir: str = ''

    def get_version_type(self, version: str) -> VersionType | None:
        if version[0] != 'v':
            version = f'v{version}'
        if Edition.validate_version(version=version, version_type=VersionType.STABLE, edition=EditionType.BEDROCK):
            return VersionType.STABLE
        if Edition.validate_version(version=version, version_type=VersionType.EXPERIMENTAL, edition=EditionType.BEDROCK):
            return VersionType.EXPERIMENTAL
        return None

    def get_latest_version(self, version_type: VersionType) -> str:

        self._update_tags()

        out = subprocess.run('git tag --list',
                             check=False,
                             cwd=self.repo_dir,
                             capture_output=True)

        tags = out.stdout.decode('utf-8').splitlines()

        tag = None

        for tag in reversed(tags):
            if Edition.validate_version(version=tag, version_type=version_type if version_type != VersionType.ALL else None, edition=EditionType.BEDROCK):
                break

        tabbed_print(
            texts.VERSION_LATEST_IS.format(version_type=version_type.value,
                                           latest_version=str(tag)))
        return tag

    def _clone_repo(self,
                    clone_dir: str = f'{DEFAULTS['TEMP_PATH']}/bedrock-samples/',
                    repo_url: str = REPO_URL):
        """Clones a git repository.

        Args:
            clone_dir (str, optional): directory to clone the repository to. Defaults to a temporary directory.
            repo_url (str, optional): URL of the repo to clone. Defaults to `BedrockEdition.REPO_URL`.
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

    def _update_tags(self):
        """Updates the tags of the git repository.
        """
        subprocess.run('git fetch --tags', check=False, cwd=self.repo_dir)

    def _change_repo_version(self, version: str, fetch_tags: bool = True):
        """Changes the version of the repository.

        Args:
            version (str): version to change to
            fetch_tags (bool, optional): whether to fetch tags from the repository. Defaults to True.
        """
        if fetch_tags:
            self._update_tags()
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

    def get_textures(
        self,
        version_or_type: VersionType | str,
        output_dir=DEFAULTS['OUTPUT_DIR'],
        scale_factor=DEFAULTS['SCALE_FACTOR'],
        do_merge=DEFAULTS['DO_MERGE'],
        do_partials=DEFAULTS['DO_PARTIALS'],
    ) -> str | None:


        if isinstance(version_or_type, str) and not Edition.validate_version(
                version_or_type, edition=EditionType.BEDROCK):
            tabbed_print(texts.ERROR_VERSION_INVALID.format(version=version_or_type))
            return None

        version_type = version_or_type if isinstance(version_or_type,
                                                     VersionType) else VersionType.ALL
        version = None
        self._clone_repo()
        if isinstance(version_or_type, str):
            version = version_or_type
        else:
            version = self.get_latest_version(version_type)


        self._change_repo_version(version)

        filtered = Edition.filter_unwanted(self.repo_dir,
                                   f'{output_dir}/bedrock/{version}',
                                   edition=EditionType.BEDROCK)

        if do_partials:
            self._create_partial_textures(filtered, version_type)

        Edition.scale_textures(filtered, scale_factor, do_merge)

        tabbed_print(texts.CLEARING_TEMP)
        rm_if_exists(DEFAULTS['TEMP_PATH'])

        output_dir = os.path.abspath(filtered).replace('\\', '/')
        print(texts.COMPLETED.format(output_dir=output_dir))
        return output_dir


    def _create_partial_textures(self, texture_dir: str, version_type: VersionType):
        UNUSED_TEXTURES: List[str] = ['carpet']

        tabbed_print(texts.CREATING_PARTIALS)
        texture_dict = self._get_blocks_json(version_type=version_type)


        for texture_name in texture_dict:
            if texture_name in UNUSED_TEXTURES:
                continue

            if 'slab' in texture_name and 'double_slab' not in texture_name:
                identifier = texture_dict[texture_name]["textures"]
                base_texture = self._identifier_to_filename(identifier, version_type)
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.SLAB, out_path)
            elif 'stairs' in texture_name:
                identifier = texture_dict[texture_name]["textures"]
                base_texture = self._identifier_to_filename(identifier, version_type)
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.STAIR, out_path)
            elif 'carpet' in texture_name and 'moss' not in texture_name:
                if 'moss' in texture_name:
                    base_texture = 'moss_block'
                else:
                    base_texture = 'wool_colored_' + texture_name.replace('_carpet', '').replace('light_gray', 'silver')
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = f'{texture_dir}/blocks/{base_texture}.png'
                out_path = f'{texture_dir}/blocks/{sub_dir}/{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.CARPET, out_path)


    def _get_blocks_json(self, version_type: VersionType) -> Dict[str, Any]:
        """Fetches the blocks dictionary from the repository.
        """

        if self._blocks is not None:
            return self._blocks

        branch = 'main' if version_type == VersionType.STABLE else 'preview'

        file = requests.get(
            f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{branch}/resource_pack/blocks.json',
            timeout=10)

        data = file.json()

        self._blocks = data
        return data


    def _get_terrain_texture_json(self, version_type: VersionType) -> Dict[str, Any]:
        """Fetches the texture dictionary from the repository.
        """

        if self._terrain_texture is not None:
            return self._terrain_texture

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

        self._terrain_texture = data
        return data


    def _identifier_to_filename(self, identifier: str, version_type: VersionType) -> str:
        if isinstance(identifier, dict):
            if 'side' in identifier:
                identifier = identifier['side']

        data = self._get_terrain_texture_json(version_type=version_type)
        textures = data["texture_data"][identifier]["textures"]

        if isinstance(textures, list):
            return textures[0].replace('textures/blocks/', '')

        return textures.replace('textures/blocks/', '')
