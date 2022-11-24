from pathlib import Path
from const import SOURCEMAP_SRC_DIR
from download import JSMapDownloader
from parse import JSMapParser



def readFile(path: Path):
    res = []
    with path.open(mode='r') as stream:
        line = stream.readline()
        while line:
            line = line.replace('\n', '')
            res.append(line)
            line = stream.readline()

    return res


if __name__ == '__main__':

    base_dir = Path('D:\\MyProjects\\BugBounty\\BugCrowd_Viator\\web\\travelagents\\front-src')  # Путь до рутовой директории
    sourcemap_src = Path(base_dir, SOURCEMAP_SRC_DIR)  # Где будут лежать скачанные файлы .js.map
    scripts_list_path = Path(base_dir, 'js.list')
    scripts_list = readFile(scripts_list_path)

    downloader = JSMapDownloader()
    downloader.download(scripts_list, base_dir)

    parser = JSMapParser(Path(sourcemap_src, 'src'))  # Куда восстанавливать сорцы из SourceMap файлов
    parser.parse(sourcemap_src)