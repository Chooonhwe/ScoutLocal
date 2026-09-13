from scoutlocal.data.statsbomb import StatsBombOpenData
import pandas as pd


def main():
    client = StatsBombOpenData()
    competitions = pd.DataFrame(client.competitions())

    columns = [
        "competition_id",
        "season_id",
        "country_name",
        "competition_name",
        "season_name",
    ]

    output = (
        competitions[columns]
        .drop_duplicates()
        .sort_values(["competition_name", "season_name"])
    )

    print(output.to_string(index=False))


if __name__ == "__main__":
    main()
