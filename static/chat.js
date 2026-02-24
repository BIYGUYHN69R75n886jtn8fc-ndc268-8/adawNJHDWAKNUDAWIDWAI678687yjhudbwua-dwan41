// static/chat.js
(function () {
  const TWELVE_API_KEY = "d3123a9d9d344ce99c9e05fa75e32b78";
  const INTERVAL = "1h";

  // --- Minimal XSS-safe escaping (single-user bile olsa UI integrity için) ---
  function escapeHtml(v) {
    return String(v ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function parseLooseNumber(str) {
    if (!str) return "";
    const s = String(str).trim().replace(/\s+/g, "").replace(",", ".");
    // allow only [-]digits[.digits]
    if (!/^-?\d+(\.\d+)?$/.test(s)) return "";
    return s;
  }

  function getCoinInfo() {
    const body = document.body;
    const coinAttr = body.getAttribute("data-coin");
    const coinNameAttr = body.getAttribute("data-coin-name");
    if (coinAttr && coinNameAttr) return { coin: coinAttr, coinName: coinNameAttr };

    const file = (window.location.pathname.split("/").pop() || "").toLowerCase();
    const map = {
      "ethereum.html": { coin: "ETHUSDT", coinName: "Ethereum" },
      "analiz.html": { coin: "BTCUSDT", coinName: "Bitcoin" },
    };
    return map[file] || { coin: "ETHUSDT", coinName: "Ethereum" };
  }

  async function fetchCurrentPrice(symbol) {
    const url = `https://api.twelvedata.com/price?symbol=${encodeURIComponent(symbol)}&apikey=${TWELVE_API_KEY}`;
    const r = await fetch(url);
    const j = await r.json();
    const p = parseFloat(j.price);
    return Number.isFinite(p) ? p : NaN;
  }

  function readIndicatorText(id) {
    const el = document.getElementById(id);
    if (!el) return "N/A";
    return (el.textContent || el.innerText || "").trim();
  }

  // Keep your existing hard-math scoring (unchanged)
  function calculateHardMath(values, price) {
    let bull = 0, bear = 0, neutral = 0;

    const rsi = parseFloat(values.RSI);
    if (Number.isFinite(rsi)) {
      if (rsi > 55) bull++;
      else if (rsi < 45) bear++;
      else neutral++;
    } else neutral++;

    // (rest of your original scoring rules...)
    // NOTE: For brevity, this block is the SAME as your existing file.
    // I’m keeping your original calculateHardMath logic intact by copying it verbatim below.

    // ---- BEGIN ORIGINAL calculateHardMath (verbatim from your file) ----
    const ema = parseFloat(values.EMA);
    if (Number.isFinite(ema) && Number.isFinite(price)) {
      if (price > ema) bull++;
      else if (price < ema) bear++;
      else neutral++;
    } else neutral++;

    const macd = parseFloat(values.MACD);
    if (Number.isFinite(macd)) {
      if (macd > 0) bull++;
      else if (macd < 0) bear++;
      else neutral++;
    } else neutral++;

    const bb = String(values.BBANDS || "");
    if (bb.includes("Upper")) bull++;
    else if (bb.includes("Lower")) bear++;
    else neutral++;

    const atr = parseFloat(values.ATR);
    if (Number.isFinite(atr)) neutral++;
    else neutral++;

    const stoch = parseFloat(values.STOCH);
    if (Number.isFinite(stoch)) {
      if (stoch > 55) bull++;
      else if (stoch < 45) bear++;
      else neutral++;
    } else neutral++;

    const adx = parseFloat(values.ADX);
    if (Number.isFinite(adx)) {
      if (adx > 20) bull++;
      else neutral++;
    } else neutral++;

    const ichi = String(values.ICHIMOKU || "");
    if (ichi.includes("Bull")) bull++;
    else if (ichi.includes("Bear")) bear++;
    else neutral++;

    const obv = String(values.OBV || "");
    if (obv.includes("Up")) bull++;
    else if (obv.includes("Down")) bear++;
    else neutral++;

    const kelt = String(values.KELTNER || "");
    if (kelt.includes("Bull")) bull++;
    else if (kelt.includes("Bear")) bear++;
    else neutral++;

    const sar = String(values.SAR || "");
    if (sar.includes("Bull")) bull++;
    else if (sar.includes("Bear")) bear++;
    else neutral++;

    const vwap = String(values.VWAP || "");
    if (vwap.includes("Above")) bull++;
    else if (vwap.includes("Below")) bear++;
    else neutral++;

    const mfi = parseFloat(values.MFI);
    if (Number.isFinite(mfi)) {
      if (mfi > 55) bull++;
      else if (mfi < 45) bear++;
      else neutral++;
    } else neutral++;

    const supertrend = String(values.Supertrend || "");
    if (supertrend.includes("Bull")) bull++;
    else if (supertrend.includes("Bear")) bear++;
    else neutral++;

    const cci = parseFloat(values.CCI);
    if (Number.isFinite(cci)) {
      if (cci > 50) bull++;
      else if (cci < -50) bear++;
      else neutral++;
    } else neutral++;
    // ---- END ORIGINAL calculateHardMath ----

    return { bull, bear, neutral };
  }

  async function buildAutoPrompt() {
    const { coin, coinName } = getCoinInfo();
    const values = {
      RSI: readIndicatorText("rsi"),
      EMA: readIndicatorText("ema"),
      MACD: readIndicatorText("macd"),
      BBANDS: readIndicatorText("bbands"),
      ATR: readIndicatorText("atr"),
      STOCH: readIndicatorText("stoch"),
      ADX: readIndicatorText("adx"),
      ICHIMOKU: readIndicatorText("ichimoku"),
      OBV: readIndicatorText("obv"),
      KELTNER: readIndicatorText("keltner"),
      SAR: readIndicatorText("sar"),
      VWAP: readIndicatorText("vwap"),
      MFI: readIndicatorText("mfi"),
      Supertrend: readIndicatorText("supertrend"),
      CCI: readIndicatorText("cci"),
    };

    const price = await fetchCurrentPrice(coin);
    window.deterministicScores = calculateHardMath(values, price);

    return (
`I am now providing you with ${coinName} 1H data:
Current price: ${price}

RSI: ${values.RSI} | EMA: ${values.EMA} | MACD: ${values.MACD}
BBANDS: ${values.BBANDS} | ATR: ${values.ATR} | STOCH: ${values.STOCH}
ADX: ${values.ADX} | ICHIMOKU: ${values.ICHIMOKU} | OBV: ${values.OBV}
KELTNER: ${values.KELTNER} | SAR: ${values.SAR} | VWAP: ${values.VWAP}
MFI: ${values.MFI} | Supertrend: ${values.Supertrend} | CCI: ${values.CCI}

🔥 HARDCODED SCORE: ${window.deterministicScores.bull} Bullish | ${window.deterministicScores.neutral} Neutral | ${window.deterministicScores.bear} Bearish.
DO NOT recalculate this score. Use it as an absolute mathematical fact.
I’m about to open a position. Based on these data, give me direction and TP/SL.`
    );
  }

  async function autoFillChat() {
    const textarea = document.getElementById("user-input");
    if (!textarea) return;
    textarea.value = await buildAutoPrompt();
    setTimeout(async () => { textarea.value = await buildAutoPrompt(); }, 1500);
  }

  function hookChatUI() {
    const toggleBtn = document.getElementById("toggle-expand");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", function () {
        const widget = document.getElementById("chat-widget");
        widget.classList.toggle("expanded");
        widget.classList.toggle("collapsed");
        this.innerHTML = widget.classList.contains("expanded") ? "&#x2923;" : "&#x2922;";
      });
    }
    const input = document.getElementById("user-input");
    if (input) {
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          if (typeof window.getSignal === "function") window.getSignal();
        }
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    hookChatUI();
    autoFillChat();
  });

  // 🔥 PROFESSIONAL SIGNAL ENGINE DISPLAY
  window.getSignal = async function () {
    const { coin, coinName } = getCoinInfo();
    const chat = document.getElementById("chat-messages");
    if (!chat) return;

    const loadingId = "loading-" + Date.now();
    chat.innerHTML += `<div id="${loadingId}" class="message" style="color:#94a3b8;"><strong>${escapeHtml(coinName)}:</strong> AI is analyzing 1H charts & liquidity pools... 🧠⚙️</div>`;
    chat.scrollTop = chat.scrollHeight;

    try {
      let promptText = await buildAutoPrompt();

      // keep textarea synced
      const textarea = document.getElementById("user-input");
      if (textarea) textarea.value = promptText;

      // Manual liquidation inputs (tolerant parsing)
      const upperRaw = document.getElementById("upper-liq") ? document.getElementById("upper-liq").value.trim() : "";
      const lowerRaw = document.getElementById("lower-liq") ? document.getElementById("lower-liq").value.trim() : "";
      const upperLiq = parseLooseNumber(upperRaw);
      const lowerLiq = parseLooseNumber(lowerRaw);

      // Still append to prompt (keeps your current behavior), but also send separately to backend
      if (upperLiq !== "" || lowerLiq !== "") {
        promptText += `\n\n🚨 LIQUIDATION MAP (MANUAL INPUT):\n`;
        if (upperLiq !== "") promptText += `- Upper Pool: ${upperLiq}\n`;
        if (lowerLiq !== "") promptText += `- Lower Pool: ${lowerLiq}\n`;
        promptText += `\nINSTRUCTION: If LONG, set 'tp' slightly below ${upperLiq || "the upper pool"}. If SHORT, set 'tp' slightly above ${lowerLiq || "the lower pool"}. Adjust 'sl' for RR >= 1.5.\n`;
      }

      const r = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: promptText,
          coin,
          upper_liq: upperLiq,
          lower_liq: lowerLiq
        })
      });

      const j = await r.json();
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      if (j.error) {
        chat.innerHTML += `<div class="message"><strong>Error:</strong> <span style="color:#ff4444;">${escapeHtml(j.error)}</span></div>`;
        return;
      }

      // sanitize fields once
      const s = {
        direction: escapeHtml(j.direction ?? "HOLD"),
        confidence: escapeHtml(j.confidence ?? 0),
        market_regime: escapeHtml(j.market_regime ?? "Unknown"),
        confluence_score: escapeHtml(j.confluence_score ?? "-"),
        resistance_level: escapeHtml(j.resistance_level ?? "N/A"),
        support_level: escapeHtml(j.support_level ?? "N/A"),
        entry: escapeHtml(j.entry ?? "N/A"),
        partial_tp: escapeHtml(j.partial_tp ?? "N/A"),
        tp: escapeHtml(j.tp ?? "N/A"),
        sl: escapeHtml(j.sl ?? "N/A"),
        rr: escapeHtml(j.rr ?? "0"),
        risk: escapeHtml(j.risk ?? "N/A"),
        liquidity_target: escapeHtml(j.liquidity_target ?? "N/A"),
        what_to_watch_for: escapeHtml(j.what_to_watch_for ?? ""),
        market_summary: escapeHtml(j.market_summary ?? ""),
        why_html: Array.isArray(j.why) ? j.why.map(escapeHtml).join("<br>") : escapeHtml(j.why ?? ""),
        cancel_html: Array.isArray(j.cancel_conditions) ? j.cancel_conditions.map(escapeHtml).join("<br>") : escapeHtml(j.cancel_conditions ?? "")
      };

      let directionColor = "#eab308";
      if (j.direction === "LONG") directionColor = "#22c55e";
      if (j.direction === "SHORT") directionColor = "#ef4444";

      let bullCount = window.deterministicScores ? window.deterministicScores.bull : 0;
      let bearCount = window.deterministicScores ? window.deterministicScores.bear : 0;
      let neutralCount = window.deterministicScores ? window.deterministicScores.neutral : 15;

      chat.innerHTML += `
        <div class="message" style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid ${directionColor}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong style="font-size: 1.2em; color: #fff;">${escapeHtml(coinName)} 1H Signal</strong> 
            <div style="background: #0f172a; padding: 4px 10px; border-radius: 6px; border: 1px solid ${directionColor};">
                <b style="color: ${directionColor}; font-size: 1.2em;">${s.direction}</b> 
                <span style="color:#94a3b8; font-size: 0.9em;">(${s.confidence}%)</span>
            </div>
          </div>
          
          <div style="background: #0f172a; padding: 10px; border-radius: 6px; font-size: 0.9em; margin-bottom: 10px; border: 1px solid #334155;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                  <div><b>📊 Market:</b> <span style="color:#38bdf8;">${s.market_regime}</span></div>
                  <div><b>🎯 Score:</b> <span style="color:#a78bfa;">${s.confluence_score}</span></div>
                  <div><b>📈 Resistance:</b> <span style="color:#f472b6;">${s.resistance_level}</span></div>
                  <div><b>📉 Support:</b> <span style="color:#34d399;">${s.support_level}</span></div>
              </div>
              
              <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed #334155; text-align: center;">
                 <span style="color: #22c55e;">🟢 ${bullCount} Bull</span> &nbsp;|&nbsp; 
                 <span style="color: #94a3b8;">⚪ ${neutralCount} Neutral</span> &nbsp;|&nbsp; 
                 <span style="color: #ef4444;">🔴 ${bearCount} Bear</span>
              </div>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div style="background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155;">
              <div><b>Entry:</b> <span style="color:#fff;">${s.entry}</span></div>
              <div><b>Partial TP:</b> <span style="color:#fff;">${s.partial_tp}</span></div>
              <div><b>TP:</b> <span style="color:#22c55e;">${s.tp}</span></div>
              <div><b>SL:</b> <span style="color:#ef4444;">${s.sl}</span></div>
            </div>
            <div style="background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155;">
              <div><b>RR:</b> <span style="color:#fff;">${s.rr}</span></div>
              <div><b>Risk:</b> <span style="color:#fff;">${s.risk}</span></div>
              <div><b>Liq Target:</b> <span style="color:#fff;">${s.liquidity_target}</span></div>
              <div style="margin-top:8px; font-size:12px; color:#94a3b8;"><b>Watch:</b> ${s.what_to_watch_for}</div>
            </div>
          </div>

          <div style="background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155; margin-bottom:10px;">
            <b style="color:#fff;">Why:</b>
            <div style="margin-top:6px; color:#cbd5e1; line-height:1.35;">${s.why_html || "—"}</div>
          </div>

          <div style="background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155; margin-bottom:10px;">
            <b style="color:#fff;">Cancel Conditions:</b>
            <div style="margin-top:6px; color:#cbd5e1; line-height:1.35;">${s.cancel_html || "—"}</div>
          </div>

          <div style="background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155;">
            <b style="color:#fff;">Market Summary:</b>
            <div style="margin-top:6px; color:#cbd5e1; line-height:1.35;">${s.market_summary || "—"}</div>
          </div>
        </div>
      `;

      chat.scrollTop = chat.scrollHeight;

    } catch (e) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      chat.innerHTML += `<div class="message"><strong>System Error:</strong> <span style="color:#ff4444;">${escapeHtml(e.message)}</span></div>`;
    }
  };
})();
