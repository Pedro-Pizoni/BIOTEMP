from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Double, ForeignKey, Integer, String

from .database import Base


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    localizacao = Column(String(100))
    temp_min = Column(Double, nullable=False, default=2)
    temp_max = Column(Double, nullable=False, default=8)
    ativo = Column(Boolean, nullable=False, default=True)


class Medicao(Base):
    __tablename__ = "medicoes"

    id = Column(Integer, primary_key=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    temperatura = Column(Double, nullable=False)
    umidade = Column(Double)
    data_hora = Column(DateTime, nullable=False, default=datetime.now)


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    tipo = Column(String(30), nullable=False)
    mensagem = Column(String(200), nullable=False)
    valor = Column(Double)
    data_hora = Column(DateTime, nullable=False, default=datetime.now)
