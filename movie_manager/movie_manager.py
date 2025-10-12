import pandas as pd

ODS_file = "./src/GodZilla_Films.ods"
movie_sheet = "Movie List"


def load_movies_df() -> pd.DataFrame:
    """
    Returns the movies DataFrame from an ODS file
    """
    return pd.read_excel(ODS_file, sheet_name=movie_sheet, engine="odf")


def set_ownership(title: str, year: int, own_status: str) -> str:
    """
    Updates the 'Own' column for a movie to 'Yes' or 'No'.
    Returns a message describing the results.
    """

    # read ODS
    df = load_movies_df()
    df = df.reset_index(drop=True)
    df.index = range(1, len(df) + 1)

    # Normalize
    mask = (df["Year"].astype(int) == int(year)) & (
        df["Title"].str.lower() == title.lower()
    )
    print("Mask value: ", mask)

    if not mask.any():
        return f"ℹ️ Information: Could not find {title} ({year})"

    idx = df.index[mask][0]
    current_status = df.at[idx, "Own"].strip().lower()
    desitred_status = own_status.lower()

    if current_status == desitred_status:
        if desitred_status == "yes":
            return f"ℹ️ Already own {title} ({year})."
        else:
            return f"ℹ️ Did not own {title} ({year})."

    df.at[idx, "Own"] = own_status
    df.to_excel(ODS_file, engine="odf", index=False, sheet_name=movie_sheet)  # type: ignore

    if desitred_status == "yes":
        return f"✅  Update: {title} ({year}) marked as owned."
    else:
        return f"✅ Update: {title} ({year}) marked as not owned."


def update_movie(title: str = "default", year: int = 0):
    return set_ownership(title, year, "Yes")


def mark_not_owned(title: str = "default", year: int = 0):
    return set_ownership(title, year, "No")


def list_movies(keyword: str = "") -> list[dict]:
    """
    Returns a formatted string of all movies contianing the keyword.
    If no keyword is given, returns all movies.
    """
    df = load_movies_df()

    if keyword:
        mask = df["Title"].str.strip().str.lower().str.contains(keyword.lower())
        df = df[mask]

    movies = []

    for _, row in df.iterrows():
        movies.append({"title": row["Title"], "year": row["Year"], "own": row["Own"]})

    return movies
