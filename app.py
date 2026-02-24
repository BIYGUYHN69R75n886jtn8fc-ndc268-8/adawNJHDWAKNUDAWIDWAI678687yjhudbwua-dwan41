import os
import json
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

# Profesyonel Loglama Başlatıldı
print("ULTRA PRO QUANT ENGINE v17 (Apex Institutional Sniper - 4 Pillar Synthesis) is starting...")

app = Flask(__name__, static_folder='static')
# 🔐 GÜVENLİK ANAHTARI
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)import os
import json
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

# Profesyonel Loglama Başlatıldı
print("ULTRA PRO QUANT ENGINE v18 (Deterministic Apex - Zero Hallucination) is starting...")

app = Flask(__name__, static_folder='static')
app.secret_key = "grypto_super_gizli_anahtar_degistir_bunu_123" 
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SİSTEM PARAMETRELERİ
MIN_CONFIDENCE = 65  
BASE_MIN_RR = 1.5    

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
    <h2 style="color: #05fd05;">GRYPTO AI</h2><p style="color: #94a3b8; font-size: 14px;">Institutional Sniper Engine v18</p>
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

    # 🔥 v18: OYLAMA KALDIRILDI, SADECE EXECUTION (INFAZ) YAPACAK.
    system_prompt = f"""
    ROLE: Tier-1 Crypto Hedge Fund Quant Executioner.
    LIVE MACRO: {live_news}
    CURRENT TIME: {current_time_utc}

    PROTOCOL:
    1. DO NOT score indicators. The user prompt already contains the absolute, hardcoded mathematical Bull/Bear score. Trust that score.
    2. Focus ONLY on matching the mathematical score and Live News against the user's Liquidation Target (tp/sl).
    3. Calculate the absolute Risk/Reward (RR) ratio.
    4. Provide 'partial_tp' at 50% distance.
    5. Output HOLD if Confidence < {MIN_CONFIDENCE}% OR RR < {BASE_MIN_RR}.

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
     "why": ["Analysis 1", "Analysis 2"],
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

        # 🛑 FIXED SNIPER GUARD
        if direction in ["LONG", "SHORT"]:
            if confidence < MIN_CONFIDENCE or rr < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                if "why" in parsed: parsed["why"].append(f"Sniper Guard: Confidence ({confidence}%) or RR ({rr}) failed minimums.")

        return jsonify(parsed)

    except Exception as e:
        logging.exception("ENGINE ERROR:")
        return jsonify({"direction": "HOLD", "why": ["System fallback engaged due to parsing error."]}), 500

@app.route('/<path:path>')
def static_proxy(path): return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

# 🔑 API ANAHTARI VE BAĞLANTI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SİSTEM PARAMETRELERİ
MIN_CONFIDENCE = 65  # Kaptan emri: %65 altı işlemler otomatik HOLD.
BASE_MIN_RR = 1.5    # Dinamik RR için taban sınır. Asla esnetilmez.

# 👥 MÜŞTERİ VERİTABANI
VIP_USERS = {
    "alpha576": "Ma-3007.1",        
    "alen": "alen.123"
} 

# 🌐 CANLI VERİ KÖPRÜSÜ (Oracle News Decay Layer)
def get_live_market_context():
    """Python aracılığıyla internete bağlanıp saniyelik haberleri ve sentimenti çeker."""
    context = "Live Context: Unavailable (API Timeout)."
    try:
        # 1. Korku ve Açgözlülük Endeksi (Canlı)
        fgi_r = requests.get("https://api.alternative.me/fng/", timeout=5)
        fgi_data = fgi_r.json()['data'][0]
        sentiment = f"Fear & Greed Index: {fgi_data['value']} ({fgi_data['value_classification']}). "
        
        # 2. Canlı Kripto Haber Başlıkları + Yayın Saatleri
        news_r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", timeout=5)
        news_data = news_r.json()['Data'][:5] # Son 5 ana haber
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
    <p style="color: #94a3b8; margin-top: 0; margin-bottom: 25px; font-size: 14px;">Institutional Sniper Engine (1H)</p>
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

    # 🔥 v17: INSTITUTIONAL APEX ORACLE PROMPT (4-PILLAR SYNTHESIS)
    system_prompt = f"""
    ROLE: You are the Lead AI-Quant Trader at a Tier-1 Crypto Hedge Fund. 
    LIVE MACRO CONTEXT: {live_news}
    CURRENT TIME: {current_time_utc}

    STRICT 4-STEP ALGORITHMIC PIPELINE:

    STEP 1: MACRO & REGIME FILTER (The Weather)
    - Evaluate 'Fear & Greed' and 'Live News'. Highly impactful recent news (<2 hours) overrules technicals. If the macro is violently bearish, do not force a long position.

    STEP 2: MICRO-MECHANICS (The 4 Pillars - ABSOLUTE ISOLATION)
    You MUST evaluate the 15 indicators across 4 domains. CRITICAL FLAG: Score them PURELY by their raw mathematical definitions. DO NOT let the user's Liquidity Target (tp/sl) alter the indicator's vote. (e.g., if RSI is 29, it is ALWAYS 'bullish' even if the target is impossible).
    - Pillar A (Volume/Flow): OBV, MFI, VWAP. (Is Smart Money accumulating or distributing?)
    - Pillar B (Momentum): RSI, MACD, STOCH, CCI. (Is the asset overbought/oversold? Speed of trend?)
    - Pillar C (Volatility/Borders): ATR, BBANDS, KELTNER. (Are we at statistical extremes or squeezing?)
    - Pillar D (Trend/Structure): EMA, ADX, ICHIMOKU, SAR, SUPERTREND. (What is the prevailing structural path?)

    STEP 3: LIQUIDITY MAGNETS (The Target)
    - Look at the user's provided Liquidity Targets (tp/sl). Based on the synthesis of Step 1 and Step 2, decide which liquidity pool the price is magnetically drawn to. 

    STEP 4: EXECUTION & RISK (The Sniper)
    - Calculate the absolute Risk/Reward (RR) ratio based strictly on Entry, Final TP, and SL. 
    - Suggest a 'partial_tp' at 50% of the distance to the Final TP. 
    - You MUST output "direction": "HOLD" if Confidence < {MIN_CONFIDENCE}% OR RR < {BASE_MIN_RR}.

    JSON FORMAT EXACTLY AS BELOW:
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
     "confluence_score": "Brief summary of confluence factors based on the 4 Pillars",
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
     "why": ["Macro Sentiment Analysis", "4-Pillar Technical Synthesis"],
     "what_to_watch_for": "Action needed for entry confirmation.",
     "cancel_conditions": ["If candle closes below/above level X"],
     "market_summary": "Sharp institutional assessment."
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

        try:
            parsed = json.loads(raw)
        except Exception as e:
            # Fallback bloğu - Sistem çökmesini önler
            return jsonify({
                "direction": "HOLD",
                "confidence": 0,
                "risk": "High",
                "rr": 0,
                "entry": None,
                "partial_tp": None,
                "tp": None,
                "sl": None,
                "support_level": None,
                "resistance_level": None,
                "liquidity_target": None,
                "indicator_votes": {},
                "why": ["Parse Error: Failed to synthesize TA and News.", "Fallback protocol engaged."],
                "what_to_watch_for": "Retry analysis.",
                "cancel_conditions": ["Automatic fallback triggered"],
                "market_summary": "Analysis failed due to core processing error.",
                "market_regime": "Unknown",
                "confluence_score": "Error"
            })

        direction = parsed.get("direction", "HOLD")
        confidence = int(parsed.get("confidence") or 0)
        rr = float(parsed.get("rr") or 0.0)

        # 🛑 APEX SNIPER PROTECTION (1.5 RR & %65 Confidence Guard)
        if direction in ["LONG", "SHORT"]:
            if confidence < MIN_CONFIDENCE or rr < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                if "why" in parsed and isinstance(parsed["why"], list):
                    parsed["why"].append(f"🚨 SNIPER GUARD: Confidence ({confidence}%) or RR ({rr}) failed Apex threshold (Target RR: {BASE_MIN_RR}).")
                parsed["market_summary"] = "Trade filtered out by institutional risk management protocol."

        return jsonify(parsed)

    except Exception as e:
        logging.exception("ORACLE ENGINE CRITICAL ERROR:")
        return jsonify({"direction": "HOLD", "why": [f"System Error: {str(e)}"]}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

