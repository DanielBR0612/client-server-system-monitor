import psutil
import random
# import wmi
class Sistema:
    @staticmethod
    def espaco_livre_hd() -> str:
        resposta = psutil.disk_usage('/').free / (1024**3)  # conversão para GB
        return f"{resposta:.2f} GB"

    @staticmethod
    def qtd_processadores() -> str:
        resposta = psutil.cpu_count(logical=True)
        return f"{resposta}"

    @staticmethod
    def espaco_memoria() -> str:
        resposta = psutil.virtual_memory().available / (1024**3)  # memória disponível em GB
        return f"{resposta:.2f} GB"
    
    @staticmethod
    def temperatura() -> int:
        resposta = random.randint(40, 80)
        return f"{resposta}°C"
    
