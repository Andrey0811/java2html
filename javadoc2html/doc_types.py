import os
import re
from re import Pattern

start_comm_big = re.compile(r'.*/\*\*.*')
finish_comm_big = re.compile(r'.*\*/.*')
class_pattern = re.compile(r'(\w+\s)?class\s(\w+)\s(.*)?.*\s?')
method_pattern = re.compile(r'^.(((?!if).)*)\((.*)\)(.*{)?$')
method_pattern_inter = re.compile(r'(.*) (.*)\((.*)\);')
interface_pattern = re.compile(r'(\w+)?.*interface.*\s(\w+).*')
field_pattern = re.compile(r'(.*) (.*);')


class Comment:
    def __init__(self):
        self.author = ''
        self.version = ''
        self.deprecated = ''
        self.since = ''
        self.see = ''
        self.throws = ''
        self.exception = ''
        self.param = list()
        self.returns = ''
        self.description = ''
        self.link = list()

    def parse_comment(self, comm):
        if comm.find('@author') != -1:
            self.author = comm.split('@author')[1].strip()
        elif comm.find('@version') != -1:
            self.version = comm.split('@version')[1].strip()
        elif comm.find('@since') != -1:
            self.since = comm.split('@since')[1].strip()
        elif comm.find('@deprecated') != -1:
            self.deprecated = comm.split('@deprecated')[1].strip()
        elif comm.find('@see') != -1:
            self.see = comm.split('@see')[1].strip()
        elif comm.find('@throws') != -1:
            self.throws = comm.split('@throws')[1].strip()
        elif comm.find('@exception') != -1:
            self.exception = comm.split('@exception')[1].strip()
        elif comm.find('@param') != -1:
            self.param.append(comm.split('@param')[1].strip())
        elif comm.find('@return') != -1:
            self.returns = comm.split('@return')[1].strip()
        elif comm.find('@link') != -1:
            try:
                self.link.append(comm
                                 .split('@link')[0]
                                 .replace('* ', '').strip())
                self.link.append(comm
                                 .split('@link')[1].strip())
            except Exception as e:
                print(e)
        else:
            self.description = comm.replace('* ', '').strip()

    def full_comment_to_html(self):
        temp = ''
        if self.author:
            temp += f'<p class = \'left\'>Author: {self.author}</p>'
        if self.version:
            temp += f'<p class = \'left\'>Version: {self.version}</p>'
        if self.since:
            temp += f'<p class = \'left\'>' \
                    f'Available since version{self.since}</p>'
        if self.deprecated:
            temp += f'<p class = \'left\'>' \
                    f'Deprecated {str.lower(self.deprecated)}</p>'
        if self.see:
            temp += f'<p class = \'left\'>Also see: ' \
                    f'<a href=\"{os.path.join(self.see + ".html")}\"' \
                    f'>{self.see}</a></p>'
        if self.description:
            temp += f'<p class = \'left\'>' \
                    f'Description: {self.description}</p>'
        return temp

    def method_comment_to_html(self):
        temp = ''
        if self.description:
            temp += f'<p class = \'left\'>{self.description}</p>'
        if self.param:
            temp += "<p class = 'left'><i>Parameters:</i></p>"
            for param in self.param:
                temp += f'<p class = \'left\'>{param}</p>'
        if self.returns:
            temp += f'<p class = \'left\'><i>' \
                    f'Returns</i> {self.returns}</p>'
        return temp


