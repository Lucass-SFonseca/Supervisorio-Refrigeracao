from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread, Lock
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian

class MainWidget(BoxLayout):
    """
    Widget principal da aplicação
    """
    _updateThread = None
    _updateWidgets = True


    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        self._meas={}
        self._meas['timestamp']=None
        self._meas['values']={}
        self._lock=Lock()
    
    def startDataRead(self, ip, port):
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Erro: ", e.args)


    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e
        inserção dos dados do Banco de Dados
        """
        try:
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ",e.args)

    def readData(self):
        """
        Método para a leitura dos dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            self._meas['values'][key] = self.read_float_point(self._tags[key]["addr"])

    def read_float_point(self, endereco):
        leitura= self._modbusClient.read_holding_registers(endereco,2)
        decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.BIG, wordorder = Endian.LITTLE)

        return decoder.decode_32bit_float()

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos
        """
        # Atualização das labels específicas
        if 'Velocidade_saida_ar' in self.ids:
            self.ids.Velocidade_saida_ar.text = f"{round(self._meas['values']['Velocidade_saida_ar'],2)} m/s"
        
        if 'Vazao_saida_ar' in self.ids:
            self.ids.Vazao_saida_ar.text = f"{round(self._meas['values']['Vazao_saida_ar'],2)} m³/s"
        
        if 'Temperatura' in self.ids:
            self.ids.Temperatura.text = f"{round(self._meas['values']['Temperatura'],2)} °C"

        # Atualização do nível do termômetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['Temperatura']/45*self.ids.termometro.size[1])

        # Atualização do gráfico
        self._graph.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['Temperatura']),0)

    def liga_motor(self):

        with self._lock:
            partida_ativa = self._modbusClient.read_holding_registers(1216,1)[0]

            if partida_ativa == 1 or partida_ativa == 2 or partida_ativa == 3:
                self._modbusClient.write_single_register(1316,1)
                pass

    def liga_motor(self):

        with self._lock:
            desliga_ativa = self._modbusClient.read_holding_registers(1216,1)[0]

            if desliga_ativa == 1 or desliga_ativa == 2 or desliga_ativa == 3:
                self._modbusClient.write_single_register(1316,1)
                pass