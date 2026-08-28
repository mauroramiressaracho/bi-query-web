# AGENTS.md

## Produto

BI Query Web é um construtor visual de consultas SQL inspirado no BI/Query legado.

## Princípios

- Usuário de negócio não deve precisar escrever SQL.
- A árvore deve representar tabelas, views, colunas e relacionamentos.
- O sistema deve gerar SQL legível.
- Nunca armazenar senha de banco em código.
- Nunca permitir DDL/DML no executor visual.
- Priorizar conexão read-only.
- Toda nova funcionalidade deve funcionar no modo demo.

## Arquitetura

### Frontend
- React + TypeScript + Vite.
- Canvas visual com `@xyflow/react`.
- Componentes simples e tipados.
- Estado local no MVP; preparar serviços para futura store.

### Backend
- FastAPI.
- Drivers de banco isolados em `app/db`.
- Metadados normalizados em modelos próprios.
- SQL gerado no servidor, não confiando em SQL arbitrário vindo do front.

## Convenções

- Python: type hints em funções públicas.
- TypeScript: evitar `any`.
- APIs em `/api`.
- Erros HTTP devem ter mensagens claras.
- Sem secrets em commits.
- Mudanças de schema da aplicação devem ser documentadas.

## Próximas entregas

1. Relacionamentos manuais.
2. Filtros WHERE visuais.
3. JOIN INNER/LEFT configurável.
4. ORDER BY/GROUP BY/agregações.
5. Modelos salvos.
6. Camada semântica com nomes amigáveis.
7. Autenticação e permissões.
8. Exportação CSV/XLSX.
