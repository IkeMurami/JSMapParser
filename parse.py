import json
from pathlib import Path


class JSMapParser(object):

    base_dir_path: Path

    def __init__(self, base_dir_path: Path):
        """
            base_dir_path — Куда сохраняем
        """
        self.base_dir_path = base_dir_path

    def _sourcemap_parse(self, file_path: Path):
        """
            file_path — путь до SourceMap-файла
        """

        with file_path.open(mode='r') as inp_stream:
            sourcemap_data = json.loads(inp_stream.read())

            try:
                for file_name, file_content in zip(sourcemap_data['sources'], sourcemap_data['sourcesContent']):
                    out_name = file_name.replace('webpack:///', '')
                    out_name = out_name.replace('../', '_1')
                    out_name = out_name if out_name[0] == '.' else '.' + out_name  # Иначе пути не правильно джойнятся (wtf?)
                    full_out_name = Path(self.base_dir_path, out_name)

                    full_out_name.parent.mkdir(parents=True, exist_ok=True)

                    with full_out_name.open(mode='w') as out_stream:
                        out_stream.write(file_content)

            except:
                pass

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