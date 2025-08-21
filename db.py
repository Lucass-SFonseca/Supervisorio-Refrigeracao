import os
import json
import threading
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import logging


# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


"""
Módulo de abstração para o banco de dados, utilizando SQLAlchemy ORM
com SQLite. Define a tabela de medições e fornece funções de escrita e
consulta de dados históricos.
"""
# Garantir que a pasta de dados exista
os.makedirs("data", exist_ok=True)

# Caminho do banco
DATABASE_PATH = "sqlite:///data/db.data"

# Configuração do engine
engine = create_engine(DATABASE_PATH, connect_args={"check_same_thread": False}, echo=False)

# Sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Base do ORM
Base = declarative_base()

# Lock global para evitar condições de corrida
_db_lock = threading.Lock()

class Measurement(Base):
    """
    Modelo genérico para guardar medições do CLP.
    Coluna 'data' guarda todas as tags lidas em formato JSON.
    """
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True)
    data = Column(Text)  # JSON string com todas as tags

    def as_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "data": json.loads(self.data)
        }

# Cria as tabelas no banco
Base.metadata.create_all(engine)

class DBWriter:
    """
    Classe para persistir e consultar medições no banco SQLite.
    """
    def save_measurement(self, timestamp, values):
        with SessionLocal() as session:
            try:
                data_json = json.dumps(values, default=str)
                m = Measurement(timestamp=timestamp, data=data_json)
                with _db_lock:
                    session.add(m)
                    session.commit()
                    session.refresh(m)
                return m.id
            except Exception as e:
                session.rollback()
                logging.error("Erro ao salvar medição: %s", e)
                return None

    def get_range(self, start: datetime, end: datetime):
        """
        Busca medições entre duas datas.
        """
        with SessionLocal() as session:
            try:
                results = (
                    session.query(Measurement)
                    .filter(Measurement.timestamp.between(start, end))
                    .order_by(Measurement.timestamp)
                    .all()
                )
                return [r.as_dict() for r in results]
            except Exception as e:
                logging.error("Erro ao buscar intervalo: %s", e)
                return []

    def get_tags_series(self, tags, start: datetime = None, end: datetime = None, limit: int = None):
        """
        Retorna um dicionário com listas alinhadas por timestamp para várias tags.
        out = {'timestamp': [..], 'tag1': [..], 'tag2': [..], ...}
        """
        with SessionLocal() as session:
            try:
                query = session.query(Measurement)
            # Permitir filtros independentes de start e end
                if start:
                    query = query.filter(Measurement.timestamp >= start)
                if end:
                    query = query.filter(Measurement.timestamp <= end)
                
                query = query.order_by(Measurement.timestamp)
                if limit:
                    query = query.limit(limit)
                results = query.all()
                
                series = {tag: [] for tag in tags}
                series["timestamp"] = []
                for r in results:
                    data = json.loads(r.data)
                    for tag in tags:
                        series[tag].append(data.get(tag))
                        series["timestamp"].append(r.timestamp)
                        
                return series
            except Exception as e:
                logging.error("Erro ao buscar séries de tags: %s", e)
                return {tag: [] for tag in tags} | {"timestamp": []}
        
        
