# Start here

Your first milestone is intentionally small:

> Select one open competition and create a dataframe where one row = one player.

Do not build machine learning yet.

## Step 1
Install Python 3.11+ and VS Code.

## Step 2
Open this folder in VS Code.

## Step 3
Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

## Step 4
Install packages:

```bash
pip install -r requirements.txt
```

## Step 5
List competitions:

```bash
python scripts/list_competitions.py
```

Choose ONE competition-season pair first.

## Step 6
Build your first player dataset:

```bash
python scripts/build_player_metrics.py --competition-id 11 --season-id 90
```

The IDs above are just an example. Use IDs shown by the competition script.

## What success looks like
You should get a CSV with columns similar to:

- player_id
- player_name
- team_name
- minutes
- passes
- completed_passes
- shots
- carries
- pressures
- passes_per90
- shots_per90
- carries_per90
- pressures_per90

Once that works, commit it to GitHub.

Suggested commit:

```text
feat: build initial StatsBomb player metrics pipeline
```

Then we move to V0.2: position-aware percentiles.
