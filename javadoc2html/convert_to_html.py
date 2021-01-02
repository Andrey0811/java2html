from pathlib import Path


class ConvertToHtml:
    def __init__(self, files: list, project_name: str, path: str):
        self.directory = Path(f'{path}{project_name}_html_doc')
        if not self.directory.exists():
            self.directory.mkdir()
        self.project_name = project_name
        self.files = files
        self.create_html_files()

    def create_html_files(self):
        with (self.directory / f'{self.project_name}.html') \
                .open('w+', encoding='utf-8') as f:
            f.write(self.get_common_file())
        for file in self.files:
            name = file.name.replace('.java', '.html')
            with (self.directory / name)\
                    .open('w+', encoding='utf-8') as f:
                f.write(file.to_html())

    def get_common_file(self):
        temp = [f'<head><title>{self.project_name}</title>',
                '<meta http-equiv="Content-Type" ',
                'content="text/html; charset=utf-8">',
                '</head><body><br>',
                f'<h1>Project {self.project_name}</h1><br>',
                '<table id = "tbl"><tr><th colspan="2">Java files</th></tr>']
        for file in self.files:
            name = file.name.replace('.java', '.html')
            temp.append(f'<tr><td><a href="{name}')
            temp.append(f'">{file.name}</a></td>')
            if len(file.comments) > 0:
                temp.append(f'<td>{file.comments[0].description}</td></tr>')
        temp.append('</table></body>')
        return ''.join(temp)
