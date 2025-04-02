from flask import Flask, request, jsonify
import requests
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# ✅ Thay bằng Access Token & ID tài khoản thật của bạn
ACCESS_TOKEN = "EAAHmyf7kOZBIBO79Q9Q6yCItZC9BAXKS2bcaiRHh2HGhbxUKT4ZA1fmViyXo7cbfB6R96LhpPSj1cb7Fc3wc72jbJr4FYioM1wBgsy4iXJ0j6nZATTr1glnIt9u87uRVcYVqtFLzSK6xa8XYJUAX288Vny8z0CeBhkfZA6CeKxyM4uUQiXtVjpiQKCS5qw2Jzy24g2W4TTdx2lJfCUrUJCoW5qCIZD"
AD_ACCOUNT_ID = "act_908237147237125"

@app.route("/ads-summary", methods=["GET"])
def ads_summary():
    date = request.args.get("date", datetime.today().strftime('%Y-%m-%d'))

    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "campaign_name,spend,ctr,cpc,actions",
        "time_range": f'{{"since":"{date}","until":"{date}"}}',
        "level": "ad",
        "access_token": ACCESS_TOKEN,
        "limit": 500
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Không thể lấy dữ liệu từ Facebook", "details": response.json()}), 400

    raw_data = response.json().get("data", [])
    grouped = defaultdict(lambda: {
        "spend": 0.0,
        "ctr_total": 0.0,
        "ctr_count": 0,
        "cpc_total": 0.0,
        "cpc_count": 0,
        "results": 0
    })

    for item in raw_data:
        name = item.get("campaign_name")
        if not name:
            continue

        spend = float(item.get("spend", 0))
        ctr = float(item.get("ctr", 0))
        cpc = float(item.get("cpc", 0))

        # ✅ Lấy đúng số lượng kết quả (kết quả = số inbox)
        results = 0
        for action in item.get("actions", []):
            if action["action_type"] == "onsite_conversion.messaging_conversation_started":
                results = int(float(action["value"]))
                break

        grouped[name]["spend"] += spend
        grouped[name]["results"] += results

        if ctr > 0:
            grouped[name]["ctr_total"] += ctr
            grouped[name]["ctr_count"] += 1
        if cpc > 0:
            grouped[name]["cpc_total"] += cpc
            grouped[name]["cpc_count"] += 1

    campaigns = []
    for name, data in grouped.items():
        avg_ctr = data["ctr_total"] / data["ctr_count"] if data["ctr_count"] > 0 else None
        avg_cpc = data["cpc_total"] / data["cpc_count"] if data["cpc_count"] > 0 else None
        cost_per_result = data["spend"] / data["results"] if data["results"] > 0 else None

        campaigns.append({
            "campaign_name": name,
            "spend": round(data["spend"], 2),
            "ctr": round(avg_ctr, 4) if avg_ctr else None,
            "cpc": round(avg_cpc, 2) if avg_cpc else None,
            "results": data["results"],
            "cost_per_result": round(cost_per_result, 2) if cost_per_result else None,
            "roas": None
        })

    return jsonify({"campaigns": campaigns})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
