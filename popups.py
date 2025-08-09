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
            self.ids.lbl_result.text = "[color=ff3333]Formato inválido: use DD/MM/AAAA HH:MM:SS[/color]"
            return

        session = Session()
        try:
            results = session.query(Medidas).filter(Medidas.data_hora.between(start_dt, end_dt)).order_by(Medidas.data_hora).all()
        finally:
            session.close()

        grid = self.ids.results_grid
        grid.clear_widgets()

        if not results:
            grid.add_widget(Label(text="Nenhum dado encontrado nesse intervalo."))
            return

        # Cabeçalho com nomes das colunas (exceto id/data_hora)
        col_names = [col.name for col in Medidas.__table__.columns if col.name not in ('id', 'data_hora')]
        header = " | ".join(["ID", "Data/Hora"] + col_names)
        grid.add_widget(Label(text=header, size_hint_y=None, height=28, bold=True))

        for med in results:
            row = [str(med.id), med.data_hora.strftime("%d/%m/%Y %H:%M:%S")]
            for col in col_names:
                val = getattr(med, col)
                if val is None:
                    row.append("")
                else:
                    # Formata floats com 2 casas
                    try:
                        row.append(f"{val:.2f}")
                    except Exception:
                        row.append(str(val))
            grid.add_widget(Label(text=" | ".join(row), size_hint_y=None, height=24))