# noqa: N999
"""Provides a class representing the Java edition of Minecraft."""

import json
import os
import sys
from enum import Enum
from pathlib import Path
from shutil import copyfile, copytree
from typing import Any, ClassVar, override
from urllib.request import urlretrieve
from zipfile import ZipFile

import requests  # type: ignore[import]

from textureminer import texts
from textureminer.exceptions import FileFormatError
from textureminer.file import mk_dir
from textureminer.options import DEFAULTS, EditionType, VersionType
from textureminer.texts import tabbed_print

from .Edition import BlockShape, Edition, TextureOptions


class VersionManifestIdentifiers(Enum):
    """Enum class representing different types of version manifest identifiers for Minecraft."""

    STABLE = 'release'
    """stable release
    """
    EXPERIMENTAL = 'snapshot'
    """snapshot
    """


class Java(Edition):
    """Represents the Java Edition of Minecraft.

    Attributes
    ----------
        VERSION_MANIFEST_URL (str): The URL of the version manifest.
        VERSION_MANIFEST (dict): The cached version manifest.

    """

    VERSION_MANIFEST_URL: ClassVar[str] = (
        'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'
    )
    ALLOWED_PARTIAL_SUFFIXES: ClassVar[list[str]] = ['_slab', '_stairs', '_carpet']
    ALLOWED_PARTIAL_LITERALS: ClassVar[list[str]] = ['snow']

    TEXTURE_EXCEPTIONS: ClassVar[list[dict[str, str]]] = [
        {'from': 'smooth_quartz', 'to': 'quartz_block_bottom'},
        {'from': 'smooth_sandstone', 'to': 'sandstone_top'},
        {'from': 'smooth_red_sandstone', 'to': 'red_sandstone_top'},
        {'from': 'smooth_stone', 'to': 'smooth_stone_slab_side'},
    ]

    REPLICATE_MAP: ClassVar[dict[str, str]] = {
        'glass_pane_top': 'glass_pane',
        'red_stained_glass_pane_top': 'red_stained_glass_pane',
        'orange_stained_glass_pane_top': 'orange_stained_glass_pane',
        'yellow_stained_glass_pane_top': 'yellow_stained_glass_pane',
        'lime_stained_glass_pane_top': 'lime_stained_glass_pane',
        'green_stained_glass_pane_top': 'green_stained_glass_pane',
        'cyan_stained_glass_pane_top': 'cyan_stained_glass_pane',
        'light_blue_stained_glass_pane_top': 'light_blue_stained_glass_pane',
        'blue_stained_glass_pane_top': 'blue_stained_glass_pane',
        'purple_stained_glass_pane_top': 'purple_stained_glass_pane',
        'magenta_stained_glass_pane_top': 'magenta_stained_glass_pane',
        'pink_stained_glass_pane_top': 'pink_stained_glass_pane',
        'white_stained_glass_pane_top': 'white_stained_glass_pane',
        'light_gray_stained_glass_pane_top': 'light_gray_stained_glass_pane',
        'gray_stained_glass_pane_top': 'gray_stained_glass_pane',
        'black_stained_glass_pane_top': 'black_stained_glass_pane',
        'brown_stained_glass_pane_top': 'brown_stained_glass_pane',
    }

    OVERWRITE_TEXTURES: ClassVar[dict[str, str]] = {
        'snow': 'snow_block',
    }

    version_manifest_cache: dict | None = None

    @override
    def get_textures(
        self,
        version_or_type: VersionType | str,
        output_dir: str = DEFAULTS['OUTPUT_DIR'],
        options: TextureOptions | None = None,
    ) -> str | None:
        if options is None:
            options = DEFAULTS['TEXTURE_OPTIONS']

        version: str | None = None

        if isinstance(version_or_type, VersionType):
            version = self.get_latest_version(version_or_type)
        elif isinstance(version_or_type, str) and Edition.validate_version(
            version_or_type,
            edition=EditionType.JAVA,
        ):
            version = version_or_type
        else:
            tabbed_print(texts.ERROR_VERSION_INVALID.format(version=version_or_type))
            return None

        tabbed_print(texts.VERSION_USING_X.format(version=version))
        assets = self._download_client_jar(version, self.temp_dir + '/version-jars')

        extracted = self._extract_jar(assets, self.temp_dir + '/extracted-files')

        textures_path = self.temp_dir + '/extracted-textures/textures'
        copytree(extracted + '/assets/minecraft/textures', textures_path)

        if options['DO_PARTIALS']:
            self._create_partial_textures(extracted, textures_path)

        filtered = Edition.filter_unwanted(
            textures_path,
            output_dir + '/java/' + version,
            edition=EditionType.JAVA,
        )

        if options['DO_REPLICATE']:
            Edition.replicate_textures(filtered, self.REPLICATE_MAP)

        Edition.scale_textures(
            filtered,
            options['SCALE_FACTOR'],
            do_merge=options['DO_MERGE'],
            do_crop=options['DO_CROP'],
        )

        return Path(filtered).resolve().as_posix()

    @override
    def get_version_type(self, version: str) -> VersionType | None:
        if Edition.validate_version(
            version=version,
            version_type=VersionType.STABLE,
            edition=EditionType.JAVA,
        ):
            return VersionType.STABLE
        if Edition.validate_version(
            version=version,
            version_type=VersionType.EXPERIMENTAL,
            edition=EditionType.JAVA,
        ):
            return VersionType.EXPERIMENTAL
        return None

    @override
    def get_latest_version(self, version_type: VersionType) -> str:
        tabbed_print(texts.VERSION_LATEST_FINDING.format(version_type=version_type.value))
        version_id = (
            VersionManifestIdentifiers.STABLE.value
            if version_type == VersionType.STABLE
            else VersionManifestIdentifiers.EXPERIMENTAL.value
        )
        return self._get_version_manifest()['latest'][version_id]

    def _get_version_manifest(self) -> dict:
        """Fetch the version manifest from Mojang. Caches the result.

        Returns
        -------
            dict: The version manifest.

        """
        if Java.version_manifest_cache is None:
            Java.version_manifest_cache = requests.get(Java.VERSION_MANIFEST_URL, timeout=10).json()

        return Java.version_manifest_cache

    def _download_client_jar(self, version: str, download_dir: str) -> str:
        """Download the client .jar file for a specific version from Mojang's servers.

        Args:
        ----
            version (str): The version to download.
            download_dir (str): The directory to download the file to

        Returns:
        -------
            str: The path of the downloaded file.

        """
        url = None
        for v in self._get_version_manifest()['versions']:
            if v['id'] == version:
                url = v['url']
                break

        if url is None:
            tabbed_print(texts.ERROR_VERSION_INVALID.format(version=version))
            sys.exit(2)

        resp_json = requests.get(url, timeout=10).json()
        client_jar_url = resp_json['downloads']['client']['url']
        if type(client_jar_url) is not str:
            client_jar_url_msg = 'Client jar URL is not a string.'
            raise TypeError(client_jar_url_msg)

        mk_dir(download_dir)
        tabbed_print(texts.FILES_DOWNLOADING)

        if not client_jar_url.startswith(('http:', 'https:')):
            invalid_url_format_msg = 'URL must start with "http:" or "https:".'
            raise ValueError(invalid_url_format_msg)
        urlretrieve(client_jar_url, f'{download_dir}/{version}.jar')  # noqa: S310
        return f'{download_dir}/{version}.jar'

    def _extract_jar(self, jar_path: str, output_dir: str) -> str:
        """Extract files from a .jar file.

        Args:
        ----
            jar_path (str): The path of the .jar file.
            output_dir (str): The path of the output directory.

        Returns:
        -------
            str: The path of the output directory.

        """
        with ZipFile(jar_path, 'r') as zip_object:
            file_amount = len(zip_object.namelist())
            tabbed_print(texts.FILES_EXTRACTING_N.format(file_amount=file_amount))
            zip_object.extractall(output_dir)

        return output_dir

    def _create_partial_textures(
        self,
        extracted_dir: str,
        texture_dir: str,
        *,
        prevent_overwrite: bool = True,
    ) -> None:
        """Create partial textures like stairs and slabs for the Java Edition.

        Args:
        ----
            extracted_dir (str): directory where the extracted files are
            texture_dir (str): directory where the textures are
            prevent_overwrite (bool, optional): whether to copy textures to prevent overwrite

        """
        tabbed_print(texts.CREATING_PARTIALS)

        recipe_dir = self.temp_dir + '/extracted-textures/recipes'
        copytree(f'{extracted_dir}/data/minecraft/recipe', recipe_dir)

        texture_dict = self._get_texture_dict(recipe_dir, texture_dir)

        for texture_name, base_texture in texture_dict.items():
            if (
                texture_name == base_texture
                and prevent_overwrite
                and texture_name in self.OVERWRITE_TEXTURES
            ):
                copyfile(
                    f'{texture_dir}/block/{texture_name}.png',
                    f'{texture_dir}/block/{self.OVERWRITE_TEXTURES[texture_name]}.png',
                )

            if 'slab' in texture_name:
                shape = BlockShape.SLAB
            elif 'stairs' in texture_name:
                shape = BlockShape.STAIR
            elif 'carpet' in texture_name:
                shape = BlockShape.CARPET
            elif texture_name == 'snow':
                shape = BlockShape.SNOW
            else:
                continue

            in_path = f'{texture_dir}/block/{base_texture}.png'
            out_path = f'{texture_dir}/block/{texture_name}.png'
            Edition.crop_texture(in_path, shape, out_path)

    def _get_texture_dict(self, recipe_dir: str, texture_dir: str) -> dict[str, str]:
        """Get texture-material mapping from recipe files.

        Args:
        ----
            recipe_dir (str): directory where the recipe files are
            texture_dir (str): directory where the texture files are

        Raises:
        ------
            FileFormatException: if the recipe file cannot be parsed

        Returns:
        -------
            dict[str, str]: texture-material mapping

        """
        texture_dict = {}
        for root, _dirs, files in os.walk(recipe_dir):
            for file in files:
                product = file.replace('.json', '')

                # skip duplicate recipes
                if 'from_' in product:
                    continue

                # skip re-dyed carpets
                if 'dye_' in product and '_carpet' in product:
                    continue

                if not any(
                    partial in product for partial in self.ALLOWED_PARTIAL_SUFFIXES
                ) and not any(literal == product for literal in self.ALLOWED_PARTIAL_LITERALS):
                    continue

                try:
                    base_material = self._get_base_material_from_recipe(
                        f'{root}/{file}',
                        texture_dir,
                    )
                except FileFormatError:
                    unknown_recipe_msg = f'Unknown recipe file format: {f'{root}/{file}'}'
                    raise FileFormatError(unknown_recipe_msg) from None

                if base_material is None:
                    not_found_msg = f'Could not find base material for {product}'
                    raise FileFormatError(not_found_msg)

                texture_dict[product] = base_material

        return texture_dict

    def _get_base_material_from_recipe(self, recipe_file_path: str, texture_dir: str) -> str | None:
        """Get the base material from a recipe file.

        Args:
        ----
            recipe_file_path (str): path of the recipe file
            texture_dir (str): directory where the texture files are

        Raises:
        ------
            FileFormatException: if the recipe file cannot be parsed

        Returns:
        -------
            str | None: base material name or None if not found

        """
        with Path(recipe_file_path).open(encoding='utf-8') as f:
            recipe_data = json.load(f)

            i = 0
            continue_loop = True
            while continue_loop:
                if 'key' in recipe_data:
                    materials = recipe_data['key']['#']
                    if isinstance(materials, list):
                        if i >= len(materials):
                            unknown_recipe_msg = f'Unknown recipe file format: {recipe_file_path}'
                            raise FileFormatError(unknown_recipe_msg)
                        base_material = self._handle_recipe_incredient_format(materials[i])
                    else:
                        base_material = self._handle_recipe_incredient_format(materials)
                elif 'ingredients' in recipe_data:
                    if i >= len(materials):
                        unknown_recipe_msg = f'Unknown recipe file format: {recipe_file_path}'
                        raise FileFormatError(unknown_recipe_msg)
                    base_material = self._handle_recipe_incredient_format(
                        recipe_data['ingredients'][i],
                    )
                else:
                    unknown_recipe_msg = f'Unknown recipe file format: {recipe_file_path}'
                    raise FileFormatError(unknown_recipe_msg)

                base_material = base_material.replace('minecraft:', '')
                base_material = self._handle_texture_exceptions(
                    base_material,
                    self.TEXTURE_EXCEPTIONS,
                    texture_dir,
                )

                if self._texture_exists(base_material, texture_dir):
                    return base_material

                i += 1

        return None

    def _handle_recipe_incredient_format(self, materials: dict[str, str] | str | Any) -> str:  # noqa: ANN401
        """Handle recipe format changes between Minecraft Java versions.

        Args:
        ----
            materials (dict[str, str] | str | Any): Incredient data for a recipe

        Raises:
        ------
            FileFormatError: if the recipe format is unknown

        Returns:
        -------
            str: name of the material used in the recipe

        """
        # pre 24w33a / 1.21.2 recipe format
        if isinstance(materials, dict):
            return materials['item']
        # post 24w33a / 1.21.2 recipe format
        # https://4mbl.link/textureminer/refs/recipe-format/24w33a
        if isinstance(materials, str):
            return materials
        unknown_recipe_msg = 'Unknown recipe file format.'
        raise FileFormatError(unknown_recipe_msg)

    def _handle_texture_exceptions(
        self,
        texture_name: str,
        texture_exceptions: list[dict[str, str]],
        texture_dir: str,
    ) -> str:
        """Handle texture exceptions.

        Args:
        ----
            texture_name (str): name of the texture to handle
            texture_exceptions (list[dict[str, str]]): list of texture exception rules
            texture_dir (str): directory where the texture files are

        Returns:
        -------
            str: texture name

        """
        # waxed copper blocks use same texture as the base variant
        if 'copper' in texture_name:
            texture_name = texture_name.replace('waxed_', '')
            if self._texture_exists(texture_name, texture_dir):
                return texture_name

        if texture_name == 'snow_block':
            return 'snow'

        for texture_exception in texture_exceptions:
            if texture_name == texture_exception['from']:
                texture_name = texture_exception['to']
                if self._texture_exists(texture_name, texture_dir):
                    return texture_name

        return texture_name

    def _texture_exists(self, texture_name: str, texture_dir: str) -> bool:
        return (
            Path(f'{texture_dir}/block/{texture_name}.png').is_file()
            if texture_name is not None
            else False
        )
