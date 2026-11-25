import importlib
import os

from flask import Flask, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")


@app.get("/health")
def health():
    return jsonify(status="ok")


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
