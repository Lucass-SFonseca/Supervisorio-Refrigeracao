from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder


class MainApp(App):
    """
    Classe com o aplicativo
    """
    def build(self):
        """
        Método que gera o aplicativo com o Widget principal
        """
        #self._widget = MainWidget(scan_time=1000, server_ip='127.0.0.1', server_port=5020,
        self._widget = MainWidget(scan_time=1000, server_ip='10.15.30.183',server_port=502,
        modbus_addrs={
            'Velocidade_saida_ar': {'addr': 712, 'tipo': 'FP', 'scale': 1},
            'Vazao_saida_ar': {'addr': 714, 'tipo': 'FP', 'scale': 1},
            'Temperatura': {'addr': 710, 'tipo': 'FP', 'scale': 1},
            'Med_demanda': {'addr': 1205, 'tipo': 'FP', 'scale': 1},
            'Velocidade_compresor': {'addr': 1236, 'tipo': 'FP', 'scale': 1},
            'Alarme_Temperatura_baixa': {'addr': 1231, 'tipo': 'FP', 'scale': 1},
            'Corrente_media': {'addr': 845, 'tipo': 'FP', 'scale': 1000},  # A → mA
            'DDP_fases': {'addr': 840, 'tipo': 'FP', 'scale': 1},
            'temp_rolamento': {'addr': 700, 'tipo': 'FP', 'scale': 1},
            'Corrente_comp': {'addr': 726, 'tipo': 'FP', 'scale': 1000},    # A → mA
            'Potencia_ativa': {'addr': 735, 'tipo': 'FP', 'scale': 1},
            'potencia_aparente': {'addr': 743, 'tipo': 'FP', 'scale': 1},
            'fator_de_pontencis': {'addr': 747, 'tipo': 'FP', 'scale': 1},
            've.frequencia': {'addr': 830, 'tipo': '4X', 'div': 100, 'scale': 1}
        }
        )

        return self._widget
    
    def on_stop(self):
        """
        Método executado quando a aplicação é fechada
        """
        self._widget.stopRefresh()

if __name__ == '__main__':
    Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(),rulesonly=True)
    Builder.load_string(open("popups.kv", encoding="utf-8").read(),rulesonly=True)
    MainApp().run()

    #Em relação ao vídeo, vai mudar banco de dados, mudar imagem e atuação