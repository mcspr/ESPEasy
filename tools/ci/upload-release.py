import sys
import os
import pathlib
from itertools import chain
from zipfile import ZipFile
from github import Github


class NoZipFilesFound(Exception):
    pass


def find_zip(directory):
    return pathlib.Path(directory).glob("**/*.zip")


def merge_zip(target, sources):
    with ZipFile(target, "a") as target_archive:
        for source in sources:
            with ZipFile(source, "r") as source_archive:
                for name in source_archive.namelist():
                    # note that .zip format allows the name to be specified multiple times
                    # only write unique names into the target archive, ignoring duplicates
                    try:
                        target_archive.getinfo(name)
                    except KeyError:
                        target_archive.writestr(name, source_archive.open(name).read())


if __name__ == "__main__":
    # artifacts/Binaries/ - .elf + .bin
    # artifacts/artifact/ - docs, upload tools, etc.
    sources = [str(zip_file) for zip_file in find_zip(sys.argv[1])]
    if not sources:
        raise NoZipFilesFound

    tag = os.environ["GITHUB_REF"][len("refs/tags/") :]
    message = os.environ.get("RELEASE_NOTES", tag)

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])

    target = "ESPEasy_{}.zip".format(tag)
    print("preparing target={} from {} sources".format(target, len(sources)))
    merge_zip(target, sources)

    release = repo.create_git_release(tag=tag, name=tag, message=message)
    release.upload_asset(target)
