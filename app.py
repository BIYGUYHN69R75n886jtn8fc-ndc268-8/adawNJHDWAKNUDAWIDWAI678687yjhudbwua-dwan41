import os
import json
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

# v14 "The Oracle" - Institutional News Decay, Divergence & Partial Profit Logic
print("ULTRA PRO QUANT ENGINE v14 (The Oracle - Institutional Synthesis) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 API ANAHTARI VE BAĞLANTI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SİSTEM PARAMETRELERİ
MIN_CONFIDENCE = 65  
BASE_MIN_RR = 1.5    

# 👥 VIP VERİTABANI
VIP_USERS = {
    "alpha576": "Ma-3007.1",        
    "alen": "alen.123"
} 

# 🌐 CANLI VERİ KÖPRÜSÜ (The Oracle News Decay Layer)
def get_live_market_context():
    """İnternetten saniyelik haberleri ve yayın saatlerini çeker."""
    context = "Live Context: Unavailable (API Timeout)."
    try:
        # 1. Korku ve Açgözlülük Endeksi (Canlı)
        fgi_r = requests.get("https://api.alternative.me/fng/", timeout=5)
        fgi_data = fgi_r.json()['data'][0]
        sentiment = f"Fear & Greed Index: {fgi_data['value']} ({fgi_data['value_classification']}). "
        
        # 2. Canlı Kripto Haber Başlıkları + Yayın Saatleri
        news_r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", timeout=5)
        news_data = news_r.json()['Data'][:5]
        # Her haberin yanına yayın saatini ekliyoruz ki AI bayatlığını ölçebilsin
        headlines = " | ".join([f"{n['title']} (Published at: {datetime.fromtimestamp(n['published_on']).strftime('%H:%M')})" for n in news_data])
        
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
<meta charset="UTF-8">
<title>Grypto AI - VIP Login</title>
<style>
  body { background: #0f172a; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
  .login-box { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; border: 1px solid #334155; width: 300px; }
  input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; outline: none; }
  input:focus { border-color: #22c55e; }
  button { width: 100%; padding: 12px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; margin-top: 10px; }
  button:hover { background: #16a34a; }
  .error { color: #ef4444; margin-bottom: 10px; font-size: 14px; }
</style>
</head>
<body>
  <div class="login-box">
    <h2 style="color: #05fd05; letter-spacing: 2px; margin-bottom: 5px;">GRYPTO AI</h2>
    <p style="color: #94a3b8; margin-top: 0; margin-bottom: 25px; font-size: 14px;">Institutional Apex Oracle (1H)</p>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Login to Dashboard</button>
    </form>
  </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in VIP_USERS and VIP_USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/index.html')
        else:
            error = "Invalid username or password!"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect('/index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json(force=True)
    user_input = data.get("input", "").strip()

    if not user_input:
        return jsonify({"error": "Input message is required."}), 400

    current_time_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    
    # 🌐 SENTINEL SEARCHER: Canlı Veri ve Haber Saatlerini Çek
    live_news = get_live_market_context()

    # 🔥 v14: INSTITUTIONAL ORACLE PROMPT
    system_prompt = f"""
    ROLE: You are the AI-Quant Oracle at a Tier-1 Crypto Hedge Fund. 
    LIVE NEWS FEED (WITH TIMES): {live_news}
    CURRENT TIME: {current_time_utc}

    STRICT ORACLE PROTOCOLS:
    1. NEWS DECAY LOGIC: 
       - Evaluate news based on publication time. If a headline is >4 hours old, reduce its weighting by 50%.
       - Immediate breaking news (<1 hour) overrides all technical signals.

    2. VOLUME DIVERGENCE (ANTI-TRAP): 
       - Strictly cross-reference Price vs Volume (OBV/MFI). 
       - If price targets the Liquidity Pool but Volume is stagnant or declining, classify as 'LIQUIDITY TRAP' and output HOLD.

    3. PARTIAL PROFIT REALIZATION: 
       - You MUST suggest a 'Partial TP' at 50% of the distance to the final target.
       - Instruction: "Move SL to Entry once Partial TP is hit."

    4. MARKET REGIME DIAGNOSIS: 
       - Use ADX/ATR to detect 'Stop Runs' or 'Mean Reversion'. 
       - Place SL at least 1.5x ATR away to survive 'News Wicks'.

    5. BAYESIAN WEIGHTED SYNTHESIS:
       - VOL/FLOW = 40%, NEWS SENTIMENT = 30%, MOMENTUM/STRUCTURE = 30%.
       - Confidence must be >= {MIN_CONFIDENCE}% for execution.

    JSON OUTPUT FORMAT:
    {{
     "direction": "LONG|SHORT|HOLD",
     "market_regime": "Diagnosis",
     "entry": float, "partial_tp": float, "tp": float, "sl": float,
     "confidence": integer, "rr": float,
     "why": ["Oracle News Decay Analysis", "Structural Divergence Analysis"],
     "what_to_watch_for": "Confirmation trigger",
     "cancel_conditions": ["Specific level invalidation"],
     "market_summary": "1-sentence sharp tactical assessment."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            top_p=0.1, 
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        # 🛑 APEX ORACLE PROTECTION
        if direction in ["LONG", "SHORT"]:
            if confidence < MIN_CONFIDENCE or rr < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"ORACLE GUARD: Confidence {confidence}% or RR {rr} failed Apex threshold.")

        return jsonify(parsed)

    except Exception as e:
        logging.exception("ORACLE ENGINE CRITICAL ERROR:")
        return jsonify({"direction": "HOLD", "why": [str(e)]}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
