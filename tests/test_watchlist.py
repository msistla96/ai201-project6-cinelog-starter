"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service, following the patterns established in
tests/test_collection.py.
"""

from datetime import datetime, timedelta, timezone

import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    add_to_watchlist,
    get_watchlist,
    AlreadyPresentinWatchListError,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


# ── Basic add ───────────────────────────────────────────────────────────────

def test_add_to_watchlist_creates_entry(app, sample_user, sample_film):
    """
    Adding a valid film should create a WatchlistEntry in the database.
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry is not None
        assert entry.user_id == sample_user
        assert entry.film_id == sample_film

        # Verify it persisted
        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db is not None


# ── Default visibility ───────────────────────────────────────────────────────

def test_add_to_watchlist_defaults_to_private(app, sample_user, sample_film):
    """
    Omitting the `public` argument should default the entry to private (False).
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry.public is False


# ── Deduplication ────────────────────────────────────────────────────────────

def test_add_to_watchlist_duplicate_same_visibility_raises(app, sample_user, sample_film):
    """
    Adding the same film twice with the same `public` value should raise
    AlreadyPresentinWatchListError, not silently create a duplicate entry.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film, public=False)

        with pytest.raises(AlreadyPresentinWatchListError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film, public=False)

        # Confirm only one entry exists
        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_add_to_watchlist_duplicate_different_visibility_updates_entry(
    app, sample_user, sample_film
):
    """
    Adding the same film again with a different `public` value should update
    the existing entry's visibility rather than raising or creating a
    duplicate row.
    """
    with app.app_context():
        first = add_to_watchlist(user_id=sample_user, film_id=sample_film, public=False)

        updated = add_to_watchlist(user_id=sample_user, film_id=sample_film, public=True)

        assert updated.id == first.id
        assert updated.public is True

        # Confirm still only one entry exists, and it reflects the new value
        entries = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).all()
        assert len(entries) == 1
        assert entries[0].public is True


# ── Ordering ─────────────────────────────────────────────────────────────────

def test_get_watchlist_orders_by_date_added_descending(app, sample_user):
    """
    get_watchlist should return entries ordered by date_added descending
    (most recently added film first), even when that contradicts title order.
    """
    with app.app_context():
        film_a = Film(title="Older Film", year=2000, genre="Drama")
        film_b = Film(title="Newer Film", year=2010, genre="Drama")
        db.session.add_all([film_a, film_b])
        db.session.commit()

        base_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        entry_a = add_to_watchlist(user_id=sample_user, film_id=film_a.id)
        entry_a.date_added = base_time
        entry_b = add_to_watchlist(user_id=sample_user, film_id=film_b.id)
        entry_b.date_added = base_time + timedelta(days=1)
        db.session.commit()

        result = get_watchlist(sample_user)

        assert [film["title"] for film in result] == ["Newer Film", "Older Film"]


# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError, not a database integrity error.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)
