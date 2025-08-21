from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, Leitura, DataGraphPopup, HistTablePopup, LabeledCheckBoxHistTable, Atuacao
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from kivy_garden.graph import LinePlot
from threading import Thread, Lock
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
from timeseriesgraph import TimeSeriesGraph
from db import DBWriter
import random
from kivy_garden.graph import LinePlot



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

        self._selected_tag = "Temperatura_saida"
        self._graph = DataGraphPopup(self._max_points, self._tags['Temperatura_saida']['color'])
        self._htable = HistTablePopup(tags=self._tags)
        # GARANTIR que as tags são passadas
        self._graph.tags = self._tags
        print("Tags passadas para o gráfico:", list(self._tags.keys()))
        print("Tags disponíveis no sistema:")
        for key in self._tags.keys():
            print(f"  - {key}")
    
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
            print("Erro startdata: ", e.args)


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
            print("Erro updater: ",e.args)

    def readData(self):
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            if value["tipo"] == 'FP':
                self._meas['values'][key] = self.read_float_point(self._tags[key]["addr"])/value["div"]
            if value["tipo"] == '4X':
                self._meas['values'][key] = self._modbusClient.read_holding_registers(self._tags[key]["addr"], 1)[0]/value["div"]

    def read_float_point(self, endereco):
        with self._lock:
            for key,value in self._tags.items():
                if value["tipo"] == 'FP':
                    self._meas['values'][key] = round(self.readFloatPoint(self._tags[key]["addr"])/value["div"], 2)
                if value["tipo"] == '4X':
                    if self._tags[key].get('bit') != None:
                        self._meas['values'][key] = self.leitura_bit(self._tags[key]["addr"],self._tags[key]["bit"])
                    else:    
                        self._meas['values'][key] = round(self._modbusClient.read_holding_registers(self._tags[key]["addr"], 1)[0]/value["div"],2)

    def readFloatPoint(self, endereco):
        # with self._lock:
        leitura = self._modbusClient.read_holding_registers(endereco,2)
        decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.Big, wordorder = Endian.Little)

        return decoder.decode_32bit_float()

    def leitura_bit(self, addr, bit):
        leitura = self._modbusClient.read_holding_registers(addr, 1)
        decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.Big, wordorder = Endian.Little)

        lista1 = decoder.decode_bits()
        lista2 = decoder.decode_bits()

        lista_retorno = lista2+lista1

        return  lista_retorno[bit]
    
    def escrita_bit(self, addr, bit, valor_escrita):
        with self._lock:
            leitura = self._modbusClient.read_holding_registers(addr, 1)
        decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.Big, wordorder = Endian.Little)

        lista1 = decoder.decode_bits()
        lista2 = decoder.decode_bits()

        lista_clp = lista2+lista1

        lista_clp[bit] = valor_escrita

        builder = BinaryPayloadBuilder()
        builder.add_bits(lista_clp)
        
        with self._lock:
            self._modbusClient.write_multiple_registers(addr, builder.to_registers())
              
        pass

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos
        """
        # Atualização das labels específicas
        if 'Velocidade_saida_ar' in self.ids:
            self.ids.Velocidade_saida_ar.text = f"{self._meas['values']['Velocidade_saida_ar']/self._tags['Velocidade_saida_ar']['div']}"
        
        if 'Vazao_saida_ar' in self.ids:
            self.ids.Vazao_saida_ar.text = f"{self._meas['values']['Vazao_saida_ar']/self._tags['Vazao_saida_ar']['div']}"
        
        if 'Temperatura_saida' in self.ids:
            self.ids.Temperatura_saida.text = f"{round(self._meas['values']['Temperatura_saida'],2)} °C"
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
        self.ids.lb_vazao.size = (self.ids.vazao.size[0] * self._meas['values']['Vazao_saida_ar'] / 2000, self.ids.vazao.size[1])

        # Atualização do gráfico    
        if (self._selected_tag in self._meas['values']and self._meas['values'][self._selected_tag] is not None ):
            self._graph.ids.graph.updateGraph((self._meas['timestamp'], self._meas['values'][self._selected_tag]), 0)
    def get_tag_nicknames(self):
        """
        Retorna um dicionário com os nicks das tags
        """
        nicks = {}
        for key, value in self._tags.items():
            nicks[key] = value.get('nick', key)  # Usa o nick se existir, senão usa a chave
        return nicks
    def set_graph_variable(self, var_name, y_label=None):
        self._selected_tag = var_name

        # pega o nome legível da tag (ou usa a chave se não tiver 'label')
        nome_legivel = self._tags[var_name].get('label', var_name)

        # atualiza título do popup
        self._graph.title = f"Gráfico de {nome_legivel}"

        # Obtém limites
        ymin = self._tags[var_name].get('ymin', 0)
        ymax = self._tags[var_name].get('ymax', 50)

        # Configura limites no gráfico
        self._graph.ids.graph.ymin = ymin
        self._graph.ids.graph.ymax = ymax
        self._graph.ids.graph.y_ticks_major = ymax / 10
        self._graph.ids.graph.padding = 5

        # Ajusta rótulo do eixo Y (se não passar y_label, usa o label do dicionário)
        self._graph.ids.graph.ylabel = y_label if y_label else nome_legivel

        # Limpa e adiciona novo plot
        self._graph.ids.graph.clearPlots()
        new_plot = LinePlot(line_width=1.5, color=self._tags[var_name]['color'])
        self._graph.plot = new_plot
        self._graph.ids.graph.add_plot(new_plot)





    def stopRefresh(self):
        self._updateWidgets = False
        
    
    def getDataDB(self):
        """ 
        Busca dados do DB e preenche tabela 
        """
        try:
            init_t = self.parseDTString(self._htable.ids.txt_init_time.text)
            final_t = self.parseDTString(self._htable.ids.txt_final_time.text)

            if not init_t or not final_t or init_t >= final_t:
                print("Intervalo de datas inválido.")
                self._htable.update_table(None, None)
                return

            selected = []
            for w in self._htable.ids.sensores.children:
                if w.ids["checkbox"].active:
                    selected.append(w.id)

            if not selected:
                print("Nenhuma variável selecionada.")
                self._htable.update_table(None, None)
                return

            dados = self._db.get_tags_series(selected, init_t, final_t)
            self._htable.update_table(dados, {k: self._tags[k] for k in selected})
        except Exception as e:
            import traceback
            print("Erro na getDataDB:", e)
            traceback.print_exc()

            
    def parseDTString(self, datetime_str):
        """ Converte string do usuário em datetime """
        try:
            return datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
        except Exception as e:
            print("Erro ao converter data/hora:", e)
            return None

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

    def variaFrequenciaMotor(self, val):
        with self._lock:
            self._modbusClient.write_single_register(1313,int(val*10))
            print("frequencia definida em: ", val)
            pass

    def defineRampa(self, tipo ,val):

        if tipo == 1:

            with self._lock:
                self._modbusClient.write_single_register(1314, int(int(self.ids.roff_label.text)*10))
                self._modbusClient.write_single_register(1317, int(self.ids.roff_label.text))

        if tipo == 2:
            
            with self._lock:
                self._modbusClient.write_single_register(1315, int(int(self.ids.roff_label.text)*10))
                self._modbusClient.write_single_register(1318, int(self.ids.roff_label.text))

    def atuaAquecedor(self, sel):
        if sel == 1:
            self.escrita_bit(1329,4,1)
            print("Aquecedor 1 ligado")
        if sel == 2:
            self.escrita_bit(1329,6,1)
            print("Aquecedor 2 ligado")
        if sel == 3:
            self.escrita_bit(1329,4,0)
            self.escrita_bit(1329,5,1)
            print("Aquecedor 1 desligado")
        if sel == 4:
            self.escrita_bit(1329,6,0)
            self.escrita_bit(1329,7,1)
            print("Aquecedor 2 desligado")
        pass

    def defineCompressor(self, type):
        if type == 1:
            self.escrita_bit(1328,1,0)
            print("Compressor Scroll selecionado")
        if type == 2:
            self.escrita_bit(1328,1,1)
            print("Compressor Hermético selecionado")
        pass

    def ligaCT(self, value):
        if value == 1:
            self.escrita_bit(1328,4,1)
            print("Controle de temperatura ligado")
        if value == 2:
            self.escrita_bit(1328,4,0)
            self.escrita_bit(1329,0,1)
            print("Controle de temperatura desligado")
        pass

    def defineTemp(self, value):
        self._modbusClient.write_single_register(1338,int(value))
        print("Temperatura alvo definida em: ", value)
        pass

    def defineFreqCompressor(self, value):
        self._modbusClient.write_single_register(1236,int(value))
        print("Frequência do compressor definida em: ", value)
        pass