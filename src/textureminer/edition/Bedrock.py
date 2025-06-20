# noqa: N999, RUF100
"""Provides a class representing the Bedrock edition of Minecraft."""

import json
import logging
import platform
import re
import subprocess
from collections.abc import Sequence
from pathlib import Path
from shutil import copyfile
from typing import Any, ClassVar, Literal, override

import requests  # type: ignore[import]

from textureminer import texts
from textureminer.edition.Edition import BlockShape, Edition, TextureOptions
from textureminer.file import rm_if_exists
from textureminer.options import DEFAULTS, EditionType, VersionType


class Bedrock(Edition):
    """Represents the Bedrock Edition of Minecraft.

    Attributes
    ----------
        REPO_URL (str): The URL of the Bedrock Edition repository.
        REPLICATE_MAP (dict): A dictionary mapping texture names to their replication counterparts.

    """

    REPO_URL = 'https://github.com/Mojang/bedrock-samples'

    REPLICATE_MAP: ClassVar[dict[str, str]] = {
        'glass_pane_top': 'glass_pane',
        'glass_pane_top_red': 'red_stained_glass_pane',
        'glass_pane_top_orange': 'orange_stained_glass_pane',
        'glass_pane_top_yellow': 'yellow_stained_glass_pane',
        'glass_pane_top_lime': 'lime_stained_glass_pane',
        'glass_pane_top_green': 'green_stained_glass_pane',
        'glass_pane_top_cyan': 'cyan_stained_glass_pane',
        'glass_pane_top_light_blue': 'light_blue_stained_glass_pane',
        'glass_pane_top_blue': 'blue_stained_glass_pane',
        'glass_pane_top_purple': 'purple_stained_glass_pane',
        'glass_pane_top_magenta': 'magenta_stained_glass_pane',
        'glass_pane_top_pink': 'pink_stained_glass_pane',
        'glass_pane_top_white': 'white_stained_glass_pane',
        'glass_pane_top_silver': 'silver_stained_glass_pane',
        'glass_pane_top_gray': 'gray_stained_glass_pane',
        'glass_pane_top_black': 'black_stained_glass_pane',
        'glass_pane_top_brown': 'brown_stained_glass_pane',
    }

    OVERWRITE_TEXTURES: ClassVar[dict[str, str]] = {
        'snow': 'snow_block',
    }

    blocks_cache: dict[str, Any] | None = None
    terrain_texture_cache: dict[str, Any] | None = None

    _git_executable: Literal['git', '/usr/bin/git']

    repo_dir: Path | None = None

    def __init__(self) -> None:
        """Initialize the Bedrock Edition."""
        super().__init__()

        if platform.system() == 'Linux':
            self._git_executable = '/usr/bin/git'
        else:
            self._git_executable = 'git'
        logging.getLogger('textureminer').debug(
            'Git executable: {git}'.format(git=self._git_executable)  # noqa: G001, UP032
        )

    @override
    def get_textures(
        self,
        version_or_type: VersionType | str,
        output_dir: Path = DEFAULTS['OUTPUT_DIR'],
        options: TextureOptions | None = None,
    ) -> Path | None:
        if options is None:
            options = DEFAULTS['TEXTURE_OPTIONS']
        logging.getLogger('textureminer').debug(
            'Texture options: {options}'.format(options=options)  # noqa: G001, UP032
        )

        if isinstance(version_or_type, str) and not Edition.validate_version(
            version_or_type,
            edition=EditionType.BEDROCK,
        ):
            raise ValueError(texts.ERROR_VERSION_INVALID.format(version=version_or_type))

        version_type = (
            version_or_type if isinstance(version_or_type, VersionType) else VersionType.ALL
        )
        version = None

        repo_dir = self.temp_dir / 'bedrock-samples'
        self._clone_repo(repo_dir)

        if isinstance(version_or_type, str):
            version = version_or_type
        else:
            version = self.get_latest_version(version_type)
            if version is None:
                raise ValueError(texts.ERROR_NO_LATEST_VERSION.format(version=version_or_type))

        self.version = version
        logging.getLogger('textureminer').info(texts.VERSION_USING_X.format(version=version))

        self._change_repo_version(version)

        filtered = Edition.filter_unwanted(
            repo_dir,
            output_dir / 'bedrock' / version,
            edition=EditionType.BEDROCK,
        )

        if options['DO_PARTIALS']:
            self._create_partial_textures(filtered, version_type)

        if options['DO_REPLICATE']:
            Edition.replicate_textures(filtered, self.REPLICATE_MAP)

        if options['SIMPLIFY_STRUCTURE']:
            Edition.simplify_structure(EditionType.BEDROCK, filtered)

        Edition.scale_textures(
            filtered,
            options['SCALE_FACTOR'],
            do_merge=options['DO_MERGE'],
            do_crop=options['DO_CROP'],
        )

        return filtered

    @override
    def get_version_type(self, version: str) -> VersionType | None:
        if version[0] != 'v':
            version = f'v{version}'
        if Edition.validate_version(
            version=version,
            version_type=VersionType.STABLE,
            edition=EditionType.BEDROCK,
        ):
            return VersionType.STABLE
        if Edition.validate_version(
            version=version,
            version_type=VersionType.EXPERIMENTAL,
            edition=EditionType.BEDROCK,
        ):
            return VersionType.EXPERIMENTAL
        return None

    @override
    def get_latest_version(self, version_type: VersionType) -> str | None:
        if self.repo_dir is None:
            repo_not_found_msg = 'Repository not found. Please clone the repository first.'
            raise OSError(repo_not_found_msg)

        self._run_git_command(
            (self._git_executable, 'fetch', '--tags'),
            check=False,
        )

        out = self._run_git_command(
            (self._git_executable, 'tag', '--list'),
            check=False,
            capture_output=True,
        )

        if not out:
            err = 'Failed to get tags.'
            raise ChildProcessError(err)

        tags = out.stdout.decode('utf-8').splitlines()

        tag = None

        for tag in reversed(tags):
            if Edition.validate_version(
                version=tag,
                version_type=version_type if version_type != VersionType.ALL else None,
                edition=EditionType.BEDROCK,
            ):
                break

        return tag

    def _run_git_command(
        self,
        command: Sequence[str],
        *,
        cwd: Path | None = None,
        check: bool = False,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess[bytes] | None:
        """Run a git command.

        Args:
        ----
            command (Sequence[str]): command to run
            cwd (str, optional): directory to run the command in
            check (bool, optional): whether to check the return code
            capture_output (bool, optional): whether to capture the output

        """
        cwd = cwd if cwd is not None else self.repo_dir

        logging.getLogger('textureminer').debug(
            'Running `{command}` on {cwd}'.format(  # noqa: G001
                command=' '.join(command),
                cwd=cwd,
            )
        )

        if capture_output:
            return subprocess.run(  # noqa: S603
                command,
                check=check,
                cwd=cwd,
                capture_output=True,
            )

        subprocess.run(  # noqa: S603
            command,
            check=check,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )

        return None

    def _clone_repo(self, clone_dir: Path, repo_url: str = REPO_URL) -> None:
        """Clone a git repository.

        Args:
        ----
            clone_dir (Path): directory to clone the repository to
            repo_url (str): URL of the repo to clone

        """
        logging.getLogger('textureminer').info(texts.FILES_DOWNLOADING)

        rm_if_exists(clone_dir)

        try:
            if re.match(r'https://github.com/[^/]+/[^/]+(.git)?$', repo_url) is None:
                invalid_repo_msg = f'Invalid repository URL: {repo_url}'
                raise OSError(invalid_repo_msg)

            self._run_git_command(
                (
                    self._git_executable,
                    'clone',
                    '--filter=blob:none',
                    '--sparse',
                    repo_url,
                    clone_dir.as_posix(),
                ),
                check=True,
            )
            self.repo_dir = clone_dir

            commands = (
                (
                    self._git_executable,
                    'config',
                    'core.sparsecheckout',
                    'true',
                ),
                (
                    'echo',
                    'resource_pack',
                    '>>',
                    '.git/info/sparse-checkout',
                ),
                (
                    self._git_executable,
                    'sparse-checkout',
                    'init',
                    '--cone',
                ),
                (
                    self._git_executable,
                    'sparse-checkout',
                    'set',
                    'resource_pack',
                ),
            )
            for cmd in commands:
                self._run_git_command(
                    cmd,
                    check=True,
                )

        except subprocess.CalledProcessError as err:
            logging.getLogger('textureminer').exception(
                texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode, error_msg=err.stderr),
            )

    def _change_repo_version(self, version: str, *, fetch_tags: bool = True) -> None:
        """Change the version of the repository.

        Args:
        ----
            version (str): version to change the repository to
            fetch_tags (bool, optional): whether to fetch tags from the repository

        """
        if not self.repo_dir or not self.repo_dir.exists() or not self.repo_dir.is_dir():
            repo_dir_not_found_msg = (
                'Repository directory not found. Please clone the repository first.'
            )
            raise OSError(repo_dir_not_found_msg)
        if fetch_tags:
            self._run_git_command(
                (self._git_executable, 'fetch', '--tags'),
                check=False,
            )

        version_type = self.get_version_type(version)
        if version_type == VersionType.EXPERIMENTAL:
            logging.getLogger('textureminer').debug('Switching git branch to preview')
            self._run_git_command(
                (self._git_executable, 'switch', 'preview'),
                check=True,
            )

        try:
            version_regex = re.compile(r'^v\d+\.\d+\.\d+(\.\d+)?(-preview)?$')
            if not version_regex.match(version):
                invalid_version_msg = (
                    f'Invalid version. The version should follow the regex {version_regex.pattern}.'
                )
                raise ValueError(invalid_version_msg)

            self._run_git_command(
                (self._git_executable, 'checkout', f'tags/v{version}'),
                check=False,
            )
        except subprocess.CalledProcessError as err:
            logging.getLogger('textureminer').exception(
                texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode, error_msg=err.stderr),
            )
            raise

    def _create_partial_textures(  # noqa: C901, PLR0915
        self,
        texture_dir: Path,
        version_type: VersionType,
        *,
        prevent_overwrite: bool = True,
    ) -> None:
        """Create partial textures like stairs and slabs for the Bedrock Edition.

        Args:
        ----
            texture_dir (Path): directory where the textures are
            version_type (VersionType): type of version to create partials for
            prevent_overwrite (bool, optional): whether to copy textures to prevent overwrite

        """
        unused_textures: Sequence[str] = ('carpet',)

        logging.getLogger('textureminer').info(texts.CREATING_PARTIALS)
        texture_dict = self._get_blocks_json(version_type=version_type)

        for texture_name in texture_dict:
            if texture_name in unused_textures:
                continue

            blocks_dir = texture_dir / 'blocks'

            if (
                prevent_overwrite
                and texture_name in self.OVERWRITE_TEXTURES
                and texture_name == texture_dict[texture_name]['textures']
            ):
                copyfile(
                    blocks_dir / f'{texture_name}.png',
                    blocks_dir / f'{self.OVERWRITE_TEXTURES[texture_name]}.png',
                )

            if 'slab' in texture_name and 'double_slab' not in texture_name:
                identifier = texture_dict[texture_name]['textures']
                base_texture = self._identifier_to_filename(identifier, version_type)
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = blocks_dir / f'{base_texture}.png'
                out_path = blocks_dir / sub_dir / f'{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.SLAB, out_path)
            elif 'stairs' in texture_name:
                identifier = texture_dict[texture_name]['textures']
                base_texture = self._identifier_to_filename(identifier, version_type)
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = blocks_dir / f'{base_texture}.png'
                out_path = blocks_dir / sub_dir / f'{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.STAIR, out_path)
            elif 'carpet' in texture_name:
                if 'moss' in texture_name:
                    base_texture = 'moss_block'
                else:
                    base_texture = 'wool_colored_' + texture_name.replace('_carpet', '').replace(
                        'light_gray',
                        'silver',
                    )
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = blocks_dir / f'{base_texture}.png'
                out_path = blocks_dir / sub_dir / f'{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.CARPET, out_path)

            elif texture_name == 'snow':
                base_texture = 'snow'
                sub_dir = base_texture.split('/').pop(0) if '/' in base_texture else ''
                in_path = blocks_dir / f'{base_texture}.png'
                out_path = blocks_dir / sub_dir / f'{texture_name}.png'
                Edition.crop_texture(in_path, BlockShape.SNOW, out_path)

            # waxed copper blocks use same texture as the base variant
            elif 'copper' in texture_name and 'waxed' in texture_name:
                base_texture = texture_name.replace('waxed_', '')

                if '_door' in texture_name:
                    base_texture_top = base_texture + '_top'
                    base_texture_bottom = base_texture + '_bottom'
                    in_path_top = blocks_dir / f'{base_texture_top}.png'
                    in_path_bottom = blocks_dir / f'{base_texture_bottom}.png'
                    out_path_top = blocks_dir / f'{texture_name}_top.png'
                    out_path_bottom = blocks_dir / f'{texture_name}_bottom.png'
                    copyfile(in_path_top, out_path_top)
                    copyfile(in_path_bottom, out_path_bottom)
                    continue

                base_texture = (
                    base_texture.replace('copper', 'copper_block')
                    if base_texture == 'copper'
                    else base_texture
                )
                in_path = blocks_dir / f'{base_texture}.png'
                out_path = blocks_dir / sub_dir / f'{texture_name}.png'
                copyfile(in_path, out_path)

    def _get_blocks_json(self, version_type: VersionType) -> dict[str, Any]:
        """Fetch the blocks dictionary.

        Args:
        ----
            version_type (VersionType): type of version to fetch the blocks dictionary for

        Returns:
        -------
            dict[str, Any]: blocks dictionary

        """
        if self.blocks_cache is not None:
            return self.blocks_cache

        branch = 'preview' if version_type == VersionType.EXPERIMENTAL else 'main'

        url = f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{branch}/resource_pack/blocks.json'
        logging.getLogger('textureminer').debug(
            'Fetching blocks.json from {url}'.format(url=url)  # noqa: G001, UP032
        )
        file = requests.get(url, timeout=10)

        data = file.json()

        self.blocks_cache = data
        return data

    def _identifier_to_filename(self, identifier: str, version_type: VersionType) -> str:
        """Convert a block identifier to a texture filename.

        Args:
        ----
            identifier (str): block identifier
            version_type (VersionType): type of version to convert the identifier for

        Returns:
        -------
            str: texture filename

        """
        if isinstance(identifier, dict) and 'side' in identifier:
            identifier = identifier['side']

        data = self._get_terrain_texture_json(version_type=version_type)
        textures = data['texture_data'][identifier]['textures']

        if isinstance(textures, list):
            return textures[0].replace('textures/blocks/', '')

        return textures.replace('textures/blocks/', '')

    def _get_terrain_texture_json(self, version_type: VersionType) -> dict[str, Any]:
        """Fetch the terrain texture dictionary.

        Args:
        ----
            version_type (VersionType): type of version to fetch the terrain texture dictionary for

        Returns:
        -------
            dict[str, Any]: terrain texture dictionary

        """
        if self.terrain_texture_cache is not None:
            return self.terrain_texture_cache

        branch = 'main' if version_type == VersionType.STABLE else 'preview'

        url = f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{branch}/resource_pack/textures/terrain_texture.json'
        logging.getLogger('textureminer').debug(
            'Fetching terrain_texture.json from {url}'.format(url=url)  # noqa: G001, UP032
        )
        file = requests.get(url, timeout=10)
        text = file.text

        json_text = ''
        for line in text.splitlines():
            if line.startswith('//'):
                continue
            json_text += line + '\n'

        data = json.loads(json_text)

        self.terrain_texture_cache = data
        return data
