from __future__ import annotations

from typing import Any
import requests

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


class StatsBombOpenData:
    """Small client for the public StatsBomb Open Data repository."""

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def _get_json(self, path: str) -> Any:
        url = f"{BASE_URL}/{path}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def competitions(self) -> list[dict]:
        return self._get_json("competitions.json")

    def matches(self, competition_id: int, season_id: int) -> list[dict]:
        return self._get_json(
            f"matches/{competition_id}/{season_id}.json"
        )

    def events(self, match_id: int) -> list[dict]:
        return self._get_json(f"events/{match_id}.json")
