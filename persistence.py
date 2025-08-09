import json
from datetime import datetime
from threading import Lock
from db import SessionLocal, engine, Base
from models import Measurement

# Cria as tabelas no banco, caso não existam
Base.metadata.create_all(engine)

class DBWriter:
    """
    Classe para persistir e consultar medições no banco SQLite.
    """
    def __init__(self):
        self._lock = Lock()

    def save_measurement(self, timestamp: datetime, values: dict) -> int:
        """Grava um registro de medição."""
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
        """Busca medições entre duas datas."""
        session = SessionLocal()
        try:
            rows = session.query(Measurement)\
                          .filter(Measurement.timestamp.between(start, end))\
                          .order_by(Measurement.timestamp)\
                          .all()
            return [r.as_dict() for r in rows]
        finally:
            session.close()

    def get_tag_series(self, tag: str, start: datetime = None, end: datetime = None, limit: int = None):
        """Retorna uma lista de (timestamp, valor) para uma tag específica."""
        session = SessionLocal()
        try:
            q = session.query(Measurement)
            if start and end:
                q = q.filter(Measurement.timestamp.between(start, end))
            q = q.order_by(Measurement.timestamp)
            if limit:
                q = q.limit(limit)

            rows = q.all()
            series = []
            for r in rows:
                data = json.loads(r.data)
                if tag in data:
                    series.append((r.timestamp, data[tag]))
            return series
        finally:
            session.close()
