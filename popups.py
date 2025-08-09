from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
from db import Session, Medidas
from kivy.lang import Builder


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
        
class HistoricalDataPopup(Popup):
    def buscar_dados(self):
        start_str = self.ids.start_datetime.text.strip()
        end_str = self.ids.end_datetime.text.strip()
        try:
            start_dt = datetime.strptime(start_str, "%d/%m/%Y %H:%M:%S")
            end_dt = datetime.strptime(end_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            self._show_error("Formato de data inválido! Use DD/MM/AAAA HH:MM:SS")
            return

        session = Session()
        results = session.query(Medidas).filter(Medidas.data_hora.between(start_dt, end_dt)).all()
        session.close()

        grid = self.ids.results_grid
        grid.clear_widgets()

        if not results:
            grid.add_widget(Label(text="Nenhum dado encontrado nesse intervalo."))
            return

        # Cabeçalho
        headers = ["ID", "Data/Hora"] + [col.name for col in Medidas.__table__.columns if col.name not in ['id','data_hora']]
        header_text = " | ".join(headers)
        grid.add_widget(Label(text=header_text, bold=True))

        for med in results:
            linha = [str(med.id), med.data_hora.strftime("%d/%m/%Y %H:%M:%S")]
            for col in Medidas.__table__.columns:
                if col.name not in ['id','data_hora']:
                    valor = getattr(med, col.name)
                    linha.append(f"{valor:.2f}" if isinstance(valor, float) else str(valor))
            grid.add_widget(Label(text=" | ".join(linha)))

    def _show_error(self, msg):
        popup = Popup(title="Erro", content=Label(text=msg), size_hint=(0.6,0.4))
        popup.open()