import re
import sys
import shutil
from pathlib import Path

from pathlib import Path

image_files = list()
docs_files = list()
audio_files = list()
video_files = list()
folders = list()
archives = list()
others = list()
unknown = set()
extensions = set()

registered_extensions = {
    'JPEG': image_files,
    'PNG': image_files,
    'JPG': image_files,

    'TXT': docs_files,
    'PDF': docs_files,
    'XLSX': docs_files,
    'PPTX': docs_files,
    'DOCX': docs_files,
    'DOC': docs_files,

    'MP3': audio_files,
    'OGG': audio_files,
    'WAV': audio_files,
    'AMR': audio_files,

    'AVI': video_files,
    'MP4': video_files,
    'MOV': video_files,
    'MKV': video_files,

    'ZIP': archives,
    'GZ': archives,
    'TAR': archives
}

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m",
               "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('Images', 'Audio', 'Video', 'Documents', 'Archives', 'OTHER'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)

def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    extension = get_extensions(path).lower()
    #print(path.name)
    new_name = normalize(path.name.replace(f".{extension}", '')) #.suffix[1:]
    #print(new_name)

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def main():
    try:
        folder_path = Path(sys.argv[1])
    except Exception as e:
        print(e)

    print(folder_path)
    scan(folder_path)

    for file in image_files:
        handle_file(file, folder_path, "Images")

    for file in docs_files:
        handle_file(file, folder_path, "Documents")

    for file in video_files:
        handle_file(file, folder_path, "Video")

    for file in audio_files:
        handle_file(file, folder_path, "Audio")

    for file in others:
        handle_file(file, folder_path, "OTHER")

    for file in archives:
        handle_archive(file, folder_path, "Archives")

    remove_empty_folders(folder_path)

if __name__ == '__main__':
    main()