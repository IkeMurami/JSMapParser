# Download js.map files
import jsbeautifier
from pathlib import Path
import requests
from typing import List
import urllib3

from const import JS_SRC_DIR, SOURCEMAP_SRC_DIR

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JSMapDownloader(object):

    IS_SOURCEMAP = 1
    IS_JS = 0
    IS_UNKNOWN = -1

    def _download(self, url: str):
        """
            Забирает файл по ссылке (js или sourcemap)
            Возвращает имя будущего файла и контент

            url: адрес файла
        """
        parsed_url = requests.utils.urlparse(url)
        path = parsed_url.path
        file_name = Path(path).name

        resp = requests.get(url)

        return (file_name, resp.content.decode('utf-8')) if resp.status_code == 200 else (file_name, '')
        

    def _check(self, url: str):
        """
            Пробует сходить по расширению url + .map
            Возвращает контент оригинального js-файла или sourcemap-файла
        """
        parsed_url = requests.utils.urlparse(url)
        path = parsed_url.path

        sourcemap_url = url.replace(path, f'{path}.map')

        resp = requests.head(sourcemap_url)
        target_url, typeof_data = (sourcemap_url, self.IS_SOURCEMAP) if resp.status_code == 200 else (url, self.IS_JS)

        file_name, content = self._download(target_url)

        return (file_name, content, typeof_data)

    def download(self, urls: List[str], base_dir: Path):
        """
            проходит по списку url и складывает результат в base_dir
        """

        js_base_dir = Path(base_dir, JS_SRC_DIR)
        map_base_dir = Path(base_dir, SOURCEMAP_SRC_DIR)

        js_base_dir.mkdir(exist_ok=True)
        map_base_dir.mkdir(exist_ok=True)

        for url in urls:
            file_name, content, typeof_data = self._check(url)
            if typeof_data == self.IS_JS :
                content = jsbeautifier.beautify(content)
                with Path(js_base_dir, file_name).open(mode='w', encoding='utf-8') as out_stream:
                    out_stream.write(content)

            if typeof_data == self.IS_SOURCEMAP:
                with Path(map_base_dir, file_name).open(mode='w', encoding='utf-8') as out_stream:
                    out_stream.write(content)

