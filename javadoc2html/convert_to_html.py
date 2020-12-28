import os


class ConvertToHtml:
    def __init__(self, files, project_name: str, path):
        self.directory = f'{path}{project_name}_html_doc/'
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.project_name = project_name
        self.files = files
        self.create_html_files()

    def create_html_files(self):
        self.create_common_file()
        for file in self.files:
            name = file.name.replace('.java', '.html')
            with open(self.directory + name, 'w+') as f:
                f.write(file.to_html())

    def create_common_file(self):
        temp = f'<head><title>{self.project_name}</title>' \
               f'<meta http-equiv="Content-Type"' \
                    ' content="text/html; ' \
               'charset=charset=utf-8"></head><body><br>' \
               f'<h1>Project {self.project_name}</h1><br>' \
               f'<table id = "tbl"><tr><th colspan="2">Java files</th></tr>'
        for file in self.files:
            name = file.name.replace(".java", ".html")
            temp += f'<tr><td><a href="{self.directory + name}' \
                    f'">{file.name}</a></td>'
            if len(file.comments) > 0:
                temp += f'<td>{file.comments[0].description}</td></tr>'
        temp += '</table></body>'
        with open(f'{self.directory}{self.project_name}.html', 'w+',
                  encoding='utf-8') as f:
            f.write(temp)
