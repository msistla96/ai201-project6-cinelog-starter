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

I also verified this via Step 3 (Add a film) under Manual testing steps.

## Comment 2 — Deduplication
**What I did:**
For the function`add_to_watchlist()` in `watchlist_service.py`, I added a separate database call to query `Watchlist` using the `user_id` and `film_id` before adding any entry as follows:

```python
    entry = WatchlistEntry.query.filter_by(user_id=user_id, film_id = film_id).first()
        if entry:
            raise AlreadyPresentinWatchListError(f"Film {film_id} is already present in this user's watchlist")
```
I added the Exception class for `AlreadyPresentinWatchListError` at the beginning of the file and modified `add_film` in route `watchlist.py` to call `add_to_watchlist` in a try except block, referring to `add_to_collection` and `collections.py`to comply with project naming conventions consistently.

**How I verified:**

I restarted the app to make sure it's running first. 

I also verified this via Step 5 (Duplicate add, same visibility) under Manual testing steps.

## Comment 3 — Missing test
**What I did:**

I added a new file `test_watchlist.py` under `tests` and included 3 tests for `add_to_watchlist()`:

1. `test_add_to_watchlist_creates_entry`: Does the basic check for the entry being present in the DB after operation.
2. `test_add_to_watchlist_duplicate_same_visibility_raises`: Makes 2 duplicate calls and checks if the second call throws an error, rather than duplicate the entry.
3. `test_add_to_watchlist_nonexistent_film_raises`: This is the missing test, which checks if a non existent film raises an exception.

I added 2 and 3 to keep my tests consistent with what was present in `test_collection.py` and test for the change I made under Comment 2.

**How I verified:**

I ran `pytests/tests` for the file and for all tests regressively to make sure nothing broke.

I also verified this via the Unit Testing section under Manual testing steps.

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

I also verified this via Step 8 (View watchlist ordering) under Manual testing steps.

## Comment 6 — Rebase
**What conflicted:**
There were 2 files that conflicted:
`.gitignore` - I already had a gitignore file present before.
`models.py` - The refactor did not have WatchListEntry, which conflicted with my current changes containing it.
**How I resolved it:**

`.gitignore` - I accepted the changes from the main branch instead of mine as it was more comprehensive.
`models.py` - I accepted the changes from the feature branch I worked on as the incoming change removed it. 

VSCode has an interactive option to decide which changes I accepted. Once that was done, I use the following commands to add the file and continue with the rebase until there were no changes left.

    git add <file.py>
    git rebase --continue
**How I verified no conflict remains:**
I followed all the steps for `Manual testing steps` under `PR Description` to test and make sure the refactor didn't change the existing behavior.

Line 80 in `models.py` was still using the old Integer Datatype for Film ID. This threw an error when seeding the database, so I changed it to `db.String(36)`, as was present in Film from the refactor.

All the tests passed after this change.

## Additional Test: Add additional test for `add_to_watchlist()`

Refer to Comment 3 for details (Git commit log shows a single commit for all the tests related to `add_to_watchlist()`).

## Additional Feature: remove_from_watchlist()

**What I did:**

I added a new function `remove_from_watchlist()` to `watchlist_service.py` and a new route `remove_film` to `watchlist.py`, following the existing implementation of `remove_from_collection` in `collection_service.py` and `remove_film` in `collection.py` for Collections. This basically checks for if there is an entry in the watchlist given the user_id and film_id first, then deletes it.

**How I verified:**

I added new tests for the function:

`test_remove_from_watchlist_removes_entry`: Checks if the entry is fully removed.
`test_remove_from_watchlist_not_present_raises`: Raises NotInWatchlistError when there is nothing to remove.
`test_remove_from_watchlist_only_removes_target_entry`: Only removes the specific entry without disturbing other entries.

I also verified this via Steps 9 and 10 (Remove a film / Remove a film not on the watchlist) under Manual testing steps.

## Additional Fix: Add a visibility toggle to add_to_watchlist()
Done as part of Comment 4.
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

I also verified this via Steps 3, 5, and 6 (Add a film, Duplicate add same visibility, Duplicate add different visibility) under Manual testing steps.

