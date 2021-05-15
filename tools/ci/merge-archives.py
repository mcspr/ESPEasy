import sys
import argparse
import os
import pathlib
from itertools import chain
from zipfile import ZipFile


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)

    args = parser.parse_args()
    sources = find_zip(args.source)
    if not sources:
        raise NoZipFilesFound

    merge_zip(args.target, sources)
