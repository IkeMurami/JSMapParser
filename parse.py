import json
from pathlib import Path
from typing import List
import random
import string
from pydantic import BaseModel, field_validator

from const import LOG_PATH

log_file = Path(LOG_PATH).open(mode='a')


class Source(BaseModel):
    path: str
    content: str | None = ''


class SourceMap(BaseModel):
    path: Path
    sources: List[Source]


class JSMapParser(object):

    base_dir_path: Path
    WEBPACK_PREFIX = 'webpack://'

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

    def _save(self, base: Path, sourcemaps: List[SourceMap]):
        sources: List[Source] = list()
        for sm in sourcemaps:
            sources.extend(sm.sources)

        rootProjPath = '/'.join(
            list(
                map(
                    lambda x: str(x),
                    range(
                        max(map(lambda p: p.path.count('../'), sources))
                    )
                )
            )
        )
        rootProjPath = base.joinpath(rootProjPath)
        rootProjPath.mkdir(parents=True, exist_ok=True)
        sources.sort(key=lambda x: len(x.path), reverse=True)
        # print('sorted', sources)
        for source in sources:
            p = source.path[len(self.WEBPACK_PREFIX):] if source.path.startswith(self.WEBPACK_PREFIX) else source.path
            p = p[1:] if p.startswith('/') else p  # '/' в начале ломает join: Path('/test/1/2/3', '/test2/./test1') -> /test2/test1
            p = p.split('?')[0]  # Убираем то, что после ?
            p = rootProjPath.joinpath(p).resolve()

            print('Path', p)

            p.parent.mkdir(parents=True, exist_ok=True)

            if p.is_dir():
                letters = string.digits
                r = ''.join(random.choice(letters) for i in range(6))
                p = p.joinpath(r)

            with p.open(mode='w') as out_stream:
                out_stream.write(source.content if source.content else '')

    def _parse(self, path: Path) -> SourceMap:
        with path.open(mode='r', encoding='utf-8') as inp_stream:
            sourcemap_data = json.loads(inp_stream.read())

            if 'sources' not in sourcemap_data or 'sourcesContent' not in sourcemap_data:
                return SourceMap(path=path, sources=list())

            return SourceMap(
                path=path,
                sources=list(
                    map(
                        lambda pair: Source(
                            path=pair[0],
                            content=pair[1],
                        ),
                        zip(sourcemap_data['sources'], sourcemap_data['sourcesContent'])
                    )
                )
            )

    def parse(self, sourcemap_dir_path: Path):
        """
            sourcemap_dir_path — путь до директории с SourceMap-файлами
        """
        assert sourcemap_dir_path.is_dir(), f'{sourcemap_dir_path} is not directory!!!'

        all_objects = sourcemap_dir_path.glob('**/*')           # 1. Собираем все дочерние файлы и директории
        paths = [path for path in all_objects if path.is_file() and path.name[-4:] == '.map']  # 2. Находим все файлы, оканчивающиеся на .map
        parsed = map(lambda p: self._parse(p), paths)   # 3. Парсим каждый файл
        self._save(self.base_dir_path, parsed)

