from typing import Any, Dict, List

import requests

from config import PEXELS_API_KEY

BASE_URL = "https://api.pexels.com/v1"
TIMEOUT_SECONDS = 12


class PexelsServiceError(Exception):
    pass


def fetch_curated_photos(page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"page": page, "per_page": per_page}

    try:
        response = requests.get(
            f"{BASE_URL}/curated",
            headers=headers,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise PexelsServiceError("Tempo limite excedido ao consultar API do Pexels.") from exc
    except requests.RequestException as exc:
        raise PexelsServiceError(f"Falha de rede ao consultar API do Pexels: {exc}") from exc

    if response.status_code != 200:
        try:
            payload = response.json()
            details = payload.get("error", response.text)
        except ValueError:
            details = response.text
        raise PexelsServiceError(
            f"Erro da API Pexels (status {response.status_code}): {details}"
        )

    data = response.json()
    return data.get("photos", [])
