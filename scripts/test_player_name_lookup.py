
from scoutlocal.reports.report_builder import find_player_id


# check player name lookup
for name in [
    "Akash Mishra",
    "Ricky Lallawmawma",
]:
    player_id = find_player_id(name)

    print(f"{name}: {player_id}")
