from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

ACCESS_TOKEN = "EAAHmyf7kOZBIBO6KTUFdqU36QoKxOjpeFRi5aHL9o9s0qkpFvSeYyqyFIRPDnZBO5leloZBbmQtVQBS6deSGZC7WlVNiz8GFDNIWqTA3ZA2snstXF6z1hmw6wAtMWWAuOEYBBxEak8vwM4tjz58gCI7aoF7xDWQg4nru0KQ3n19gZAepPwzJ3yjCO3WBprYODuEsgz4zqQxm0MuZB36xU6pUS8b0coZD"
AD_ACCOUNT_ID = "908237147237125"

@app.route("/ads-summary", methods=["GET"])
def ads_summary():
    date = request.args.get("date", datetime.today().strftime('%Y-%m-%d'))

    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "campaign_name,spend,ctr,cpc,actions",
        "time_range": f'{{"since":"{date}","until":"{date}"}}',
        "level": "campaign",
        "access_token": ACCESS_TOKEN,
        "action_attribution_windows": "1d_click",
        "action_breakdowns": "action_type"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Không thể lấy dữ liệu từ Facebook", "details": response.json()}), 400

    raw_data = response.json().get("data", [])
    campaigns = []

    for item in raw_data:
        spend = float(item.get("spend", 0))
        results = 0

        for action in item.get("actions", []):
            if action.get("action_type") == "onsite_conversion.messaging_conversation_started_7d":
                results += int(float(action.get("value", 0)))

        campaign = {
            "campaign_name": item.get("campaign_name"),
            "spend": spend,
            "ctr": float(item.get("ctr", 0)),
            "cpc": float(item.get("cpc", 0)),
            "results": results,
            "cost_per_result": round(spend / results, 2) if results else None,
            "roas": None  # nếu chưa dùng purchase conversion
        }

        campaigns.append(campaign)

    return jsonify({"campaigns": campaigns})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