## Git commit log
``` bash
    a18dfc7 (HEAD -> feature/watchlist) docs: update information for Comment 6, modify PR Description and clean up documentation
    20cde6e fix: modify film id in WatchlistEntry to match refactored id in Film
    ea2ea06 docs: Update pr-response.md to include PR Description; modify Manual Testing to include unit, regression and user testing in separate modules
    618a14f chore: Add script for seeding database
    2886ecf docs: add information for remove_to_watchlist and add_to_watchlist and modify AI Usage section
    59a63c3 test: Add tests for remove_to_watchlist
    2b34d45 feat: add new function remove_from_watchlist to allow removing a film from the watchlist
    73d0753 docs: Update Comment 5 to add details about the changes done and verified
    ef0fad7 test: Add new test for get_watchlist
    4b7a72b fix: Use date_added to sort Watchlist Entries based on Comment 5
    5d016d3 test: Add tests for toggle feature
    e850663 feat: add toggle to add_to_watchlist for making watchlist private or public and update add_film route to parse public for Comment 4: Default visibility
    0a80be1 docs: add informaton about Comment 3: Missing test, visibility and sort order decisions
    a1d053c test: Added missing test for non existent film id when adding to watchlist; added additional tests
    9c74046 docs: Added informaton about Comment 2: Deduplication; Refactored Comment 1
    9d1b261 fix: add deduplication in add_to_watchlist and add try block in add_film route for new check for Comment 2: Deduplication
    ae982ba docs: Add details about Comment 1: Renaming
    00ab6d5 fix: rename save_to_watchlist to add_to_watchlist
    2f25e52 fix: update film retrieval method to use db.session.get in collection and watchlist services
    819762f feat: add watchlist model and endpoint
    718a9a8 chore: add .gitignore for generated files
    07ca580 refactor: migrate film IDs from integer to UUID
    014ae54 feat: initial CineLog API with film collection feature
```
## PR Description

### Overview
This PR adds the watchlist feature to CineLog: users can save films they want to watch later (`add_to_watchlist`), view their watchlist sorted by most recently added (`get_watchlist`), and remove films from it (`remove_from_watchlist`). A user can also set their watchlist entry to be public or private, defaulting to private if there's no user input.

### Endpoints
- `GET /watchlist/<user_id>` — returns the user's watchlist, most recently added film first.
- `POST /watchlist/<user_id>/add` — body `{ "film_id": <int>, "public": <bool, optional> }`. Adds a film to the watchlist.
- `DELETE /watchlist/<user_id>/remove` — body `{ "film_id": <int> }`. Removes a film from the watchlist.

### Design decisions
**Comment 4 — Default visibility**: `public` defaults to `False` (private) when the user doesn't set it, prioritizing safety for potentially sensitive viewing preferences over discoverability. See Comment 4 for the full reasoning and acknowledged tradeoffs (this may undercut the community-discovery angle of public watchlists, and toggling visibility adds request-handling complexity).
**Comment 5 — sort order**: watchlist entries are sorted by `date_added` descending (most recent first) rather than by film title. See Comment 5 for the full reasoning; Title/Genre-based sort filters are left as future work.

### Manual testing steps

There are two paths to testing

#### Unit Testing
Run the test suite: `pytest tests -v` — all tests should pass.

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

    Request format
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>"}' | python3 -m json.tool
    ```
    You can substitute with the user_id and film_id from the seeded database.
    
    Sample Request and Response
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/32c65c35-2859-471f-8bf6-2cecf9ac7f7f/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "11dc1011-855b-434a-bc07-8ba008516081"}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T04:32:23.369633",
        "film_id": "c3f72e45-3fd5-4d40-86c8-d7674c434438",
        "id": "1d863c83-029c-4df9-a917-b13089239efd",
        "public": false,
        "user_id": "acbb1bbd-b9c3-47f0-b135-52b84ad93bb5"
    }
    ```
4. **Add a film with explicit visibility** (different film) — expect 201 with `"public": true`:

    Request format
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>", "public": true}' | python3 -m json.tool
    ```
    You can substitute with the user_id and film_id from the seeded database.
    Sample Request and Response
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "e66276cb-acb2-4d1d-a524-bb19e8d2460c", "public": true}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T04:32:34.520661",
        "film_id": "e66276cb-acb2-4d1d-a524-bb19e8d2460c",
        "id": "a2fc758d-fc7d-44da-9037-eed1ec1ede43",
        "public": true,
        "user_id": "acbb1bbd-b9c3-47f0-b135-52b84ad93bb5"
    }
    ```
5. **Duplicate add, same visibility** — expect 409 with an `AlreadyPresentinWatchlistError` message, and no duplicate entry created:

    Request format
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>"}' | tail -5
    ```
    You can substitute with the same user_id and film_id used in step 3.
    Sample Request and Response
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "c3f72e45-3fd5-4d40-86c8-d7674c434438"}' | tail -5
    ```
    ``` json
    {
        "error": "Film c3f72e45-3fd5-4d40-86c8-d7674c434438 is already present in this user's watchlist"
    }
    ```
