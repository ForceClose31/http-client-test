import socket

HOST = 'localhost'
PORT = 80

file_name = "demo.pdf"  

start_byte = 100
end_byte = 700

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

request = (
    f"GET /pemro-jar/files/{file_name} HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Range: bytes={start_byte}-{end_byte}\r\n"
    f"Connection: close\r\n"
    "\r\n"
)

client_socket.sendall(request.encode('utf-8'))

response = b""

while b"\r\n\r\n" not in response:
    chunk = client_socket.recv(1024)
    if not chunk:
        break
    response += chunk

print(f"Response diterima (untuk debugging):\n{response.decode('utf-8', errors='replace')}\n")

if b"\r\n\r\n" in response:
    header, content = response.split(b'\r\n\r\n', 1)
    print(f"Header diterima:\n{header.decode('utf-8')}\n")

    if b"206 Partial Content" in header:
        file_path = f"downloaded_{file_name}"

        with open(file_path, 'wb') as file:
            file.write(content)

            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                file.write(chunk)

        print(f"File '{file_name}' berhasil diunduh (byte {start_byte} hingga {end_byte}) dan disimpan sebagai '{file_path}'.")
    else:
        print("Server tidak mendukung partial content atau file tidak ditemukan.")
else:
    print("Header HTTP tidak lengkap atau tidak ditemukan.")

# Menutup koneksi
client_socket.close()
