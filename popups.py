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

class HistTablePopup(Popup):
    def __init__(self, **kwargs):
        tags = kwargs.pop("tags", {})
        super().__init__(**kwargs)
        for key, value in tags.items():
            cb = LabeledCheckBoxHistTable()
            cb.ids.label.text = self.LABELS.get(key, key)
            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)
            
    def update_table(self, data, tags_info):
        self.ids.data_table.clear_widgets()
        if not data or len(data.get("timestamp", [])) == 0:
            self.ids.data_table.add_widget(Label(text="Nenhum dado encontrado para o período selecionado.", color=(0,0,0,1)))
            return

        # Create header row
        header_row = GridLayout(cols=len(tags_info) + 1, size_hint_y=None, height=dp(30))
        header_row.add_widget(Label(text="Timestamp", bold=True, color=(0,0,0,1)))
        for tag_name in tags_info:
            header_row.add_widget(Label(text=f"[{tag_name}\n({tags_info[tag_name]['unid']}]"), bold=True, color=(0,0,0,1))
        self.ids.data_table.add_widget(header_row)

        # Add data rows
        for i in range(len(data["timestamp"])):
            data_row = GridLayout(cols=len(tags_info) + 1, size_hint_y=None, height=dp(30))
            data_row.add_widget(Label(text=data["timestamp"][i].strftime("%d/%m/%Y %H:%M:%S"), color=(0,0,0,1)))
            for tag_name in tags_info:
                value = data[tag_name][i]
                data_row.add_widget(Label(text=f"{value:.2f}" if isinstance(value, (int, float)) else "-", color=(0,0,0,1)))
            self.ids.data_table.add_widget(data_row)
                       
class LabeledCheckBoxHistTable(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)