from threading import Thread, Lock
locks = {}
def get_file_content(file_path):
    file = open(file_path, 'r')
    file_content = file.read()
    file.close()
    return file_content


def write_to_file(content, file_path):
    global locks
    if file_path in locks:
        locks[file_path].acquire()
    else:
        locks[file_path] = Lock()
        locks[file_path].acquire()
    f = open(file_path, "w", encoding="utf-8")
    f.write(content)
    f.close()
    locks[file_path].release()
