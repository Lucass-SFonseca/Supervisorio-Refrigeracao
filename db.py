"""
Objetos do SQLAlchemy Core para conexão e operação do Banco de Dados
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import json
from datetime import datetime
from threading import Lock
from sqlalchemy import Column, Integer, DateTime, Text

# Pasta para o banco
DB_FOLDER = "data"
os.makedirs(DB_FOLDER, exist_ok=True)

# Arquivo do banco
DB_FILE = os.path.join(DB_FOLDER, "db.data")

# String de conexão (com check_same_thread=False para threads)
DB_CONNECTION = f"sqlite:///{DB_FILE}"
engine = create_engine(DB_CONNECTION, echo=False, connect_args={"check_same_thread": False})

# Fábrica de sessões
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Classe base para os modelos
Base = declarative_base()

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

# Cria as tabelas no banco, caso não existam
Base.metadata.create_all(engine)

class DBWriter:
    """
    Classe para persistir e consultar medições no banco SQLite.
    """
    def __init__(self):
        self._lock = Lock()

    def save_measurement(self, timestamp: datetime, values: dict) -> int:
        """
        Grava um registro de medição.
        """
        session = SessionLocal()
        try:
            m = Measurement(timestamp=timestamp, data=json.dumps(values, default=str))
            with self._lock:
                session.add(m)
                session.commit()
                session.refresh(m)
            return m.id
        except Exception as e:
            session.rollback()
            print("Erro ao salvar medição:", e)
            return None
        finally:
            session.close()

    def get_range(self, start: datetime, end: datetime):
        """
        Busca medições entre duas datas.
        """
        session = SessionLocal()
        try:
            rows = session.query(Measurement)\
                          .filter(Measurement.timestamp.between(start, end))\
                          .order_by(Measurement.timestamp)\
                          .all()
            return [r.as_dict() for r in rows]
        finally:
            session.close()

    def get_tags_series(self, tags, start: datetime = None, end: datetime = None, limit: int = None):
        """
        Retorna um dicionário com listas alinhadas por timestamp para várias tags.
        out = {'timestamp': [..], 'tag1': [..], 'tag2': [..], ...}
        """
        session = SessionLocal()
        try:
            q = session.query(Measurement)
            if start and end:
                q = q.filter(Measurement.timestamp.between(start, end))
            q = q.order_by(Measurement.timestamp)
            if limit:
                q = q.limit(limit)

            rows = q.all()
            out = {t: [] for t in tags}
            ts = []
            for r in rows:
                payload = json.loads(r.data)
                ts.append(r.timestamp)
                for t in tags:
                    out[t].append(payload.get(t))
            out['timestamp'] = ts
            return out
        finally:
            session.close()
    
        
