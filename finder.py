#!/usr/bin/env python
import getopt
import json
import os
import subprocess
import sys

from shutil import copyfile
from typing import Dict, Tuple


def get_input(*argv) -> str:
    usage = "Usage:\nfinder.py -p <project_directory> -l <locale_directory>"
    project_directory = ''
    locale_directory = ''

    try:
        opts, args = getopt.getopt(
                argv,
                'hp:l:',
                ['project-dir=','locale-dir='])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        if opt in ('-p', '--project-dir'):
            project_directory = arg
        if opt in ('-l', '--locale-dir'):
            locale_directory = arg

    if not (os.path.isdir(project_directory) and
            os.path.isdir(locale_directory)):
        print(usage)
        sys.exit(1)

    print("Project directory set to {}".format(project_directory))
    print("Locale directory set to {}".format(locale_directory))


    return project_directory, locale_directory


def find_translate_tags(project_directory: str) -> Dict[str, str]:
    def prepare_string(s):
        return s.strip("''").strip('"').replace('&quot;', '')

    p1 = subprocess.Popen(['ag', '-o', '--nofilename', '--nobreak', '--silent',
            '{{[^{]*\| translate ?(?:\||}})', project_directory],
            stdout=subprocess.PIPE)
    output = subprocess.check_output(['ag', '-o',
            r'("|\'|&quot;).*?(\1)'],
            stdin=p1.stdout)
    return {(prepare_string(e), prepare_string(e))
            for e in output.decode().strip().split('\n')}


def get_current_translations(locale_directory) -> Dict[str, Dict[str, str]]:
    translations = {}
    for file_ in os.listdir(locale_directory):
        if file_.endswith('.json'):
            file_path = os.path.join(locale_directory, file_)
            with open(file_path) as data:
                try:
                    translations[file_path] = json.load(data)
                except json.decoder.JSONDecodeError:
                    translations[file_path] = {}
    return translations


def update_translations(locales: Dict[str, str],
        translations: Dict[str, Dict[str, str]]) -> None:
    for file_path, translation in translations.items():
        original = dict(translation)
        translation.update(locales)
        translation.update(original)
        copyfile(file_path, '{}.bak'.format(file_path))
        with open(file_path, 'w') as data:
            json.dump(translation, data, indent=4, sort_keys=True,
                    ensure_ascii=False)


def main(*argv):
    project_directory, locale_directory = get_input(*argv)
    locales = find_translate_tags(project_directory)
    translations = get_current_translations(locale_directory)
    update_translations(locales, translations)


if __name__ == '__main__':
    main(*sys.argv[1:])