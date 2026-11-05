import os
import sqlite3
from pathlib import Path

from flask import Flask, g, redirect, render_template, request

MAX_TITLE_LENGTH = 200


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("DATABASE_PATH", "instance/securetask.sqlite3")
    )
    if test_config:
        app.config.update(test_config)

    database_path = app.config["DATABASE"]
    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 200)"
            ")"
        )

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        database = g.pop("db", None)
        if database is not None:
            database.close()

    @app.route("/")
    def home():
        tasks = get_db().execute("SELECT id, title FROM tasks ORDER BY id").fetchall()
        return render_template("index.html", tasks=tasks)

    @app.route("/add", methods=["POST"])
    def add_task():
        title = request.form.get("title", "").strip()
        if not title or len(title) > MAX_TITLE_LENGTH:
            return render_template(
                "index.html",
                tasks=get_db().execute("SELECT id, title FROM tasks ORDER BY id").fetchall(),
                error=f"Task title must be between 1 and {MAX_TITLE_LENGTH} characters.",
            ), 400

        database = get_db()
        database.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        database.commit()
        return redirect("/")

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000))
    )