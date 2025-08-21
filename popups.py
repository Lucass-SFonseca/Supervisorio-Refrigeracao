from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from datetime import datetime
from db import DBWriter
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

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

class LabeledChangeBoxDataGraph(BoxLayout):
    pass

class DataGraphPopup(Popup):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax
    def update_nicknames(self):
        """
        Atualiza os textos dos checkboxes com os nicks das tags
        """
        try:
            if hasattr(self, 'tags') and self.tags:
                print("Tags disponíveis para atualização:", list(self.tags.keys()))
                
                # MAPEAMENTO CORRETO - use os nomes EXATOS das suas tags
                widget_map = {
                    'calores': 'Temperatura_saida',      # ← Nome exato da tag
                    'pot': 'potencia_ativa_total',       # ← Nome exato da tag  
                    'vel': 'Velocidade_saida_ar',        # ← Nome exato da tag
                    'crnt': 'corrente_media'             # ← Nome exato da tag
                }
                
                for widget_id, tag_name in widget_map.items():
                    if tag_name in self.tags:
                        nick = self.tags[tag_name].get('nick', tag_name)
                        print(f"Atualizando {widget_id} com nick: {nick}")
                        
                        # Atualiza diretamente o texto do nick_label
                        if hasattr(self.ids, widget_id):
                            widget = self.ids[widget_id]
                            if hasattr(widget.ids, 'nick_label'):
                                widget.ids.nick_label.text = nick
                                print(f"✅ {widget_id} -> {nick}")
                            else:
                                print(f"❌ nick_label não encontrado em {widget_id}")
                        else:
                            print(f"❌ Widget {widget_id} não encontrado")
                    else:
                        print(f"❌ Tag {tag_name} não encontrada nas tags disponíveis")
                        
            else:
                print("❌ Tags não disponíveis para atualização")
                
        except Exception as e:
            print(f"❌ Erro ao atualizar nicks: {e}")
            import traceback
            traceback.print_exc()

class HistTablePopup(Popup):
    def __init__(self, **kwargs):
        tags = kwargs.pop("tags", {})
        super().__init__(**kwargs)
        self.bind(on_open=lambda *a: self._populate_checkboxes(tags))
        for key, value in tags.items():
            cb = LabeledCheckBoxHistTable()
            cb.ids.label.text = key
            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)
    
    def _populate_checkboxes(self, tags):
        self.ids.sensores.clear_widgets()
        for key, value in tags.items():
            cb = LabeledCheckBoxHistTable()
            cb.ids.label.text = key
            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)
            
    def update_table(self, data, tags_info):
        self.ids.data_table.clear_widgets()
        if not data or len(data.get("timestamp", [])) == 0:
            self.ids.data_table.add_widget(Label(
                text="Nenhum dado encontrado.", color=(0,0,0,1)))
            return

        # Cabeçalho
        header_row = GridLayout(cols=len(tags_info) + 1,
                                size_hint_y=None, height=dp(30))
        header_row.add_widget(Label(text="Timestamp", bold=True, color=(0,0,0,1)))
        for tag_name in tags_info:
            txt = f"{self.LABELS.get(tag_name, tag_name)}\n({tags_info[tag_name]['unid']})"
            header_row.add_widget(Label(text=txt, bold=True, color=(0,0,0,1)))
        self.ids.data_table.add_widget(header_row)

        # Linhas de dados
        for i in range(len(data["timestamp"])):
            data_row = GridLayout(cols=len(tags_info) + 1,
                                  size_hint_y=None, height=dp(30))
            ts = data["timestamp"][i]
            ts_fmt = ts.strftime("%d/%m/%Y %H:%M:%S")
            data_row.add_widget(Label(text=ts_fmt, color=(0,0,0,1)))
            for tag_name in tags_info:
                value = data[tag_name][i]
                txt = f"{value:.2f}" if isinstance(value, (int, float)) else "-"
                data_row.add_widget(Label(text=txt, color=(0,0,0,1)))
            self.ids.data_table.add_widget(data_row)
                       
class LabeledCheckBoxHistTable(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)