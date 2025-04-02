
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Dữ liệu mẫu giả lập
sample_data = {
    "2025-04-01": [
        {"campaign_name": "Live 1/4", "spend": 5000000, "roas": 4.2, "ctr": 2.1, "cpc": 1500},
        {"campaign_name": "ADS trị nám", "spend": 2000000, "roas": 0.9, "ctr": 1.2, "cpc": 3200},
        {"campaign_name": "Remarketing", "spend": 1000000, "roas": 6.0, "ctr": 3.1, "cpc": 800}
    ],
    "2025-03-31": [
        {"campaign_name": "Live 31/3", "spend": 4500000, "roas": 3.8, "ctr": 2.5, "cpc": 1700}
    ]
}

@app.route("/ads-summary", methods=["GET"])
def ads_summary():
    date = request.args.get("date", datetime.today().strftime('%Y-%m-%d'))
    campaigns = sample_data.get(date, [])
    return jsonify({"campaigns": campaigns})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
