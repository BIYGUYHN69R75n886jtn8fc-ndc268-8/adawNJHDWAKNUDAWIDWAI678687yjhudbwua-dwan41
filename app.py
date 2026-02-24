import os
import json
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
from openai import OpenAI

print("ULTRA PRO QUANT ENGINE v19 (Execution-First) starting...")

app = Flask(__name__, static_folder="static")

# Kapalı ortam tek kullanıcı olsa bile bunu env'den vermen iyi olur.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "grypto_super_gizli_anahtar_degistir_bunu_123")

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY missing. /chat will fail until you set it.")

MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-4o")
client = OpenAI(api_key=OPENAI_API_KEY)

# ENGINE PARAMETERS
MIN_CONFIDENCE = 65
BASE_MIN_RR = 1.5

# VIP USERS (kapalı ağ/tek kullanıcı için şimdilik böyle kalsın)
VIP_USERS = {"alpha576": "Ma-3007.1", "alen": "alen.123"}

# --- Live context cache (jitter/latency azaltır) ---
_LIVE_CTX_CACHE = {"ts": 0.0, "value": "Live Context: Unavailable."}
_LIVE_CTX_TTL_SECONDS = 90


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def get_live_market_context() -> str:
    """Fetches macro/news context with a short cache."""
    now_ts = _now_ts()
    if (now_ts - _LIVE_CTX_CACHE["ts"]) < _LIVE_CTX_TTL_SECONDS:
        return _LIVE_CTX_CACHE["value"]

    context = "Live Context: Unavailable."
    try:
        fgi_r = requests.get("https://api.alternative.me/fng/", timeout=5)
        fgi_r.raise_for_status()
        fgi_data = fgi_r.json()["data"][0]
        sentiment = f"Fear & Greed Index: {fgi_data['value']} ({fgi_data['value_classification']}). "

        news_r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", timeout=5)
        news_r.raise_for_status()
        news_data = (news_r.json().get("Data") or [])[:5]

        def _fmt_item(n):
            try:
                t = datetime.fromtimestamp(int(n.get("published_on", 0))).strftime("%H:%M")
            except Exception:
                t = "??:??"
            return f"{n.get('title','').strip()} (Pub: {t})"

        headlines = " | ".join([_fmt_item(n) for n in news_data if n.get("title")])
        context = f"{sentiment} Recent Headlines: {headlines}" if headlines else sentiment.strip()
    except Exception as e:
        logging.error(f"Live data fetch error: {e}")

    _LIVE_CTX_CACHE["ts"] = now_ts
    _LIVE_CTX_CACHE["value"] = context
    return context


@app.before_request
def check_auth():
    # login + static serbest; HTML sayfaları VIP korumalı
    if request.endpoint in ["login", "static_proxy"]:
        if request.path.endswith(".html") and not session.get("logged_in"):
            return redirect(url_for("login"))
        return
    if not session.get("logged_in"):
        if request.path in ["/", "/chat"]:
            return redirect(url_for("login"))


LOGIN_HTML = """<!DOCTYPE html>
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
    <h2 style="color: #05fd05;">GRYPTO AI</h2><p style="color: #94a3b8; font-size: 14px;">Institutional Sniper Engine v19</p>
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


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        u, p = request.form.get("username"), request.form.get("password")
        if u in VIP_USERS and VIP_USERS[u] == p:
            session["logged_in"] = True
            return redirect("/index.html")
        error = "Invalid credentials!"
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    return redirect("/index.html")


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True) or {}
    user_input = (data.get("input") or "").strip()

    # Optional structured additions from client
    coin = (data.get("coin") or "").strip()
    upper_liq = (data.get("upper_liq") or "").strip()
    lower_liq = (data.get("lower_liq") or "").strip()

    if any([coin, upper_liq, lower_liq]):
        user_input += "\n\n[CLIENT_META]\n"
        if coin:
            user_input += f"symbol={coin}\n"
        if upper_liq:
            user_input += f"upper_liq={upper_liq}\n"
        if lower_liq:
            user_input += f"lower_liq={lower_liq}\n"

    current_time_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    live_news = get_live_market_context()

    system_prompt = f"""
ROLE: Tier-1 Crypto Hedge Fund Quant Executioner (1H).
LIVE MACRO: {live_news}
CURRENT TIME: {current_time_utc}

RULES:
1) DO NOT score indicators. The user prompt contains the absolute hardcoded Bull/Bear/Neutral score. Treat it as ground truth.
2) Use liquidation pool targets (if provided) ONLY as TP/SL anchors, not as a reason to ignore market regime.
3) Prefer HOLD in choppy/ranging regime unless confluence is exceptional.
4) Output HOLD if confidence < {MIN_CONFIDENCE}% OR rr < {BASE_MIN_RR}.

OUTPUT: Return JSON ONLY with the following schema (no extra keys):
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
  "why": ["Point 1", "Point 2"],
  "what_to_watch_for": "Confirmation",
  "cancel_conditions": ["Invalidation"],
  "market_summary": "Institutional summary"
}}
"""

    if not user_input:
        return jsonify({"direction": "HOLD", "why": ["Empty input."], "confidence": 0, "rr": 0.0}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            top_p=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )

        parsed = json.loads(response.choices[0].message.content.strip())

        # Normalize
        direction = str(parsed.get("direction", "HOLD")).upper().strip()
        if direction not in ("LONG", "SHORT", "HOLD"):
            direction = "HOLD"
        parsed["direction"] = direction

        parsed["confidence"] = _safe_int(parsed.get("confidence"), 0)
        parsed["rr"] = _safe_float(parsed.get("rr"), 0.0)

        if not isinstance(parsed.get("why"), list):
            parsed["why"] = [str(parsed.get("why"))] if parsed.get("why") else []
        if not isinstance(parsed.get("cancel_conditions"), list):
            parsed["cancel_conditions"] = [str(parsed.get("cancel_conditions"))] if parsed.get("cancel_conditions") else []

        # Sniper Guard
        if parsed["direction"] in ("LONG", "SHORT"):
            if parsed["confidence"] < MIN_CONFIDENCE or parsed["rr"] < BASE_MIN_RR:
                parsed["direction"] = "HOLD"
                parsed["why"].append(
                    f"Sniper Guard: Confidence ({parsed['confidence']}%) or RR ({parsed['rr']}) failed minimums."
                )

        return jsonify(parsed)

    except Exception:
        logging.exception("ENGINE ERROR:")
        return jsonify({"direction": "HOLD", "why": ["System fallback engaged due to parsing error."], "confidence": 0, "rr": 0.0}), 500


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
