import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

print("ULTRA PRO QUANT ENGINE v8 (1H Sniper - Anti-Falling Knife Edition) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 API ANAHTARINI GÜVENLİ ŞEKİLDE ÇEKİYORUZ
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🚀 MOTORU ÇALIŞTIR 
client = OpenAI(api_key=OPENAI_API_KEY)

MIN_RR = 1.5       
MIN_CONFIDENCE = 65  # 🔥 1H grafikleri için ayarlı

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

    # 🔥 BÜYÜK GÜNCELLEME: DÜŞEN BIÇAĞI TUTMA (ANTI-FALLING KNIFE) KURALI EKLENDİ
    system_prompt = f"""
    You are an elite, cold-blooded crypto futures Market Maker and Institutional Quant.
    Timeframe: 1H (One Hour). Your ONLY objective is maximum accuracy. The user expects a high win rate (e.g., winning 12 out of 16 trades). 

    CURRENT SYSTEM TIME: {current_time_utc}
    
    SESSION RULES:
    - Asian Session (00:00-08:00 UTC): Low volume. Expect fake breakouts. NEVER give a LONG/SHORT signal here unless a massive whale target is triggered.
    - London & NY Sessions: Real trends and institutional money flow occur here.

    STRICT QUANT RULES (THE REALITY CHECK):
    1. THE EXHAUSTION TRAP: If RSI is > 70 or < 30 AND the ADX is very high (>30), the trend is exhausted. Whales are trapping retail traders. DO NOT enter in the direction of the trend. Give a HOLD.
    
    2. 🛑 COMMANDER OVERRIDE & SAFETY VALVE (CRITICAL): The user will provide liquidation targets.
       - If the user types "NONE", "YOK", or "0" for a direction, this means that side is completely EMPTY. DO NOT target empty zones.
       - If a specific number is provided, it is a magnetic target.
       - ⚠️ THE "ANTI-FALLING KNIFE" PROTOCOL: Even if there is a massive liquidity target, you MUST check the indicator alignment. If the indicators are overwhelmingly against the target (e.g., 0, 1 or 2 Bullish indicators but the target requires a LONG, OR 0, 1 or 2 Bearish indicators but the target requires a SHORT), YOU MUST IMMEDIATELY OUTPUT "HOLD". Do not step in front of a strong opposing trend just to grab liquidity. This is a suicide trade.
       
    3. THE 85%+ RULE (CRITICAL): The user demands REALITY, not perfection. Do NOT give a confidence score of 85%, 90%, or 95% unless the setup is a guaranteed, sniper-level entry with perfect confluence on the 1H timeframe. 
    
    4. RUTHLESS DOWNGRADING: If the data is mixed or the trend opposes the liquidity target, be absolutely ruthless. Downgrade the confidence score to 40-60% and output "HOLD". It is better to miss a trade than to lose capital.
    5. Minimum viable RR for entry is {MIN_RR}. If RR is lower, it is an automatic HOLD.

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
     "confluence_score": "e.g., 12/15 Perfect Alignment",
     "indicator_votes": {{
        "RSI": "bullish|bearish|neutral",
        "EMA": "bullish|bearish|neutral",
        "MACD": "bullish|bearish|neutral",
        "BBANDS": "bullish|bearish|neutral",
        "ATR": "bullish|bearish|neutral",
        "STOCH": "bullish|bearish|neutral",
        "ADX": "bullish|bearish|neutral",
        "ICHIMOKU": "bullish|bearish|neutral",
        "OBV": "bullish|bearish|neutral",
        "KELTNER": "bullish|bearish|neutral",
        "SAR": "bullish|bearish|neutral",
        "VWAP": "bullish|bearish|neutral",
        "MFI": "bullish|bearish|neutral",
        "SUPERTREND": "bullish|bearish|neutral",
        "CCI": "bullish|bearish|neutral"
     }},
     "why": ["Reason 1", "Reason 2"],
     "what_to_watch_for": "Specific action to wait for before entering a trade.",
     "cancel_conditions": ["If 1H candle closes below X"],
     "market_summary": "1 sentence sharp tactical assessment."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2, 
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
                "direction": "HOLD",
                "confidence": 0,
                "risk": "High",
                "rr": 0,
                "entry": None,
                "tp": None,
                "sl": None,
                "support_level": None,
                "resistance_level": None,
                "liquidity_target": None,
                "indicator_votes": {},
                "why": ["AI failed to generate valid JSON: " + str(e)],
                "what_to_watch_for": "System parsing error, retrying...",
                "cancel_conditions": ["System fallback"],
                "market_summary": "Parse error in AI generation.",
                "market_regime": "Unknown",
                "confluence_score": "Error"
            })

        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        if direction in ["LONG", "SHORT"]:
            if rr < MIN_RR or confidence < MIN_CONFIDENCE:
                parsed["direction"] = "HOLD"
                parsed["entry"] = None
                parsed["tp"] = None
                parsed["sl"] = None
                parsed["risk"] = "High"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"Backend Filter: RR ({rr}) or Confidence Score ({confidence}%) is too low. ({MIN_CONFIDENCE}% required)")
                parsed["market_summary"] = "Trade cancelled due to strict backend risk parameters."
                parsed["what_to_watch_for"] = f"Waiting for a higher probability setup (Confidence >= {MIN_CONFIDENCE}%)."

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
