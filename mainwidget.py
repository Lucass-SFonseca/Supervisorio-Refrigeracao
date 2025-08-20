from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, Leitura, DataGraphPopup, HistGraphPopup, LabeledCheckBoxHistGraph, Atuacao
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from kivy_garden.graph import LinePlot
from threading import Thread, Lock
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from timeseriesgraph import TimeSeriesGraph
from db import DBWriter
import random

class MainWidget(BoxLayout):
    """
    Widget principal da aplicação
    """
    _updateThread = None
    _updateWidgets = True
    _tags={}
    _max_points = 20


    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        super().__init__()
        self._db = DBWriter()
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
        self._leitura=Leitura()
        self._atuacao=Atuacao()
        self.motor_ligado = False
        self.tipo_partida = 3

        self._tags = kwargs.get('modbus_addrs')
        for key,value in self._tags.items():
            plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key]['color'] = plot_color

        self._graph = DataGraphPopup(self._max_points, self._tags['Temperatura_saida']['color'])
        self._hgraph = HistGraphPopup(tags=self._tags)

        
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
                mid = self._db.save_measurement(self._meas['timestamp'], self._meas['values'])
                if mid:
                    print(f"[DB] Medição salva ID={mid} em {self._meas['timestamp']}")
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)

    def readData(self):
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            if value["tipo"] == 'FP':
                self._meas['values'][key] = round(self.readFloatPoint(self._tags[key]["addr"])/value["div"], 2)
            if value["tipo"] == '4X':
                self._meas['values'][key] = round(self._modbusClient.read_holding_registers(self._tags[key]["addr"], 1)[0]/value["div"],2)

    def readFloatPoint(self, endereco):
        with self._lock:
            leitura = self._modbusClient.read_holding_registers(endereco,2)
            decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.Big, wordorder = Endian.Little)

        return decoder.decode_32bit_float()

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos
        """
        # Atualização das labels específicas
        if 'Velocidade_saida_ar' in self.ids:
            self.ids.Velocidade_saida_ar.text = f"{self._meas['values']['Velocidade_saida_ar']/self._tags['Velocidade_saida_ar']['div']}"
        
        if 'Vazao_saida_ar' in self.ids:
            self.ids.Vazao_saida_ar.text = f"{self._meas['values']['Vazao_saida_ar']/self._tags['Vazao_saida_ar']['div']}"
        
        if 'Temperatura' in self.ids:
            self.ids.Temperatura.text = f"{self._meas['values']['Temperatura_saida']} °C"

        if 'pit01' in self.ids:
            self.ids.pit01.text = f"{self._meas['values']['ve.pit01']}"
        
        if 'pit02' in self.ids:
            self.ids.pit02.text = f"{self._meas['values']['ve.pit02']}"

        if 'pit03' in self.ids:
            self.ids.pit03.text = f"{self._meas['values']['ve.pit03']}"
        
        if 'tit01' in self.ids:
            self.ids.tit01.text = f"{self._meas['values']['ve.tit01']}"
        
        if 'tit02' in self.ids:
            self.ids.tit02.text = f"{self._meas['values']['ve.tit02']}"

        # Atualização das labels do popup Leituras
        for key,value in self._tags.items():
            if self.ids.get(key) != None:
                self.ids[key].text = str(self._meas['values'][key])
            elif self._leitura.ids.get(key) != None:
                self._leitura.ids[key].text = str(self._meas['values'][key])

        # Atualização do nível do termômetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['Temperatura_saida']/45*self.ids.termometro.size[1])

        # Atualização do widget de vazão
        self.ids.lb_vazao.size = (self.ids.vazao.size[0] * self._meas['values']['Vazao_saida_ar'] / 1000, self.ids.vazao.size[1])

        # Atualização do gráfico    
        self._graph.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['Temperatura_saida']),0)

    def stopRefresh(self):
        self._updateWidgets = False
    
    def getDataDB(self):
        print("DEBUG: getDataDB foi chamada.")
        """ 
        Coleta os parâmetros do popup e desenha o histórico das tags selecionadas
        """
        print("DEBUG sensores children:")
        for w in self._hgraph.ids.sensores.children:
            print(" -", type(w), getattr(w, "ids", None))

        try:
            print(f"DEBUG: Valor de txt_init_time: {self._hgraph.ids.txt_init_time.text}")
            print(f"DEBUG: Valor de txt_final_time: {self._hgraph.ids.txt_final_time.text}")
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            print(f"DEBUG: init_t formatado: {init_t}")
            print(f"DEBUG: final_t formatado: {final_t}")

            selected = []
            print("DEBUG: Iterando sobre checkboxes...")
            for w in self._hgraph.ids.sensores.children:
                print(f"DEBUG: Checkbox encontrada: {w.id}, active: {w.ids['checkbox'].active}")
                if w.ids["checkbox"].active:
                    selected.append(w.id)
            print(f"DEBUG: Checkboxes selecionadas: {selected}")

            dados = self._db.get_tags_series(selected, init_t, final_t)
            print("DEBUG histórico (dados brutos):")
            print(dados)

            if not dados or len(dados.get("timestamp", [])) == 0:
                print("DEBUG: Nenhum dado retornado do DB ou timestamp vazio.")
                return
            self._hgraph.ids.graph.clearPlots()
            
            for key in selected:
                print(f"DEBUG: Plotando {key} com dados: {dados[key]}")
                p = LinePlot(line_width=1.5, color=self._tags[key]["color"])
                # Certifique-se de que os dados são numéricos e que o enumerate está correto
                # O problema pode estar aqui se os valores forem None ou não numéricos
                valid_points = [(i, v) for i, v in enumerate(dados[key]) if v is not None]
                p.points = valid_points
                self._hgraph.ids.graph.add_plot(p)

            self._hgraph.ids.graph.xmax = len(dados["timestamp"])
            # update_x_labels aceita datetime; ótimo para formatar HH:MM:SS
            self._hgraph.ids.graph.update_x_labels(dados["timestamp"])
            print("DEBUG: Gráfico atualizado com sucesso.")

        except Exception as e:
            import traceback
            print("Erro na getDataDB:", e)
            traceback.print_exc()
            
    def parseDTString(self, datetime_str):
        """ 
        Método que converte a string inserida pelo usuário para o formato utilizado
        na busca de dados do DB
        """
        try:
            d=datetime.strptime(datetime_str,'%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro ", e.args)
            

    def selecionarPartida(self, tipo):
        self.tipo_partida = tipo

        # Atualiza imagens dos botões
        self.ids.btn_soft.background_normal = "imgs/botao_soft_press.jpg" if tipo == 1 else "imgs/botao_soft.jpg"
        self.ids.btn_inversor.background_normal = "imgs/botao_inv_press.jpg" if tipo == 2 else "imgs/botao_inv.jpg"
        self.ids.btn_direta.background_normal = "imgs/botao_direta_press.jpg" if tipo == 3 else "imgs/botao_direta.jpg"

        with self._lock:
            self._modbusClient.write_single_register(1324,tipo)

    def alternaMotor(self):
        if self.motor_ligado:
            self.desligar()
            self.ids.botao_toggle.background_normal = "imgs/icone_mot_off.jpg"
            self.motor_ligado = False
        else:
            self.ligar()
            self.ids.botao_toggle.background_normal = "imgs/icone_mot_on.jpg"
            self.motor_ligado = not self.motor_ligado

    def ligar(self):
        if self.tipo_partida == 1:
            self.ligaSoft()
        elif self.tipo_partida == 2:
            self.ligaInversor()
        elif self.tipo_partida == 3:
            self.ligaDireta()

    def desligar(self):
        if self.tipo_partida == 1:
            self.desligaSoft()
        elif self.tipo_partida == 2:
            self.desligaInversor()
        elif self.tipo_partida == 3:
            self.desligaDireta()

    def ligaDireta(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 0 and self._modbusClient.read_holding_registers(1319,1)[0] == 0:
                self._modbusClient.write_single_register(1319,1)
                pass

    def desligaDireta(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 0 and self._modbusClient.read_holding_registers(1319,1)[0] == 1:
                self._modbusClient.write_single_register(1319,0)
                pass

    def ligaSoft(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 1 and self._modbusClient.read_holding_registers(1316,1)[0] == 0:
                self._modbusClient.write_single_register(1316,1)
                pass

    def desligaSoft(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 1 and self._modbusClient.read_holding_registers(1316,1)[0] == 1:
                self._modbusClient.write_single_register(1316,0)
                pass

    def ligaInversor(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 2 and self._modbusClient.read_holding_registers(1312,1)[0] == 0:
                self._modbusClient.write_single_register(1312,1)
                pass

    def desligaInversor(self):

        with self._lock:

            if self._modbusClient.read_holding_registers(1216,1)[0] == 2 and self._modbusClient.read_holding_registers(1312,1)[0] == 1:
                self._modbusClient.write_single_register(1312,0)
                pass

    def variaFrequenciaMotor(self, *args):
        with self._lock:
            self._modbusClient.write_single_register(1313,args[1]/10)
            print("frequencia definida em: ", args[1]/10)
            pass
