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
    is_long_pass,
    is_cross,
    is_shot_assist,
    is_goal_assist,
    is_key_pass,
    aggregate_passing,
)

from scoutlocal.metrics.carrying import is_progressive_carry
from scoutlocal.metrics.shooting import (
    is_shot_on_target,
    is_goal,
    is_shot_inside_box,
    get_non_penalty_xg,
    is_shot_body_part,
    aggregate_shooting,
)
# get statsbomb data
client = StatsBombOpenData()

# using this match to test first
events = client.events(3827336)
# look at shot events
shots = [
    event for event in events
    if event.get("type", {}).get("name") == "Shot"
]

print(f"Total shots: {len(shots)}")

# show the first shot
if shots:
    from pprint import pprint
    pprint(shots[0])
# check all shot outcomes
shot_outcomes = set()

for shot in shots:
    outcome = shot.get("shot", {}).get("outcome", {}).get("name")

    if outcome:
        shot_outcomes.add(outcome)

print("\nSHOT OUTCOMES\n")
print(shot_outcomes)

# see how many events there are
print("Total events:", len(events))


# find all the different event types
event_types = set()

for event in events:
    event_types.add(event["type"]["name"])

print("\nEVENT TYPES\n")
print(event_types)
# test shots on target
shots_on_target = [
    shot for shot in shots
    if is_shot_on_target(shot)
]

print("\nSHOOTING TEST\n")
print("Total shots:", len(shots))
print("Shots on target:", len(shots_on_target))

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
    on=[
        "player_id",
        "player_name",
        "team_name",
    ],
    how="left",
)

print(combined)


# add per 90 stats so playing time is more fair
print("\nPLAYER METRICS PER 90\n")

#combined = add_per90_metrics(combined)

print(combined)


# look at some passes and their locations
print("\nPASS LOCATIONS\n")

pass_count = 0

for event in events:
    if event["type"]["name"] != "Pass":
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print(
        "End:",
        event.get("pass", {}).get("end_location"),
    )
    print(
        "Length:",
        event.get("pass", {}).get("length"),
    )
    print(
        "Angle:",
        event.get("pass", {}).get("angle"),
    )
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

# make sure completed stats are not higher than attempts
assert (
    passing_metrics["completed_progressive_passes"]
    <= passing_metrics["progressive_passes"]
).all()

assert (
    passing_metrics["completed_penalty_box_entries"]
    <= passing_metrics["penalty_box_entries"]
).all()

assert (
    passing_metrics["completed_long_passes"]
    <= passing_metrics["long_passes"]
).all()
assert (
    passing_metrics["completed_crosses"]
    <= passing_metrics["crosses"]
).all()
assert (
    passing_metrics["key_passes"]
    == (
        passing_metrics["shot_assists"]
        + passing_metrics["goal_assists"]
    )
).all()
print(
    passing_metrics.sort_values(
        "passes",
        ascending=False,
    ).to_string(index=False)
)

# find some progressive passes
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
    # only checking 10 passes
    if progressive_count == 10:
        break

# find some passes that enter the penalty box
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
     # only checking 10 passes
    if box_entry_count == 10:
        break

# check statsbomb pass length and height
print("\nPASS LENGTH AND HEIGHT\n")

pass_count = 0

for event in events:
    if event.get("type", {}).get("name") != "Pass":
        continue

    pass_data = event.get("pass", {})

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print("End:", pass_data.get("end_location"))
    print("Length:", pass_data.get("length"))

    print(
        "Height:",
        pass_data.get("height", {}).get("name"),
    )

    print(
        "Completed:",
        pass_data.get("outcome") is None,
    )

    print()

    pass_count += 1

    # only checking 15 passes
    if pass_count == 15:
        break


# find some long passes
print("\nLONG PASSES\n")

long_pass_count = 0

