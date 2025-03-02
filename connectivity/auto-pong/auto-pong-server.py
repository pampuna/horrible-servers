import socket
import threading
import sys

def pong(client, port):
    """ Send 'pong' back to the client and attempt to set up a shell """
    try:
        client.sendall(b'pong')
        while True:
            recv_len = 1
            response = ''
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()
                if recv_len < 4096:
                    break
            if response:
                print(response)
            buffer = input(']> ')
            buffer += '\n'
            client.send(buffer.encode())
    except Exception as e:
        print(f"[*] Failed to send pong to {client}")
        print(e)
    finally:
        client.close()

def start_listener(port):
    """ For the given port, set up a TCP listener. On each incoming connection, log the client details and current port. """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)

    while True:
        client, addr = server.accept()
        print(f"[+] {addr} on port {port}")
        handler = threading.Thread(target=pong, args=(client,port))
        handler.start()

def main():
    ports = [21, 22, 23, 25, 53, 67, 88, 110, 139, 143, 179, 443, 445, 636, 1433, 2483, 3128, 3306, 3389, 8080, 8443, 9001]
    threads = []

    for port in ports:
        listener = threading.Thread(target=start_listener, args=(port,), daemon=True)
        listener.start()
        threads.append(listener)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n[*] User aborted. Exiting")
        sys.exit()

if __name__ == '__main__':
    main()
