# PR Response Doc — CineLog Watchlist Feature

## AI Usage
I used Claude Code for the following:
1. Debugging test issues.
2. Setting up new tests for the fixes and features. I edited  as it worked with 
3. Querying how SQLAlchemy queries are setup (as I am more familiar with SQL queries than ORM queries)
4. Tested my responses to Comment 4 and 5 against it.

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
I added the Exception class for `AlreadyPresentinWatchListError` at the beginning of the file.
<!-- > and modified `add_film` in route `watchlist.py` to call `add_to_watchlist` in a try except block, referring to `add_to_collection` and `collections.py`to comply with project naming conventions consistently. -->

**How I verified:**
I restarted the app to make sure it's running first. 

## Comment 3 — Missing test
**What I did:**

I added a new file `test_watchlist.py` under `tests` and included 3 tests for `add_to_watchlist()`:

1. `test_add_to_watchlist_creates_entry`: Does the basic check for the entry being present in the DB after operation.
2. `test_add_to_watchlist_duplicate_raises`: Makes 2 duplicate calls and checks if the second call throws an error, rather than duplicate the entry.
3.  `test_add_to_watchlist_nonexistent_film_raises`: This is the missing test, which checks if a non existent film raises an exception.

I added 2 and 3 to keep my tests consistent with what was present in `test_collection.py` and test for the change I made under Comment 2.

**How I verified:**
I ran `pytests/tests` for the file and for all tests regressively to make sure nothing broke.

## Comment 4 — Default visibility
**My position:**
My initial thought was to make the visibility as default to True however, upon reviewing it, my proposed alternative is to also allow the user to set the visibility when they want to. Specifically when calling `add_to_watchlist()`, a parameter called `public` which allows `True` or `False` can be set by the user, which gets passed from the main request through `add_film` in route `watchlist.py` as a HTTP query parameter. There will still be a default option in the case that the user does not set any value, which is `False` rather than `True`.

**Reasoning:**
My initial reasoning to keep the default as `True` was to help users know what kinds of films are trending by allowing them to share their watchlists with others, like how Spotify allows public playlists. Cinelog is primarily a community forward app and providing public watchlists is part of the collaboration experience that film lovers seek where they can get films that are popular as well as niche, indie or unique films that cater to certain groups.

However, I do acknowledge that not all communities may prefer to have their watchlist public all the time and may want to keep it private to themselves or within certain groups. Watchlists indicate a user's preference, which can indicate sensitive and personal information in cases where a playlist only lists horror, gore or slasher films or only lists R-rated romantic, sexual or other mature films, which may not be suitable for all users to view. A solution to satisfy both can be to let the user make the decision instead and when the user doesn't set anything, it can be set to `False` instead, as it's a safer option in the case that the user did not want the watchlist to be public yet, or the watchlist should not have been public yet. This avoids any backlash from these situations.

**Tradeoff acknowledged:**
Not defaulting public to True in the case when the user doesn't set a value can fragment the community to have public, private groups and users and could undermine the purpose of community sharing. 

Also, providing the choice to the user also means handling cases where public can be changed from True to False and False to True, which adds extra complexity in how these requests get handled. For simplicity in this PR, we can do a simple toggle assignment, but future work could add additional user warnings and validations so that the changes that go in are intentional.

These tradeoffs can change as the community evolves and it's important to constantly monitor how the app is being used. For future work, we can setup metrics in a dashboard that captures number of public vs private watchlists, engagement with public and private watchlists etc.

## Comment 5 — Sort order
**My position:**
I initially decided to use the Title of the show for sorting the watchlist, upon reviewing the comment to use `date_added` instead in the descending order, I reflected on this and decided to use `date_added` as a first choice.
**Reasoning:**
In the initial decision, using Title provided a more natural ordering format that allows for easier searching and viewing by a fellow app user. However, watchlists are usually more closer to the user that created it and the most recent entries can reflect what they would want to watch first. As a first sort order, `date_added` in the descending order is a better choice than Title, however future work can allow for sorting with Title, Genre through a sort filter which the user can select later on.