class Method:
    def __init__(self, prototype, mod, name, args, return_type, comment):
        self.prototype: str = prototype
        self.mod: str = mod
        self.name: str = name
        self.args: str = args
        self.return_type: str = return_type
        self.comment: Comment = comment

    def to_html(self):
        name = self.name
        temp = f'<tr><td>{name}</td>' \
               f'<td>{self.prototype}</td>'
        if self.comment:
            if self.comment.description:
                temp += f'<td>{self.comment.description}</td>'
            else:
                temp += f'<td>Returns {self.comment.returns}</td>'
        else:
            temp += '<td>None</td>'
        temp += '</tr>'
        return temp

    def method_details_to_html(self):
        temp = f'<h4 class = \'details\'><i>method</i> {self.name} :' \
               f'</h4><div class = \'detblock\'>' \
               f'<p class = \'left\'>{self.prototype}</p>' \
               f'<p class = \'left\'>' \
               f'<i>Access modifier:</i> {self.mod}</p>'
        if self.return_type.strip() != 'void':
            temp += f'<p class = \'left\'><i>Returns:</i> ' \
                    f'{self.return_type}</p>'
        else:
            temp += '<p class = \'left\'><i>Returns nothing</i></p>'
        if self.comment is not None:
            temp += self.comment.method_comment_to_html()
        temp += '</div>'
        return temp

    @classmethod
    def parse_method_name(cls, line: str,
                          pattern: Pattern = method_pattern,
                          comment: Comment = None):
        match = pattern.match(line)
        index = match.group(1).rfind(' ')
        name = match.group(1)[index:].strip()
        doc_type = match.group(1)[:index]
        args = match.group(3)
        doc_type, mod = DocFile.get_mod_and_doc_type(doc_type)

        return cls(match.group(0), mod, name, args, doc_type, comment)

    @classmethod
    def parse_interface_method_name(cls, line: str,
                                    pattern: Pattern = method_pattern_inter):
        match = pattern.match(line)
        doc_type = match.group(1)
        name = match.group(2)
        args = match.group(3)
        doc_type, mod = DocFile.get_mod_and_doc_type(doc_type)
        return cls(match.group(0), mod, name, args, doc_type, None)


class Field:
    def __init__(self, mod, name, doc_type):
        self.mod: str = mod
        self.name: str = name
        self.type: str = doc_type

    def to_html(self):
        return f'<tr><td>{self.name}</td>' \
               f'<td>{self.mod}</td>' \
               f'<td>{self.type}</td></tr>'

    @classmethod
    def parse_field_name(cls, line: str,
                         pattern: Pattern = field_pattern):
        match = pattern.match(line)
        name = match.group(2).split(' ').pop()
        doc_type = match.group(1).strip()
        doc_type, mod = DocFile.get_mod_and_doc_type(doc_type)
        if '=' in doc_type:
            doc_type = doc_type.split('=')[0].strip().split(' ')
            name = doc_type[len(doc_type) - 1].strip()
            doc_type = doc_type[0].strip()
        return cls(mod, name, doc_type)


class DocClass:
    def __init__(self, name: str, mod: str, parent):
        self.name: str = name
        self.mod: str = mod
        self.interface = ''
        self.parent: str = parent
        self.methods = list()
        self.fields = list()

    # def add_method(self, prototype, mod, name,
    #                args, return_type, comment=None):
    #     self.methods.append(Method(prototype, mod, name,
    #                                args, return_type, comment))

    def add_method(self, method: Method):
        self.methods.append(method)

    # def add_field(self, mod, name, doc_type):
    #     self.fields.append(Field(mod, name, doc_type))

    def add_field(self, field):
        self.fields.append(field)

    def add_interface(self, row):
        self.interface = row

    def add_parent(self, row):
        self.parent = row

    def to_html(self):
        type_class = 'Class' if self.parent != 'Interface' else self.parent
        temp = f'\r<p class = "left">{type_class} name: {self.name}</br>'
        temp += f'Access modifier: {self.mod}</br>'
        if self.parent and self.parent != 'Interface':
            temp += f'Parent: {self.parent}<br>'
        if self.interface:
            temp += f'Implements interface: {self.interface}<br>'
        temp += '</p><ul>'
        temp += f'<h3>{type_class} {self.name} contains fields: </h3>'
        field_html = self.fields_to_html()
        met_html = self.methods_to_html()
        temp += f'{field_html}<br><br><h3>{type_class} {self.name} ' \
                f'contains methods: </h3>{met_html}</div>'
        if self.parent and self.parent != 'Interface':
            temp += self.create_methods_details
        return temp

    def methods_to_html(self):
        temp = '<table id = "tbl"><tr><th>Method name</th>' \
               '<th>Prototype</th> <th>Description</th></tr>'
        for method in self.methods:
            temp += method.to_html()
        temp += '</table>'
        return temp

    def fields_to_html(self):
        temp = '<table id = "tbl"><tr> <th>Field name</th>' \
               '<th>Modifier</th><th>Type</th></tr>'
        for field in self.fields:
            temp += field.to_html()
        temp += '</table>'
        return temp

    def create_methods_details(self):
        temp = '<h3>Method Details:</h3><br></br>'
        for method in self.methods:
            temp += method.method_details_to_html()
        return temp


