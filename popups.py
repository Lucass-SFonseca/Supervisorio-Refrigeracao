from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
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

            # Monta colunas e dados
            colunas = ["Timestamp"] + list(resultados[0]["data"].keys())
            dados = []
            for reg in resultados:
                linha = [reg["timestamp"].strftime("%d/%m/%Y %H:%M:%S")]
                linha.extend([reg["data"][tag] for tag in reg["data"].keys()])
                dados.append(linha)

            # Abre novo popup com tabela
            TabelaPopup(colunas, dados).open()

        except Exception as e:
            self.ids.lbl_resultado.text = f"[color=ff0000]Erro: {e}[/color]"

    
class TabelaPopup(Popup):
    def __init__(self, colunas, dados, **kwargs):
        super().__init__(**kwargs)
        self.title = "Resultados da Busca"
        self.size_hint = (0.95, 0.95)

        # Layout da tabela
        tabela = GridLayout(cols=len(colunas),
                            size_hint=(None, None),
                            spacing=2,
                            padding=2)
        tabela.bind(minimum_height=tabela.setter('height'))
        tabela.bind(minimum_width=tabela.setter('width'))

        
        # Cabeçalho com fundo cinza
        for col in colunas:
            header = Label(
                text=f"[b]{col}[/b]",
                markup=True,
                size_hint=(None, None),
                size=(150, 30),
                color=(1, 1, 1, 1)
            )
            with header.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.2, 0.2, 0.2, 1)  # cinza escuro
                header._rect = Rectangle(size=header.size, pos=header.pos)
                header.bind(size=lambda inst, val: setattr(header._rect, 'size', val))
                header.bind(pos=lambda inst, val: setattr(header._rect, 'pos', val))
            tabela.add_widget(header)

        max_chars_timestamp = 19  # timestamp completo (ex: dd/mm/yyyy hh:mm:ss)
        max_chars_valores = 9    # demais colunas

        for i, reg in enumerate(dados):
            bg_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (1, 1, 1, 1)
            for j, valor in enumerate(reg):
                texto = str(valor)
                if j == 0:  # coluna do timestamp
                    if len(texto) > max_chars_timestamp:
                        texto = texto[:max_chars_timestamp] + "..."
                    largura = 180  # largura maior para timestamp
                else:
                    if len(texto) > max_chars_valores:
                        texto = texto[:max_chars_valores] + "..."
                    largura = 150  # largura padrão

                cell = Label(
                    text=texto,
                    size_hint=(None, None),
                    size=(largura, 25),
                    color=(0, 0, 0, 1)
                )
                with cell.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(*bg_color)
                    cell._rect = Rectangle(size=cell.size, pos=cell.pos)
                    cell.bind(size=lambda inst, val: setattr(cell._rect, 'size', val))
                    cell.bind(pos=lambda inst, val: setattr(cell._rect, 'pos', val))
                tabela.add_widget(cell)


        # ScrollView dupla
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=True)
        scroll.add_widget(tabela)

        # Layout final do popup
        layout = BoxLayout(orientation="vertical", spacing=5)
        layout.add_widget(scroll)

        btn_fechar = Button(text="Fechar", size_hint_y=None, height=40)
        btn_fechar.bind(on_release=self.dismiss)
        layout.add_widget(btn_fechar)

        self.add_widget(layout)

