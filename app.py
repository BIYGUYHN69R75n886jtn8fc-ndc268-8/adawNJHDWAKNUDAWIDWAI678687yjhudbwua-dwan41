import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

# Profesyonel Loglama Başlatıldı
print("ULTRA PRO QUANT ENGINE v12 (Institutional Apex - Full Integration) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 API ANAHTARI VE BAĞLANTI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SİSTEM PARAMETRELERİ (v12 GÜNCEL)
MIN_CONFIDENCE = 65  # Kaptan emri: %65 altı otomatik HOLD.
BASE_MIN_RR = 1.5    # Dinamik RR için taban sınır.

# 👥 VIP VERİTABANI
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
    <p style="color: #94a3b8; margin-top: 0; margin-bottom: 25px; font-size: 14px;">Institutional Apex Engine (1H)</p>
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

    # 🔥 v12: LİKİDİTE AVCISI + BAYESIAN SENTEZ + VOLATİLİTE ADAPTASYONU
    system_prompt = f"""
    ROLE: You are the AI-Quant Lead at a Tier-1 Crypto Hedge Fund. 
    STRATEGY: 1H Liquidity Hunting with Multi-Timeframe Confluence.
    CURRENT TIME: {current_time_utc}

    STRICT OPERATIONAL PROTOCOLS:
    1. MARKET REGIME (THE CONTEXT): 
       - Diagnose if the market is in 'Stop Run', 'Trend Continuation', or 'Volatility Exhaustion'.
       - Use ADX and ATR to set the expectation: High Volatility (Wide SL/TP) vs Low Volatility (Tight SL/TP).

    2. LIQUIDITY GRAVITY (THE COMPASS):
       - User Liquidity Targets (numeric) are your Primary Mission.
       - CALCULATE: If price is moving to the target but OBV/MFI is decreasing, mark as 'Bull Trap'.
       - NEVER trade into "YOK" or "0" zones. They are liquidity vacuums.

    3. BAYESIAN WEIGHTED SYNTHESIS:
       - No simple counting. Use weighted conviction:
         * SMART MONEY FLOW (OBV, MFI, VWAP, Volume) = 40%
         * MOMENTUM (RSI, MACD, STOCH) = 30%
         * STRUCTURAL PERMISSION (EMA, Supertrend, Ichimoku) = 30%
       - If total probability < {MIN_CONFIDENCE}%, output HOLD.

    4. RISK & EXECUTION RIGOR:
       - DINAMIC RR: Target RR 2.5+ for Trending markets; 1.5 for Ranging markets.
       - SL PLACEMENT: Use ATR. Place SL at least 1.2x ATR away from the entry to avoid 'Wick Hunting'.
       - ENTRY: Prefer Limit Entries at structural levels (VWAP/EMA) if RSI is overextended.

    5. MULTI-TIMEFRAME OVERRIDE:
       - If 1H signal is LONG but you detect 4H structural breakdown, reduce confidence by 20%.

    JSON OUTPUT FORMAT:
    {{
     "direction": "LONG|SHORT|HOLD",
     "market_regime": "Diagnosis",
     "entry": float, "tp": float, "sl": float,
     "support_level": float, "resistance_level": float,
     "liquidity_target": float,
     "confidence": integer 0-100,
     "risk": "Low|Medium|High",
     "rr": float,
     "confluence_score": "Bayesian Summary",
     "indicator_votes": {{ "RSI": "status", "EMA": "status", ... }},
     "why": ["Professional analysis 1", "Analysis 2"],
     "what_to_watch_for": "Trigger for entry",
     "cancel_conditions": ["Invalidation level"],
     "market_summary": "1-sentence sharp tactical brief."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            top_p=0.1, # 🔥 v12: Mantıksal tutarlılığı maksimize eder
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

        # 🛑 APEX RISK FİLTRESİ (Gelişmiş v12 Koruma)
        if direction in ["LONG", "SHORT"]:
            # Güven puanı barajı kontrolü
            if confidence < MIN_CONFIDENCE:
                parsed["direction"] = "HOLD"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"🚨 APEX GUARD: Confidence ({confidence}%) below threshold ({MIN_CONFIDENCE}%).")
            
            # Dinamik RR kontrolü
            if rr < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"🚨 APEX GUARD: RR ({rr}) is mathematically inefficient for 1H structure.")

        return jsonify(parsed)

    except Exception as e:
        logging.exception("QUANT ENGINE CRITICAL ERROR:")
        return jsonify({
            "direction": "HOLD",
            "why": ["Engine Error: " + str(e)],
            "market_summary": "System failure. Do not trade."
        }), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Render ve yerel ortam uyumluluğu için port ayarı
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
