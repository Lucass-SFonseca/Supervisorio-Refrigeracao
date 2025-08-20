from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from db import DBWriter
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class ModbusPopup(Popup):
    """
    Popup da configuração do tempo de varredura
    """
    _info_lb = None
    def __init__(self, server_ip, server_port, **kwargs):
        """
        Construtor da classe ModbusPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_porta.text = str(server_port)

    def setInfo(self, message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)
    
    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)


class ScanPopup(Popup):
    """
    Popup da configuração do tempo de varredura
    """
    def __init__(self, scantime, **kwargs):
        """
        Construtor da classe ScanPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)

class Leitura(Popup):
    """
    Popup de apresentação das leituras em tempo real
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Atuacao(Popup):
    """
    Popup dos botões de atuação
    """
    def _init_(self, **kwargs):
       """
       Construtor da classe
       """
       super()._init_(**kwargs)

class LabeledCheckBoxDataGraph(BoxLayout):
    pass

class DataGraphPopup(Popup):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax

class HistGraphPopup(Popup):
    # whitelist das 4 medidas
    ALLOWED = {
        'Temperatura_saida',
        'Velocidade_saida_ar',
        'potencia_ativa_total',  # mude para 'potencia_aparente_total' se preferir
        'corrente_media'
    }
    # nomes amigáveis
    LABELS = {
        'Temperatura_saida': 'Temperatura de saída',
        'Velocidade_saida_ar': 'Velocidade de saída de ar',
        'potencia_ativa_total': 'Potência total',
        'corrente_media': 'Corrente média'
    }

    def __init__(self, **kwargs):
        tags = kwargs.pop("tags", {})
        super().__init__(**kwargs)
        for key, value in tags.items():
            if key in self.ALLOWED:
                cb = LabeledCheckBoxHistGraph()
                cb.ids.label.text = self.LABELS.get(key, key)
                cb.ids.label.color = value['color']
                cb.id = key
                self.ids.sensores.add_widget(cb)
            

class LabeledCheckBoxHistGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)