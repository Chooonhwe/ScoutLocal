from scoutlocal.data.statsbomb import StatsBombOpenData
from scoutlocal.data.minutes import calculate_minutes
from scoutlocal.metrics.player_metrics import (
    aggregate_events,
    add_per90_metrics,
)


from scoutlocal.metrics.passing import (
    is_forward_pass,
    is_final_third_pass,
    is_final_third_entry,
    is_penalty_box_entry,
    is_progressive_pass,
    aggregate_passing,
)

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
        event
        for event in events
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
            event
            for event in events
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


# look at some passes and their locations
print("\nPASS LOCATIONS\n")

pass_count = 0

for event in events:
    if event["type"]["name"] != "Pass":
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print("End:", event.get("pass", {}).get("end_location"))
    print("Length:", event.get("pass", {}).get("length"))
    print("Angle:", event.get("pass", {}).get("angle"))
    print()

    pass_count += 1

    # only checking 5 passes
    if pass_count == 5:
        break


# find some forward passes
print("\nFORWARD PASSES\n")

forward_count = 0

for event in events:
    if not is_forward_pass(event):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event["location"])
    print("End:", event["pass"]["end_location"])
    print()

    forward_count += 1

    # only checking 5 passes
    if forward_count == 5:
        break


# find some passes that end in the final third
print("\nFINAL THIRD PASSES\n")

final_third_count = 0

for event in events:
    if not is_final_third_pass(event):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event["location"])
    print("End:", event["pass"]["end_location"])
    print()

    final_third_count += 1

    # only checking 5 passes
    if final_third_count == 5:
        break


# find some passes that enter the final third
print("\nFINAL THIRD ENTRIES\n")

final_third_entry_count = 0

for event in events:
    if not is_final_third_entry(event):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event["location"])
    print("End:", event["pass"]["end_location"])
    print()

    final_third_entry_count += 1

    # only checking 5 passes
    if final_third_entry_count == 5:
        break


# see what pass types statsbomb gives us
print("\nPASS TYPES\n")

pass_types = set()

for event in events:
    if event.get("type", {}).get("name") != "Pass":
        continue

    pass_type = (
        event
        .get("pass", {})
        .get("type", {})
        .get("name")
    )

    if pass_type:
        pass_types.add(pass_type)

print(pass_types)


# test all the passing stats
print("\nPASSING METRICS\n")

passing_metrics = aggregate_passing(events)

assert (
    passing_metrics["completed_penalty_box_entries"]
    <= passing_metrics["penalty_box_entries"]
).all()

assert (
    passing_metrics["completed_progressive_passes"]
    <= passing_metrics["progressive_passes"]
).all()
print(
    passing_metrics.sort_values(
        "passes",
        ascending=False,
    ).to_string(index=False)
)

print("\nPROGRESSIVE PASSES\n")

progressive_count = 0

for event in events:
    if not is_progressive_pass(event):
        continue

    start = event["location"]
    end = event["pass"]["end_location"]

    print("Player:", event["player"]["name"])
    print("Start:", start)
    print("End:", end)

    print(
        "Completed:",
        event["pass"].get("outcome") is None,
    )

    print(
        "Pass type:",
        event.get("pass", {})
        .get("type", {})
        .get("name"),
    )

    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )

    print()

    progressive_count += 1

    if progressive_count == 10:
        break

print("\nPENALTY BOX ENTRIES\n")

box_entry_count = 0

for event in events:
    if not is_penalty_box_entry(event):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event["location"])
    print("End:", event["pass"]["end_location"])
    print(
        "Completed:",
        event["pass"].get("outcome") is None,
    )
    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )
    print()

    box_entry_count += 1

    if box_entry_count == 10:
        break