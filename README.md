# ScoutLocal

Open-source football recruitment analytics for clubs working with limited data and resources.

## V0.1 goal
Turn legally available StatsBomb Open Data into a player-level scouting table with per-90 metrics.

## Current features
- List available StatsBomb open competitions
- Download match/event data directly from the StatsBomb Open Data GitHub repository
- Aggregate player actions
- Calculate basic per-90 metrics
- Export a clean CSV for later scouting analysis

## Planned next steps
1. Position groups
2. Percentile rankings
3. Role-fit scoring
4. Player similarity
5. Under-the-radar player detection
6. Interactive scouting dashboard

## Quick start

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/list_competitions.py
```

Pick one competition_id and season_id from the output, then:

```bash
python scripts/build_player_metrics.py --competition-id YOUR_ID --season-id YOUR_ID
```

The generated file will appear in:

```text
data/player_metrics.csv
```

## Data source
StatsBomb Open Data:
https://github.com/statsbomb/open-data

Use of StatsBomb open data should follow the repository's attribution requirements.
