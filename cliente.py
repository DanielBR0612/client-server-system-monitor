import socket
from threading import Thread
import time
from sistema import Sistema
import json

class Cliente:
    servidores = {}

    def __init__(self) -> None:
        self.server_ip = None
        self.server_port = None

        self.publicador = Thread(target=self.escutarServidores, daemon=True)
        self.publicador.start()
        print("Executador Iniciado...")

    def escutarServidores(self):
        print("Esperando servidores...")
        HOST = ''
        PORT = 5005
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp.bind((HOST, PORT))
        
        while True:
            msg, cliente = udp.recvfrom(1024)
            ip_cliente = cliente[0]
            tupla = eval(msg.decode("utf-8"))  # Ex: ('192.168.1.87', 8888)
            self.servidores[ip_cliente] = {"porta": tupla[1], "lastPing": int(time.time())}

            # Define o primeiro servidor encontrado como o principal
            if self.server_ip is None:
                self.server_ip = ip_cliente
                self.server_port = tupla[1]
                print(f"Servidor principal definido: {self.server_ip}:{self.server_port}")

    def showServers(self):
        print("Servidores disponíveis:")
        for ip, info in self.servidores.items():
            print(f"{ip}:{info['porta']} (último ping: {info['lastPing']})")
            
    def enviarComando(self, ip: str, porta: int, comando: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
            tcp.connect((ip, porta))
            tcp.sendall(comando.encode("utf-8"))
            resposta = tcp.recv(1024).decode("utf-8")
            print("Resposta do servidor:", resposta)
    
    def enviar_info(self):
        if self.server_ip is None or self.server_port is None:
            print("Nenhum servidor conhecido ainda.")
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, self.server_port))

                dados = {
                    "espaço_livre_hd": Sistema.espaco_livre_hd(),
                    "qtd_processadores": Sistema.qtd_processadores(),
                    "espaco_memoria": Sistema.espaco_memoria(),
                    "temperatura": Sistema.temperatura()
                }

                dados_json = json.dumps(dados)
                s.send(dados_json.encode("utf-8"))
                print("Dados enviados ao servidor.")
        except Exception as e:
            print(f"Erro ao enviar dados ao servidor: {e}")

def main():
    c = Cliente()
    while True:
        c.enviar_info()
        time.sleep(10)

if __name__ == "__main__":
    main()
