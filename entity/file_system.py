from typing import Dict
from entity.inode import Inode
import time

BLOCK_SIZE = 8
TOTAL_BLOCKS = 10000

class FileSystem:
    def __init__(self):
        self.inodes: Dict[str, Inode] = {}
        self.root = Inode("/", True)
        self.inodes[self.root.id] = self.root
        self.current_dir = self.root
        self.current_path = "/"
        self.next_block_id = 0
        self.disk = [''] * TOTAL_BLOCKS
        self.free_blocks = list(range(TOTAL_BLOCKS))

    def create_file(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        inode = Inode(name, False)
        self.inodes[inode.id] = inode
        self.current_dir.entries[name] = inode.id
        print(f"Arquivo '{name}' criado com sucesso.")

    def create_dir(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        inode = Inode(name, True)
        self.inodes[inode.id] = inode
        self.current_dir.entries[name] = inode.id
        print(f"Diretório '{name}' criado com sucesso.")

    def ls(self):
        if not self.current_dir.entries:
            print("Diretório vazio.")
            return
        for name in self.current_dir.entries:
            inode = self.inodes[self.current_dir.entries[name]]
            type_str = "dir" if inode.is_dir else "file"
            print(f"{type_str}\t{name}")

    def cd(self, path: str):
        if path == ".":
            return
        if path == "..":
            # Encontrar o diretório pai
            for inode in self.inodes.values():
                if inode.is_dir and self.current_dir.id in inode.entries.values():
                    self.current_dir = inode
                    self._update_path()
                    return
            if self.current_dir.id == self.root.id:
                print("Já está na raiz.")
            return
        if path not in self.current_dir.entries:
            print(f"Erro: Diretório '{path}' não encontrado.")
            return
        inode_id = self.current_dir.entries[path]
        inode = self.inodes[inode_id]
        if not inode.is_dir:
            print(f"Erro: '{path}' não é um diretório.")
            return
        self.current_dir = inode
        self._update_path()

    def _update_path(self):
        if self.current_dir.id == self.root.id:
            self.current_path = "/"
            return
        path = []
        current = self.current_dir
        while current.id != self.root.id:
            for inode in self.inodes.values():
                if inode.is_dir and current.id in inode.entries.values():
                    for name, id in inode.entries.items():
                        if id == current.id:
                            path.append(name)
                            current = inode
                            break
            if current.id == self.root.id:
                path.append("")
                break
        self.current_path = "/".join(reversed(path)) or "/"

    def move(self, file_name: str, dest_path: str):
        # ve se o arquivo existe no diretório atual
        if file_name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
            print(f"Diretório atual: {self.current_path}")
            print(f"Conteúdo do diretório atual: {list(self.current_dir.entries.keys())}")
            return
        
        # pega o inote do arquivo
        file_inode_id = self.current_dir.entries[file_name]
        file_inode = self.inodes[file_inode_id]
        
        # ve se é um arquivo ou diretório
        if file_inode.is_dir:
            print(f"Erro: '{file_name}' é um diretório. Apenas arquivos podem ser movidos.")
            return

        # acha o diretório de destino
        if dest_path == "/":
            dest_dir = self.root
        else:
            # encontra o diretório de destino no diretório atual
            if dest_path not in self.current_dir.entries:
                print(f"Erro: Diretório de destino '{dest_path}' não encontrado.")
                return
            dest_inode_id = self.current_dir.entries[dest_path]
            dest_dir = self.inodes[dest_inode_id]
            if not dest_dir.is_dir:
                print(f"Erro: '{dest_path}' não é um diretório.")
                return

        # ve se já existe um arquivo com o mesmo nome no destino
        if file_name in dest_dir.entries:
            print(f"Erro: Já existe um arquivo ou diretório chamado '{file_name}' em '{dest_path}'.")
            return

        del self.current_dir.entries[file_name]
        dest_dir.entries[file_name] = file_inode_id
        print(f"Arquivo '{file_name}' movido para '{dest_path}' com sucesso.")


    def write_file(self, name: str, data: str):

        if name not in self.current_dir.entries:
            self.create_file(name)

        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]

        for b in inode.data_blocks:
            self.disk[b] = ''
            self.free_blocks.append(b)

        num_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if len(self.free_blocks) < num_blocks:
            print("Erro: Espaço insuficiente em disco.")
            return

        blocos_alocados = [self.free_blocks.pop(0) for _ in range(num_blocks)]

        for i, b in enumerate(blocos_alocados):
            inicio = i * BLOCK_SIZE
            fim = inicio + BLOCK_SIZE
            self.disk[b] = data[inicio:fim]

        inode.size = len(data)
        inode.data_blocks = blocos_alocados

        print(f"Dados escritos em '{name}' ({inode.size} bytes) nos blocos {blocos_alocados}")

    def read_file(self, name: str):
        if name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{name}' não encontrado.")
            return

        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]

        if inode.is_dir:
            print(f"Erro: '{name}' é um diretório.")
            return

        conteudo = ''.join([self.disk[b] for b in inode.data_blocks])
        print(f"Conteúdo de '{name}' ({inode.size} bytes):")
        print(conteudo[:inode.size])

    def delete(self, name: str):
        if name not in self.current_dir.entries:
            print(f"Erro: '{name}' não existe no diretório atual.")
            return

        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]

        # Se for diretório, verifica se está vazio
        if inode.is_dir:
            if inode.entries:
                print(f"Erro: Diretório '{name}' não está vazio.")
                return
            else:
                del self.inodes[inode_id]
                del self.current_dir.entries[name]
                print(f"Diretório '{name}' excluído com sucesso.")
        else:
            # Arquivo: liberar blocos e remover inode
            for b in inode.data_blocks:
                self.disk[b] = ''
                self.free_blocks.append(b)
            del self.inodes[inode_id]
            del self.current_dir.entries[name]
            print(f"Arquivo '{name}' excluído com sucesso.")

def benchmark_inode_access(fs: FileSystem, file_name: str, k: int) -> float:
    """Mede o tempo para acessar o bloco k de um arquivo via inode."""
    if file_name not in fs.current_dir.entries:
        print(f"Arquivo '{file_name}' não encontrado.")
        return -1

    inode_id = fs.current_dir.entries[file_name]
    inode = fs.inodes[inode_id]

    if k >= len(inode.data_blocks):
        print(f"Bloco {k} fora do intervalo do arquivo.")
        return -1

    start = time.perf_counter()
    _ = fs.disk[inode.data_blocks[k]]
    end = time.perf_counter()

    return (end - start)*1000

