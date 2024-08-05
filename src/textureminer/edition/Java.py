from enum import Enum
import json
import os
from shutil import copytree, rmtree
import sys
from typing import Any
from zipfile import ZipFile
import urllib.request
import requests  # type: ignore

from textureminer.exceptions import FileFormatException  # type: ignore
from .. import texts
from .Edition import BlockShape, Edition, TextureOptions
from ..file import mk_dir, rm_if_exists
from ..options import DEFAULTS, EditionType, VersionType
from ..texts import tabbed_print


class VersionManifestIdentifiers(Enum):
    """Enum class representing different types of version manifest identifiers for Minecraft
    """

    STABLE = 'release'
    """stable release
    """
    EXPERIMENTAL = 'snapshot'
    """snapshot
    """


class Java(Edition):
    """
    Represents the Java Edition of Minecraft.

    Attributes:
        VERSION_MANIFEST_URL (str): The URL of the version manifest.
        VERSION_MANIFEST (dict): The cached version manifest.

    """
    VERSION_MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'
    ALLOWED_PARTIALS = ['_slab', '_stairs', '_carpet']
    TEXTURE_EXCEPTIONS = [
        {
            'from': 'smooth_quartz',
            'to': 'quartz_block_bottom'
        },
        {
            'from': 'smooth_sandstone',
            'to': 'sandstone_top'
        },
        {
            'from': 'smooth_red_sandstone',
            'to': 'red_sandstone_top'
        },
        {
            'from': 'smooth_stone',
            'to': 'smooth_stone_slab_side'
        },
    ]

    REPLICATE_MAP: dict[str, str] = {
        'glass_pane_top': 'glass_pane',
        'red_stained_glass_pane_top': 'red_glass_pane',
        'orange_stained_glass_pane_top': 'orange_glass_pane',
        'yellow_stained_glass_pane_top': 'yellow_glass_pane',
        'lime_stained_glass_pane_top': 'lime_glass_pane',
        'green_stained_glass_pane_top': 'green_glass_pane',
        'cyan_stained_glass_pane_top': 'cyan_glass_pane',
        'light_blue_stained_glass_pane_top': 'light_blue_glass_pane',
        'blue_stained_glass_pane_top': 'blue_glass_pane',
        'purple_stained_glass_pane_top': 'purple_glass_pane',
        'magenta_stained_glass_pane_top': 'magenta_glass_pane',
        'pink_stained_glass_pane_top': 'pink_glass_pane',
        'black_stained_glass_pane_top': 'black_glass_pane',
        'brown_stained_glass_pane_top': 'brown_glass_pane',
    }

    def __init__(self):
        self.VERSION_MANIFEST: dict | None = None

    def get_textures(self,
                     version_or_type: VersionType | str,
                     output_dir: str = DEFAULTS['OUTPUT_DIR'],
                     options: TextureOptions | None = None) -> str | None:

        if options is None:
            options = DEFAULTS['TEXTURE_OPTIONS']

        version: str | None = None

        if isinstance(version_or_type, VersionType):
            version = self.get_latest_version(version_or_type)
        elif isinstance(version_or_type, str) and Edition.validate_version(
                version_or_type, edition=EditionType.JAVA):
            version = version_or_type
        else:
            tabbed_print(
                texts.ERROR_VERSION_INVALID.format(version=version_or_type))
            return None

        tabbed_print(texts.VERSION_USING_X.format(version=version))
        assets = self._download_client_jar(
            version, DEFAULTS['TEMP_PATH'] + '/version-jars')

        extracted = self._extract_jar(
            assets, DEFAULTS['TEMP_PATH'] + '/extracted-files')
        rmtree(DEFAULTS['TEMP_PATH'] + '/version-jars/')

        textures_path = DEFAULTS['TEMP_PATH'] + '/extracted-textures/textures'
        if os.path.isdir(textures_path):
            rmtree(textures_path)
        copytree(extracted + '/assets/minecraft/textures', textures_path)

        if options['DO_PARTIALS']:
            self._create_partial_textures(extracted, textures_path)

        rm_if_exists(DEFAULTS['TEMP_PATH'] + '/extracted-files/')

        filtered = Edition.filter_unwanted(textures_path,
                                           output_dir + '/java/' + version,
                                           edition=EditionType.JAVA)

        if options['DO_REPLICATE']:
            Edition.replicate_textures(filtered, self.REPLICATE_MAP)

        Edition.scale_textures(filtered, options['SCALE_FACTOR'],
                               options['DO_MERGE'], options['DO_CROP'])

        tabbed_print(texts.CLEARING_TEMP)
        rm_if_exists(DEFAULTS['TEMP_PATH'])

        output_dir = os.path.abspath(filtered).replace('\\', '/')
        print(texts.COMPLETED.format(output_dir=output_dir))
        return output_dir

    def get_version_type(self, version: str) -> VersionType | None:
        if Edition.validate_version(version=version,
                                    version_type=VersionType.STABLE,
                                    edition=EditionType.JAVA):
            return VersionType.STABLE
        if Edition.validate_version(version=version,
                                    version_type=VersionType.EXPERIMENTAL,
                                    edition=EditionType.JAVA):
            return VersionType.EXPERIMENTAL
        return None

    def get_latest_version(self, version_type: VersionType) -> str:
        tabbed_print(
            texts.VERSION_LATEST_FINDING.format(
                version_type=version_type.value))

        version_id = VersionManifestIdentifiers.STABLE.value if version_type == VersionType.STABLE else VersionManifestIdentifiers.EXPERIMENTAL.value
        latest_version = self._get_version_manifest()['latest'][version_id]
        tabbed_print(
            texts.VERSION_LATEST_IS.format(version_type=version_type.value,
                                           latest_version="" + latest_version))
        return latest_version

    def _get_version_manifest(self) -> dict:
        """
        Fetches the version manifest from Mojang's servers.
        If the manifest has already been fetched, it will return the cached version.

        Returns:
            dict: The version manifest.
        """
        if self.VERSION_MANIFEST is None:
            self.VERSION_MANIFEST = requests.get(Java.VERSION_MANIFEST_URL,
                                                 timeout=10).json()

        return self.VERSION_MANIFEST

    def _download_client_jar(self, version: str, download_dir: str) -> str:
        """
        Downloads the client .jar file for a specific version from Mojang's servers.

        Args:
            version (str): The version to download.
            download_dir (str, optional): The directory to download the file to. Defaults to a temporary directory.

        Returns:
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

        mk_dir(download_dir)
        tabbed_print(texts.FILES_DOWNLOADING)
        urllib.request.urlretrieve(client_jar_url,
                                   f'{download_dir}/{version}.jar')
        return f'{download_dir}/{version}.jar'

    def _extract_jar(self, jar_path: str, output_dir: str) -> str:
        """
        Extracts files from a .jar file.

        Args:
            jar_path (str): The path of the .jar file.
            output_dir (str, optional): The path of the output directory.

        Returns:
            str: The path of the output directory.
        """
        with ZipFile(jar_path, 'r') as zip_object:
            file_amount = len(zip_object.namelist())
            tabbed_print(
                texts.FILES_EXTRACTING_N.format(file_amount=file_amount))
            zip_object.extractall(output_dir)

        return output_dir

    def _create_partial_textures(self, extracted_dir: str, texture_dir: str):
        tabbed_print(texts.CREATING_PARTIALS)

        recipe_dir = DEFAULTS['TEMP_PATH'] + '/extracted-textures/recipes'
        if os.path.isdir(recipe_dir):
            rmtree(recipe_dir)
        copytree(f'{extracted_dir}/data/minecraft/recipe', recipe_dir)

        texture_dict = self._get_texture_dict(recipe_dir, texture_dir)

        for texture_name, base_texture in texture_dict.items():
            if 'slab' in texture_name:
                shape = BlockShape.SLAB
            elif 'stairs' in texture_name:
                shape = BlockShape.STAIR
            elif 'carpet' in texture_name:
                shape = BlockShape.CARPET
            else:
                continue

            in_path = f'{texture_dir}/block/{base_texture}.png'
            out_path = f'{texture_dir}/block/{texture_name}.png'
            Edition.crop_texture(in_path, shape, out_path)

    def _get_texture_dict(self, recipe_dir: str,
                          texture_dir: str) -> dict[str, Any]:
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

                if not self._is_allowed_partial(product, self.ALLOWED_PARTIALS):
                    continue

                base_material = self._get_base_material_from_recipe(
                    f'{root}/{file}', texture_dir)

                if base_material is None:
                    raise FileFormatException(
                        f'Could not find base material for {product}')
                texture_dict[product] = base_material

        return texture_dict

    def _is_allowed_partial(self, texture_name: str,
                            allowed: list[str]) -> bool:
        return any(partial in texture_name for partial in allowed)

    def _get_base_material_from_recipe(self, recipe_file_path: str,
                                       texture_dir: str) -> str | None:
        with open(recipe_file_path, encoding='utf-8') as f:
            recipe_data = json.load(f)

            i = 0
            continue_loop = True
            while continue_loop:
                if 'key' in recipe_data:
                    materials = recipe_data['key']["#"]
                    if isinstance(materials, list):
                        if i >= len(materials):
                            raise FileFormatException(
                                f'Unknown recipe file format: {recipe_file_path}'
                            )
                        base_material = materials[i]['item']
                    else:
                        base_material = materials['item']
                        continue_loop = False
                elif 'ingredients' in recipe_data:
                    if i >= len(materials):
                        raise FileFormatException(
                            f'Unknown recipe file format: {recipe_file_path}')
                    base_material = recipe_data['ingredients'][i]['item']
                else:
                    raise FileFormatException(
                        f'Unknown recipe file format: {recipe_file_path}')

                base_material = base_material.replace('minecraft:', '')
                base_material = self._handle_texture_exceptions(
                    base_material, self.TEXTURE_EXCEPTIONS, texture_dir)

                if self._texture_exists(base_material, texture_dir):
                    return base_material

                i += 1

        return None

    def _handle_texture_exceptions(self, base_material: str,
                                   texture_exceptions: list[dict[str, str]],
                                   texture_dir: str) -> str | None:

        # waxed copper blocks use same texture as the base variant
        if 'copper' in base_material:
            base_material = base_material.replace('waxed_', '')
            if self._texture_exists(base_material, texture_dir):
                return base_material

        for texture_exception in texture_exceptions:
            if base_material == texture_exception['from']:
                base_material = texture_exception['to']
                if self._texture_exists(base_material, texture_dir):
                    return base_material

        return base_material

    def _texture_exists(self, texture_name: str, texture_dir: str) -> bool:
        return os.path.isfile(f'{texture_dir}/block/{texture_name}.png'
                             ) if texture_name is not None else False
