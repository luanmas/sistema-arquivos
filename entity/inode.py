import uuid
from typing import List, Dict, Optional

class Inode:
    def __init__(self, name: str, is_dir: bool, parent: Optional['Inode'] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.data_blocks = []
        self.entries = {} if is_dir else None
        self.parent = parent