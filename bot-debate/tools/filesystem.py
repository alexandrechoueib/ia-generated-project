def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def write_file(path:str, content : str) -> str:
    with open(path,"a",encoding="utf-8") as f:
        file.write(content)



