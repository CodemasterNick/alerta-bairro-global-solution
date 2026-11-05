# Alerta Bairro — Relatório da Global Solution

**Aluno:** [preencher] | **Disciplina:** Coding for Security

## Problema, cidadão e ODS
A proposta facilita o compartilhamento de relatos de pontos de alagamento por moradores, trabalhadores e estudantes. Complementar com evidência real (notícia, dado público ou observação documentada), fonte e data. Não tratar dados fictícios como evidência real. ODS 11 e 13.

## Arquitetura e dados
Interface HTML/CSS/JavaScript, API Flask, MongoDB via PyMongo sem ORM, Open-Meteo via requests/JSON e módulo TCP. Banco `alerta_bairro`, coleção `occurrences`, campos `_id`, `location`, `description`, `severity`, `status`, `created_at`, `updated_at`. Operações GET, POST, PUT e DELETE.

## Segurança
- Consultas indevidas: filtros construídos com chaves fixas e entradas validadas.
- XSS: renderização com `textContent`.
- Exposição de credenciais/dados: URI no `.env`, coleta mínima e logs sem texto dos relatos.

## Validação e limitações
[Inserir testes realmente executados e resultados.] Limitações: relatos não verificados, ausência de autenticação/moderação, coordenadas fixas e dependência de serviços externos.

## Uso de IA
Declarar que ChatGPT foi usado como apoio ao planejamento, estruturação inicial, explicação e depuração. O aluno deve revisar, testar e explicar o código.
