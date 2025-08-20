from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import random
import time
from threading import Thread

# Cria bloco de registradores com espaço suficiente
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*5000)  # Holding Registers (4x)
)
context = ModbusServerContext(slaves=store, single=True)

# Endereços retirados do main.py
enderecos = {
    # Floats (FP)
    700:  ("temp_enrolamento_R_motor", "FP"),
    702:  ("temp_enrolamento_S_motor", "FP"),
    704:  ("temp_enrolamento_T_motor", "FP"),
    706:  ("temperatura_carcaca", "FP"),
    884:  ("rot_motor", "FP"),
    1422: ("torque_motor", "FP"),
    710:  ("Temperatura_saida", "FP"),
    714:  ("Vazao_saida_ar", "FP"),
    712:  ("Velocidade_saida_ar", "FP"),
    1218: ("ve.tit02", "FP"),
    1220: ("ve.tit01", "FP"),
    1222: ("ve.pit01", "FP"),
    1224: ("ve.pit02", "FP"),
    1226: ("ve.pit03", "FP"),
    1310: ("ve.nv_escreve", "FP"),

    # Inteiros (4X)
    840: ("corrente_R", "4X"),
    841: ("corrente_S", "4X"),
    842: ("corrente_T", "4X"),
    843: ("corrente_N", "4X"),
    845: ("corrente_media", "4X"),
    847: ("tensao_RS", "4X"),
    848: ("tensao_ST", "4X"),
    849: ("tensao_TR", "4X"),
    863: ("potencia_aparente_total", "4X"),
    860: ("potencia_aparente_r", "4X"),
    861: ("potencia_aparente_s", "4X"),
    862: ("potencia_aparente_t", "4X"),
    859: ("potencia_reativa_total", "4X"),
    856: ("potencia_reativa_r", "4X"),
    857: ("potencia_reativa_s", "4X"),
    858: ("potencia_reativa_t", "4X"),
    855: ("potencia_ativa_total", "4X"),
    852: ("potencia_ativa_r", "4X"),
    853: ("potencia_ativa_s", "4X"),
    854: ("potencia_ativa_t", "4X"),
}

def atualizar_valores():
    """Atualiza valores aleatórios nos endereços usados pelo app."""
    while True:
        for addr, (nome, tipo) in enderecos.items():
            if tipo == "FP":
                # Gera um float 32 bits e escreve em 2 registradores
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
                builder.add_32bit_float(random.uniform(10, 100))  # valor float
                regs = builder.to_registers()
                store.setValues(3, addr, regs)
            elif tipo == "4X":
                # Gera inteiro simples de 16 bits
                valor = random.randint(100, 5000)
                store.setValues(3, addr, [valor])
        time.sleep(1)  # atualiza a cada 1 segundo

if __name__ == "__main__":
    # Thread para atualizar valores continuamente
    t = Thread(target=atualizar_valores)
    t.daemon = True
    t.start()

    print("Servidor Modbus fake rodando em 127.0.0.1:5020")
    StartTcpServer(context, address=("localhost", 5020))