**Engagement with reviewer's point:**
Agreed to use `date_added` as a first choice.

**What I did:**

Modify Line 61 in `get_watchlist.py` in `watchlist_service.py` to use `date_added` as sort order:
    WatchlistEntry.date_added.desc()

**How I verified:**
I added a test to `test_watchlist.py` called `test_get_watchlist_orders_by_date_added_descending` which checks the sort order to be by the date_added column. This test failed with an error:
     AttributeError: 'WatchlistEntry' object has no attribute 'film'
After some debugging, the reason was that `WatchlistEntry` in `models.py` needed a relationship to Film in order to access the film element, which was currently not available. I added the following relationship to `WatchlistEntry`:
    film = db.relationship("Film", lazy=True)
The test passed after this change. 

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## Additional Test: Add additional tests for `add_to_watchlist()`

Refer Comment 2 for details.

## Additional Feature: remove_from_watchlist()

**What I did:**

I added a new function `remove_from_watchlist()` to `watchlist_service.py` and a new route `remove_film` to `watchlist.py`, following the existing implementation of `remove_from_collection` in `collection_service.py` and `remove_film` in `collection.py` for Collections.

**How I verified:**
I added new tests for the function:

`test_remove_from_watchlist_removes_entry`: Checks if the entry is fully removed.
`test_remove_from_watchlist_not_present_raises`: Raises NotInWatchlistError when there is nothing to remove.
`test_remove_from_watchlist_only_removes_target_entry`: Only removes the specific entry without disturbing other entries.

## Additional Fix: Add a visibility toggle to add_to_watchlist()

As part of Comment 4
**What I did:**
I added an extra parameter to `add_to_watchlist()` under `watch_service` called `public` which can be set to True or False and set by the user through the router `add_film()` in `watchlist.py`, for which I added an extra parameter check for public.

`add_film()`

    ``` python
            public = data["public"] if data["public"] is not None else False
            entry = add_to_watchlist(user_id=user_id, film_id=data["film_id"], public = public)
        except FilmNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except AlreadyPresentinWatchListError as e:
            return jsonify({"error": str(e)}), 409
    ```

`add_to_watchlist()`
    ``` python
    if entry:
            if public == entry.public:
                raise AlreadyPresentinWatchListError(f"Film {film_id} is already present in this user's watchlist")
            else:
                entry.public = public
        else:
            entry = WatchlistEntry(user_id=user_id, film_id=film_id, public = public)
            db.session.add(entry)
        db.session.commit()
    ```
**How I verified:**
I updated the tests under `test_watchlist.py` to validate the following:
1. Public is set to False by default without user input.
2. When Public is set to a different value, it updates the existing entry in the watchlist, instead of duplicating.
3. When Public has not changed and there is a duplicate film being added, it raises an error.


## PR Description

### Overview
This PR adds the watchlist feature to CineLog: users can save films they want to watch later (`add_to_watchlist`), view their watchlist sorted by most recently added (`get_watchlist`), and remove films from it (`remove_from_watchlist`). A user can also set their watchlist entry to be public or private, defaulting to private if there's no user input.

### Endpoints
- `GET /watchlist/<user_id>` — returns the user's watchlist, most recently added film first.
- `POST /watchlist/<user_id>/add` — body `{ "film_id": <int>, "public": <bool, optional> }`. Adds a film to the watchlist.
- `DELETE /watchlist/<user_id>/remove` — body `{ "film_id": <int> }`. Removes a film from the watchlist.

### Design decisions
**Comment 4 — Default visibility**: `public` defaults to `False` (private) when the user doesn't set it, prioritizing safety for potentially sensitive viewing preferences over discoverability. See Comment 4 for the full reasoning and acknowledged tradeoffs (this may undercut the community-discovery angle of public watchlists, and toggling visibility adds request-handling complexity).
**Comment 4 — sort order**: watchlist entries are sorted by `date_added` descending (most recent first) rather than by film title. See Comment 5 for the full reasoning; Title/Genre-based sort filters are left as future work.

