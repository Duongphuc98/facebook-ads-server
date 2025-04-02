from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Thay bằng Access Token và ID tài khoản quảng cáo thật của bạn
ACCESS_TOKEN = "EAAHmyf7kOZBIBO7jNqVwroeaURb9Ld0OTmRl2BvHFTTpEZBXZAcH9Bnzw04Bb8maNuifrnX43vU2RI3fwXhdcdyGSZCcr6clXcZB4M1gIAIJMXyFdK8nZA03m1N5ZADOM6xs5ogOoagDjXlXwdrBf7gf9fEKEmTnD17WYlWnpNXE2sjueOhBHzPcmPdsKOoNdWXYR2R5kpMqxB5a8SMcDvJVHGWFx0ZD"
AD_ACCOUNT_ID = "act_908237147237125"

@app.route("/ads-summary", methods=["GET"])
def ads_summary():
    date = request.args.get("date", datetime.today().strftime('%Y-%m-%d'))

    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "campaign_name,spend,ctr,cpc,actions",
        "time_range": f'{{"since":"{date}","until":"{date}"}}',
        "level": "campaign",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Không thể lấy dữ liệu từ Facebook", "details": response.json()}), 400

    raw_data = response.json().get("data", [])
    campaigns = []

    for item in raw_data:
        # Lấy đúng kết quả là lượt bắt đầu cuộc trò chuyện
        results = 0
        for action in item.get("actions", []):
            if action["action_type"] == "onsite_conversion.messaging_conversation_started":
                results = int(float(action.get("value", 0)))
                break

        cost_per_result = float(item.get("spend", 0)) / results if results > 0 else None

        campaign = {
            "campaign_name": item.get("campaign_name"),
            "spend": float(item.get("spend", 0)),
            "ctr": float(item.get("ctr", 0)),
            "cpc": float(item.get("cpc", 0)),
            "roas": None,  # bạn có thể bổ sung nếu cần
            "results": results,
            "cost_per_result": round(cost_per_result, 2) if cost_per_result else None
        }
        campaigns.append(campaign)

    return jsonify({"campaigns": campaigns})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
