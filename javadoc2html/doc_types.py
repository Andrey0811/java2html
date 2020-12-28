import os


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


class Field:
    def __init__(self, mod, name, doc_type):
        self.mod: str = mod
        self.name: str = name
        self.type: str = doc_type

    def to_html(self):
        return f'<tr><td>{self.name}</td>' \
               f'<td>{self.mod}</td>' \
               f'<td>{self.type}</td></tr>'


class DocClass:
    def __init__(self, name: str, mod: str, parent):
        self.name: str = name
        self.mod: str = mod
        self.interface = ''
        self.parent: str = parent
        self.methods = list()
        self.fields = list()

    def add_method(self, prototype, mod, name,
                   args, return_type, comment=None):
        self.methods.append(Method(prototype, mod, name,
                                   args, return_type, comment))

    def add_field(self, mod, name, doc_type):
        self.fields.append(Field(mod, name, doc_type))

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
