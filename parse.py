import json
from pathlib import Path
import random
import string

from const import LOG_PATH

log_file = Path(LOG_PATH).open(mode='w')

class JSMapParser(object):

    base_dir_path: Path

    def __init__(self, base_dir_path: Path):
        """
            base_dir_path — Куда сохраняем
        """
        self.base_dir_path = base_dir_path

    def _correct_filename(self, file_path: Path):
        """
            Если файл уже существует, добавляем 10 цифр к имени
        """
        if file_path.exists():
            file_name = file_path.name
            ext = file_name.split('.')[-1]
            file_name = '.'.join(file_name.split('.')[:-1])

            letters = string.digits
            r = ''.join(random.choice(letters) for i in range(10))

            file_path = Path(file_path.parent, f'{file_name}.{r}.{ext}')

        return file_path

    def _sourcemap_parse(self, file_path: Path):
        """
            file_path — путь до SourceMap-файла
        """

        with file_path.open(mode='r', encoding='utf-8') as inp_stream:
            sourcemap_data = json.loads(inp_stream.read())

            if 'sources' not in sourcemap_data or 'sourcesContent' not in sourcemap_data:
                print(f'Sourcemap {file_path} is empty', file=log_file)
                return

            for file_name, file_content in zip(sourcemap_data['sources'], sourcemap_data['sourcesContent']):
                
                out_name = file_name.replace('webpack:///', '')
                out_name = out_name.replace('../', '_1')
                out_name = out_name if out_name[0] == '.' else '.' + out_name  # Иначе пути не правильно джойнятся (wtf?)
                out_name = out_name.split('?')[0]
                
                # it's exception
                if 'i18n lazy' in out_name:
                    continue
                
                full_out_name = Path(self.base_dir_path, out_name)

                # Есть предположение, что могут быть одинаковые файлы в SourceMap файлах => они будут переписывать друг друга и мы потеряем кусочек кода
                # full_out_name = self._correct_filename(full_out_name)

                try:
                    full_out_name.parent.mkdir(parents=True, exist_ok=True)

                    with full_out_name.open(mode='w', encoding='utf-8') as out_stream:
                        out_stream.write(file_content)
                except FileNotFoundError:
                    print(f'Something wrong in sourcemap file: {file_path}, I couldnot save: {full_out_name}', file=log_file)

               

    def parse(self, sourcemap_dir_path: Path):
        """
            sourcemap_dir_path — путь до директории с SourceMap-файлами
        """
        assert sourcemap_dir_path.is_dir(), f'{sourcemap_dir_path} is not directory!!!'

        all_objects = sourcemap_dir_path.glob('**/*')           # 1. Собираем все дочерние файлы и директории
        [
            self._sourcemap_parse(path)                         # 3. Парсим каждый файл
            for path in all_objects 
            if path.is_file() and path.name[-4:] == '.map'      # 2. Находим все файлы, оканчивающиеся на .map
        ]  # parse .js.map files