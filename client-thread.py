import socket
import threading
import os

HOST = 'localhost'
PORT = 80
FILE_NAME = 'demo.pdf'
NUM_THREADS = 4  

def get_file_size():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    request = (
        f"HEAD /pemro-jar/files/{FILE_NAME} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )
    client.sendall(request.encode())
    response = b""
    while True:
        chunk = client.recv(1024)
        if not chunk:
            break
        response += chunk
    client.close()

    header = response.decode(errors='replace')
    print("=== HEADER RESPONS HEAD ===")
    print(header)
    print("============================\n")

    for line in header.split('\r\n'):
        if line.lower().startswith("content-length:"):
            return int(line.split(":")[1].strip())
    return None

def download_range(start, end, part_index):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    request = (
        f"GET /pemro-jar/files/{FILE_NAME} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"Range: bytes={start}-{end}\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )
    client.sendall(request.encode())
    response = b""

    while b'\r\n\r\n' not in response:
        chunk = client.recv(1024)
        if not chunk:
            break
        response += chunk

    if b'\r\n\r\n' in response:
        header, content = response.split(b'\r\n\r\n', 1)
        print(f"=== HEADER RESPONS PART {part_index} (bytes {start}-{end}) ===")
        print(header.decode(errors='replace'))
        print("=============================================================\n")
    else:
        print(f"Header tidak lengkap di part {part_index}")
        header = b""
        content = b""

    with open(f"part_{part_index}.tmp", 'wb') as f:
        f.write(content)
        while True:
            chunk = client.recv(1024)
            if not chunk:
                break
            f.write(chunk)

    client.close()
    print(f"[INFO] Part {part_index} selesai diunduh (byte {start}-{end})")

def merge_parts(output_name, total_parts):
    with open(output_name, 'wb') as output_file:
        for i in range(total_parts):
            part_name = f"part_{i}.tmp"
            with open(part_name, 'rb') as part_file:
                output_file.write(part_file.read())
            os.remove(part_name)
    print(f"[INFO] Semua bagian digabung menjadi {output_name}")

def main():
    file_size = get_file_size()
    if file_size is None:
        print("[ERROR] Gagal mendapatkan ukuran file.")
        return

    print(f"[INFO] Ukuran file: {file_size} bytes\n")

    part_size = file_size // NUM_THREADS
    threads = []

    for i in range(NUM_THREADS):
        start = i * part_size
        end = (start + part_size - 1) if i < NUM_THREADS - 1 else file_size - 1
        print(f"[INFO] Membuat thread {i} untuk byte {start} hingga {end}")
        t = threading.Thread(target=download_range, args=(start, end, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    merge_parts(f"downloaded_{FILE_NAME}", NUM_THREADS)

if __name__ == "__main__":
    main()
