import os
from shutil import copytree, rmtree
from zipfile import ZipFile
import urllib.request
import requests  # type: ignore
from textureminer import texts
from textureminer.edition.Edition import Edition
from textureminer.file import mk_dir, rm_if_exists
from textureminer.options import DEFAULTS, EditionType, VersionType
from textureminer.texts import tabbed_print


class Java(Edition):
    """
    Represents the Java Edition of Minecraft.

    Attributes:
        VERSION_MANIFEST_URL (str): The URL of the version manifest.
        VERSION_MANIFEST (dict): The cached version manifest.

    """
    VERSION_MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

    def __init__(self):
        self.VERSION_MANIFEST: dict = None

    def get_version_type(self, version: str) -> VersionType | None:
        if version[0] != 'v':
            version = f'v{version}'
        if Edition.validate_version(version=version, version_type=VersionType.RELEASE, edition=EditionType.JAVA):
            return VersionType.RELEASE
        if Edition.validate_version(version=version, version_type=VersionType.EXPERIMENTAL, edition=EditionType.JAVA) :
            return VersionType.EXPERIMENTAL
        return None

    def _get_version_manifest(self) -> dict:
        """
        Fetches the version manifest from Mojang's servers.
        If the manifest has already been fetched, it will return the cached version.

        Returns:
            dict: The version manifest.
        """
        if self.VERSION_MANIFEST is None:
            self.VERSION_MANIFEST = requests.get(Java.VERSION_MANIFEST_URL, timeout=10).json()

        return self.VERSION_MANIFEST

    def get_latest_version(self, version_type: VersionType) -> str:
        tabbed_print(
            texts.VERSION_LATEST_FINDING.format(
                version_type=version_type.value))

        version_id = 'release' if version_type.value == VersionType.RELEASE else 'snapshot'
        latest_version = self._get_version_manifest()['latest'][version_id]
        tabbed_print(
            texts.VERSION_LATEST_IS.format(version_type=version_type.value,
                                           latest_version="" + latest_version))
        return latest_version

    def _download_client_jar(
        self,
        version: str,
        download_dir: str = f'{DEFAULTS['TEMP_PATH']}/version-jars',
    ) -> str:
        """
        Downloads the client .jar file for a specific version from Mojang's servers.

        Args:
            version (str): The version to download.
            download_dir (str, optional): The directory to download the file to. Defaults to a temporary directory.

        Returns:
            str: The path of the downloaded file.
        """
        for v in self._get_version_manifest()['versions']:
            if v['id'] == version:
                url = v['url']
                break
            else:
                url = None

        json = requests.get(url, timeout=10).json()
        client_jar_url = json['downloads']['client']['url']

        mk_dir(download_dir)
        tabbed_print(texts.FILE_DOWNLOADING)
        urllib.request.urlretrieve(client_jar_url,
                                   f'{download_dir}/{version}.jar')
        return f'{download_dir}/{version}.jar'

    def extract_textures(
            self,
            input_path: str,
            output_path: str = f'{DEFAULTS['TEMP_PATH']}/extracted-textures') -> str:
        """
        Extracts textures from a .jar file.

        Args:
            input_path (str): The path of the .jar file.
            output_path (str, optional): The path of the output directory.

        Returns:
            str: The path of the output directory.
        """
        with ZipFile(input_path, 'r') as zip_object:
            file_amount = len(zip_object.namelist())
            tabbed_print(texts.FILES_EXTRACTING.format(file_amount=file_amount))
            zip_object.extractall(f'{DEFAULTS['TEMP_PATH']}/extracted-files/')
        rmtree(f'{DEFAULTS['TEMP_PATH']}/version-jars/')

        if os.path.isdir(output_path):
            rmtree(output_path)

        copytree(f'{DEFAULTS['TEMP_PATH']}/extracted-files/assets/minecraft/textures',
                 output_path)
        rmtree(f'{DEFAULTS['TEMP_PATH']}/extracted-files/')

        return output_path

    def get_textures(self,
                     version_or_type: VersionType | str,
                     output_dir: str = DEFAULTS['OUTPUT_DIR'],
                     scale_factor: int = DEFAULTS['SCALE_FACTOR'],
                     do_merge: bool = True) -> str | None:

        if isinstance(version_or_type, str) and not Edition.validate_version(
                version_or_type, edition=EditionType.JAVA):
            print(texts.VERSION_INVALID.format(version=version_or_type))
            return None

        version_type = version_or_type if isinstance(version_or_type,
                                                     VersionType) else None

        version = None
        if isinstance(version_or_type, str):
            version = version_or_type
        else:
            version = self.get_latest_version(
                version_type if version_type is not None else VersionType.
                RELEASE)

        tabbed_print(texts.VERSION_USING_X.format(version=version))
        assets = self._download_client_jar(version)
        extracted = self.extract_textures(assets)
        filtered = Edition.filter_unwanted(extracted,
                                   f'{output_dir}/java/{version}',
                                   edition=EditionType.JAVA)
        Edition.scale_textures(filtered, scale_factor, do_merge)

        tabbed_print(texts.CLEARING_TEMP)
        rm_if_exists(DEFAULTS['TEMP_PATH'])

        output_dir = os.path.abspath(filtered).replace('\\', '/')
        print(texts.COMPLETED.format(output_dir=output_dir))
        return output_dir
