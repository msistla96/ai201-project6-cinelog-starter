"""
scripts/seed_watchlist_demo.py — CineLog

Seeds the dev database (instance/cinelog.db) with a couple of users, films,
and a collection entry for manual testing of the watchlist feature. If a
database already exists, it is dropped and recreated first for a clean slate.

Usage (from the project root):
    python -m scripts.seed_sample_data

Run this once, then start the app separately with `python app.py` and use
the printed IDs to build requests against the watchlist endpoints.
"""

import os

from app import create_app, db
from models import User, Film, CollectionEntry

app = create_app()

with app.app_context():
    if os.path.exists("instance/cinelog.db"):
        db.drop_all()
        db.create_all()
        print("Existing database found — dropped and recreated all tables.")

    user_a = User(username="alice_demo", email="alice_demo@example.com")
    user_b = User(username="bob_demo", email="bob_demo@example.com")
    db.session.add_all([user_a, user_b])
    db.session.commit()

    film_1 = Film(title="Paddington 2", year=2017, genre="Comedy", director="Paul King")
    film_2 = Film(title="The Grand Budapest Hotel", year=2014, genre="Comedy", director="Wes Anderson")
    film_3 = Film(title="Hereditary", year=2018, genre="Horror", director="Ari Aster")
    db.session.add_all([film_1, film_2, film_3])
    db.session.commit()

    print("Seeded data:")
    print(f"  user_a (alice_demo): {user_a.id}")
    print(f"  user_b (bob_demo):   {user_b.id}")
    print(f"  film_1 (Paddington 2):              {film_1.id}")
    print(f"  film_2 (The Grand Budapest Hotel):  {film_2.id}")
    print(f"  film_3 (Hereditary):                {film_3.id}")
