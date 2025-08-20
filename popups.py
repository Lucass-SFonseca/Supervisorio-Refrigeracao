from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
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
        """
        Método que atualiza os nicks - AGORA DEFINIDO
        """
        print("Método update_nicknames() chamado!")
        # Adicione aqui a lógica de atualização
        if hasattr(self, 'tags') and self.tags:
            print("Tags disponíveis:", list(self.tags.keys()))
        try:
            if hasattr(self, 'tags') and self.tags:
                print("Tags disponíveis para atualização:", list(self.tags.keys()))
                
                # Atualiza cada widget individualmente
                widget_map = {
                    'calores': 'Temperatura',
                    'pot': 'Potencia_ativa', 
                    'vel': 'Velocidade_saida_ar',
                    'crnt': 'Corrente_media'
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
                            else:
                                print(f"nick_label não encontrado em {widget_id}")
                    
            else:
                print("Tags não disponíveis para atualização")
                
        except Exception as e:
            print(f"Erro ao atualizar nicks: {e}")
            import traceback
            traceback.print_exc()