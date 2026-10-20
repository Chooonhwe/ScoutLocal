
# define metrics for each scouting role
SCOUTING_PROFILES = {
    "Full Back": [
        "tackles_won_per90",
        "interceptions_won_per90",
        "progressive_passes_per90",
        "progressive_carries_per90",
        "final_third_entries_per90",
    ],
    "Center Back": [
        "interceptions_won_per90",
        "total_clearances_per90",
        "shot_blocks_per90",
        "progressive_passes_per90",
        "completed_long_passes_per90",
    ],
    "Defensive Midfielder": [
        "tackles_won_per90",
        "interceptions_won_per90",
        "progressive_passes_per90",
        "completed_forward_passes_per90",
        "ball_recoveries_per90",
    ],
    "Central Midfielder": [
        "progressive_passes_per90",
        "progressive_carries_per90",
        "key_passes_per90",
        "completed_forward_passes_per90",
        "ball_recoveries_per90",
    ],
    "Attacking Midfielder": [
        "key_passes_per90",
        "shot_assists_per90",
        "progressive_passes_per90",
        "penalty_box_entries_per90",
        "non_penalty_goals_minus_xg",
    ],
    "Winger": [
        "progressive_carries_per90",
        "penalty_box_carry_entries_per90",
        "key_passes_per90",
        "shots_per90",
        "xg_per90",
    ],
    "Forward": [
        "shots_per90",
        "xg_per90",
        "shots_on_target",
        "non_penalty_xg",
        "key_passes_per90",
    ],
}


# get scouting metrics for a chosen role
def get_profile_metrics(position_group):
    if position_group not in SCOUTING_PROFILES:
        raise ValueError(
            f"No scouting profile for: {position_group}"
        )

    return SCOUTING_PROFILES[position_group]