class DocFile:
    def __init__(self):
        self.classes = list()
        self.comments = list()
        self.name = ''
        self.description = ''

    def add_class(self, doc_class):
        self.classes.append(doc_class)

    def add_comments(self, comment):
        self.comments.append(comment)

    def add_name(self, name):
        self.name = name

    def to_html(self):
        temp = f'<head><title>{self.name}</title>' \
               f'<meta http-equiv="Content-Type"' \
                    ' content="text/html; charset=charset=utf-8"></head><body>'
        temp += f'<h2> Documentation : {self.name}</h1><br>'

        for comment in self.comments:
            temp += comment.full_comment_to_html()

        temp += f'<br><br><h4 class = \'left\'>{self.name} ' \
                f'contains class/interface:</h3>'

        for doc_class in self.classes:
            temp += doc_class.to_html()
        return temp

    @classmethod
    def read_java_file(cls, file_path):
        is_class = False
        is_interface = False
        is_comment = False
        is_method = False
        parse_file = DocFile()
        with open(file_path) as f:
            for line in f:
                if not is_class and not is_interface:
                    if class_pattern.match(line):
                        is_class = True
                        doc_class = cls.parse_class_name(class_pattern
                                                         .match(line))
                    elif interface_pattern.match(line):
                        is_interface = True
                        doc_interface = cls.parse_interface_name(
                            interface_pattern.match(line))
                    elif start_comm_big.match(line) \
                            and not is_comment:
                        temp = line
                        comment = Comment()
                        is_comment = True
                    elif is_comment \
                            and finish_comm_big.match(line) is None:
                        temp += line
                        comment.parse_comment(line)
                    elif is_comment and finish_comm_big.match(line):
                        is_comment = False
                        parse_file.add_comments(comment)

                elif is_class:
                    if start_comm_big.match(line) \
                            and not is_comment:
                        temp = line
                        comment = Comment()
                        is_comment = True
                        stop = False
                    elif is_comment \
                            and finish_comm_big.match(line) is None \
                            and not stop:
                        temp += line
                        comment.parse_comment(line)
                    elif finish_comm_big.match(line):
                        stop = True
                    elif method_pattern.match(line) and \
                            is_method is False:
                        is_method = True
                        if is_comment:
                            doc_class.add_method(Method.parse_method_name(line, comment=comment))
                            is_comment = False
                            stop = False
                        else:
                            doc_class.add_method(Method.parse_method_name(line))
                    elif is_method and '   }' in line:
                        is_method = False
                    elif field_pattern.match(line) and \
                            is_method is False:
                        doc_class.add_field(Field.parse_field_name(line))
                elif is_interface:
                    if method_pattern_inter.match(line):
                        doc_interface.add_method(Method.parse_interface_method_name(line))
                    elif field_pattern.match(line) and \
                            is_method is False:
                        doc_interface.add_field(Field.parse_field_name(line))
        if is_class:
            parse_file.add_class(doc_class)
        if is_interface:
            parse_file.add_class(doc_interface)

        parse_file.add_name(file_path)
        return parse_file

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
