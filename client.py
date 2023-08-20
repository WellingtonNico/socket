import socket

from utils import (
    MESSAGE_TYPE_IDENTIFICATION,
    MESSAGE_TYPE_STRING_DATA,
    PORT,
    TextColor,
    clear_input_line,
    get_local_ip,
    send_message,
    start_receive_thread,
)

def get_username():
    while True:
        _username = input("Digite seu nome de usuário:\n")
        if  len(_username.strip())>4:
            return _username
        print(TextColor.get_text('Nome de usuário inválido',TextColor.RED))

server_ip = get_local_ip()[-1]
def get_new_ip():
    while True:
        _server_ip = input(f"Insira um endereço(padrão {server_ip})")
        if len(_server_ip) > 8:
            return _server_ip
        else:
            return None

username = get_username()


new_ip = get_new_ip()

if new_ip:
    server_ip = new_ip

server_port = PORT
address = (server_ip, server_port)

print("Endereço: ", address)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

send_message(client_socket, MESSAGE_TYPE_IDENTIFICATION, username)
# Start a separate thread for receiving messages

start_receive_thread(client_socket, "servidor")

print("Pode começar enviar mensagens, use CTRL+c para parar:\n")

try:
    while True:
        message = input()
        clear_input_line()
        if not message.strip():
            continue
        print(f"{TextColor.get_text('[você]',TextColor.CYAN)} - {message}")
        send_message(client_socket, MESSAGE_TYPE_STRING_DATA, message)
except:
    pass


client_socket.close()
