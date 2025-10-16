# filename: calltracer_api_final.py
# Make by @ig_banz

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route("/track/<number>", methods=["GET"])
def track_number(number):
    try:
        url = f"https://calltracer.in/in/{number}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "trace-details"})

        if not table:
            return jsonify({"error": "Number not found or page structure changed", "made_by": "@ig_banz"}), 404

        data = {}
        rows = table.find_all("tr")
        last_key = None

        # Parse all table rows
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                data[key] = value
                last_key = key
            elif len(cols) == 1 and last_key:
                # For multi-row entries (Tracking History etc.)
                data[last_key] += " | " + cols[0].text.strip()

        # Extract Google Maps coordinates and create clickable link
        map_iframe = soup.find("iframe", {"id": "map"})
        if map_iframe:
            src = map_iframe.get("src", "")
            match = re.search(r"q=([0-9\.\-]+),([0-9\.\-]+)", src)
            if match:
                lat, lon = match.groups()
                data["GPS_Coordinates"] = {"latitude": lat, "longitude": lon}
                data["Google_Map_Link"] = f"https://www.google.com/maps?q={lat},{lon}"

        return jsonify({
            "success": True,
            "number": number,
            "data": data,
            "made_by": "@ig_banz"
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}", "made_by": "@ig_banz"}), 500
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}", "made_by": "@ig_banz"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
