#!/usr/bin/env python3
from json import dumps
from argparse import ArgumentParser
from os import walk
from os.path import abspath, expanduser, join, getsize, islink, exists
from hashlib import md5


def parse_arguments():
    """ Create a mandatory argument `-p` or `--path` (which identifies
    the root directory) to start scanning for duplicate files.
    """
    parser = ArgumentParser(description='Duplicate Files Finder')
    parser.add_argument('-p', '--path', required=True,
                        help="""identifies the root directory
                        to start scanning for duplicate files.""")

    return parser.parse_args()


def scan_files(directory):
    """Search for all the Files.

    retrieve the list of files in every directory of the tree root `path`.
    :param directory: the root directory

    :return: file_path_names
    """
    if exists(directory):
        file_path_names = []
        for root, dirs, files in walk(directory):
            for name in files:
                path = join(root, name)
                # ignore symbolic links that resolve to directories and files.
                if not islink(path):
                    file_path_names.append(path)
        return file_path_names
    else:
        print("File Not Exist")


def add_dictionary(key, value, dictionary):
    """Add more value if key exist in dictionary.

    """
    dictionary.setdefault(key, []).append(value)
    return dictionary


def group_file(dictionary):
    """I have a dictionary, if len(value) > 1
    I will append it to a list , and return that list

    :param dictionary: any dictionary
    :return: group
    """
    group = []
    for key in dictionary:
        if len(dictionary[key]) > 1:
            group.append(dictionary[key])
    return group


def group_files_by_size(file_path_names):
    """Group Files by their Size.

    :param file_path_names: the list of files in every directory
    of the tree root `path`

    :return: a list of groups (with at least two files)
             which have the same size.
             ignore empty files
    """
    dict_size = {}
    for path in file_path_names:
        size = getsize(path)
        if size > 0:
            if size not in dict_size:
                dict_size[size] = [path]
            else:
                add_dictionary(size, path, dict_size)

    group_size = group_file(dict_size)

    return group_size


def get_file_checksum(file_path):
    """Generate a Hash Value for a File.

    :param file_path: the absolute path and name of a file
    :return: the MD5 hash value of the content of this file.
    """
    try:
        with open(file_path, "rb") as file:
            return md5(file.read()).hexdigest()
    except OSError:
        return None


def group_files_by_checksum(file_path_names):
    """Group Files by their Checksum.

    MUST use the function `get_file_checksum` to detect duplicate files.

    :param file_path_names: the list of files in every directory of
    the tree root `path`

    :return: a list of groups that contain duplicate files.
    """
    dict_hash = {}
    for path in file_path_names:
        hash_file = get_file_checksum(path)
        if hash_file not in dict_hash:
            dict_hash[hash_file] = [path]
        else:
            add_dictionary(hash_file, path, dict_hash)

    group_hash = group_file(dict_hash)

    return group_hash


def find_duplicate_files(file_path_names):
    """Find all Duplicate Files.

    MUST use the two previous functions `group_files_by_size` and
    `group_files_by_checksum`.

    :param file_path_names: the list of files in every directory of
    the tree root `path`

    :return: a list of groups that contain duplicate files.
    """
    group_path = []
    for list_path in group_files_by_size(file_path_names):
        group_path.extend(group_files_by_checksum(list_path))
    return group_path


def print_output(group_path):
    """Output a JSON Expression.

    :param group_path: a list of groups that contain duplicate files
    :return: output project need
    """
    print(dumps(group_path, separators=(",\n", "")))


def main():
    try:
        args = parse_arguments()
        directory = args.path
        file_path_names = scan_files(abspath(expanduser(directory)))
        print_output(find_duplicate_files(file_path_names))
    except Exception:
        pass


if __name__ == '__main__':
    main()
