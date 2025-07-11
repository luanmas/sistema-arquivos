from typing import Dict
from entity.inode import Inode
import time
import random


def generate_random_data(size):
    """Gera dados aleatórios do tamanho especificado."""
    import random
    import string
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))

BLOCK_SIZE = 8
TOTAL_BLOCKS = 1000000

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
        inode = Inode(name, False, parent=self.current_dir)
        self.inodes[inode.id] = inode
        self.current_dir.entries[name] = inode.id
        print(f"Arquivo '{name}' criado com sucesso.")

    def create_dir(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        inode = Inode(name, True, parent=self.current_dir)
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
            if self.current_dir.parent is not None:
                self.current_dir = self.current_dir.parent
                self._update_path()
            else:
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
        if self.current_dir == self.root:
            self.current_path = "/"
            return
        path = []
        current = self.current_dir
        while current != self.root:
            path.append(current.name)
            current = current.parent
        self.current_path = "/" + "/".join(reversed(path))

    def move(self, file_name: str, dest_path: str):
        if file_name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
            print(f"Diretório atual: {self.current_path}")
            print(f"Conteúdo do diretório atual: {list(self.current_dir.entries.keys())}")
            return

        file_inode_id = self.current_dir.entries[file_name]
        file_inode = self.inodes[file_inode_id]

        if file_inode.is_dir:
            print(f"Erro: '{file_name}' é um diretório. Apenas arquivos podem ser movidos.")
            return

        dest_dir = None
        if dest_path == "/":
            dest_dir = self.root
        else:
            for inode in self.inodes.values():
                if inode.is_dir and inode.name == dest_path:
                    dest_dir = inode
                    break

        if dest_dir is None:
            print(f"Erro: Diretório de destino '{dest_path}' não encontrado.")
            return

        if file_name in dest_dir.entries:
            print(f"Erro: Já existe um arquivo ou diretório chamado '{file_name}' em '{dest_path}'.")
            return

        del self.current_dir.entries[file_name]
        dest_dir.entries[file_name] = file_inode_id
        file_inode.parent = dest_dir
        print(f"Arquivo '{file_name}' movido para '{dest_path}' com sucesso.")

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

    def write_file(self, name: str, data: str):
        if name not in self.current_dir.entries:
            self.create_file(name)

        inode_id = self.current_dir.entries[name]
        inode = self.inodes[inode_id]

        num_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if len(self.free_blocks) < num_blocks:
            print("Erro: Espaço insuficiente em disco.")
            inode.size = 0
            inode.data_blocks = []
            return

        for b in inode.data_blocks:
            self.disk[b] = ''
            self.free_blocks.append(b)

        random.shuffle(self.free_blocks)
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

        if inode.is_dir:
            if inode.entries:
                print(f"Erro: Diretório '{name}' não está vazio.")
                return
            else:
                del self.inodes[inode_id]
                del self.current_dir.entries[name]
                print(f"Diretório '{name}' excluído com sucesso.")
        else:
            for b in inode.data_blocks:
                self.disk[b] = ''
                self.free_blocks.append(b)
            del self.inodes[inode_id]
            del self.current_dir.entries[name]
            print(f"Arquivo '{name}' excluído com sucesso.")
            
    def detalhes(self, nome: str):
        if nome not in self.current_dir.entries:
            print(f"Erro: '{nome}' não encontrado.")
            return

        inode_id = self.current_dir.entries[nome]
        inode = self.inodes[inode_id]

        print(f"ID: {inode.id}")
        print(f"Nome: {inode.name}")
        print(f"Diretório: {'Sim' if inode.is_dir else 'Não'}")

        if inode.is_dir:
            print(f"Entradas: {list(inode.entries.keys())}")
        else:
            print(f"Tamanho: {inode.size} bytes")
            print(f"Blocos alocados: {inode.data_blocks}")

    def status(self):
        total_blocos = TOTAL_BLOCKS
        livres = len(self.free_blocks)
        usados = total_blocos - livres

        arquivos = sum(1 for i in self.inodes.values() if not i.is_dir)
        diretorios = sum(1 for i in self.inodes.values() if i.is_dir)

        print("\n=== STATUS DO SISTEMA DE ARQUIVOS (i-nodes) ===")
        print(f"Blocos totais: {total_blocos}")
        print(f"Blocos usados: {usados}")
        print(f"Blocos livres: {livres}")
        print(f"Arquivos: {arquivos}")
        print(f"Diretórios: {diretorios}")
        print("Uso por arquivo:")
        for inode in self.inodes.values():
            if not inode.is_dir:
                print(f"  - {inode.name}: {inode.data_blocks} ({inode.size} bytes)")


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

import time

def benchmark_move_inode(fs: FileSystem, file_name: str, dest_path: str) -> float:
    """
    Mede o tempo para mover um arquivo no sistema de arquivos com i-nodes.
    Retorna o tempo em milissegundos.
    """
    if file_name not in fs.current_dir.entries:
        print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
        return -1

    inode_id = fs.current_dir.entries[file_name]
    inode = fs.inodes[inode_id]

    if inode.is_dir:
        print(f"Erro: '{file_name}' é um diretório.")
        return -1

    if dest_path == "/":
        dest_dir = fs.root
    else:
        dest_dir = fs._resolve_path(dest_path)
        if dest_dir is None or not dest_dir.is_dir:
            print(f"Erro: Diretório de destino '{dest_path}' não encontrado ou não é um diretório.")
            return -1

    if file_name in dest_dir.entries:
        print(f"Erro: Já existe um arquivo chamado '{file_name}' em '{dest_path}'.")
        return -1

    start = time.perf_counter()
    del fs.current_dir.entries[file_name]
    dest_dir.entries[file_name] = inode_id
    end = time.perf_counter()

    return (end - start) * 1000

def benchmark_inode_delete(fs: FileSystem, file_name: str) -> float:
    """Mede o tempo para excluir um arquivo usando a estratégia de inode."""
    if file_name not in fs.current_dir.entries:
        print(f"Arquivo '{file_name}' não encontrado.")
        return -1

    start = time.perf_counter()
    fs.delete(file_name)
    end = time.perf_counter()

    return (end - start) * 1000

def benchmark_write_file(fs: FileSystem, file_name: str, data_size: int, repetitions: int = 10) -> dict:
    """
    Mede o tempo médio de escrita para um arquivo de determinado tamanho.
    
    Args:
        fs: Instância do FileSystem
        file_name: Nome do arquivo a ser escrito
        data_size: Tamanho dos dados a serem escritos (em bytes)
        repetitions: Número de repetições para cálculo da média
    
    Returns:
        Dicionário com métricas de desempenho
    """
    results = {
        'file_size': data_size,
        'write_times': [],
        'average_time': 0,
        'min_time': float('inf'),
        'max_time': 0,
        'blocks_used': 0
    }
    
    if file_name in fs.current_dir.entries:
        fs.delete(file_name)

    data = generate_random_data(data_size)
    
    for _ in range(repetitions):
        start = time.perf_counter()
        fs.write_file(file_name, data)
        end = time.perf_counter()
        
        write_time = (end - start) * 1000
        results['write_times'].append(write_time)
        
        if write_time < results['min_time']:
            results['min_time'] = write_time
        if write_time > results['max_time']:
            results['max_time'] = write_time
            
        inode_id = fs.current_dir.entries[file_name]
        inode = fs.inodes[inode_id]
        results['blocks_used'] = len(inode.data_blocks)
        
        fs.delete(file_name)
    
    results['average_time'] = sum(results['write_times']) / repetitions
    
    return results