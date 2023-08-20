import json
import socket
import threading
from typing import Any

PORT = 4040

MESSAGE_TYPE_IDENTIFICATION = 0
MESSAGE_TYPE_JSON_DATA = 1
MESSAGE_TYPE_STRING_DATA = 2


class MessageData:
    message_type: int
    message_data: str | dict | list

    def __init__(self, message_type, message_data) -> None:
        self.message_data = message_data
        self.message_type = message_type
        pass

    @property
    def is_identification(self):
        return self.message_type == MESSAGE_TYPE_IDENTIFICATION


def send_message(client_socket: socket.socket, message_type, message_data):
    client_socket.send(
        json.dumps(
            {"message_type": message_type, "message_data": message_data}
        ).encode()
    )


class ConnectedClient:
    client_socket: socket.socket
    username: str
    client_address: Any

    def __init__(
        self,
        client_socket: socket.socket,
        client_address: Any,
        username: str,
    ) -> None:
        self.client_address = client_address
        self.client_socket = client_socket
        self.username = username

    def send_message(self, message_data: str):
        send_message(self.client_socket, MESSAGE_TYPE_STRING_DATA, message_data)


def get_local_ip():
    hostname = socket.gethostname()
    ip_list = socket.getaddrinfo(hostname, None, socket.AF_INET)
    local_ips = [ip[4][0] for ip in ip_list if ip[1] == socket.SOCK_STREAM]
    return local_ips


def get_decoded_data(data: bytes) -> MessageData:
    decodedData = json.loads(data.decode())
    return MessageData(
        message_data=decodedData["message_data"],
        message_type=decodedData["message_type"],
    )


def get_decoded_message(data: bytes):
    m = get_decoded_data(data)
    return m.message_data


def receive_messages(client_socket: socket.socket, username: str,on_close):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print(f"Encerrando conexão de {username}")
                client_socket.close()
                if on_close is not None and callable(on_close):
                    on_close(client_socket)
                break
            print(f"Mensagem de {username}: {get_decoded_message(data)}")
        except Exception as e:
            print("Erro: ", e)
            break


def start_receive_thread(client_socket: socket.socket, username: str,on_close=None):
    t = threading.Thread(target=receive_messages, args=(client_socket, username,on_close))
    t.daemon = True
    t.start()
