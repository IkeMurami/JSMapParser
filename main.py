from pathlib import Path
from const import SOURCEMAP_SRC_DIR
from download import JSMapDownloader
from parse import JSMapParser
import argparse
from enum import Enum


class Mode(Enum):
    javascript = 'js'
    sourcemap = 'map'

    def __str__(self):
        return self.value


def arg_parser():
    parser = argparse.ArgumentParser(description="""JSMapParser

        Usage:

        Download and beatify JS files, try to download and parse SourceMap files:
            python3 main.py -m js -i D:\\path\\to\\folder\\js.list -o D:\\save\\here

        Parse SourceMap files:
            python3 main.py -m map -i D:\\path\\to\\sourcemap\\folder -o D:\\save\\here
    """)

    parser.add_argument('-m', '--mode', help='Parse SourceMaps or JavaScripts', type=Mode, default=Mode.javascript, required=False)
    parser.add_argument('-i', '--input', help='Folder with loaded sourcemap files or path to list of files that should be loaded and parsed', default='js.list', required=True)

    parser.add_argument('-o', '--output', help='Where should be saved', required=True)
    
    args = parser.parse_args()

    return args


def read_file(path: Path):
    res = []
    with path.open(mode='r', encoding='utf-8') as stream:
        line = stream.readline()
        while line:
            line = line.replace('\n', '')
            res.append(line)
            line = stream.readline()

    return res


if __name__ == '__main__':

    args = arg_parser()

    path = Path(args.input)
    output = Path(args.output)
    mode = args.mode

    base_dir = path if path.is_dir() else path.parent
        
    if mode == Mode.javascript:
        if path.is_file():
            base_dir = path.parent
            sourcemap_src = Path(base_dir, SOURCEMAP_SRC_DIR)  # Где будут лежать скачанные файлы .js.map
            scripts_list_path = path
            scripts_list = read_file(scripts_list_path)

            downloader = JSMapDownloader()
            downloader.download(scripts_list, base_dir)

        else:
            ...
    
    if mode == Mode.sourcemap:
        if path.is_dir():
            base_dir = path
            sourcemap_src = path

    parser = JSMapParser(output)  # Куда восстанавливать сорцы из SourceMap файлов
    parser.parse(sourcemap_src)
