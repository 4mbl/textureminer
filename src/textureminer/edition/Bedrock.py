import os
import subprocess
from .. import texts
from ..file import rm_if_exists
from ..edition.Edition import Edition
from ..options import DEFAULTS, EditionType, VersionType
from ..texts import tabbed_print


class Bedrock(Edition):
    """A class representing the Bedrock Edition of Minecraft.

    This class provides methods for retrieving information about versions, downloading textures, and more.

    Attributes:
        REPO_URL (str): The URL of the Bedrock Edition repository.

    """

    REPO_URL = 'https://github.com/Mojang/bedrock-samples'

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

        tabbed_print(texts.FILE_DOWNLOADING)

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
    ) -> str | None:

        if isinstance(version_or_type, str) and not Edition.validate_version(
                version_or_type, edition=EditionType.BEDROCK):
            tabbed_print(texts.VERSION_INVALID.format(version=version_or_type))
            return None

        version_type = version_or_type if isinstance(version_or_type,
                                                     VersionType) else None
        version = None
        self._clone_repo()
        if isinstance(version_or_type, str):
            version = version_or_type
        else:
            version = self.get_latest_version(version_type if version_type is not None else VersionType.ALL)

        self._change_repo_version(version)

        filtered = Edition.filter_unwanted(self.repo_dir,
                                   f'{output_dir}/bedrock/{version}',
                                   edition=EditionType.BEDROCK)
        Edition.scale_textures(filtered, scale_factor, do_merge)

        tabbed_print(texts.CLEARING_TEMP)
        rm_if_exists(DEFAULTS['TEMP_PATH'])

        output_dir = os.path.abspath(filtered).replace('\\', '/')
        print(texts.COMPLETED.format(output_dir=output_dir))
        return output_dir
