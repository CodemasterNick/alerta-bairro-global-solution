import logging
import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from database import (
    create_occurrence,
    delete_occurrence,
    get_occurrence,
    list_occurrences,
    update_occurrence,
)
from services.weather import get_weather
from services.validation import validate_occurrence
from services.socket_client import notify_tcp

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/alerta_bairro.log",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("alerta_bairro")

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Alerta Bairro"}), 200


@app.get("/api/ocorrencias")
def api_list_occurrences():
    try:
        rows = list_occurrences()
        logger.info("LISTAR_OCORRENCIAS | sucesso | quantidade=%s", len(rows))
        return jsonify(rows), 200
    except Exception:
        logger.exception("LISTAR_OCORRENCIAS | falha")
        return jsonify({"erro": "Não foi possível consultar as ocorrências."}), 500


@app.get("/api/ocorrencias/<occurrence_id>")
def api_get_occurrence(occurrence_id):
    try:
        row = get_occurrence(occurrence_id)
        if row is None:
            return jsonify({"erro": "Ocorrência não encontrada."}), 404
        return jsonify(row), 200
    except ValueError:
        return jsonify({"erro": "Identificador inválido."}), 400
    except Exception:
        logger.exception("BUSCAR_OCORRENCIA | falha | id=%s", occurrence_id)
        return jsonify({"erro": "Não foi possível consultar a ocorrência."}), 500


@app.post("/api/ocorrencias")
def api_create_occurrence():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"erro": "Envie um objeto JSON válido."}), 400

    data, errors = validate_occurrence(payload, partial=False)
    if errors:
        return jsonify({"erro": "Dados inválidos.", "detalhes": errors}), 400

    try:
        new_id = create_occurrence(data)
        logger.info("CRIAR_OCORRENCIA | sucesso | id=%s", new_id)
        notify_tcp({"event": "occurrence_created", "occurrence_id": new_id})
        created = get_occurrence(new_id)
        return jsonify(created), 201
    except Exception:
        logger.exception("CRIAR_OCORRENCIA | falha")
        return jsonify({"erro": "Não foi possível cadastrar a ocorrência."}), 500


@app.put("/api/ocorrencias/<occurrence_id>")
def api_update_occurrence(occurrence_id):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"erro": "Envie um objeto JSON válido."}), 400

    data, errors = validate_occurrence(payload, partial=True)
    if errors:
        return jsonify({"erro": "Dados inválidos.", "detalhes": errors}), 400
    if not data:
        return jsonify({"erro": "Informe ao menos um campo para atualizar."}), 400

    try:
        if get_occurrence(occurrence_id) is None:
            return jsonify({"erro": "Ocorrência não encontrada."}), 404
        update_occurrence(occurrence_id, data)
        logger.info("ATUALIZAR_OCORRENCIA | sucesso | id=%s", occurrence_id)
        notify_tcp({"event": "occurrence_updated", "occurrence_id": occurrence_id})
        return jsonify(get_occurrence(occurrence_id)), 200
    except ValueError:
        return jsonify({"erro": "Identificador inválido."}), 400
    except Exception:
        logger.exception("ATUALIZAR_OCORRENCIA | falha | id=%s", occurrence_id)
        return jsonify({"erro": "Não foi possível atualizar a ocorrência."}), 500


@app.delete("/api/ocorrencias/<occurrence_id>")
def api_delete_occurrence(occurrence_id):
    try:
        deleted = delete_occurrence(occurrence_id)
        if not deleted:
            return jsonify({"erro": "Ocorrência não encontrada."}), 404
        logger.info("EXCLUIR_OCORRENCIA | sucesso | id=%s", occurrence_id)
        notify_tcp({"event": "occurrence_deleted", "occurrence_id": occurrence_id})
        return jsonify({"mensagem": "Ocorrência excluída com sucesso."}), 200
    except ValueError:
        return jsonify({"erro": "Identificador inválido."}), 400
    except Exception:
        logger.exception("EXCLUIR_OCORRENCIA | falha | id=%s", occurrence_id)
        return jsonify({"erro": "Não foi possível excluir a ocorrência."}), 500


@app.get("/api/clima")
def api_weather():
    latitude = request.args.get("latitude", " -23.5505").strip()
    longitude = request.args.get("longitude", "-46.6333").strip()
    try:
        lat = float(latitude)
        lon = float(longitude)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("coordenadas fora do intervalo")
        weather = get_weather(lat, lon)
        logger.info("CONSULTAR_CLIMA | sucesso | lat=%s | lon=%s", lat, lon)
        return jsonify(weather), 200
    except ValueError:
        return jsonify({"erro": "Latitude ou longitude inválida."}), 400
    except Exception:
        logger.exception("CONSULTAR_CLIMA | falha")
        return jsonify({"erro": "Não foi possível consultar os dados climáticos."}), 502


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"erro": "Recurso não encontrado."}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"erro": "Método HTTP não permitido para este recurso."}), 405


if __name__ == "__main__":
    # debug=False evita expor detalhes internos em ambiente de demonstração.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
