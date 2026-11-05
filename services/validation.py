ALLOWED_SEVERITIES = {"baixa", "moderada", "alta"}
ALLOWED_STATUSES = {"aberta", "em_verificacao", "resolvida"}
ALLOWED_FIELDS = {"location", "description", "severity", "status"}


def validate_occurrence(payload, partial=False):
    """Valida e normaliza os campos aceitos pela API."""
    errors = []
    data = {}

    unknown = set(payload.keys()) - ALLOWED_FIELDS
    if unknown:
        errors.append("Existem campos não permitidos.")

    required = {"location", "description", "severity"}
    if not partial:
        for field in required:
            if field not in payload:
                errors.append(f"O campo '{field}' é obrigatório.")

    if "location" in payload:
        value = payload["location"]
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 120:
            errors.append("Local deve ser um texto entre 1 e 120 caracteres.")
        else:
            data["location"] = value.strip()

    if "description" in payload:
        value = payload["description"]
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 500:
            errors.append("Descrição deve ser um texto entre 1 e 500 caracteres.")
        else:
            data["description"] = value.strip()

    if "severity" in payload:
        value = payload["severity"]
        if not isinstance(value, str) or value not in ALLOWED_SEVERITIES:
            errors.append("Gravidade deve ser baixa, moderada ou alta.")
        else:
            data["severity"] = value

    if "status" in payload:
        value = payload["status"]
        if not isinstance(value, str) or value not in ALLOWED_STATUSES:
            errors.append("Status deve ser aberta, em_verificacao ou resolvida.")
        else:
            data["status"] = value
    elif not partial:
        data["status"] = "aberta"

    return data, errors
