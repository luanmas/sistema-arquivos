from typing import Dict, Optional
from uuid import uuid4

BLOCK_SIZE = 8
TOTAL_BLOCKS = 10

class LinkedFile:
    def __init__(self, name: str):
        self.id = str(uuid4())
        self.name = name
        self.is_dir = False
        self.size = 0
        self.start_block: Optional[int] = None

class LinkedDirectory:
    def __init__(self, name: str):
        self.id = str(uuid4())
        self.name = name
        self.is_dir = True
        self.entries: Dict[str, str] = {}  # nome -> id

class LinkedFileSystem:
    def __init__(self):
        self.inodes: Dict[str, object] = {}  # pode ser LinkedFile ou LinkedDirectory
        self.root = LinkedDirectory("/")
        self.inodes[self.root.id] = self.root
        self.current_dir = self.root
        self.current_path = "/"
        self.disk = [{'data': '', 'next': None} for _ in range(TOTAL_BLOCKS)]
        self.free_blocks = list(range(TOTAL_BLOCKS))

    def create_file(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        f = LinkedFile(name)
        self.inodes[f.id] = f
        self.current_dir.entries[name] = f.id
        print(f"Arquivo '{name}' criado com sucesso.")

    def create_dir(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        d = LinkedDirectory(name)
        self.inodes[d.id] = d
        self.current_dir.entries[name] = d.id
        print(f"Diretório '{name}' criado com sucesso.")

    def write_file(self, name: str, data: str):
        if name not in self.current_dir.entries:
            self.create_file(name)
        inode_id = self.current_dir.entries[name]
        file = self.inodes[inode_id]
        self._free_blocks(file.start_block)

        num_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if len(self.free_blocks) < num_blocks:
            print("Erro: Espaço insuficiente em disco.")
            return

        blocks = [self.free_blocks.pop(0) for _ in range(num_blocks)]
        file.start_block = blocks[0]

        for i, block in enumerate(blocks):
            inicio = i * BLOCK_SIZE
            fim = inicio + BLOCK_SIZE
            self.disk[block]['data'] = data[inicio:fim]
            self.disk[block]['next'] = blocks[i+1] if i+1 < len(blocks) else None

        file.size = len(data)
        print(f"Dados escritos em '{name}' ({file.size} bytes) com alocação encadeada.")

    def read_file(self, name: str):
        if name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{name}' não encontrado.")
            return
        inode_id = self.current_dir.entries[name]
        file = self.inodes[inode_id]
        if file.is_dir:
            print(f"Erro: '{name}' é um diretório.")
            return

        data = ""
        idx = file.start_block
        while idx is not None:
            data += self.disk[idx]['data']
            idx = self.disk[idx]['next']
        print(f"Conteúdo de '{name}' ({file.size} bytes):")
        print(data[:file.size])

    def _free_blocks(self, start_block: Optional[int]):
        idx = start_block
        while idx is not None:
            next_idx = self.disk[idx]['next']
            self.disk[idx] = {'data': '', 'next': None}
            self.free_blocks.append(idx)
            idx = next_idx

    def ls(self):
        if not self.current_dir.entries:
            print("Diretório vazio.")
            return
        for name, inode_id in self.current_dir.entries.items():
            inode = self.inodes[inode_id]
            tipo = "dir" if inode.is_dir else "file"
            print(f"{tipo}\t{name}")

    def cd(self, name: str):
        if name == ".":
            return
        if name == "..":
            for inode in self.inodes.values():
                if inode.is_dir and self.current_dir.id in inode.entries.values():
                    self.current_dir = inode
                    return
            return
        if name not in self.current_dir.entries:
            print(f"Erro: Diretório '{name}' não encontrado.")
            return
        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]
        if not inode.is_dir:
            print(f"Erro: '{name}' não é um diretório.")
            return
        self.current_dir = inode

    def _resolve_path(self, path: str):
        if path == "/":
            return self.root

        parts = path.strip("/").split("/")
        current = self.root if path.startswith("/") else self.current_dir

        for part in parts:
            if part == ".":
                continue
            elif part == "..":
                for inode in self.inodes.values():
                    if inode.is_dir and current.id in inode.entries.values():
                        current = inode
                        break
            else:
                if part not in current.entries:
                    return None
                inode_id = current.entries[part]
                inode = self.inodes[inode_id]
                if not inode.is_dir:
                    return None
                current = inode
        return current


    def move(self, file_name: str, dest_path: str):
    # Verifica se o arquivo existe no diretório atual
        if file_name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
            return

        file_inode_id = self.current_dir.entries[file_name]
        file_inode = self.inodes[file_inode_id]

        if file_inode.is_dir:
            print(f"Erro: '{file_name}' é um diretório. Apenas arquivos podem ser movidos.")
            return

        # Resolve o diretório de destino
        dest_dir = self._resolve_path(dest_path)
        if dest_dir is None or not dest_dir.is_dir:
            print(f"Erro: Diretório de destino '{dest_path}' não encontrado ou não é um diretório.")
            return

        if file_name in dest_dir.entries:
            print(f"Erro: Já existe um arquivo chamado '{file_name}' em '{dest_path}'.")
            return

        # Remove do diretório atual e adiciona ao destino
        del self.current_dir.entries[file_name]
        dest_dir.entries[file_name] = file_inode_id
        print(f"Arquivo '{file_name}' movido com sucesso para '{dest_path}'.")


    def delete(self, name: str):
        if name not in self.current_dir.entries:
            print(f"Erro: '{name}' não encontrado.")
            return
        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]

        if inode.is_dir:
            if inode.entries:
                print(f"Erro: Diretório '{name}' não está vazio.")
                return
            del self.inodes[inode_id]
            del self.current_dir.entries[name]
            print(f"Diretório '{name}' excluído com sucesso.")
        else:
            self._free_blocks(inode.start_block)
            del self.inodes[inode_id]
            del self.current_dir.entries[name]
            print(f"Arquivo '{name}' excluído com sucesso.")