### Manual testing steps

There are two paths to testing

#### Unit Testing
Run the test suite: `pytest tests/test_watchlist.py -v` — all tests should pass.

#### User Testing
To test the actual APIs:

1. Start the app on the CLI with 
    ``` sh
    export FLASK_APP=app:create_app 
    export FLASK_DEBUG=1
    flask run --port=8000
    ```
    FLASK_DEBUG=1 shows up any errors when sending a request.

2. Run `python -m scripts.seed_sample_data` to seed the database before testing the watchlist feature.
3. **Add a film (default visibility)** — expect 201 and `"public": false`:
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": 1}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T03:53:52.643482",
        "film_id": 1,
        "id": "d84c6f57-e6f8-47a7-adb2-ba24c0ff1481",
        "public": false,
        "user_id": "9df00460-8dc7-444d-aef6-53c407ff69c9"
    }
    ```
4. **Add a film with explicit visibility** (different film) — expect 201 with `"public": true`:
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": 2, "public": true}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T03:55:25.581590",
        "film_id": 2,
        "id": "b36b7ab5-6135-44b2-ba64-818bddb9d565",
        "public": true,
        "user_id": "9df00460-8dc7-444d-aef6-53c407ff69c9"
    }
    ```
5. **Duplicate add, same visibility** — expect 409 with an `AlreadyPresentinWatchlistError` message, and no duplicate entry created:
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": 1}' | tail -5
    ```
    ``` json
    {
      "error": "Film 1 is already present in this user's watchlist"
    }
    ```
6. **Duplicate add, different visibility** — expect 201 and the existing entry's `public` updated to `true`, not a new entry:
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": 1, "public": true}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T03:53:52.643482",
        "film_id": 1,
        "id": "d84c6f57-e6f8-47a7-adb2-ba24c0ff1481",
        "public": true,
        "user_id": "9df00460-8dc7-444d-aef6-53c407ff69c9"
    }
    ```
7. **Nonexistent film** — expect 404 with a `FilmNotFoundError` message:
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": 999999}' | tail -5
    ```
    ``` json
    {
      "error": "No film found with id '999999'"
    }
    ```
8. **View watchlist ordering** — confirm the most recently added film appears first, regardless of title:
    ``` sh
    curl -s http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9 | python3 -m json.tool
    ```
    ``` json
    [
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T03:55:25.581590",
            "director": "Wes Anderson",
            "genre": "Comedy",
            "id": 2,
            "poster_url": null,
            "public": true,
            "title": "The Grand Budapest Hotel",
            "year": 2014
        },
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T03:53:52.643482",
            "director": "Paul King",
            "genre": "Comedy",
            "id": 1,
            "poster_url": null,
            "public": true,
            "title": "Paddington 2",
            "year": 2017
        }
    ]
    ```
9. **Remove a film** — expect 200, and it no longer appears in the watchlist:
    ``` sh
    curl -s -X DELETE http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": 2}' | python3 -m json.tool
    ```
    ``` json
    {
        "message": "Removed from watchlist"
    }
    ```
10. **Remove a film not on the watchlist** — expect 404 with a `NotInWatchlistError` message:
    ``` sh
    curl -i -s -X DELETE http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": 2}' | tail -5
    ```
    ``` json
    {
      "error": "Film '2' is not in this user's watchlist"
    }
    ```
11. **Confirm final watchlist state**:
    ``` sh
    curl -s http://localhost:8000/watchlist/9df00460-8dc7-444d-aef6-53c407ff69c9 | python3 -m json.tool
    ```
    ``` json
    [
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T03:53:52.643482",
            "director": "Paul King",
            "genre": "Comedy",
            "id": 1,
            "poster_url": null,
            "public": true,
            "title": "Paddington 2",
            "year": 2017
        }
    ]
    ```
