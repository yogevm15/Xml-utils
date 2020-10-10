def get_file_content(file_path):
    file = open(file_path, 'r')
    file_content = file.read()
    file.close()
    return file_content


def write_to_file(content, file_path):
    f = open(file_path, "w")
    f.write(content)
    f.close()
