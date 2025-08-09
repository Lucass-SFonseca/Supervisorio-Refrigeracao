from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from persistence import DBWriter
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

class HistoricoPopup(Popup):
    """
    Popup para busca e exibição de dados históricos do banco.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db = DBWriter()

    def buscar_dados(self):
        """Busca dados no banco e exibe na área de resultados.
        """
        try:
            inicio = self.ids.txt_inicio.text.strip()
            fim = self.ids.txt_fim.text.strip()

            if not inicio or not fim:
                self.ids.lbl_resultado.text = "[color=ff0000]Preencha as duas datas[/color]"
                return

            dt_inicio = datetime.strptime(inicio, "%d/%m/%Y %H:%M:%S")
            dt_fim = datetime.strptime(fim, "%d/%m/%Y %H:%M:%S")

            resultados = self._db.get_range(dt_inicio, dt_fim)

            if not resultados:
                self.ids.lbl_resultado.text = "[color=ff0000]Nenhum registro encontrado[/color]"
                return

            tabela = GridLayout(cols=1, size_hint_y=None)
            tabela.bind(minimum_height=tabela.setter('height'))

            for reg in resultados:
                linha = f"{reg['id']} | {reg['timestamp'].strftime('%d/%m/%Y %H:%M:%S')} | {reg['data']}"
                tabela.add_widget(Label(text=linha, size_hint_y=None, height=25))

            scroll = ScrollView()
            scroll.add_widget(tabela)

            self.ids.area_resultado.clear_widgets()
            self.ids.area_resultado.add_widget(scroll)

        except Exception as e:
            self.ids.lbl_resultado.text = f"[color=ff0000]Erro: {e}[/color]"