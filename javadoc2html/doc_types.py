import os
import re
from dataclasses import dataclass, field
from re import Pattern
from typing import List

start_comm_big = re.compile(r'.*/\*\*.*')
finish_comm_big = re.compile(r'.*\*/.*')
class_pattern = re.compile(r'(\w+\s)?class\s(\w+)\s(.*)?.*\s?')
method_pattern = re.compile(r'^.(((?!if).)*)\((.*)\)(.*{)?$')
method_pattern_interface = re.compile(r'(.*) (.*)\((.*)\);')
interface_pattern = re.compile(r'(\w+)?.*interface.*\s(\w+).*')
field_pattern = re.compile(r'(.*) (.*);')


@dataclass
class Comment:
    author: str = ''
    version: str = ''
    deprecated: str = ''
    since: str = ''
    see: str = ''
    throws: str = ''
    exception: str = ''
    param: list = field(default_factory=list)
    returns: str = ''
    description: str = ''
    link: list = field(default_factory=list)

    def parse_comment_along_line(self, line):
        if line.find('@author') != -1:
            self.author = line.split('@author')[1].strip()
        elif line.find('@version') != -1:
            self.version = line.split('@version')[1].strip()
        elif line.find('@since') != -1:
            self.since = line.split('@since')[1].strip()
        elif line.find('@deprecated') != -1:
            self.deprecated = line.split('@deprecated')[1].strip()
        elif line.find('@see') != -1:
            self.see = line.split('@see')[1].strip()
        elif line.find('@throws') != -1:
            self.throws = line.split('@throws')[1].strip()
        elif line.find('@exception') != -1:
            self.exception = line.split('@exception')[1].strip()
        elif line.find('@param') != -1:
            self.param.append(line.split('@param')[1].strip())
        elif line.find('@return') != -1:
            self.returns = line.split('@return')[1].strip()
        elif line.find('@link') != -1:
            self.link.append(line
                             .split('@link')[0]
                             .replace('* ', '').strip())
            self.link.append(line
                             .split('@link')[1].strip())
        else:
            self.description += line.replace('* ', '').strip() + '\n'

    def full_comment_to_html(self):
        temp = []
        if self.author:
            temp.append(f'<p class = \'left\'>Author: {self.author}</p>')
        if self.version:
            temp.append(f'<p class = \'left\'>Version: {self.version}</p>')
        if self.since:
            temp.append(f'<p class = \'left\'>'
                        f'Available since version{self.since}</p>')
        if self.deprecated:
            temp.append(f'<p class = \'left\'>'
                        f'Deprecated {str.lower(self.deprecated)}</p>')
        if self.see:
            temp.append(f'<p class = \'left\'>Also see: '
                        f'<a href=\"{os.path.join(self.see + ".html")}\"'
                        f'>{self.see}</a></p>')
        if self.description:
            temp.append(f'<p class = \'left\'>'
                        f'Description: {self.description}</p>')
        return ''.join(temp)

    def method_comment_to_html(self):
        temp = []
        if self.description:
            temp.append(f'<p class = \'left\'>{self.description}</p>')
        if self.param:
            temp.append('<p class = \'left\'><i>Parameters:</i></p>')
            for param in self.param:
                temp.append(f'<p class = \'left\'>{param}</p>')
        if self.returns:
            temp.append(f'<p class = \'left\'><i>'
                        f'Returns</i> {self.returns}</p>')
        return ''.join(temp)


