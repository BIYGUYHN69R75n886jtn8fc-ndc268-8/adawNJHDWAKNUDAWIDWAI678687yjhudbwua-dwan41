import os
import json
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

# Profesyonel Loglama Başlatıldı
print("ULTRA PRO QUANT ENGINE v20 (Pro Analyst Synthesis - AI RR Management) is starting...")

app = Flask(__name__, static_folder='static')
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SİSTEM PARAMETRELERİ (Kaptan Emriyle Güncellendi)
MIN_CONFIDENCE = 65  
BASE_MIN_RR = 1.4    # RR sınırı 1.4'e esnetildi.

# 👥 MÜŞTERİ VERİTABANI
VIP_USERS = {"alpha576": "Ma-3007.1", "alen": "alen.123"} 

def get_live_market_context():
    context = "Live Context: Unavailable."
    try:
        fgi_r = requests.get("https://api.alternative.me/fng/", timeout=5)
        fgi_data = fgi_r.json()['data'][0]
        sentiment = f"Fear & Greed Index: {fgi_data['value']} ({fgi_data['value_classification']}). "
        
        news_r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", timeout=5)
        news_data = news_r.json()['Data'][:5]
        headlines = " | ".join([f"{n['title']} (Pub: {datetime.fromtimestamp(n['published_on']).strftime('%H:%M')})" for n in news_data])
        context = f"{sentiment} Recent Headlines: {headlines}"
    except Exception as e:
        logging.error(f"Live data fetch error: {e}")
    return context

@app.before_request
def check_auth():
    if request.endpoint in ['login', 'static_proxy']:
        if request.path.endswith('.html') and not session.get('logged_in'):
            return redirect(url_for('login'))
        return
    if not session.get('logged_in'):
        if request.path == '/' or request.path == '/chat':
            return redirect(url_for('login'))

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><title>Grypto AI - VIP Login</title>
<style>
  body { background: #0f172a; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
  .login-box { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; border: 1px solid #334155; width: 300px; }
  input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; outline: none; }
  button { width: 100%; padding: 12px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; margin-top: 10px; }
  .error { color: #ef4444; margin-bottom: 10px; font-size: 14px; }
</style>
</head>
<body>
  <div class="login-box">
    <h2 style="color: #05fd05;">GRYPTO AI</h2><p style="color: #94a3b8; font-size: 14px;">Institutional Sniper Engine v20</p>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST"><input type="text" name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><button type="submit">Login to Dashboard</button></form>
  </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        if u in VIP_USERS and VIP_USERS[u] == p:
            session['logged_in'] = True
            return redirect('/index.html')
        error = "Invalid credentials!"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index(): return redirect('/index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True)
    user_input = data.get("input", "").strip()
    current_time_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    live_news = get_live_market_context()

    # 🔥 v20: PRO ANALYST SYNTHESIS PROMPT
    system_prompt = f"""
    ROLE: Tier-1 Crypto Hedge Fund Quant Executioner & Pro Analyst.
    LIVE MACRO CONTEXT: {live_news}
    CURRENT TIME: {current_time_utc}

    PROTOCOL:
    1. SYNTHESIS OVER TALLY: Do not just blindly follow the Bull/Bear tally. Synthesize the provided hardcoded mathematical score with the Live Macro Context (Fear/Greed & News) and the user's Liquidation Magnets. Macro overrides micro.
    2. ACCURATE RR CALCULATION: You MUST calculate the exact Risk/Reward (RR) ratio accurately based on your Entry, TP, and SL. Do not hallucinate this number.
    3. EXECUTION: Output HOLD if Confidence < {MIN_CONFIDENCE}% OR your calculated RR < {BASE_MIN_RR}.
    4. Provide 'partial_tp' at 50% distance.

    JSON OUTPUT EXACTLY AS BELOW:
    {{
     "direction": "LONG|SHORT|HOLD",
     "market_regime": "Trending|Volatility Squeeze|Ranging|Exhausted|Liquidity Hunt",
     "entry": float or null,
     "partial_tp": float or null,
     "tp": float or null,
     "sl": float or null,
     "support_level": float or null,
     "resistance_level": float or null,
     "liquidity_target": float or null,
     "confidence": integer 0-100,
     "risk": "Low|Medium|High",
     "rr": float,
     "confluence_score": "Brief summary",
     "why": ["Deep analyst reasoning 1", "Deep analyst reasoning 2"],
     "what_to_watch_for": "Confirmation",
     "cancel_conditions": ["Invalidation level"],
     "market_summary": "Institutional summary"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            top_p=0.1, 
            response_format={ "type": "json_object" },
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
        )

        parsed = json.loads(response.choices[0].message.content.strip())
        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        # 🛑 RR Yetkisi AI'da, sadece limit kontrolü yapıyoruz (1.4)
        if direction in ["LONG", "SHORT"]:
            if confidence < MIN_CONFIDENCE or rr < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                if "why" in parsed: 
                    parsed["why"].append(f"🚨 Sniper Guard: Confidence ({confidence}%) or AI-calculated RR ({rr}) failed Apex threshold (Target RR: {BASE_MIN_RR}).")

        return jsonify(parsed)

    except Exception as e:
        logging.exception("ENGINE ERROR:")
        return jsonify({"direction": "HOLD", "why": ["System fallback engaged due to parsing error."]}), 500

@app.route('/<path:path>')
def static_proxy(path): return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
