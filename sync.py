import os
import shutil
import time
import hashlib
import argparse
from datetime import datetime

def calculate_md5(file_path):
    """Calcula o hash MD5 de um arquivo."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def log_action(log_file, message):
    """Registra uma ação no log e imprime no console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(log_file, 'a') as log:
        log.write(log_entry + '\n')

def sync_folders(source, replica, log_file):
    """Sincroniza a pasta fonte com a réplica."""
    if not os.path.exists(replica):
        os.makedirs(replica)
        log_action(log_file, f"Criado diretório: {replica}")
    
    source_files = {}
    replica_files = {}
    
    # Mapeia os arquivos na pasta fonte
    for root, _, files in os.walk(source):
        for file in files:
            source_path = os.path.join(root, file)
            rel_path = os.path.relpath(source_path, source)
            source_files[rel_path] = source_path
    
    # Mapeia os arquivos na pasta réplica
    for root, _, files in os.walk(replica):
        for file in files:
            replica_path = os.path.join(root, file)
            rel_path = os.path.relpath(replica_path, replica)
            replica_files[rel_path] = replica_path
    
    # Copia/atualiza arquivos da fonte para a réplica
    for rel_path, source_path in source_files.items():
        replica_path = os.path.join(replica, rel_path)
        if rel_path not in replica_files or calculate_md5(source_path) != calculate_md5(replica_path):
            os.makedirs(os.path.dirname(replica_path), exist_ok=True)
            shutil.copy2(source_path, replica_path)
            log_action(log_file, f"Arquivo copiado/atualizado: {replica_path}")
    
    # Remove arquivos que não estão mais na fonte
    for rel_path, replica_path in replica_files.items():
        if rel_path not in source_files:
            os.remove(replica_path)
            log_action(log_file, f"Arquivo removido: {replica_path}")
    
    # Remove diretórios vazios na réplica
    for root, dirs, _ in os.walk(replica, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                log_action(log_file, f"Diretório removido: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description="Sincroniza duas pastas periodicamente.")
    parser.add_argument("source", nargs="?", default="./source", help="Caminho da pasta fonte")
    parser.add_argument("replica", nargs="?", default="./replica", help="Caminho da pasta réplica")
    parser.add_argument("interval", nargs="?", type=int, default=60, help="Intervalo de sincronização em segundos")
    parser.add_argument("log_file", nargs="?", default="./logs/sync.log", help="Caminho do arquivo de log")
    
    args = parser.parse_args()

    print(f"Sincronização iniciada de {args.source} para {args.replica} a cada {args.interval} segundos.")
    
    while True:

        print("Executando sincronização...")
        sync_folders(args.source, args.replica, args.log_file)
        print(f"Sincronização concluída. Próxima em {args.interval} segundos.")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
