import os
import re
import sys
import requests
from dotenv import load_dotenv
from plexapi.server import PlexServer

# -------------------------
# CONFIG
# -------------------------

load_dotenv()

PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_TOKEN")

PLEX_LIBRARY = os.getenv("PLEX_LIBRARY", "TV Shows")
DEFAULT_SHOW_NAME = os.getenv("DEFAULT_SHOW_NAME", "Pokémon")

# Defaults can be overridden in .env
DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
LOCK_TITLE = os.getenv("LOCK_TITLE", "true").lower() in ("true", "1", "yes")
SKIP_SPECIALS = os.getenv("SKIP_SPECIALS", "true").lower() in ("true", "1", "yes")

# Manual fallback offsets.
# Used when Plex episode numbers are absolute/global numbers.
# Example: Plex S8E376 -> TMDb S8E1, so offset is 375.
SEASON_EPISODE_OFFSETS = {
    8: 375,
    10: 1000
}

# -------------------------
# VALIDATION
# -------------------------

if not PLEX_URL:
    sys.exit("Missing PLEX_URL in .env")

if not PLEX_TOKEN:
    sys.exit("Missing PLEX_TOKEN in .env")

if not TMDB_API_KEY:
    sys.exit("Missing TMDB_TOKEN in .env")

# -------------------------
# HELPERS
# -------------------------

headers = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

def tmdb_get(url, params=None):
    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"TMDb API error {response.status_code}: {response.text}")

    return response.json()

def get_show_name():
    show_input = input(f"\nEnter show name [{DEFAULT_SHOW_NAME}] or type Q to quit: ").strip()

    if show_input.lower() in ("q", "quit", "exit"):
        return None

    return show_input or DEFAULT_SHOW_NAME

def ask_fix_another_show():
    answer = input("\nWould you like to fix another show? [y/N]: ").strip().lower()
    return answer in ("y", "yes")

def confirm_write_mode():
    if DRY_RUN:
        print("DRY_RUN is enabled. No Plex titles will be changed.")
        return True

    print("WARNING: DRY_RUN is disabled. This will update Plex episode titles.")
    confirm = input("Type YES to continue: ").strip()

    return confirm == "YES"

def select_tmdb_show(results):
    """
    Lets the user confirm/select the TMDb match instead of always using the first result.
    """

    print("\nTMDb search results:")

    for index, item in enumerate(results[:10], start=1):
        name = item.get("name", "Unknown")
        first_air_date = item.get("first_air_date", "No date")
        tmdb_id = item.get("id")

        print(f"{index}. {name} ({first_air_date}) - TMDb ID: {tmdb_id}")

    selection = input("\nSelect TMDb result [1]: ").strip()

    if not selection:
        return results[0]

    try:
        selected_index = int(selection) - 1
        return results[selected_index]
    except (ValueError, IndexError):
        print("Invalid selection. Using first result.")
        return results[0]

def get_tmdb_episode_number(season_num, plex_episode_num, plex_title):
    """
    Converts Plex episode numbers/titles into TMDb episode numbers.

    Handles:
      Plex title "Episode 1001" in Season 10 -> TMDb S10E1
      Plex episode index S8E376 -> TMDb S8E1 using offsets
      Normal Plex S10E1 -> TMDb S10E1
    """

    title = plex_title or ""

    # Case 1:
    # Plex title is "Episode 1001", "Episode 1002", etc.
    title_match = re.match(r"^Episode\s+(\d+)$", title, re.IGNORECASE)

    if title_match:
        raw_num = int(title_match.group(1))

        # Example:
        # Season 10, Episode 1001 -> 1001 - 1000 = 1
        season_prefix = season_num * 100

        if raw_num > season_prefix:
            converted = raw_num - season_prefix

            if converted > 0:
                return converted

    # Case 2:
    # Plex episode index itself is absolute/global.
    # Example:
    # S8E376 -> 376 - 375 = 1
    offset = SEASON_EPISODE_OFFSETS.get(season_num, 0)

    if offset:
        converted = plex_episode_num - offset

        if converted > 0:
            return converted

    # Case 3:
    # Normal behavior.
    return plex_episode_num

