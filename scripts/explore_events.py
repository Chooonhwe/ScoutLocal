from scoutlocal.data.statsbomb import StatsBombOpenData
from scoutlocal.metrics.player_metrics import (
    aggregate_events,
    add_per90_metrics,
)
from scoutlocal.data.minutes import calculate_minutes


# get statsbomb data
client = StatsBombOpenData()

# using this match to test first
events = client.events(3827336)


# see how many events there are
print("Total events:", len(events))


# find all the different event types
event_types = set()

for event in events:
    event_types.add(event["type"]["name"])

print("\nEVENT TYPES\n")
print(event_types)


# check what each event type contains
print("\nEVENT STRUCTURES\n")

for event_type in sorted(event_types):

    example = next(
        event for event in events
        if event["type"]["name"] == event_type
    )

    print(event_type)
    print(example.keys())
    print()


# check what is inside the more important event types
print("\nNESTED EVENT FIELDS\n")

special_fields = [
    "pass",
    "shot",
    "carry",
    "duel",
    "dribble",
    "clearance",
    "interception",
    "goalkeeper",
    "substitution",
    "tactics",
]

for field in special_fields:

    example = next(
        (
            event for event in events
            if field in event
        ),
        None,
    )

    if example is not None:
        print(field)
        print(example[field].keys())
        print()


# make the basic player stats
print("\nPLAYER METRICS\n")

player_metrics = aggregate_events(events)

print(player_metrics)


# check starting 11
print("\nSTARTING XI\n")

for event in events:
    if event["type"]["name"] == "Starting XI":
        print(event)
        print()


# check who got subbed and when
print("\nSUBSTITUTIONS\n")

for event in events:
    if event["type"]["name"] == "Substitution":
        print(event)
        print()


# check when each half ended
print("\nHALF END\n")

for event in events:
    if event["type"]["name"] == "Half End":
        print(event)
        print()


# calculate how long everyone played
print("\nPLAYER MINUTES\n")

player_minutes = calculate_minutes(events)

print(player_minutes)


# put player stats and minutes together
print("\nPLAYER METRICS + MINUTES\n")

combined = player_metrics.merge(
    player_minutes,
    on=["player_id", "player_name", "team_name"],
    how="left",
)

print(combined)


# add per 90 stats so playing time is more fair
print("\nPLAYER METRICS PER 90\n")

combined = add_per90_metrics(combined)

print(combined)