import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

print("ULTRA PRO QUANT ENGINE v5 (SaaS VIP Edition) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI: Oturumların hacklenmemesi için buraya rastgele bir şeyler yaz.
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

# 🔑 BURAYA API KEY 
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

MIN_RR = 1.5       
MIN_CONFIDENCE = 65 

# 👥 MÜŞTERİ VERİTABANI (Sadece bu listeye eklediğin kişiler sisteme girebilir)
VIP_USERS = {
    "admin": "admin123",        # Kendin için

}

# 🎨 ŞIK GİRİŞ EKRANI TASARIMI (Müşterilerin göreceği ilk ekran)
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
    <p style="color: #94a3b8; margin-top: 0; margin-bottom: 25px; font-size: 14px;">Exclusive VIP Signal Engine</p>
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

# 🛡️ GÜVENLİK DUVARI: Giriş yapmayanları dışarı atar
@app.before_request
def check_auth():
    # Giriş yapılmışsa veya giriş sayfasına/resimlere erişiliyorsa izin ver
    if request.endpoint in ['login', 'static_proxy']:
        # Ancak static altındaki .html dosyalarına direkt erişimi engelle
        if request.path.endswith('.html') and not session.get('logged_in'):
            return redirect(url_for('login'))
        return
    
    # Giriş yapılmadıysa ana sayfayı ve chat'i engelle
    if not session.get('logged_in'):
        if request.path == '/' or request.path == '/chat':
            return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Müşteri kontrolü
        if username in VIP_USERS and VIP_USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/')
        else:
            error = "Invalid username or password!"
            
    return render_template_string(LOGIN_HTML, error=error)

# 🚪 Çıkış yapma linki (Sistemi test ederken kullanabilirsin: /logout)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return send_from_directory(app.static_folder, "ethereum.html")

@app.route('/chat', methods=['POST'])
def chat():
    # Sadece giriş yapanlar API'ye istek atabilir
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json(force=True)
    user_input = data.get("input", "").strip()

    if not user_input:
        return jsonify({"error": "Input message is required."}), 400

    system_prompt = f"""
    You are an elite, disciplined crypto futures sniper (Day Trader).
    Timeframe: 15m scalp. Your goal is to find 3-4 high-probability setups per day.

    I am giving you 15 indicators. Analyze them in these categories:
    1. TREND: EMA, ADX, Supertrend, SAR, Ichimoku
    2. MOMENTUM: RSI, MACD, STOCH, CCI
    3. VOLATILITY/LEVELS: BBANDS, ATR, Keltner
    4. VOLUME/MONEY FLOW: OBV, MFI, VWAP

    RULES FOR ENTRY (SNIPER MODE):
    - MOMENTUM IS KING: If Momentum and Volume align, you CAN enter even if Macro Trend is neutral.
    - RISK/REWARD: Minimum viable RR must be {MIN_RR}.
    - CONFIDENCE: Must be {MIN_CONFIDENCE} or higher. Take the shot if it's a solid setup.
    - If HOLDing, you MUST provide actionable advice on what the user should wait for.
    - Provide nearest Support and Resistance levels based on Volatility indicators (BBANDS, Keltner) and current price.

    JSON FORMAT EXACTLY AS BELOW:
    {{
     "direction": "LONG|SHORT|HOLD",
     "market_regime": "Trending|Micro-Trend|Ranging",
     "entry": float or null,
     "tp": float or null,
     "sl": float or null,
     "support_level": float or null,
     "resistance_level": float or null,
     "confidence": integer 0-100,
     "risk": "Low|Medium|High",
     "rr": float,
     "confluence_score": "e.g., 10/15 Strong Momentum",
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
     "cancel_conditions": ["If price drops below X"],
     "market_summary": "1 sentence sharp tactical assessment."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
                "indicator_votes": {},
                "why": ["AI failed to generate valid JSON: " + str(e)],
                "what_to_watch_for": "System parsing error, retrying...",
                "cancel_conditions": ["System fallback"],
                "market_summary": "Parse error in AI generation.",
                "market_regime": "Unknown",
                "confluence_score": "Error"
            })

        direction = parsed.get("direction", "HOLD")
        
        raw_conf = parsed.get("confidence")
        confidence = int(raw_conf) if raw_conf is not None else 0
        
        raw_rr = parsed.get("rr")
        rr = float(raw_rr) if raw_rr is not None else 0.0

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