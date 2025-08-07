# cliente_final.py
import socket
import json
from cryptography.fernet import Fernet
from sistema import Sistema

# Classe Cliente, mantendo a estrutura que você criou
class Cliente:
    def __init__(self):
        self.servidor_encontrado = None 
        chave_secreta = b'pe7TtaxA65h4y5e0k2z3D-gGyx3g2H2aI8_Jd3g-2Zc='
        self.fernet = Fernet(chave_secreta)

    def escutarServidores(self, timeout=15):
        print(f"Procurando por um servidor na rede por até {timeout} segundos...")
        
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.settimeout(timeout)
        sock_udp.bind(('', 5005))

        try:
            msg_bytes, endereco_servidor = sock_udp.recvfrom(1024)
            dados_servidor = json.loads(msg_bytes.decode('utf-8'))
            
            ip_servidor = endereco_servidor[0]
            porta_servidor = dados_servidor['porta_servidor']
            
            self.servidor_encontrado = (ip_servidor, porta_servidor)
            print(f"Servidor encontrado em {self.servidor_encontrado}!")
        except socket.timeout:
            print("Nenhum servidor encontrado no tempo limite.")
        finally:
            sock_udp.close()

    def enviar_info(self):
        if not self.servidor_encontrado:
            print("Não é possível enviar dados, nenhum servidor foi encontrado.")
            return

        print("Coletando informações do sistema...")
        dados_coletados = {
            "qtd_processadores": Sistema.qtd_processadores(),
            "memoria_ram_livre": Sistema.espaco_memoria(),
            "espaco_disco_livre": Sistema.espaco_disco_livre(),
            "ips_interfaces": Sistema.ips_interfaces(),
            "interfaces_desativadas": Sistema.interfaces_desativadas(),
            "portas_tcp_abertas": Sistema.portas_tcp_abertas(),
            "portas_udp_abertas": Sistema.portas_udp_abertas(),
        }

        dados_criptografados = self.fernet.encrypt(
            json.dumps(dados_coletados).encode('utf-8')
        )
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
                print(f"Conectando a {self.servidor_encontrado}...")
                sock_tcp.connect(self.servidor_encontrado)
                sock_tcp.sendall(dados_criptografados)
                print("Dados enviados com sucesso!")
        except Exception as e:
            print(f"Falha ao enviar dados: {e}")


def main():
    # Orquestra a execução do cliente
    cliente = Cliente()
    cliente.escutarServidores()
    cliente.enviar_info()
    print("Cliente finalizou sua execução.")

if __name__ == "__main__":
    main()