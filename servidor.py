import socket
from threading import Thread
import time
import random

class Servidor:
    def __init__(self, ip: str, porta: int):
        self.ip = ip
        self.porta = porta
        self.servidor_tcp_thread = None

    def publicarCoiso(self) -> None:
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        allips = [ip[-1][0] for ip in interfaces]
        msg = str((self.ip, self.porta)).encode("utf-8")
        
        while True:
            for ip in allips:
                print(f'Publicando em {ip}:{5005}')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))
                sock.sendto(msg, ("255.255.255.255", 5005)) 
                sock.close()
            time.sleep(60)

    def lidar_com_cliente(self, conexao_cliente: socket.socket, endereco_cliente: tuple) -> None:
        print(f"Conexão aceita de {endereco_cliente}")

        while True:
            dados_recebidos = conexao_cliente.recv(1024) 
            if not dados_recebidos:
                break 
            
            comando = dados_recebidos.decode("utf-8")
            print(f"Comando recebido de {endereco_cliente}: {comando}")

            if comando.lower() == "ping":
                resposta_servidor = "Pong!"
            elif comando.lower() == "hora":
                resposta_servidor = f"A hora atual é {time.strftime('%H:%M:%S')}"
            else:
                resposta_servidor = f"Comando '{comando}' recebido com sucesso!"
            
            conexao_cliente.sendall(resposta_servidor.encode("utf-8"))

    def iniciar_servidor_tcp(self) -> None:
        print(f"Servidor TCP iniciando em {self.ip}:{self.porta}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.porta))
            s.listen()
            print(f"Servidor TCP escutando em {self.ip}:{self.porta}")
            
            while True:
                # Aceita uma nova conexão de cliente
                conexao, endereco = s.accept()
                # Inicia uma nova thread para lidar com este cliente, chamando lidar_com_cliente
                Thread(target=self.lidar_com_cliente, args=(conexao, endereco)).start()

    def ligar(self) -> None:
        publicador_thread = Thread(target=self.publicarCoiso, daemon=True)
        publicador_thread.start()

        self.servidor_tcp_thread = Thread(target=self.iniciar_servidor_tcp)
        self.servidor_tcp_thread.start()

def main_servidor():
    porta =  random.randint(10000, 65000)
    server = Servidor("0.0.0.0", porta) 
    server.ligar()
    
    try:
        if server.servidor_tcp_thread:
            server.servidor_tcp_thread.join()
    except KeyboardInterrupt:
        print("\nServidor encerrado manualmente.")

if __name__ == "__main__":
    main_servidor()