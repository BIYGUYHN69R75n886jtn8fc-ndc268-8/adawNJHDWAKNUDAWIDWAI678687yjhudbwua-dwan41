import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

print("ULTRA PRO QUANT ENGINE v9.2 (1H Smart Alignment Edition) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 API ANAHTARINI GÜVENLİ ŞEKİLDE ÇEKİYORUZ
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🚀 MOTORU ÇALIŞTIR 
client = OpenAI(api_key=OPENAI_API_KEY)

MIN_RR = 1.5       
MIN_CONFIDENCE = 65  # 🔥 Kaptanın emriyle 65'te tutuldu.

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

    # 🔥 BÜYÜK GÜNCELLEME: "HEDEF = ROTA, İNDİKATÖR = İZİN" DENGESİ KURULDU
    system_prompt = f"""
    You are a top-tier, cold-blooded Institutional Quant and Crypto Futures Market Maker.
    Your timeframe is strictly 1H (One Hour). Your ONLY objective is institutional-grade accuracy.

    CURRENT SYSTEM TIME: {current_time_utc}
    
    INSTITUTIONAL QUANT RULES (THE PERFECT BALANCE):
    
    1. THE DESTINATION (Liquidity Targets):
       - The user will provide a Liquidity Target (e.g., Upper Target: 1922). This target is your DESTINATION. It shows where the market magnet is.
       - If the user types "YOK", "0", or "NONE", that direction is empty. NEVER trade towards an empty zone.
       
    2. THE PERMISSION (Indicator Alignment):
       - The indicators are your GATEKEEPERS. You CANNOT force a trade to the Destination if the Gatekeepers say NO.
       - Do not ignore the indicators just because a target exists.
       - If the user gives an Upper Target (LONG), BUT the structural trend (VWAP, EMA) is bearish or volume (OBV) is declining, you MUST output HOLD. You must wait for the indicators to turn bullish before you hunt the upper target.
       - If the user gives a Lower Target (SHORT), BUT the indicators are bullish, output HOLD.
       
    3. MARKET REGIME SYNTHESIS:
       - Synthesize the indicators. ADX for trend strength, BBands for volatility, OBV for smart money flow.
       - Do not just count signals. If price is structurally bearish, a high RSI just means a lower-high pullback, not a LONG signal.

    4. DISTANCE & RISK MANAGEMENT:
       - 1H charts require breathing room. Ensure the price distance between ENTRY, SL, and TP reflects a 1H institutional swing trade.
       - Minimum viable Risk/Reward (RR) is {MIN_RR}.

    5. SCORING REALITY: 
       - If Destination and Permission perfectly align (Target is up, indicators are strongly bullish), score 80-95%.
       - If Target is up, but indicators are mixed or slightly bearish, SCORE IT LOW (40-55%) AND OUTPUT "HOLD". Tell the user what indicator needs to flip before entry.

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
     "confluence_score": "e.g., Target aligns with Structural Trend",
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
     "why": ["Destination analysis", "Permission/Indicator analysis"],
     "what_to_watch_for": "Specific action to wait for before entering a trade.",
     "cancel_conditions": ["If 1H candle closes below structural support"],
     "market_summary": "1 sentence institutional assessment."
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
                "why": ["System Error: AI failed to parse TA synthesis.", "Fallback protocol engaged."],
                "what_to_watch_for": "Wait for the next 1H candle and re-analyze.",
                "cancel_conditions": ["Automatic fallback triggered"],
                "market_summary": "Analysis failed due to core processing error.",
                "market_regime": "Unknown",
                "confluence_score": "Error"
            })

        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        # 🛑 QUANT RISK YÖNETİMİ FİLTRESİ
        if direction in ["LONG", "SHORT"]:
            if rr < MIN_RR or confidence < MIN_CONFIDENCE:
                parsed["direction"] = "HOLD"
                parsed["entry"] = None
                parsed["tp"] = None
                parsed["sl"] = None
                parsed["risk"] = "High"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"🚨 QUANT OVERRIDE: Setup lacks institutional viability. Expected Confidence: {MIN_CONFIDENCE}%, Actual: {confidence}%. Trade blocked.")
                parsed["market_summary"] = "Trade blocked by Quant Risk Management Protocol."
                parsed["what_to_watch_for"] = f"Awaiting structural alignment with Confidence >= {MIN_CONFIDENCE}%."

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
