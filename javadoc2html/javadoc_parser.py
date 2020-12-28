import os
import re
from os import path

from javadoc2html.doc_types import DocFile, Comment, DocClass

start_comm_big = re.compile(r'.*/\*\*.*')
finish_comm_big = re.compile(r'.*\*/.*')
class_pattern = re.compile(r'(\w+\s)?class\s(\w+)\s(.*)?.*\s?')
method_pattern = re.compile(r'^.(((?!if).)*)\((.*)\)(.*{)?$')
method_pattern_inter = re.compile(r'(.*) (.*)\((.*)\);')
interface_pattern = re.compile(r'(\w+)?.*interface.*\s(\w+).*')
field_pattern = re.compile(r'(.*) (.*);')


class JavaDocParser:
    def __init__(self, directory):
        self.dir = directory
        self.is_class = False
        self.is_interface = False
        self.is_comment = False
        self.is_method = False

    def get_files_from_dir(self):
        files = []
        for file in os.listdir(self.dir):
            if file.endswith('.java'):
                files.append(self.read_java_file(file))
        return files

    def read_java_file(self, file):
        parse_file = DocFile()
        with open(path.join(self.dir, file)) as f:
            for line in f:
                if not self.is_class and not self.is_interface:
                    if class_pattern.match(line):
                        self.is_class = True
                        doc_class = self.parse_class_name(class_pattern
                                                          .match(line))
                    elif interface_pattern.match(line):
                        self.is_interface = True
                        doc_interface = self.parse_interface_name(
                            interface_pattern.match(line))
                    elif start_comm_big.match(line) \
                            and not self.is_comment:
                        temp = line
                        comment = Comment()
                        self.is_comment = True
                    elif self.is_comment \
                            and finish_comm_big.match(line) is None:
                        temp += line
                        comment.parse_comment(line)
                    elif self.is_comment and finish_comm_big.match(line):
                        self.is_comment = False
                        parse_file.add_comments(comment)

                elif self.is_class:
                    if start_comm_big.match(line) \
                            and not self.is_comment:
                        temp = line
                        comment = Comment()
                        self.is_comment = True
                        stop = False
                    elif self.is_comment \
                            and finish_comm_big.match(line) is None \
                            and not stop:
                        temp += line
                        comment.parse_comment(line)
                    elif finish_comm_big.match(line):
                        stop = True
                    elif method_pattern.match(line) and \
                            self.is_method is False:
                        self.is_method = True
                        if self.is_comment:
                            self.parse_method_name(method_pattern
                                                   .match(line), doc_class,
                                                   comment=comment)
                            self.is_comment = False
                            stop = False
                        else:
                            self.parse_method_name(method_pattern
                                                   .match(line), doc_class)
                    elif self.is_method and '   }' in line:
                        self.is_method = False
                    elif field_pattern.match(line) and \
                            self.is_method is False:
                        self.parse_field_name(field_pattern
                                              .match(line), doc_class)
                elif self.is_interface:
                    if method_pattern_inter.match(line):
                        self.parse_interface_method_name(
                            method_pattern_inter.match(line), doc_interface)
                    elif field_pattern.match(line) and \
                            self.is_method is False:
                        self.parse_field_name(field_pattern
                                              .match(line), doc_interface)
        if self.is_class:
            parse_file.add_class(doc_class)
            self.is_class = False
        if self.is_interface:
            parse_file.add_class(doc_interface)
            self.is_interface = False
        self.is_comment = False
        self.is_method = False
        parse_file.add_name(file)
        return parse_file

    @staticmethod
    def parse_method_name(match, obj, comment=None):
        index = match.group(1).rfind(' ')
        name = match.group(1)[index:].strip()
        doc_type = match.group(1)[:index]
        args = match.group(3)
        doc_type, mod = JavaDocParser.get_mod_and_doc_type(doc_type)
        if comment is not None:
            obj.add_method(match.group(0), mod, name, args, doc_type, comment)
        else:
            obj.add_method(match.group(0), mod, name, args, doc_type)

    @staticmethod
    def get_mod_and_doc_type(doc_type):
        if doc_type.find('public') != -1:
            mod = 'public'
            doc_type = doc_type[9:]
        elif doc_type.find('private') != -1:
            mod = 'private'
            doc_type = doc_type[7:]
        elif doc_type.find('protected') != -1:
            mod = 'protected'
            doc_type = doc_type[9:]
        else:
            mod = 'package-private'
        doc_type = doc_type.strip()
        return doc_type, mod

    @staticmethod
    def parse_class_name(match):
        doc_class = DocClass(match.group(2), match.group(1), '')
        doc_property = match.group(3)
        if re.match(r'extends (.*) implements (.*)', doc_property):
            doc_class.add_parent(re.match(r'extends (.*) implements (.*)',
                                          doc_property).group(1))
            doc_class.add_interface(re.match(r'extends (.*) implements (.*)',
                                             doc_property).group(2))
        if re.match(r'extends (.*)', doc_property):
            doc_class.add_parent(re.match(r'extends (.*)',
                                          doc_property).group(1))
        if re.match(r'implements (.*)', doc_property):
            doc_class.add_interface(re.match(r'implements (.*)',
                                             doc_property).group(1))
        return doc_class

    @staticmethod
    def parse_interface_name(match):
        return DocClass(match.group(2), match.group(1), 'Interface')

    @staticmethod
    def parse_field_name(match, obj):
        name = match.group(2).split(' ').pop()
        doc_type = match.group(1).strip()
        doc_type, mod = JavaDocParser.get_mod_and_doc_type(doc_type)
        if '=' in doc_type:
            doc_type = doc_type.split('=')[0].strip().split(' ')
            name = doc_type[len(doc_type) - 1].strip()
            doc_type = doc_type[0].strip()
        obj.add_field(mod, name, doc_type)

    @staticmethod
    def parse_interface_method_name(match, doc_interface):
        doc_type = match.group(1)
        name = match.group(2)
        args = match.group(3)
        doc_type, mod = JavaDocParser.get_mod_and_doc_type(doc_type)
        doc_interface.add_method(match.group(0), mod, name, args, doc_type)
