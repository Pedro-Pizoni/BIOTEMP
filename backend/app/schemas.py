from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EquipamentoEntrada(BaseModel):
    nome: str
    localizacao: str | None = None
    temp_min: float = 2
    temp_max: float = 8
    ativo: bool = True


class EquipamentoSaida(EquipamentoEntrada):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MedicaoEntrada(BaseModel):
    equipamento_id: int
    temperatura: float
    umidade: float | None = None


class MedicaoSaida(MedicaoEntrada):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data_hora: datetime


class MedicaoRegistrada(MedicaoSaida):
    fora_do_limite: bool


class AlertaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    equipamento_id: int
    tipo: str
    mensagem: str
    valor: float | None
    data_hora: datetime