def process_show(plex, show_name):
    """
    Processes one Plex show, matches it to TMDb, and updates episode titles.
    """

    try:
        show = plex.library.section(PLEX_LIBRARY).get(show_name)
    except Exception as plex_error:
        print(f"\nCould not find Plex show '{show_name}' in library '{PLEX_LIBRARY}'.")
        print(f"Error: {plex_error}")
        return

    print(f"\nProcessing Plex show: {show.title}")

    # -------------------------
    # SEARCH TMDB SHOW
    # -------------------------

    search_url = "https://api.themoviedb.org/3/search/tv"

    search_data = tmdb_get(
        search_url,
        params={"query": show_name}
    )

    results = search_data.get("results", [])

    if not results:
        print(f"No TMDb results found for: {show_name}")
        return

    selected_show = select_tmdb_show(results)
    tmdb_show_id = selected_show["id"]

    print(f"\nSelected TMDb Show ID: {tmdb_show_id}")
    print(f"Selected TMDb Match: {selected_show.get('name')}")

    # -------------------------
    # PROCESS EPISODES
    # -------------------------

    updated_count = 0
    skipped_count = 0
    missing_count = 0
    error_count = 0

    for season in show.seasons():
        season_num = season.index

        if SKIP_SPECIALS and season_num == 0:
            continue

        print(f"\nProcessing Plex Season {season_num}")

        tmdb_season_url = f"https://api.themoviedb.org/3/tv/{tmdb_show_id}/season/{season_num}"

        try:
            tmdb_data = tmdb_get(tmdb_season_url)
        except Exception as tmdb_error:
            error_count += 1
            print(f"Could not load TMDb season {season_num}: {tmdb_error}")
            continue

        tmdb_episodes = {
            ep["episode_number"]: ep["name"]
            for ep in tmdb_data.get("episodes", [])
            if ep.get("episode_number") is not None and ep.get("name")
        }

        if not tmdb_episodes:
            print(f"No TMDb episodes found for season {season_num}")
            continue

        for episode in season.episodes():
            plex_ep_num = episode.index
            current_title = episode.title

            tmdb_ep_num = get_tmdb_episode_number(
                season_num=season_num,
                plex_episode_num=plex_ep_num,
                plex_title=current_title
            )

            new_title = tmdb_episodes.get(tmdb_ep_num)

            if not new_title:
                missing_count += 1
                print(
                    f"No TMDb title found for Plex S{season_num}E{plex_ep_num} "
                    f"({current_title}) -> TMDb S{season_num}E{tmdb_ep_num}"
                )
                continue

            if current_title == new_title:
                skipped_count += 1
                print(f"Already correct: Plex S{season_num}E{plex_ep_num} - {current_title}")
                continue

            print(
                f"Matched Plex S{season_num}E{plex_ep_num} "
                f"({current_title}) -> TMDb S{season_num}E{tmdb_ep_num}: {new_title}"
            )

            if DRY_RUN:
                print("  DRY RUN: No change made")
                skipped_count += 1
                continue

            try:
                episode.editTitle(new_title)
                updated_count += 1

                if LOCK_TITLE:
                    try:
                        episode.editField("title.locked", 1)
                    except Exception as lock_error:
                        print(f"  Title updated, but lock failed: {lock_error}")

            except Exception as update_error:
                error_count += 1
                print(f"  Failed to update Plex title: {update_error}")

    print(f"\nFinished: {show.title}")
    print(f"Updated: {updated_count}")
    print(f"Skipped/already correct/dry run: {skipped_count}")
    print(f"Missing TMDb matches: {missing_count}")
    print(f"Errors: {error_count}")

# -------------------------
# MAIN
# -------------------------

def main():
    if not confirm_write_mode():
        print("Cancelled.")
        return

    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    print(f"\nConnected to Plex: {plex.friendlyName}")
    print(f"Using Plex library: {PLEX_LIBRARY}")

    while True:
        show_name = get_show_name()

        if not show_name:
            print("\nExiting.")
            break

        process_show(plex, show_name)

        if not ask_fix_another_show():
            print("\nDone.")
            break

if __name__ == "__main__":
    main()