for event in events:
    if not is_long_pass(event):
        continue

    pass_data = event["pass"]

    print("Player:", event["player"]["name"])
    print("Start:", event["location"])
    print("End:", pass_data["end_location"])
    print("Length:", pass_data["length"])

    print(
        "Height:",
        pass_data.get("height", {}).get("name"),
    )

    print(
        "Completed:",
        pass_data.get("outcome") is None,
    )

    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )

    print()

    long_pass_count += 1

    # only checking 15 passes
    if long_pass_count == 15:
        break

# find some crosses
print("\nCROSSES\n")

cross_count = 0

for event in events:
    if event.get("type", {}).get("name") != "Pass":
        continue

    pass_data = event.get("pass", {})

    if not pass_data.get("cross"):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print("End:", pass_data.get("end_location"))

    print(
        "Completed:",
        pass_data.get("outcome") is None,
    )

    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )

    print(
        "Pass type:",
        pass_data.get("type", {}).get("name"),
    )

    print()

    cross_count += 1

    # only checking 15 crosses
    if cross_count == 15:
        break

    # check what statsbomb gives for shot assists
print("\nSHOT ASSISTS\n")

shot_assist_count = 0

for event in events:
    if event.get("type", {}).get("name") != "Pass":
        continue

    pass_data = event.get("pass", {})

    if not pass_data.get("shot_assist"):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print("End:", pass_data.get("end_location"))

    print(
        "Completed:",
        pass_data.get("outcome") is None,
    )

    print(
        "Goal assist:",
        pass_data.get("goal_assist"),
    )

    print(
        "Assisted shot ID:",
        pass_data.get("assisted_shot_id"),
    )

    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )

    print()

    shot_assist_count += 1

    # only checking 15 shot assists
    if shot_assist_count == 15:
        break

    # check goal assists
print("\nGOAL ASSISTS\n")

goal_assist_count = 0

for event in events:
    if event.get("type", {}).get("name") != "Pass":
        continue

    pass_data = event.get("pass", {})

    if not pass_data.get("goal_assist"):
        continue

    print("Player:", event["player"]["name"])
    print("Start:", event.get("location"))
    print("End:", pass_data.get("end_location"))

    print(
        "Shot assist:",
        pass_data.get("shot_assist"),
    )

    print(
        "Goal assist:",
        pass_data.get("goal_assist"),
    )

    print(
        "Assisted shot ID:",
        pass_data.get("assisted_shot_id"),
    )

    print(
        "Play pattern:",
        event.get("play_pattern", {})
        .get("name"),
    )

    print()

    goal_assist_count += 1

print("Total goal assists:", goal_assist_count)

print("\nCARRY EXAMPLE")

for event in events:
    if event.get("type", {}).get("name") == "Carry":
        print(event)
        break

print("\nLONGEST CARRY EXAMPLES")

carry_examples = []

for event in events:
    if event.get("type", {}).get("name") != "Carry":
        continue

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    if not start or not end:
        continue

    distance = (
        (end[0] - start[0]) ** 2
        + (end[1] - start[1]) ** 2
    ) ** 0.5

    carry_examples.append(
        (
            distance,
            event.get("player", {}).get("name"),
            start,
            end,
            event.get("play_pattern", {}).get("name"),
        )
    )

carry_examples.sort(reverse=True)

for carry in carry_examples[:10]:
    print(carry)

print("\nPROGRESSIVE CARRY EXAMPLES")

count = 0

for event in events:
    if is_progressive_carry(event):
        print(
            event.get("player", {}).get("name"),
            event.get("location"),
            event.get("carry", {}).get("end_location"),
        )

        count += 1

        if count == 10:
            break

from scoutlocal.metrics.carrying import is_forward_carry

print("\nFORWARD CARRY TEST")

total_carries = 0
forward_carries = 0
progressive_carries = 0

for event in events:
    if event.get("type", {}).get("name") != "Carry":
        continue

    total_carries += 1

    if is_forward_carry(event):
        forward_carries += 1

    if is_progressive_carry(event):
        progressive_carries += 1

