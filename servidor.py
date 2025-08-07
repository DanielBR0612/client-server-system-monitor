# servidor_final_com_menu.py
import socket
import json
from threading import Thread, Lock
import time
from cryptography.fernet import Fernet
import statistics
import random

class Servidor:
    def __init__(self, ip: str, porta: int):
        self.ip = ip
        self.porta = porta
        self.clientes_info = {}
        self.servidor_online = True 
        self.lock = Lock() 
        
        chave_secreta = b'pe7TtaxA65h4y5e0k2z3D-gGyx3g2H2aI8_Jd3g-2Zc='
        self.fernet = Fernet(chave_secreta)

    def publicarCoiso(self):
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mensagem = json.dumps({'ip_servidor': self.ip, 'porta_servidor': self.porta}).encode('utf-8')
        
        while self.servidor_online:
            sock_udp.sendto(mensagem, ('255.255.255.255', 5005))
            time.sleep(10)

    def lidar_com_cliente(self, conexao, endereco):
        """Lógica para tratar um único cliente."""
        ip_cliente = endereco[0]
        print(f"\n[INFO] Conexão aceita de {ip_cliente}. Processando...")
        try:
            dados_criptografados = conexao.recv(4096)
            if not dados_criptografados:
                return

            dados_decriptados = self.fernet.decrypt(dados_criptografados)
            dados_cliente = json.loads(dados_decriptados.decode('utf-8'))
            
            with self.lock:
                self.clientes_info[ip_cliente] = dados_cliente
            
            print(f"[INFO] Dados de {ip_cliente} armazenados com sucesso.")

        except Exception as e:
            print(f"Erro ao comunicar com {ip_cliente}: {e}")
        finally:
            conexao.close()

    def iniciar_servidor_tcp(self):
        """Este método agora roda em uma thread, apenas ouvindo conexões."""
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor_socket.bind((self.ip, self.porta))
        servidor_socket.listen()
        print(f"[TCP] Servidor escutando em {self.ip}:{self.porta}")

        while self.servidor_online:
            try:
                servidor_socket.settimeout(1.0) 
                conexao, endereco = servidor_socket.accept()
                
                thread_cliente = Thread(target=self.lidar_com_cliente, args=(conexao, endereco))
                thread_cliente.start()
            
            except socket.timeout:
                continue
            except Exception as e:
                if self.servidor_online:
                    print(f"Erro no servidor TCP: {e}")
        
        servidor_socket.close()
        print("[TCP] Servidor TCP encerrado.")

    def ligar(self):
        """Inicia os 'trabalhadores' (threads) do servidor."""
        thread_broadcast = Thread(target=self.publicarCoiso, daemon=True)
        thread_broadcast.start()
        
        thread_servidor = Thread(target=self.iniciar_servidor_tcp, daemon=True)
        thread_servidor.start()

    def desligar(self):
        """Sinaliza para as threads pararem."""
        print("\nFinalizando o servidor...")
        self.servidor_online = False
        time.sleep(1.5) 

    def listar_clientes(self):
        with self.lock:
            if not self.clientes_info:
                print("\nNenhum cliente conectado ainda.")
                return
            
            print("\n--- Clientes Conectados ---")
            for ip in self.clientes_info:
                print(f"- {ip}")
    
    def detalhar_cliente(self, ip):
        with self.lock:
            if ip not in self.clientes_info:
                print(f"\nErro: Cliente com IP {ip} não encontrado.")
                return
            
            print(f"\n--- Detalhes de {ip} ---")
            print(json.dumps(self.clientes_info[ip], indent=2))
            
    def calcular_media_cliente(self, ip):
        with self.lock:
            if ip not in self.clientes_info:
                print(f"\nErro: Cliente com IP {ip} não encontrado.")
                return
            
            dados = self.clientes_info[ip]
            vals = [v for k, v in dados.items() if k in ['qtd_processadores', 'memoria_ram_livre', 'espaco_disco_livre'] and isinstance(v, (int, float))]
            if not vals:
                print("\nNão há dados numéricos para calcular a média.")
                return

            print(f"\n>>> Média para {ip}: {statistics.mean(vals):.2f}")


def menu_interativo(servidor: Servidor):
    """Loop principal que mostra o menu e interage com o usuário."""
    time.sleep(1) 
    while servidor.servidor_online:
        print("\n--- Menu do Servidor ---")
        print("1. Listar clientes")
        print("2. Detalhar cliente")
        print("3. Calcular média de um cliente")
        print("4. Sair")
        
        escolha = input(">> Digite sua escolha: ").strip()

        if escolha == '1':
            servidor.listar_clientes()
        elif escolha == '2':
            ip = input("Digite o IP do cliente: ").strip()
            servidor.detalhar_cliente(ip)
        elif escolha == '3':
            ip = input("Digite o IP do cliente: ").strip()
            servidor.calcular_media_cliente(ip)
        elif escolha == '4':
            servidor.desligar()
            break
        else:
            print("Opção inválida.")


def main():
    porta = random.randint(10000, 65535)
    servidor = Servidor('0.0.0.0', porta)
    servidor.ligar()
    
    try:
        menu_interativo(servidor)
    except KeyboardInterrupt:
        servidor.desligar()
    
    print("Programa finalizado.")

if __name__ == "__main__":
    main()