import unittest
from pathlib import Path

import os

from javadoc2html.convert_to_html import ConvertToHtml
from javadoc2html.javadoc_parser import JavaDocParser


class Test(unittest.TestCase):
    handler = JavaDocParser(str(Path.cwd() / 'tests' / 'resources'))
    files = handler.get_files_from_dir()
    converter = ConvertToHtml(files, 'resources', str(Path.cwd() / 'tests' / 'resources') + '/')

    def test_project_exist(self):
        for i in {'', 'Book.html', 'Product.html', 'resources.html'}:
            assert os.path.exists(str(os.getcwd())
                                  + f'/tests/resources/resources_html_doc/{i}')

    def test_to_html(self):
        assert self.files[0].to_html().startswith('<head>')
        assert self.files[0].name == 'Book.java'
        assert len(self.files[0].classes) == 1
        assert len(self.files[0].comments) == 1

    def test_javadoc_parser(self):
        assert len(self.files) == 2
        assert self.handler.dir.startswith(os.getcwd())


if __name__ == '__main__':
    unittest.main()