@dataclass
class Method:
    prototype: str
    mod: str
    name: str
    args: str
    return_type: str
    comment: Comment

    def to_html(self):
        name = self.name
        temp = [f'<tr><td>{name}</td>'
                f'<td>{self.prototype}</td>']
        if self.comment:
            if self.comment.description:
                temp.append(f'<td>{self.comment.description}</td>')
            else:
                temp.append(f'<td>Returns {self.comment.returns}</td>')
        else:
            temp.append('<td>None</td>')
        temp.append('</tr>')
        return ''.join(temp)

    def method_details_to_html(self):
        temp = [f'<h4 class = \'details\'><i>method</i> {self.name} :'
                f'</h4><div class = \'detblock\'>'
                f'<p class = \'left\'>{self.prototype}</p>'
                f'<p class = \'left\'>'
                f'<i>Access modifier:</i> {self.mod}</p>']
        if self.return_type.strip() != 'void':
            temp.append(f'<p class = \'left\'><i>Returns:</i> '
                        f'{self.return_type}</p>')
        else:
            temp.append('<p class = \'left\'><i>Returns nothing</i></p>')
        if self.comment:
            temp.append(self.comment.method_comment_to_html())
        temp.append('</div>')
        return ''.join(temp)

    @classmethod
    def parse_method_name(cls, line: str,
                          pattern: Pattern = method_pattern,
                          comment: Comment = None,
                          is_interface=False):
        match = pattern.match(line)
        if not is_interface:
            index = match.group(1).rfind(' ')
            name = match.group(1)[index:].strip()
            doc_type = match.group(1)[:index]
        else:
            doc_type = match.group(1)
            name = match.group(2)
        args = match.group(3)
        doc_type, mod = cls.get_mod_and_doc_type(doc_type)

        return cls(match.group(0), mod, name, args, doc_type, comment)

    @staticmethod
    def get_mod_and_doc_type(line):
        mod = 'package-private'
        doc_type = ''
        for item in {'public', 'private', 'protected', 'strictfp'}:
            if line.find(item) != -1:
                mod = item
                doc_type = line[len(item):]
                break

        return doc_type.strip(), mod


@dataclass
class Field:
    name: str
    mod: str
    type: str

    def to_html(self):
        return f'<tr><td>{self.name}</td>' \
               f'<td>{self.mod}</td>' \
               f'<td>{self.type}</td></tr>'

    @classmethod
    def parse_field_name(cls, line: str,
                         pattern: Pattern = field_pattern):
        match = pattern.match(line)
        name = match.group(2).split(' ').pop()
        doc_type, mod = Method.get_mod_and_doc_type(match.group(1).strip())
        if '=' in doc_type:
            doc_type = doc_type.split('=')[0].strip().split(' ')
            name = doc_type[len(doc_type) - 1].strip()
            doc_type = doc_type[0].strip()
        return cls(name, mod, doc_type)


