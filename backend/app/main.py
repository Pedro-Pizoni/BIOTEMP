from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BioTemp API", description="Monitoramento de temperatura de refrigeradores")


def buscar_equipamento(db: Session, equipamento_id: int) -> models.Equipamento:
    equipamento = db.get(models.Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return equipamento


def validar_limites(dados: schemas.EquipamentoEntrada):
    if dados.temp_min >= dados.temp_max:
        raise HTTPException(status_code=400, detail="A temperatura mínima deve ser menor que a máxima")


def temperatura_fora_do_limite(equipamento, temperatura) -> bool:
    return temperatura < equipamento.temp_min or temperatura > equipamento.temp_max


def registrar_alerta(db: Session, equipamento, nova, anterior):
    temp = nova.temperatura
    estava_fora = anterior is not None and temperatura_fora_do_limite(equipamento, anterior.temperatura)

    if temperatura_fora_do_limite(equipamento, temp) and not estava_fora:
        if temp > equipamento.temp_max:
            tipo = "TEMPERATURA_ALTA"
            mensagem = f"Temperatura {temp:.1f} °C acima do máximo ({equipamento.temp_max:.1f} °C)"
        else:
            tipo = "TEMPERATURA_BAIXA"
            mensagem = f"Temperatura {temp:.1f} °C abaixo do mínimo ({equipamento.temp_min:.1f} °C)"
        db.add(models.Alerta(equipamento_id=equipamento.id, tipo=tipo, mensagem=mensagem, valor=temp))
        db.commit()


@app.post("/medicoes", response_model=schemas.MedicaoRegistrada, status_code=201)
def registrar_medicao(dados: schemas.MedicaoEntrada, db: Session = Depends(get_db)):
    equipamento = buscar_equipamento(db, dados.equipamento_id)
    if not equipamento.ativo:
        raise HTTPException(status_code=400, detail="Equipamento está desativado")

    anterior = (db.query(models.Medicao)
                .filter(models.Medicao.equipamento_id == equipamento.id)
                .order_by(models.Medicao.id.desc())
                .first())

    medicao = models.Medicao(**dados.model_dump())
    db.add(medicao)
    db.commit()
    db.refresh(medicao)

    registrar_alerta(db, equipamento, medicao, anterior)

    resposta = schemas.MedicaoSaida.model_validate(medicao).model_dump()
    resposta["fora_do_limite"] = temperatura_fora_do_limite(equipamento, medicao.temperatura)
    return resposta


@app.get("/medicoes", response_model=list[schemas.MedicaoSaida])
def listar_medicoes(equipamento_id: int | None = None, limite: int = 50, db: Session = Depends(get_db)):
    consulta = db.query(models.Medicao)
    if equipamento_id is not None:
        consulta = consulta.filter(models.Medicao.equipamento_id == equipamento_id)
    return consulta.order_by(models.Medicao.id.desc()).limit(limite).all()


@app.get("/medicoes/{medicao_id}", response_model=schemas.MedicaoSaida)
def consultar_medicao(medicao_id: int, db: Session = Depends(get_db)):
    medicao = db.get(models.Medicao, medicao_id)
    if medicao is None:
        raise HTTPException(status_code=404, detail="Medição não encontrada")
    return medicao


@app.delete("/medicoes/{medicao_id}", status_code=204)
def excluir_medicao(medicao_id: int, db: Session = Depends(get_db)):
    medicao = db.get(models.Medicao, medicao_id)
    if medicao is None:
        raise HTTPException(status_code=404, detail="Medição não encontrada")
    db.delete(medicao)
    db.commit()


@app.post("/equipamentos", response_model=schemas.EquipamentoSaida, status_code=201)
def cadastrar_equipamento(dados: schemas.EquipamentoEntrada, db: Session = Depends(get_db)):
    validar_limites(dados)
    equipamento = models.Equipamento(**dados.model_dump())
    db.add(equipamento)
    db.commit()
    db.refresh(equipamento)
    return equipamento


@app.get("/equipamentos", response_model=list[schemas.EquipamentoSaida])
def listar_equipamentos(db: Session = Depends(get_db)):
    return db.query(models.Equipamento).order_by(models.Equipamento.id).all()


@app.get("/equipamentos/{equipamento_id}", response_model=schemas.EquipamentoSaida)
def consultar_equipamento(equipamento_id: int, db: Session = Depends(get_db)):
    return buscar_equipamento(db, equipamento_id)


@app.put("/equipamentos/{equipamento_id}", response_model=schemas.EquipamentoSaida)
def atualizar_equipamento(equipamento_id: int, dados: schemas.EquipamentoEntrada,
                          db: Session = Depends(get_db)):
    validar_limites(dados)
    equipamento = buscar_equipamento(db, equipamento_id)
    for campo, valor in dados.model_dump().items():
        setattr(equipamento, campo, valor)
    db.commit()
    db.refresh(equipamento)
    return equipamento


@app.delete("/equipamentos/{equipamento_id}", status_code=204)
def remover_equipamento(equipamento_id: int, db: Session = Depends(get_db)):
    equipamento = buscar_equipamento(db, equipamento_id)
    db.query(models.Alerta).filter(models.Alerta.equipamento_id == equipamento_id).delete()
    db.query(models.Medicao).filter(models.Medicao.equipamento_id == equipamento_id).delete()
    db.delete(equipamento)
    db.commit()


@app.get("/alertas", response_model=list[schemas.AlertaSaida])
def listar_alertas(equipamento_id: int | None = None, limite: int = 50, db: Session = Depends(get_db)):
    consulta = db.query(models.Alerta)
    if equipamento_id is not None:
        consulta = consulta.filter(models.Alerta.equipamento_id == equipamento_id)
    return consulta.order_by(models.Alerta.id.desc()).limit(limite).all()


pasta_frontend = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=pasta_frontend, html=True), name="frontend")
