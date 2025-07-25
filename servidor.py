import socket
from threading import Thread
import time
import random
import json

class Servidor:
    def __init__(self, ip: str, porta: int):
        self.ip = ip
        self.porta = porta
        self.servidor_tcp_thread = None
        self.info = {}  # ← armazena dados recebidos por IP
        self.recebendo_dados = True

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
            time.sleep(10)

    def lidar_com_cliente(self, conexao_cliente: socket.socket, endereco_cliente: tuple) -> None:
        print(f"Conexão aceita de {endereco_cliente}")
        try:
            dados_recebidos = conexao_cliente.recv(4096)
            if not dados_recebidos:
                conexao_cliente.close()
                return

            # Tenta decodificar como JSON
            try:
                dados = json.loads(dados_recebidos.decode("utf-8"))
                self.info[endereco_cliente[0]] = {
                    'espaco_livre_hd': dados.get("espaco_livre_hd", "Desconhecido"),
                    'qtd_processadores': dados.get("qtd_processadores", "Desconhecido"),
                    'espaco_memoria': dados.get("espaco_memoria", "Desconhecido"),
                    'temperatura': dados.get("temperatura", "Desconhecido")
                }
                self.salvar_em_json()
                if self.recebendo_dados:
                    print(f"Dados do IP {endereco_cliente[0]} armazenados com sucesso.")
                conexao_cliente.sendall(b"Dados recebidos e salvos com sucesso.")
            except json.JSONDecodeError:
                comando = dados_recebidos.decode("utf-8").strip()
                print(f"Comando recebido de {endereco_cliente}: {comando}")

            if comando.lower() == "ping":
                resposta_servidor = "Pong!"
            elif comando.lower() == "hora":
                resposta_servidor = f"A hora atual é {time.strftime('%H:%M:%S')}"
            else:
                resposta_servidor = f"Comando '{comando}' recebido com sucesso!"
            
            conexao_cliente.sendall(resposta_servidor.encode("utf-8"))

        except Exception as e:
            print(f"Erro ao lidar com cliente {endereco_cliente}: {e}")
        finally:
            conexao_cliente.close()

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

    def receber_dados(self, conexao_cliente: socket.socket, endereco_cliente: tuple):
        try:
            msg = conexao_cliente.recv(1024).decode("utf-8")
            try:
                dados_recebidos = json.loads(msg)
                self.info[endereco_cliente[0]] = {
                    'espaco_livre_hd': dados_recebidos.get("espaco_livre_hd", "Desconhecido"),
                    'qtd_processadores': dados_recebidos.get("qtd_processadores", "Desconhecido"),
                    'espaco_memoria': dados_recebidos.get("espaco_memoria", "Desconhecido"),
                    'temperatura': dados_recebidos.get("temperatura", "Desconhecido")
                }
                self.salvar_em_json()
                if self.recebendo_dados:
                    print(f"Dados do IP {endereco_cliente[0]} armazenados.")
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON de {endereco_cliente[0]}. Dados recebidos: {msg}")

            conexao_cliente.close()
        except Exception as e:
            print(f"Erro ao receber dados: {e}")

    def salvar_em_json(self):
        try:
            dados_salvos = {}
            try:
                with open("informacoes_sistema.json", "r") as file:
                    dados_salvos = json.load(file)
            except FileNotFoundError:
                pass

            dados_salvos.update(self.info)

            with open("informacoes_sistema.json", 'w') as file:
                json.dump(dados_salvos, file, indent=4)

        except Exception as e:
            print(f"Erro ao salvar arquivo JSON: {e}")

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