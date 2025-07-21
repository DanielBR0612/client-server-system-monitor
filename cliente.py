import socket
from threading import Thread
import time

class Cliente:
    servidores = {}

    def __init__(self) -> None:
        self.publicador = Thread(target=self.escutarServidores)
        self.publicador.start()
        print("Executador Iniciado...")

    def escutarServidores(self):
        print("Esperando servidores...")
        HOST = ''  # Endereço IP local
        PORT = 5005            # Porta que o servidor usa para broadcast
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        orig = (HOST, PORT)
        udp.bind(orig)
        while True:
            msg, cliente = udp.recvfrom(1024)
            tupla = eval(msg.decode("utf-8"))  # ex: ('192.168.1.87', 8888)
            self.servidores[cliente[0]] = {"porta": tupla[1], "lastPing": int(time.time())}

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

def main():
    c = Cliente()
    while True:
        c.showServers()
        if c.servidores:
            ip = list(c.servidores.keys())[0]
            porta = c.servidores[ip]['porta']
            comando = input("Digite um comando para enviar ao servidor: ")
            c.enviarComando(ip, porta, comando)
        time.sleep(30)

if __name__ == "__main__":
    main()
