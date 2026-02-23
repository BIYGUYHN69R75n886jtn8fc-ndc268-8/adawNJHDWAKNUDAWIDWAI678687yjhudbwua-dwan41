import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

print("ULTRA PRO QUANT ENGINE v11 (1H Institutional Liquidity Hunter) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 API ANAHTARINI GÜVENLİ ŞEKİLDE ÇEKİYORUZ
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🚀 MOTORU ÇALIŞTIR 
client = OpenAI(api_key=OPENAI_API_KEY)

MIN_RR = 1.5       
MIN_CONFIDENCE = 65  # 🔥 Kaptan emri: %65 altı işlemler otomatik HOLD.

# 👥 MÜŞTERİ VERİTABANI
VIP_USERS = {
    "alpha576": "Ma-3007.1",        
    "alen": "alen.123"
} 

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
    <p style="color: #94a3b8; margin-top: 0; margin-bottom: 25px; font-size: 14px;">Institutional Quant Engine (1H)</p>
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

    # 🔥 v11: LİKİDİTE AVCISI + AKILLI SENTEZ PROTOKOLÜ
    system_prompt = f"""
    You are a legendary Institutional Quant Trader specializing in 1H Liquidity Hunting.
    Your mission: Use Liquidity Maps as your Compass (Destination), and Indicators as your Permission (Entry Timing).

    INSTITUTIONAL QUANT RULES (THE GOLDEN BALANCE):
    
    1. THE DESTINATION (Liquidity Target):
       - The user provides exact liquidation targets (magnetic zones). These are your PRIMARY objectives. 
       - If the user types "YOK", "0", or "NONE", that direction is a total void. Never trade into a void.
       - You MUST NOT ignore these targets. They dictate where the market 'fuel' is located.

    2. THE PERMISSION (Indicator Synergy):
       - Indicators are your gatekeepers. You do not blind-trade to a target.
       - If Destination is UP (Whale Target exists), but structural trend (VWAP, EMA) is heavily Bearish, you must wait for a "Trend Exhaustion" signal. 
       - If RSI is low (<35) or price touches Lower BBands, this is your permission to hunt the Upper Liquidity Target (Reversal Trade).
       - Only output HOLD if the market is aggressively trending AWAY from the target with high volume conviction (OBV/MFI alignment).

    3. MARKET REGIME SYNTHESIS (NO SIMPLE COUNTING):
       - Determine if the market is Trending, Ranging, or Exhausted. 
       - Volume (OBV/MFI) is the ultimate truth. A move to liquidity without volume support is a trap.

    4. RISK MANAGEMENT (1H PROTOCOL):
       - 1H trades require logical breathing room. Ensure Entry, SL, and TP reflect institutional levels.
       - Minimum viable RR is {MIN_RR}.

    5. SCORING REALITY: 
       - Align Destination and Permission. 
       - If Target and Indicators match perfectly: 80-95% Confidence.
       - If Target exists but indicators are slightly lagging/exhausted: 65-75% Confidence (Reversal setup).
       - If Target exists but indicators are violently opposing: Output HOLD and explain the "Conflict of Interest".

    JSON FORMAT EXACTLY AS BELOW:
    {{
     "direction": "LONG|SHORT|HOLD",
     "market_regime": "Trending|Volatility Squeeze|Ranging|Exhausted",
     "entry": float or null,
     "tp": float or null,
     "sl": float or null,
     "support_level": float or null,
     "resistance_level": float or null,
     "liquidity_target": float or null,
     "confidence": integer 0-100,
     "risk": "Low|Medium|High",
     "rr": float,
     "confluence_score": "Brief summary of confluence factors",
     "indicator_votes": {{
        "RSI": "bullish|bearish|neutral", "EMA": "bullish|bearish|neutral", "MACD": "bullish|bearish|neutral",
        "BBANDS": "bullish|bearish|neutral", "ATR": "bullish|bearish|neutral", "STOCH": "bullish|bearish|neutral",
        "ADX": "bullish|bearish|neutral", "ICHIMOKU": "bullish|bearish|neutral", "OBV": "bullish|bearish|neutral",
        "KELTNER": "bullish|bearish|neutral", "SAR": "bullish|bearish|neutral", "VWAP": "bullish|bearish|neutral",
        "MFI": "bullish|bearish|neutral", "SUPERTREND": "bullish|bearish|neutral", "CCI": "bullish|bearish|neutral"
     }},
     "why": ["Specific reasoning 1", "Specific reasoning 2"],
     "what_to_watch_for": "Action needed for entry confirmation.",
     "cancel_conditions": ["If candle closes below/above level X"],
     "market_summary": "Sharp institutional assessment."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2, # 🔥 Analitik sentez için optimize edildi
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
        )

        raw = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw)
        except Exception as e:
            return jsonify({
                "direction": "HOLD", "confidence": 0, "risk": "High", "rr": 0, "entry": None, "tp": None, "sl": None,
                "support_level": None, "resistance_level": None, "liquidity_target": None, "indicator_votes": {},
                "why": ["Parse Error"], "what_to_watch_for": "Retry", "cancel_conditions": [], 
                "market_summary": "Internal error.", "market_regime": "Unknown", "confluence_score": "Error"
            })

        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        # 🛑 SYSTEM OVERRIDE FİLTRESİ (%65 BARDAĞI)
        if direction in ["LONG", "SHORT"]:
            if rr < MIN_RR or confidence < MIN_CONFIDENCE:
                parsed["direction"] = "HOLD"
                parsed["entry"] = None
                parsed["tp"] = None
                parsed["sl"] = None
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"PROTECTION: Confidence ({confidence}%) or RR ({rr}) failed to meet the {MIN_CONFIDENCE}% institutional threshold.")
                parsed["market_summary"] = "Trade filtered out by risk management protocol."

        parsed["confidence"] = confidence
        parsed["rr"] = rr
        return jsonify(parsed)

    except Exception as e:
        logging.exception("An error occurred:")
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
