import argparse
import os
from pathlib import Path

from javadoc2html.convert_to_html import ConvertToHtml
from javadoc2html.doc_types import DocFile


def get_files_from_dir(dir_name):
    files = []
    for file in os.listdir(dir_name):
        if file.endswith('.java'):
            files.append(DocFile.read_java_file(dir_name + '/' + file))
    return files


def get_parser():
    parser = argparse.ArgumentParser(description='javaDoc2HTML')
    parser.add_argument('files', type=str,
                        help='path to files or directories of files')
    return parser


files = get_files_from_dir(str(Path.cwd() / 'resources'))
converter = ConvertToHtml(files, 'resources', str(Path.cwd() / 'resources') + '/')
# arg = get_parser().parse_args()
# if arg.files[0] and os.path.exists(arg.files[0]):
#     handler = JavaDocParser(arg.files[0])
#     files = handler.get_files_from_dir()
#     ConvertToHtml(files, 'temp', arg.files[0] + '/')
# else:
#     print('you did not specify a directory or not found')
