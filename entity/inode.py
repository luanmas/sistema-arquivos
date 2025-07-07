import uuid

class Inode:
    def __init__(self, name: str, is_dir: bool):
        self.id = str(uuid.uuid4())
        self.name = name 
        self.is_dir = is_dir
        self.size = 0 
        self.data_blocks = []
        self.entries = {} if is_dir else None