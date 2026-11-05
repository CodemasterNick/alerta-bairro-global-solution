# Alerta Bairro — CitizenTech (MongoDB)

Protótipo acadêmico para registrar ocorrências comunitárias de alagamento e consultar dados meteorológicos públicos. Relaciona-se aos ODS 11 e 13.

## Atenção: Compass não é o servidor
MongoDB Compass é a interface gráfica. Para o banco local, instale e inicie o **MongoDB Community Server**. Alternativamente, use um cluster MongoDB Atlas. No Compass, conecte com `mongodb://localhost:27017/`.

## Preparação (Windows PowerShell)
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edite `.env` se necessário. A coleção `occurrences` no banco `alerta_bairro` será criada automaticamente no primeiro cadastro.

## Executar
```powershell
python app.py
```
Acesse http://127.0.0.1:5000. Para o módulo TCP, em outro terminal execute `python socket_server.py`.

## Endpoints
- GET `/api/ocorrencias` — lista (200)
- GET `/api/ocorrencias/<id>` — consulta (200/400/404)
- POST `/api/ocorrencias` — cria (201/400)
- PUT `/api/ocorrencias/<id>` — atualiza (200/400/404)
- DELETE `/api/ocorrencias/<id>` — exclui (200/400/404)
- GET `/api/clima` — Open-Meteo (200/400/502)

Exemplo POST:
```json
{"location":"Rua de exemplo","description":"Água acumulada após chuva","severity":"moderada"}
```
Gravidade: `baixa`, `moderada`, `alta`. Status: `aberta`, `em_verificacao`, `resolvida`.

## Modelo de dados
Banco `alerta_bairro`, coleção `occurrences`. Documentos têm `_id` (ObjectId), `location`, `description`, `severity`, `status`, `created_at` e `updated_at`. PyMongo é usado diretamente, sem ORM.

## Segurança
1. Consultas MongoDB usam filtros construídos com chaves fixas e valores validados; não aceitam operadores enviados pelo usuário.
2. A interface usa `textContent`, reduzindo risco de XSS.
3. URI e credenciais ficam no `.env`, ignorado pelo Git. Coleta mínima e logs sem conteúdo dos relatos.
Também há validação de tipo/tamanho, lista permitida de gravidade/status e mensagens de erro genéricas.

## Testes e limitações
Testar CRUD, JSON inválido, campos ausentes, valores não permitidos, ID inválido/inexistente, MongoDB desligado, API externa indisponível e TCP desligado. Limitações: relatos não verificados, sem autenticação/moderação e coordenadas climáticas fixas. Para produção seriam necessários autenticação, moderação, HTTPS e política de retenção.

## Evidência e uso de IA
Acrescente ao relatório evidência real do problema com fonte e data; não apresente exemplos fictícios como evidência real. Declare o uso do ChatGPT como apoio de planejamento, estruturação e depuração; revise e saiba explicar o código.
