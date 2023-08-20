import json
import socket
import threading

PORT = 4040

MESSAGE_TYPE_IDENTIFICATION = 0
MESSAGE_TYPE_JSON_DATA = 1
MESSAGE_TYPE_STRING_DATA = 2


def get_local_ip():
    hostname = socket.gethostname()
    ip_list = socket.getaddrinfo(hostname, None, socket.AF_INET)
    local_ips = [ip[4][0] for ip in ip_list if ip[1] == socket.SOCK_STREAM]
    return local_ips


def get_decoded_data(data: bytes):
    return json.loads(data.decode())


def get_decoded_message(data: bytes):
    messageDict = get_decoded_data(data)
    return messageDict["message_data"]


def send_message(client_socket: socket.socket, message_type, message_data):
    client_socket.send(json.dumps({"message_type": message_type, "message_data": message_data}).encode())


def receive_messages(client_socket: socket.socket, username: str):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print(f"Encerrando conexão de {username}")
                client_socket.close()
                break
            print(f"Recebido de {username}: {get_decoded_message(data)}")
        except Exception as e:
            print("Erro: ", e)
            break


def start_receive_thread(client_socket: socket.socket, username: str):
    t = threading.Thread(target=receive_messages, args=(client_socket, username))
    t.daemon = True
    t.start()