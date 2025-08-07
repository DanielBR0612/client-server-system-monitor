# sistema.py
import psutil
import socket

class Sistema:
    @staticmethod
    def espaco_disco_livre():
        return round(psutil.disk_usage('/').free / (1024**3), 2)

    @staticmethod
    def qtd_processadores():
        return psutil.cpu_count(logical=True)

    @staticmethod
    def espaco_memoria():
        return round(psutil.virtual_memory().available / (1024**3), 2)
    
    @staticmethod
    def ips_interfaces():
        ips = []
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for nome, enderecos in addrs.items():
            if stats[nome].isup:
                for addr in enderecos:
                    if addr.family == socket.AF_INET:
                        ips.append(f"{nome}: {addr.address}")
        return ips

    @staticmethod
    def interfaces_desativadas():
        desativadas = []
        for nome, info in psutil.net_if_stats().items():
            if not info.isup:
                desativadas.append(nome)
        return desativadas
        
    @staticmethod
    def portas_tcp_abertas():
        return sorted(list(set([c.laddr.port for c in psutil.net_connections(kind='tcp') if c.status == 'LISTEN'])))

    @staticmethod
    def portas_udp_abertas():
        return sorted(list(set([c.laddr.port for c in psutil.net_connections(kind='udp')])))