import socket
from utils import (
    MESSAGE_TYPE_IDENTIFICATION,
    MESSAGE_TYPE_STRING_DATA,
    PORT,
    ConnectedClient,
    get_decoded_data,
    get_local_ip,
    send_message,
    start_receive_thread,
)
import threading


local_ip = get_local_ip()[-1]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ("0.0.0.0", PORT)

server_socket.bind(address)

server_socket.listen(5)

is_socket_running = True

connected_clients = []

print("Socket ouvindo em: ", local_ip)


def wait_for_connections():
    while True:
        try:
            print("Aguardando conexão...")

            client_socket, client_address = server_socket.accept()

            while True:
                data = client_socket.recv(1024 * 10)
                if not data:
                    print("Cliente saiu sem se identificar...")
                    client_socket.close()
                message = get_decoded_data(data)
                if message.is_identification:
                    print(
                        f"Usuário {message.message_data} identificado em {client_address}, iniciando recebimento de mensagens..."
                    )
                    connected_clients.append(
                        ConnectedClient(
                            client_socket=client_socket,
                            username=message.message_data,
                            client_address=client_address,
                        )
                    )
                    start_receive_thread(client_socket, message.message_data)
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
        print('\nAinda não há clientes conectados!')
        continue

    print("\nSelecione um cliente conectado para enviar uma mensagem:\n")
    connected_client: ConnectedClient

    for index, connected_client in enumerate(connected_clients):
        print(index + 1, f"\t -- \t{connected_client.username}")
    print('\n')
    choice = input("digite um número: ")
    try:
        connectedClient:ConnectedClient = connected_clients[int(choice)-1]
        print(f'Cliente {connectedClient.username} selecionado, envie uma mensagem:')
        connectedClient.send_message(input())
        
    except:
        print('Escolha inválida!')
