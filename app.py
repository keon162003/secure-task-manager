from flask import Flask, render_template, request, redirect

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Learn CI/CD"},
    {"id": 2, "title": "Add security scanning"}
]


@app.route("/")
def home():
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        tasks.append({
            "id": len(tasks) + 1,
            "title": title
        })

    return redirect("/")


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(debug=True)