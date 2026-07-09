# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:**

Renamed `save_to_watchlist()` on Line 12 of `watchlist_service.py` to `add_to_watchlist()`, to comply with project naming conventions. Updated `watchlist.py` to use the updated function name.

**How I verified:**

I used my VSCode Editor to search for `save_to_watchlist` (which gave me `watchlist.py`) to make sure the changes are reflected or not and also restarted app to make sure startup is not broken.

## Comment 2 — Deduplication
**What I did:**
For the function`add_to_watchlist()` in `watchlist_service.py`, I added a separate database call to query `Watchlist` using the `user_id` and `film_id` before adding any entry as follows:
    ``` python
    entry = WatchlistEntry.query.filter_by(user_id=user_id, film_id = film_id).first()
        if entry:
            raise AlreadyPresentinWatchListError(f"Film {film_id} is already present in this user's watchlist")
    ```
I added the Exception class for `AlreadyPresentinWatchListError` at the beginning of the file, making sure to refer to `add_to_collection` to comply with project naming conventions consistently.

**How I verified:**
I restarted the app to make sure it's running.

## Comment 3 — Missing test
**What I did:**
**How I verified:**

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->