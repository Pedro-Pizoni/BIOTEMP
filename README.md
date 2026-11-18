# BioTemp – Monitoramento de Temperatura de Refrigerador Hospitalar

Sistema embarcado para monitorar a temperatura e a umidade de um refrigerador usado em ambiente hospitalar.
O ESP32 lê o sensor DHT22 e envia os dados por Wi-Fi para uma API REST em Python (FastAPI),
que grava as informações no MariaDB e disponibiliza uma página web para consulta.

```
ESP32 + DHT22  --Wi-Fi/HTTP (JSON)-->  API FastAPI  -->  MariaDB
                                            |
                                       Página web
```

> Protótipo acadêmico. Não é um equipamento de monitoramento hospitalar validado ou certificado.

## Estrutura

```
biotemp/
├── backend/
│   ├── app/
│   │   ├── main.py         rotas da API e regra de alertas
│   │   ├── database.py     conexão com o MariaDB
│   │   ├── models.py       tabelas
│   │   └── schemas.py      formato dos dados (JSON)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html          monitoramento
│   ├── equipamentos.html   cadastro de refrigeradores
│   └── css/style.css
├── database/schema.sql     criação do banco e das tabelas
├── firmware/biotemp_esp32/ código do ESP32
└── scripts/iniciar_mariadb.bat
```

## Tecnologias

| Tecnologia | Uso |
|---|---|
| ESP32 + C++ (Arduino) | Leitura do sensor e envio dos dados |
| DHT22 | Temperatura e umidade |
| Buzzer | Aviso sonoro quando a temperatura sai da faixa |
| Python + FastAPI | API REST |
| SQLAlchemy + PyMySQL | Acesso ao banco |
| MariaDB | Armazenamento |
| HTML, CSS e JavaScript | Interface web |

## Como executar

### 1. Banco de dados

Com o MariaDB rodando, execute o script uma única vez (no `cmd`, dentro da pasta `bin` do MariaDB):

```
mariadb -u root -p < C:\dev\biotemp\database\schema.sql
```

O script cria o banco `biotemp`, o usuário `biotemp` (senha `biotemp123`) e as tabelas.

### 2. API e página web

```
cd C:\dev\biotemp\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Página web: http://localhost:8000
- Documentação da API (Swagger): http://localhost:8000/docs

Se a porta 8000 estiver em uso, troque por outra (ex.: `--port 8001`).

### 3. Cadastro do refrigerador

Na página **Equipamentos**, cadastre o refrigerador e anote o **ID** exibido na tabela.
Esse número é configurado no ESP32 (`EQUIPAMENTO_ID` no arquivo `config.h`).

### 4. ESP32

| Componente | ESP32 |
|---|---|
| DHT22 – VCC / DATA / GND | 3V3 / GPIO 27 / GND |
| Buzzer ativo – (+) / (−) | GPIO 26 / GND |

No arquivo `firmware/biotemp_esp32/config.h`, configure o Wi-Fi (2,4 GHz), o endereço da API com o IP do
computador (`http://IP:PORTA/medicoes`) e o `EQUIPAMENTO_ID`. Bibliotecas necessárias no Arduino IDE:
**DHT sensor library** (Adafruit) e **ArduinoJson**. A API deve estar rodando com `--host 0.0.0.0`.

## API REST

| Método | Rota | Descrição |
|---|---|---|
| POST | /medicoes | Registrar uma nova medição |
| GET | /medicoes | Consultar medições (`?equipamento_id=1&limite=50`) |
| GET | /medicoes/{id} | Consultar uma medição específica |
| DELETE | /medicoes/{id} | Excluir uma medição de teste |
| POST | /equipamentos | Cadastrar um refrigerador |
| GET | /equipamentos | Listar refrigeradores |
| GET | /equipamentos/{id} | Consultar um refrigerador |
| PUT | /equipamentos/{id} | Atualizar dados, limites e situação (ativo/inativo) |
| DELETE | /equipamentos/{id} | Remover o refrigerador com suas medições e alertas |
| GET | /alertas | Consultar ocorrências (`?equipamento_id=1`) |

Medição enviada pelo ESP32:

```json
{ "equipamento_id": 1, "temperatura": 4.6, "umidade": 55.3 }
```

Resposta (`201 Created`):

```json
{ "id": 10, "equipamento_id": 1, "temperatura": 4.6, "umidade": 55.3,
  "data_hora": "2026-11-15T21:53:24", "fora_do_limite": false }
```

O campo `fora_do_limite` indica ao ESP32 se o buzzer deve ser ligado.

## Alertas

A cada medição, a temperatura é comparada com a faixa configurada no refrigerador (`temp_min` e `temp_max`).
Quando a temperatura sai da faixa, é registrado um alerta `TEMPERATURA_ALTA` ou `TEMPERATURA_BAIXA`.
Enquanto continuar fora, nenhum alerta novo é criado; um novo alerta só ocorre se ela voltar ao normal e sair novamente.

## Banco de dados

| Tabela | Campos |
|---|---|
| equipamentos | id, nome, localizacao, temp_min, temp_max, ativo |
| medicoes | id, equipamento_id, temperatura, umidade, data_hora |
| alertas | id, equipamento_id, tipo, mensagem, valor, data_hora |

## Interface web

- **Monitoramento:** temperatura e umidade atuais, situação (normal ou fora do limite), últimas medições e alertas. Atualiza a cada 10 segundos.
- **Equipamentos:** cadastro, edição dos limites de temperatura, ativação/desativação e remoção.
