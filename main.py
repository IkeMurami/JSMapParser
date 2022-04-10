import json
import os
import errno
from pathlib import Path


class JSMapParser:

    out: str

    def __init__(self, out_dirname):
        self.out = out_dirname

    def _parse(self, filename):
        print(f'Start parse file {os.path.basename(filename)}')

        with open(filename) as fileStream:
            js_map = json.loads(fileStream.read())
            try:
                for fname, fcontent in zip(js_map['sources'], js_map['sourcesContent']):
                    print(f'{fname}')
                    outname = fname.replace('webpack:///', '')
                    outname = outname.replace('../', '_1')
                    outname = outname if outname[0] == '.' else '.' + outname  # Иначе пути не правильно джойнятся (wtf?)
                    filename = os.path.join(self.out, outname)

                    if not os.path.exists(os.path.dirname(filename)):
                        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

                    with open(filename, 'w') as fileStream:
                        fileStream.write(fcontent)  # need beautifier!
                    # else:
                    #     ...  # some external js-code
            except:
                pass

        print(f'End parse file {os.path.basename(filename)}')

    def round(self, dirname):
        assert os.path.isdir(dirname), f'{dirname} is not directory!!!'

        for dr in os.listdir(dirname):
            abs_path = os.path.join(dirname, dr)
            # print(abs_path)
            if os.path.isdir(abs_path):
                print(f'Search sourcemap files in {abs_path}')
                self.round(abs_path)    # recursive search .js.map
            elif dr[-4:] == '.map':
                print(abs_path)
                self._parse(abs_path)   # parse .js.map file


if __name__ == '__main__':
    """
    base_path - путь до директории, куда сохраняем файл
    map_folder - путь до директории, в которой могут лежать *.js.map-файлы
    """
    base_path = '/path/to/out/you.site.com_vendor'
    map_folder = '/path/to/sourcemap/files'

    parser = JSMapParser(base_path)
    parser.round(map_folder)