6. **Duplicate add, different visibility** — expect 201 and the existing entry's `public` updated to `true`, not a new entry:

    Request format
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>", "public": true}' | python3 -m json.tool
    ```
    You can substitute with the same user_id and film_id used in step 3.
    Sample Request and Response
    ``` sh
    curl -s -X POST http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "c3f72e45-3fd5-4d40-86c8-d7674c434438", "public": true}' | python3 -m json.tool
    ```
    ``` json
    {
        "date_added": "2026-07-11T04:32:23.369633",
        "film_id": "c3f72e45-3fd5-4d40-86c8-d7674c434438",
        "id": "1d863c83-029c-4df9-a917-b13089239efd",
        "public": true,
        "user_id": "acbb1bbd-b9c3-47f0-b135-52b84ad93bb5"
    }
    ```
7. **Nonexistent film** — expect 404 with a `FilmNotFoundError` message:

    Request format
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/<user_id>/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<nonexistent_film_id>"}' | tail -5
    ```
    You can substitute with the user_id from the seeded database and any film_id that doesn't exist.

    Sample Request and Response
    ``` sh
    curl -i -s -X POST http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/add \
      -H "Content-Type: application/json" \
      -d '{"film_id": "00000000-0000-0000-0000-000000000000"}' | tail -5
    ```
    ``` json
    {
        "error": "No film found with id '00000000-0000-0000-0000-000000000000'"
    }
    ```
8. **View watchlist ordering** — confirm the most recently added film appears first, regardless of title:

    Request format
    ``` sh
    curl -s http://localhost:8000/watchlist/<user_id> | python3 -m json.tool
    ```
    You can substitute with the user_id from the seeded database.

    Sample Request and Response
    ``` sh
    curl -s http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5 | python3 -m json.tool
    ```
    ``` json
    [
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T04:32:34.520661",
            "director": "Wes Anderson",
            "genre": "Comedy",
            "id": "e66276cb-acb2-4d1d-a524-bb19e8d2460c",
            "poster_url": null,
            "public": true,
            "title": "The Grand Budapest Hotel",
            "year": 2014
        },
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T04:32:23.369633",
            "director": "Paul King",
            "genre": "Comedy",
            "id": "c3f72e45-3fd5-4d40-86c8-d7674c434438",
            "poster_url": null,
            "public": true,
            "title": "Paddington 2",
            "year": 2017
        }
    ]
    ```
9. **Remove a film** — expect 200, and it no longer appears in the watchlist:

    Request format
    ``` sh
    curl -s -X DELETE http://localhost:8000/watchlist/<user_id>/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>"}' | python3 -m json.tool
    ```
    You can substitute with the user_id and film_id from step 4.

    Sample Request and Response
    ``` sh
    curl -s -X DELETE http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": "e66276cb-acb2-4d1d-a524-bb19e8d2460c"}' | python3 -m json.tool
    ```
    ``` json
    {
        "message": "Removed from watchlist"
    }
    ```
10. **Remove a film not on the watchlist** — expect 404 with a `NotInWatchlistError` message:

    Request format
    ``` sh
    curl -i -s -X DELETE http://localhost:8000/watchlist/<user_id>/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": "<film_id>"}' | tail -5
    ```
    You can substitute with the same user_id and film_id used in step 9, now that it's already been removed.

    Sample Request and Response
    ``` sh
    curl -i -s -X DELETE http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5/remove \
      -H "Content-Type: application/json" \
      -d '{"film_id": "e66276cb-acb2-4d1d-a524-bb19e8d2460c"}' | tail -5
    ```
    ``` json   
    {
        "error": "Film 'e66276cb-acb2-4d1d-a524-bb19e8d2460c' is not in this user's watchlist"
    }
    ```
11. **Confirm final watchlist state**:

    Request format
    ``` sh
    curl -s http://localhost:8000/watchlist/<user_id> | python3 -m json.tool
    ```
    You can substitute with the user_id from the seeded database.

    Sample Request and Response
    ``` sh
    curl -s http://localhost:8000/watchlist/acbb1bbd-b9c3-47f0-b135-52b84ad93bb5 | python3 -m json.tool
    ```
    ``` json
    [
        {
            "average_rating": 0.0,
            "date_added": "2026-07-11T04:32:23.369633",
            "director": "Paul King",
            "genre": "Comedy",
            "id": "c3f72e45-3fd5-4d40-86c8-d7674c434438",
            "poster_url": null,
            "public": true,
            "title": "Paddington 2",
            "year": 2017
        }
    ]
    ```
