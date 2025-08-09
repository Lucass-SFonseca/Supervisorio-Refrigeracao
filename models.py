from sqlalchemy import Column, Integer, DateTime, Text
from db import Base
import json

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
