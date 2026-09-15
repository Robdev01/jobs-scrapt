from flask import Flask, jsonify, request

from scraps.linkedin import buscar_vagas_linkedin

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "service": "Job Scraper API",
        "status": "online"
    })


@app.post("/api/jobs/search")
def buscar_vagas():
    data = request.get_json(silent=True) or {}

    keyword = data.get("keyword", "Java")
    location = data.get("location", "Brazil")
    limit = data.get("limit", 20)

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return jsonify({
            "error": "O campo 'limit' precisa ser um número."
        }), 400

    limit = max(1, min(limit, 100))

    try:
        vagas = buscar_vagas_linkedin(
            keyword=keyword,
            location=location,
            limit=limit
        )

        return jsonify({
            "success": True,
            "source": "linkedin",
            "keyword": keyword,
            "location": location,
            "total": len(vagas),
            "jobs": vagas
        })

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=9099,
        debug=True
    )