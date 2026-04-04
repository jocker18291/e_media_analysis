PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def readFile(path_to_file):
    with open(path_to_file, 'rb') as file:
        file_beginning = file.read(8)
        return file_beginning == PNG_SIGNATURE