print("Total carries:", total_carries)
print("Forward carries:", forward_carries)
print("Progressive carries:", progressive_carries)

assert forward_carries <= total_carries
assert progressive_carries <= total_carries

from scoutlocal.metrics.carrying import is_final_third_carry_entry

print("\nFINAL THIRD CARRY ENTRY TEST")

final_third_entries = 0

for event in events:
    if is_final_third_carry_entry(event):
        final_third_entries += 1

print("Final third carry entries:", final_third_entries)

assert final_third_entries <= total_carries

from scoutlocal.metrics.carrying import is_penalty_box_carry_entry

print("\nPENALTY BOX CARRY ENTRY TEST")

penalty_box_carry_entries = 0

for event in events:
    if is_penalty_box_carry_entry(event):
        penalty_box_carry_entries += 1

print("Penalty box carry entries:", penalty_box_carry_entries)

assert penalty_box_carry_entries <= total_carries

from scoutlocal.metrics.carrying import (
    get_carry_distance,
    get_forward_carry_distance,
)

print("\nCARRY DISTANCE TEST")

total_distance = 0.0
forward_distance = 0.0

for event in events:
    total_distance += get_carry_distance(event)
    forward_distance += get_forward_carry_distance(event)

print("Total carry distance:", round(total_distance, 2))
print("Forward carry distance:", round(forward_distance, 2))

assert total_distance >= 0
assert forward_distance >= 0
assert forward_distance <= total_distance + 0.000001

from scoutlocal.metrics.carrying import aggregate_carrying

print("\nCARRYING AGGREGATION TEST")

carrying_metrics = aggregate_carrying(events)

print(
    carrying_metrics.sort_values(
        "progressive_carries",
        ascending=False,
    ).head(10).to_string(index=False)
)

assert carrying_metrics["carries"].sum() == total_carries

assert (
    carrying_metrics["forward_carries"].sum()
    == forward_carries
)

assert (
    carrying_metrics["progressive_carries"].sum()
    == progressive_carries
)

assert (
    carrying_metrics["final_third_carry_entries"].sum()
    == final_third_entries
)

assert (
    carrying_metrics["penalty_box_carry_entries"].sum()
    == penalty_box_carry_entries
)

assert abs(
    carrying_metrics["carry_distance"].sum()
    - total_distance
) < 0.000001

assert abs(
    carrying_metrics["forward_carry_distance"].sum()
    - forward_distance
) < 0.000001

# test goals
goals = [
    shot for shot in shots
    if is_goal(shot)
]

print("\nGOALS TEST\n")
print("Total goals:", len(goals))
# test shots inside penalty box
inside_box_shots = [
    shot for shot in shots
    if is_shot_inside_box(shot)
]

print("\nSHOTS INSIDE BOX TEST\n")
print("Shots inside box:", len(inside_box_shots))
print("Shots outside box:", len(shots) - len(inside_box_shots))

# test non penalty xg
total_xg = sum(
    shot.get("shot", {}).get("statsbomb_xg", 0.0)
    for shot in shots
)

non_penalty_xg = sum(
    get_non_penalty_xg(shot)
    for shot in shots
)

print("\nNON PENALTY XG TEST\n")
print(f"Total xG: {total_xg:.2f}")
print(f"Non penalty xG: {non_penalty_xg:.2f}")
print(f"Penalty xG: {total_xg - non_penalty_xg:.2f}")

# test shot body parts
body_parts = set()

for shot in shots:
    body_part = shot.get("shot", {}).get("body_part", {}).get("name")

    if body_part:
        body_parts.add(body_part)

print("\nSHOT BODY PART TEST\n")

for body_part in sorted(body_parts):
    count = sum(
        is_shot_body_part(shot, body_part)
        for shot in shots
    )

    print(f"{body_part}: {count}")

    # test shooting aggregation
shooting_df = aggregate_shooting(events)

