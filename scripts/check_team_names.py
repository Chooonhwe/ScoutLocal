
from collections import defaultdict

from scoutlocal.data.statsbomb import StatsBombOpenData


# load indian super league matches
client = StatsBombOpenData()

matches = client.matches(1238, 108)

# collect team names from match records
team_names = defaultdict(set)
suspicious_matches = []

for match in matches:
    match_id = match["match_id"]

    home = match.get("home_team") or {}
    away = match.get("away_team") or {}

    for team in [home, away]:
        team_id = team.get("home_team_id") or team.get("away_team_id")
        team_name = team.get("home_team_name") or team.get("away_team_name")

        if team_id is not None and team_name:
            team_names[team_id].add(team_name)

    # find matches involving suspicious team names
    names = [
        home.get("home_team_name"),
        away.get("away_team_name"),
    ]

    if "SC Delhi" in names or "Hyderabad" in names:
        suspicious_matches.append(match_id)

print("\nTEAM NAMES FROM MATCH RECORDS\n")

for team_id, names in sorted(team_names.items()):
    print(team_id, sorted(names))

print("\nSUSPICIOUS MATCH EVENT TEAMS\n")

# inspect actual event team ids and names
for match_id in suspicious_matches:
    events = client.events(match_id)

    event_teams = set()

    for event in events:
        team = event.get("team") or {}

        if team.get("id") is not None:
            event_teams.add(
                (team.get("id"), team.get("name"))
            )

    print(
        "Match:",
        match_id,
        "Event teams:",
        sorted(event_teams),
    )
