from ast import List
import socket
from utils import (
    MESSAGE_TYPE_IDENTIFICATION,
    MESSAGE_TYPE_STRING_DATA,
    PORT,
    ConnectedClient,
    TextColor,
    clear_input_line,
    get_decoded_data,
    get_local_ip,
    send_message,
    start_receive_thread,
)
import threading


local_ip = get_local_ip()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ("0.0.0.0", PORT)

server_socket.bind(address)

server_socket.listen(5)

is_socket_running = True

connected_clients = []
connected_clients_lock = threading.Lock()

print(TextColor.get_text(f"Socket ouvindo em: {local_ip}", TextColor.GREEN))


def on_close_socket(client_socket: socket.socket):
    with connected_clients_lock:
        connectedClient: ConnectedClient
        for index, connectedClient in enumerate(connected_clients):
            if connectedClient.client_socket == client_socket:
                print(
                    TextColor.get_text(
                        f"Cliente {connectedClient.username} removido dos clientes conectados.",
                        TextColor.MAGENTA,
                    )
                )
                del connected_clients[index]
                break


def wait_for_connections():
    while True:
        try:
            print("Aguardando conexão...")

            client_socket, client_address = server_socket.accept()

            while True:
                data = client_socket.recv(1024 * 10)
                if not data:
                    print(
                        TextColor.get_text(
                            "Cliente saiu sem se identificar...", TextColor.RED
                        )
                    )
                    client_socket.close()
                message = get_decoded_data(data)
                if message.is_identification:
                    print(
                        TextColor.get_text(
                            f"Usuário {message.message_data} identificado em {client_address}, iniciando recebimento de mensagens...",
                            TextColor.GREEN,
                        )
                    )
                    connected_clients.append(
                        ConnectedClient(
                            client_socket=client_socket,
                            username=message.message_data,
                            client_address=client_address,
                        )
                    )
                    start_receive_thread(
                        client_socket, message.message_data, on_close_socket
                    )
                    break
                else:
                    send_message(
                        client_socket,
                        MESSAGE_TYPE_STRING_DATA,
                        "Por gentileza, envie sua identificação",
                    )
        except Exception as e:
            is_socket_running = False
            print("Encerrando servidor...")
            server_socket.close()
            break


wait_thread = threading.Thread(target=wait_for_connections)
wait_thread.daemon = True
wait_thread.start()


while True:
    if not is_socket_running:
        break
    input("\nPressione ENTER para continuar\n")

    if not connected_clients:
        print("\nAinda não há clientes conectados!")
        continue

    print("\nSelecione um cliente conectado para enviar uma mensagem:\n")
    connected_client: ConnectedClient

    for index, connected_client in enumerate(connected_clients):
        print(index + 1, f"\t -- \t{connected_client.username}")
    print("\n")
    choice = input("digite um número: ")
    try:
        connectedClient: ConnectedClient = connected_clients[int(choice) - 1]
        print(
            f"Cliente {connectedClient.username} selecionado, pode começar enviar mensagens. Para escolher outro use CTRL+d ou CTRL+c .\n"
        )

        while True:
            message = input()
            clear_input_line()
            if not message.strip():
                continue
            print(f"{TextColor.get_text('[você]',TextColor.CYAN)} - {message}")
            connectedClient.send_message(message)
    except KeyboardInterrupt:
        continue
    except:
        print("Escolha inválida!")
