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
        self._widget = MainWidget(scan_time=1000, server_ip='127.0.0.1', server_port=5020,
        #self._widget = MainWidget(scan_time=1000, server_ip='10.15.30.183',server_port=502,
        modbus_addrs = {
            'temp_enrolamento_R_motor': {'addr': 700, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            'temp_enrolamento_S_motor': {'addr': 702, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            'temp_enrolamento_T_motor': {'addr': 704, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            'temperatura_carcaca': {'addr': 706, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            'corrente_R': {'addr': 840, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'valor': 1, 'unid': 'A'},
            'corrente_S': {'addr': 841, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'valor': 1, 'unid': 'A'},
            'corrente_T': {'addr': 842, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'valor': 1, 'unid': 'A'},
            'corrente_N': {'addr': 843, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'valor': 1, 'unid': 'A'},
            'corrente_media': {'addr': 845, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'valor': 1, 'unid': 'A'},
            'tensao_RS': {'addr': 847, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'unid': 'V'},
            'tensao_ST': {'addr': 848, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'unid': 'V'},
            'tensao_TR': {'addr': 849, 'tipo': '4X', 'l/e': 'l', 'div': 10, 'unid': 'V'},
            'potencia_aparente_total': {'addr': 863, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VA'},
            'potencia_aparente_r': {'addr': 860, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VA'},
            'potencia_aparente_s': {'addr': 861, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VA'},
            'potencia_aparente_t': {'addr': 862, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VA'},
            'potencia_reativa_total': {'addr': 859, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VAr'},
            'potencia_reativa_r': {'addr': 856, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VAr'},
            'potencia_reativa_s': {'addr': 857, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VAr'},
            'potencia_reativa_t': {'addr': 858, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'VAr'},
            'potencia_ativa_total': {'addr': 855, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'W'},
            'potencia_ativa_r': {'addr': 852, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'W'},
            'potencia_ativa_s': {'addr': 853, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'W'},  
            'potencia_ativa_t': {'addr': 854, 'tipo': '4X', 'l/e': 'l', 'div': 1, 'unid': 'W'},
            'rot_motor': {'addr': 884, 'tipo': 'FP', 'l/e': 'l', 'div': 1, 'valor': 1, 'unid': 'RPM'},
            'torque_motor': {'addr': 1422, 'tipo': 'FP', 'l/e': 'l', 'div': 1, 'valor': 1, 'unid': 'N*m'},
            'Temperatura_saida': {'addr': 710, 'tipo': 'FP', 'l/e': 'l', 'div': 1, 'valor': 1, 'unid': '°C'},
            'Vazao_saida_ar': {'addr': 714, 'tipo': 'FP', 'l/e': 'l', 'div': 1, 'unid': 'm^3/h'},
            'Velocidade_saida_ar': {'addr': 712, 'tipo': 'FP', 'l/e': 'l', 'div': 1, 'unid': 'm/s'},
            've.tit02': {'addr': 1218, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            've.tit01': {'addr': 1220, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': '°C'},
            've.pit01': {'addr': 1222, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': 'PSI'},
            've.pit02': {'addr': 1224, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': 'PSI'},
            've.pit03': {'addr': 1226, 'tipo': 'FP', 'l/e': 'l', 'div': 10, 'unid': 'mmH2O'},
            've.nv_escreve': {'addr': 1310, 'tipo': 'FP', 'l/e': 'l/e', 'div': 1, 'unid': '%'},
            've.habilita': { 'addr': 1330, 'tipo': '4X','div':	1, 'bit': 3}
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