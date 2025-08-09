"""
Objetos do SQLAlchemy Core para conexão e operação do Banco de Dados
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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
