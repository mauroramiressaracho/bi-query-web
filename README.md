# BI Query Web

MVP de um construtor visual de consultas SQL inspirado no BI/Query clássico.

## Objetivo

Permitir que o usuário:

1. conecte em um banco;
2. veja uma árvore de tabelas e colunas;
3. adicione tabelas ao canvas;
4. visualize relacionamentos;
5. selecione campos;
6. gere SQL automaticamente;
7. execute a consulta e visualize resultados.

O projeto nasce com suporte de arquitetura para Oracle e SQL Server, além de um modo `demo` para desenvolvimento sem banco.

## Stack

- Front-end: React + TypeScript + Vite
- Canvas visual: `@xyflow/react`
- Back-end: FastAPI
- Oracle: `oracledb`
- SQL Server: `pyodbc`

## Estrutura

```text
bi-query-web/
├─ frontend/
├─ backend/
├─ AGENTS.md
├─ docker-compose.yml
└─ README.md
```

## Rodando em modo demo

### Back-end

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS

uvicorn app.main:app --reload
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs

### Front-end

```bash
cd frontend
npm install
npm run dev
```

Front-end: http://localhost:5173

## Conexão Oracle

No `backend/.env`:

```env
DB_ENGINE=oracle
DB_HOST=servidor
DB_PORT=1521
DB_SERVICE=servico
DB_USER=usuario
DB_PASSWORD=senha
DB_SCHEMA=SCHEMA_RH
```

## Conexão SQL Server

```env
DB_ENGINE=sqlserver
DB_HOST=servidor
DB_PORT=1433
DB_DATABASE=banco
DB_USER=usuario
DB_PASSWORD=senha
DB_SCHEMA=dbo
ODBC_DRIVER=ODBC Driver 17 for SQL Server
```

## Segurança

O MVP impõe somente `SELECT` no endpoint de execução. Em produção, use uma conta de banco apenas de leitura e limite schemas/views expostos aos usuários.