print("\nSHOOTING AGGREGATION TEST\n")
print(
    shooting_df.sort_values(
        "shots_on_target",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal shots on target:", shooting_df["shots_on_target"].sum())
# test player goals aggregation
print("\nPLAYER GOALS TEST\n")

print(
    shooting_df[shooting_df["goals"] > 0][
        ["player_name", "team_name", "goals"]
    ].to_string(index=False)
)

print("\nTotal goals:", shooting_df["goals"].sum())
# test player shots inside box aggregation
print("\nPLAYER SHOTS INSIDE BOX TEST\n")

print(
    shooting_df[
        ["player_name", "shots_inside_box"]
    ].sort_values(
        "shots_inside_box",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal shots inside box:", shooting_df["shots_inside_box"].sum())
# test player non penalty xg aggregation
print("\nPLAYER NON PENALTY XG TEST\n")

print(
    shooting_df[
        ["player_name", "non_penalty_xg"]
    ].sort_values(
        "non_penalty_xg",
        ascending=False
    ).to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

print(
    "\nTotal non penalty xg:",
    f"{shooting_df['non_penalty_xg'].sum():.2f}"
)

# test player headed shots aggregation
print("\nPLAYER HEADED SHOTS TEST\n")

print(
    shooting_df[
        ["player_name", "headed_shots"]
    ].sort_values(
        "headed_shots",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal headed shots:", shooting_df["headed_shots"].sum())

# testinng player left foot shots aggregation
print("\nPLAYER LEFT FOOT SHOTS TEST\n")

print(
    shooting_df[
        ["player_name", "left_footed_shots"]
    ].sort_values(
        "left_footed_shots",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal left foot shots:", shooting_df["left_footed_shots"].sum())

# test player right foot shots aggregation
print("\nPLAYER RIGHT FOOT SHOTS TEST\n")

print(
    shooting_df[
        ["player_name", "right_footed_shots"]
    ].sort_values(
        "right_footed_shots",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal right foot shots:", shooting_df["right_footed_shots"].sum())

# test player total shots aggregation
print("\nPLAYER TOTAL SHOTS TEST\n")

print(
    shooting_df[
        ["player_name", "total_shots"]
    ].sort_values(
        "total_shots",
        ascending=False
    ).to_string(index=False)
)

print("\nTotal shots:", shooting_df["total_shots"].sum())

# test player shooting accuracy
print("\nPLAYER SHOOTING ACCURACY TEST\n")

print(
    shooting_df[
        ["player_name", "total_shots", "shots_on_target", "shooting_accuracy"]
    ].sort_values(
        "shooting_accuracy",
        ascending=False
    ).to_string(index=False)
)

# test player goal conversion rate
print("\nPLAYER GOAL CONVERSION RATE TEST\n")

print(
    shooting_df[
        ["player_name", "total_shots", "goals", "goal_conversion_rate"]
    ].sort_values(
        "goal_conversion_rate",
        ascending=False
    ).to_string(index=False)
)

# test player xg per shot
print("\nPLAYER XG PER SHOT TEST\n")

print(
    shooting_df[
        ["player_name", "total_shots", "total_xg", "xg_per_shot"]
    ].sort_values(
        "xg_per_shot",
        ascending=False
    ).to_string(index=False)
)

# test player goals minus xg
print("\nPLAYER GOALS MINUS XG TEST\n")

print(
    shooting_df[
        ["player_name", "goals", "total_xg", "goals_minus_xg"]
    ].sort_values(
        "goals_minus_xg",
        ascending=False
    ).to_string(index=False)
)
# test player non penalty goals minus xg
print("\nPLAYER NON PENALTY GOALS MINUS XG TEST\n")

print(
    shooting_df[
        [
            "player_name",
            "non_penalty_goals",
            "non_penalty_xg",
            "non_penalty_goals_minus_xg",
        ]
    ].sort_values(
        "non_penalty_goals_minus_xg",
        ascending=False
    ).to_string(index=False)
)