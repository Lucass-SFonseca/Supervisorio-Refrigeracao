from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Medidas(Base):
    __tablename__ = 'medidas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_hora = Column(DateTime, default=datetime.now)

    # Exemplo de colunas (adicione as que precisar, seguindo o padrão)
    temp_enrolamento_R_motor = Column(Float)
    temp_enrolamento_S_motor = Column(Float)
    temp_enrolamento_T_motor = Column(Float)
    temperatura_carcaca = Column(Float)
    corrente_R = Column(Float)
    corrente_S = Column(Float)
    corrente_T = Column(Float)
    corrente_N = Column(Float)
    corrente_media = Column(Float)
    tensao_RS = Column(Float)
    tensao_ST = Column(Float)
    tensao_TR = Column(Float)
    potencia_aparente_total = Column(Float)
    potencia_aparente_r = Column(Float)
    potencia_aparente_s = Column(Float)
    potencia_aparente_t = Column(Float)
    potencia_reativa_total = Column(Float)
    potencia_reativa_r = Column(Float)
    potencia_reativa_s = Column(Float)
    potencia_reativa_t = Column(Float)
    potencia_ativa_total = Column(Float)
    potencia_ativa_r = Column(Float)
    potencia_ativa_s = Column(Float)
    potencia_ativa_t = Column(Float)
    rot_motor = Column(Float)
    torque_motor = Column(Float)
    Temperatura_saida = Column(Float)
    Vazao_saida_ar = Column(Float)
    Velocidade_saida_ar = Column(Float)
    ve_tit02 = Column(Float)
    ve_tit01 = Column(Float)
    ve_pit01 = Column(Float)
    ve_pit02 = Column(Float)
    ve_pit03 = Column(Float)

# Configura o banco e cria a tabela (SQLite)
engine = create_engine("sqlite:///medidas.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

def criar_tabela():
    Base.metadata.create_all(engine)
