import argparse
from pathlib import Path

from javadoc2html.convert_to_html import ConvertToHtml
from javadoc2html.doc_types import DocFile


def get_files_from_dir(dir_name: str, files):
    for file in Path(dir_name).iterdir():
        if file.is_dir():
            get_files_from_dir(str(file), files)
        if file.name.endswith('.java'):
            files.append(DocFile.parse_file(dir_name + '/' + file.name))
    return files


def get_parser():
    parser = argparse.ArgumentParser(description='javaDoc2HTML')
    parser.add_argument('files', type=str, nargs='+', default=[],
                        help='path to files or directories of files')
    return parser


if __name__ == '__main__':
    arg = get_parser().parse_args()
    for directory in arg.files:
        if Path(directory).exists():
            files = get_files_from_dir(directory, [])
            ConvertToHtml(files, 'html', directory + '/')
        else:
            print(f'You did not specify a directory({directory}) or not found')
