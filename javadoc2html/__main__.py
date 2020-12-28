import argparse
import os

from javadoc2html.convert_to_html import ConvertToHtml
from javadoc2html.javadoc_parser import JavaDocParser


def get_parser():
    parser = argparse.ArgumentParser(description='javaDoc2HTML')
    parser.add_argument('files', type=str,
                        help='path to files or directories of files')
    return parser


arg = get_parser().parse_args()
if arg.files[0] and os.path.exists(arg.files[0]):
    handler = JavaDocParser(arg.files[0])
    files = handler.get_files_from_dir()
    ConvertToHtml(files, 'temp', arg.files[0] + '/')
else:
    print('you did not specify a directory or not found')
