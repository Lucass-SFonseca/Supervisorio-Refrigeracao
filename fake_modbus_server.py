from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import random
import time
from threading import Thread

# Cria bloco de registradores com espaço suficiente
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*2000)  # Holding Registers (4x)
)
context = ModbusServerContext(slaves=store, single=True)

# Endereços usados no seu projeto (main.py)
enderecos = {
    712: "Velocidade_saida_ar",
    714: "Vazao_saida_ar",
    710: "Temperatura",
    1205: "Med_demanda",
    1236: "Velocidade_compresor",
    1231: "Alarme_Temperatura_baixa",
    845: "Corrente_media",
    840: "DDP_fases",
    700: "temp_rolamento",
    726: "Corrente_comp",
    735: "Potencia_ativa",
    743: "potencia_aparente",
    747: "fator_de_pontencis",
    830: "ve.frequencia"
}

def atualizar_valores():
    """Atualiza valores aleatórios nos endereços usados pelo app."""
    while True:
        for addr in enderecos:
            valor = random.randint(100, 5000)  # valores simulados
            store.setValues(3, addr, [valor])
        time.sleep(1)  # atualiza a cada 1 segundo

if __name__ == "__main__":
    # Thread para atualizar valores continuamente
    t = Thread(target=atualizar_valores)
    t.daemon = True
    t.start()

    print("Servidor Modbus fake rodando em 127.0.0.1:5020")
    StartTcpServer(context, address=("localhost", 5020))