@dataclass
class DocClass:
    name: str
    mod: str
    parent: str
    interface: str
    methods: List[Method] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    is_comment = False
    stop = False
    is_method = False
    temp_comment: Comment = None

    def to_html(self):
        type_class = 'Class' if self.parent != 'Interface' else self.parent
        temp = [f'\r<p class = "left">{type_class} name: {self.name}</br>',
                f'Access modifier: {self.mod}</br>']
        if self.parent and self.parent != 'Interface':
            temp.append(f'Parent: {self.parent}<br>')
        if self.interface:
            temp.append(f'Implements interface: {self.interface}<br>')
        temp.append('</p><ul>')
        temp.append(f'<h3>{type_class} {self.name} contains fields: </h3>')
        field_html = self.fields_to_html()
        met_html = self.methods_to_html()
        temp.append(f'{field_html}<br><br><h3>{type_class} {self.name} '
                    f'contains methods: </h3>{met_html}</div>')
        if self.parent and self.parent != 'Interface':
            temp.append(self.create_methods_details)
        return ''.join(temp)

    def methods_to_html(self):
        temp = ['<table id = "tbl"><tr><th>Method name</th>'
                '<th>Prototype</th> <th>Description</th></tr>']
        for method in self.methods:
            temp.append(method.to_html())
        temp.append('</table>')
        return ''.join(temp)

    def fields_to_html(self):
        temp = ['<table id = "tbl"><tr> <th>Field name</th>'
                '<th>Modifier</th><th>Type</th></tr>']
        for item in self.fields:
            temp.append(item.to_html())
        temp.append('</table>')
        return ''.join(temp)

    def create_methods_details(self):
        temp = ['<h3>Method Details:</h3><br></br>']
        for method in self.methods:
            temp.append(method.method_details_to_html())
        return ''.join(temp)

    @classmethod
    def parse_class_name(cls, line: str):
        match = class_pattern.match(line)
        parent, interface = '', ''
        parent_and_interface = re.match(
            r'extends (.*) implements (.*)', match.group(3))
        if parent_and_interface:
            parent = parent_and_interface.group(1)
            interface = parent_and_interface.group(2)
        else:
            extends = re.match(r'extends (.*)', match.group(3))
            implements = re.match(r'implements (.*)', match.group(3))
            if extends:
                parent = extends.group(1)
            if implements:
                interface = implements.group(1)
        return cls(match.group(2), match.group(1), parent, interface)

    @classmethod
    def parse_interface_name(cls, line: str):
        match = interface_pattern.match(line)
        return cls(match.group(2), match.group(1), 'Interface', '')

    def parse_class_along_line(self, line: str):
        if start_comm_big.match(line) and not self.is_comment:
            self.temp_comment = Comment()
            self.is_comment = True

        elif (self.is_comment and
              not finish_comm_big.match(line) and
              not self.stop):
            self.temp_comment.parse_comment_along_line(line)

        elif finish_comm_big.match(line):
            self.stop = True

        elif method_pattern.match(line) and not self.is_method:
            self.is_method = True
            self.methods.append(
                Method.parse_method_name(
                    line,
                    comment=self.temp_comment))
            self.is_comment, self.stop = False, False
            self.temp_comment = None
        elif self.is_method and '}' in line:
            self.is_method = False
        elif field_pattern.match(line) and not self.is_method:
            self.fields.append(Field.parse_field_name(line))

    def parse_interface_along_line(self, line):
        if method_pattern_interface.match(line):
            self.methods.append(
                Method.parse_method_name(
                    line,
                    pattern=method_pattern_interface,
                    is_interface=True))
        elif field_pattern.match(line) and not self.is_method:
            self.fields.append(Field.parse_field_name(line))


@dataclass
class DocFile:
    name: str
    classes: List[DocClass]
    comments: List[Comment]

    def to_html(self):
        temp = [f'<head><title>{self.name}</title>'
                f'<meta http-equiv="Content-Type"'
                ' content="text/html; charset=utf-8"></head><body>',
                f'<h2> Documentation : {self.name}</h1><br>']
        for comment in self.comments:
            temp.append(comment.full_comment_to_html())
        temp.append(f'<br><br><h4 class = \'left\'>{self.name} '
                    f'contains class/interface:</h3>')
        for doc_class in self.classes:
            temp.append(doc_class.to_html())
        return ''.join(temp)

    @classmethod
    def parse_file(cls, file_path: str):
        is_class, is_interface, is_comment = False, False, False
        classes, interfaces, comments = [], [], []

        with open(file_path) as lines:
            for line in lines:
                if not is_class and not is_interface:
                    if class_pattern.match(line):
                        is_class = True
                        classes.append(DocClass.parse_class_name(line))

                    elif interface_pattern.match(line):
                        is_interface = True
                        interfaces.append(DocClass.parse_interface_name(line))

                    elif start_comm_big.match(line) and not is_comment:
                        comment = Comment()
                        is_comment = True

                    elif is_comment and not finish_comm_big.match(line):
                        comment.parse_comment_along_line(line)

                    elif is_comment and finish_comm_big.match(line):
                        is_comment = False
                        comments.append(comment)

                elif is_class:
                    classes[-1].parse_class_along_line(line)
                elif is_interface:
                    interfaces[-1].parse_interface_along_line(line)

        name = file_path.split('/')[-1]
        return cls(name, classes + interfaces, comments)
