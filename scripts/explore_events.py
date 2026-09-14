from scoutlocal.data.statsbomb import StatsBombOpenData


# Create the StatsBomb data client
client = StatsBombOpenData()


# Download all events from one match
# Match ID 3827336 = the match we are currently exploring
events = client.events(3827336)


# Check how many events exist in this match
print("Total events:", len(events))


# --------------------------------------------------
# 1. FIND ALL UNIQUE EVENT TYPES
# --------------------------------------------------

# A set stores unique values only
event_types = set()

# Go through every event
for event in events:

    # Get the event type, e.g. Pass, Shot, Carry
    event_type = event["type"]["name"]

    # Add it to our set
    event_types.add(event_type)


print("\nEVENT TYPES\n")
print(event_types)


# --------------------------------------------------
# 2. SEE THE STRUCTURE OF EACH EVENT TYPE
# --------------------------------------------------

print("\nEVENT STRUCTURES\n")

# sorted() puts the event types in alphabetical order
for event_type in sorted(event_types):

    # Find the first example of this event type
    example = next(
        event for event in events
        if event["type"]["name"] == event_type
    )

    # Print the event type
    print(event_type)

    # Show what fields exist inside that event
    print(example.keys())

    print()


# --------------------------------------------------
# 3. EXPLORE SPECIAL FIELDS INSIDE EVENTS
# --------------------------------------------------

print("\nNESTED EVENT FIELDS\n")

# Different event types contain their own special data
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
    "tactics"
]


# Check each special field
for field in special_fields:

    # Find the first event containing this field
    example = next(
        (
            event for event in events
            if field in event
        ),
        None
    )

    # Only print if we found one
    if example is not None:

        print(field)

        # Show the fields inside it
        print(example[field].keys())

        print()