// static/chat.js
(function () {
  const TWELVE_API_KEY = "d3123a9d9d344ce99c9e05fa75e32b78";
  const INTERVAL = "1h";

  // UI integrity (single-user bile olsa): model ya da input HTML basıp paneli bozmasın
  function escapeHtml(v) {
    return String(v ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // 3920, 3920.5, 3,920.5 gibi girdileri tolere eder; sayı değilse "" döner
  function parseLooseNumber(str) {
    if (!str) return "";
    const s = String(str).trim().replace(/\s+/g, "").replace(/,/g, ".");
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

  // ✅ FIXED: TwelveData price (encode + correct symbol format)
  async function fetchCurrentPrice(symbol) {
    try {
      // ETHUSDT -> ETH/USDT (sadece USDT ile bitiyorsa)
      const formatted = String(symbol || "").replace(/USDT$/i, "/USDT");

      const url = `https://api.twelvedata.com/price?symbol=${encodeURIComponent(formatted)}&apikey=${TWELVE_API_KEY}`;
      const r = await fetch(url);
      const j = await r.json();

      // TwelveData bazen {status:"error", message:"..."} döndürür
      if (!j || j.status === "error" || !j.price) {
        console.error("Price fetch error:", j);
        return "N/A";
      }

      const p = parseFloat(j.price);
      if (!Number.isFinite(p)) return "N/A";

      // İstersen sanity check (ETH/BTC gibi coinlerde 100 altı saçma):
      // if (p < 100) return "N/A";

      return p.toFixed(2);
    } catch (e) {
      console.error("Price fetch failed:", e);
      return "N/A";
    }
  }

  function readIndicatorText(id) {
    const el = document.getElementById(id);
    if (!el) return "N/A";
    return (el.textContent || el.innerText || "").trim();
  }

  // (Opsiyonel ama faydalı) Prompt'taki "RSI: RSI:" gibi çift prefixleri azaltır
  function stripDoublePrefix(text, prefixes) {
    let t = String(text || "").trim();
    for (const p of prefixes) {
      const re = new RegExp("^\\s*" + p + "\\s*:\\s*", "i");
      t = t.replace(re, "");
    }
    return t.trim();
  }

  // ✅ Orijinal deterministik skor fonksiyonun (DEĞİŞTİRİLMEDİ)
  function calculateHardMath(values, currentPriceStr) {
    let p = parseFloat(currentPriceStr);
    let bull = 0, bear = 0, neutral = 0;
    if (isNaN(p)) return { bull: 0, bear: 0, neutral: 15 };

    const parseVal = (str) => parseFloat((str || "").replace(/[^0-9.-]/g, ""));

    // 1. RSI
    let rsi = parseVal(values.RSI);
    if (!isNaN(rsi)) {
      if (rsi <= 30) bull++;
      else if (rsi >= 70) bear++;
      else neutral++;
    }

    // 2. MFI
    let mfi = parseVal(values.MFI);
    if (!isNaN(mfi)) {
      if (mfi <= 20) bull++;
      else if (mfi >= 80) bear++;
      else neutral++;
    }

    // 3. CCI
    let cci = parseVal(values.CCI);
    if (!isNaN(cci)) {
      if (cci <= -100) bull++;
      else if (cci >= 100) bear++;
      else neutral++;
    }

    // 4. STOCH
    if (values.STOCH && values.STOCH.includes("/")) {
      let parts = values.STOCH.split("/");
      let k = parseVal(parts[0]),
        d = parseVal(parts[1]);
      if (k <= 20 && d <= 20) bull++;
      else if (k >= 80 && d >= 80) bear++;
      else neutral++;
    }

    // 5. BBANDS
    if (values.BBANDS && values.BBANDS.includes("/")) {
      let parts = values.BBANDS.split("/");
      let upper = parseVal(parts[0]),
        mid = parseVal(parts[1]),
        lower = parseVal(parts[2]);
      if (!isNaN(upper) && !isNaN(lower)) {
        if (p < lower) bull++;
        else if (p > upper) bear++;
        else neutral++;
      }
    }

    // 6. MACD
    let macd = parseVal(values.MACD);
    if (!isNaN(macd)) {
      if (macd > 0) bull++;
      else if (macd < 0) bear++;
      else neutral++;
    }

    // 7. VWAP
    let vwap = parseVal(values.VWAP);
    if (!isNaN(vwap)) {
      if (p > vwap) bull++;
      else if (p < vwap) bear++;
      else neutral++;
    }

    // 8. SAR
    let sar = parseVal(values.SAR);
    if (!isNaN(sar)) {
      if (p > sar) bull++;
      else if (p < sar) bear++;
      else neutral++;
    }

    // 9. Supertrend
    let supertrend = parseVal(values.Supertrend);
    if (!isNaN(supertrend)) {
      if (p > supertrend) bull++;
      else if (p < supertrend) bear++;
      else neutral++;
    }

    // 10. Keltner
    if (values.KELTNER && values.KELTNER.includes("/")) {
      let parts = values.KELTNER.split("/");
      let upper = parseVal(parts[0]),
        mid = parseVal(parts[1]),
        lower = parseVal(parts[2]);
      if (!isNaN(upper) && !isNaN(lower)) {
        if (p < lower) bull++;
        else if (p > upper) bear++;
        else neutral++;
      }
    }

    // 11. ADX
    let adx = parseVal(values.ADX);
    if (!isNaN(adx)) {
      if (adx > 25) bull++;
      else neutral++;
    } else neutral++;

    // 12. Ichimoku
    if (values.ICHIMOKU && values.ICHIMOKU.includes("Bull")) bull++;
    else if (values.ICHIMOKU && values.ICHIMOKU.includes("Bear")) bear++;
    else neutral++;

    // 13. EMA
    if (values.EMA && values.EMA.includes("/")) {
      let parts = values.EMA.split("/");
      let ema20 = parseVal(parts[0]),
        ema50 = parseVal(parts[1]),
        ema200 = parseVal(parts[2]);
      let currentEma = ema20 || ema50 || ema200;
      if (!isNaN(currentEma)) {
        if (p > currentEma) bull++;
        else if (p < currentEma) bear++;
        else neutral++;
      } else {
        neutral++;
      }
    } else {
      neutral++;
    }

    // 14. OBV
    let obv = parseVal(values.OBV);
    if (!isNaN(obv)) {
      if (obv > 0) bull++;
      else if (obv < 0) bear++;
      else neutral++;
    } else {
      neutral++;
    }

    // 15. ATR
    neutral++;

    return { bull, bear, neutral };
  }

  async function buildAutoPrompt() {
    const { coin, coinName } = getCoinInfo();

    // RAW read
    let rsiText = readIndicatorText("rsi");
    let emaText = readIndicatorText("ema");
    let macdText = readIndicatorText("macd");
    let bbandsText = readIndicatorText("bbands");
    let atrText = readIndicatorText("atr");
    let stochText = readIndicatorText("stoch");
    let adxText = readIndicatorText("adx");
    let ichimokuText = readIndicatorText("ichimoku");
    let obvText = readIndicatorText("obv");
    let keltnerText = readIndicatorText("keltner");
    let sarText = readIndicatorText("sar");
    let vwapText = readIndicatorText("vwap");
    let mfiText = readIndicatorText("mfi");
    let supertrendText = readIndicatorText("supertrend");
    let cciText = readIndicatorText("cci");

    // Optional cleanup to reduce "RSI: RSI:"
    rsiText = stripDoublePrefix(rsiText, ["RSI"]);
    emaText = stripDoublePrefix(emaText, ["EMA"]);
    macdText = stripDoublePrefix(macdText, ["MACD"]);
    bbandsText = stripDoublePrefix(bbandsText, ["BBANDS", "BBANDS"]);
    atrText = stripDoublePrefix(atrText, ["ATR"]);
    stochText = stripDoublePrefix(stochText, ["STOCH"]);
    adxText = stripDoublePrefix(adxText, ["ADX"]);
    ichimokuText = stripDoublePrefix(ichimokuText, ["ICHIMOKU"]);
    obvText = stripDoublePrefix(obvText, ["OBV"]);
    keltnerText = stripDoublePrefix(keltnerText, ["KELTNER"]);
    sarText = stripDoublePrefix(sarText, ["SAR"]);
    vwapText = stripDoublePrefix(vwapText, ["VWAP"]);
    mfiText = stripDoublePrefix(mfiText, ["MFI"]);
    supertrendText = stripDoublePrefix(supertrendText, ["SUPERTREND", "Supertrend"]);
    cciText = stripDoublePrefix(cciText, ["CCI"]);

    const currentPrice = await fetchCurrentPrice(coin);

    const values = {
      RSI: rsiText,
      EMA: emaText,
      MACD: macdText,
      BBANDS: bbandsText,
      ATR: atrText,
      STOCH: stochText,
      ADX: adxText,
      ICHIMOKU: ichimokuText,
      OBV: obvText,
      KELTNER: keltnerText,
      SAR: sarText,
      VWAP: vwapText,
      MFI: mfiText,
      Supertrend: supertrendText,
      CCI: cciText,
    };

    window.deterministicScores = calculateHardMath(values, currentPrice);

    return `I am now providing you with ${coinName} 1H data:
Current price: ${currentPrice}
RSI: ${rsiText} | EMA: ${emaText} | MACD: ${macdText}
BBANDS: ${bbandsText} | ATR: ${atrText} | STOCH: ${stochText}
ADX: ${adxText} | ICHIMOKU: ${ichimokuText} | OBV: ${obvText}
KELTNER: ${keltnerText} | SAR: ${sarText} | VWAP: ${vwapText}
MFI: ${mfiText} | Supertrend: ${supertrendText} | CCI: ${cciText}

🔥 HARDCODED SCORE: ${window.deterministicScores.bull} Bullish | ${window.deterministicScores.neutral} Neutral | ${window.deterministicScores.bear} Bearish.
DO NOT recalculate this score. Use it as an absolute mathematical fact.
I’m about to open a position. Based on these data, give me direction and TP/SL.`;
  }

  async function autoFillChat() {
    const textarea = document.getElementById("user-input");
    if (!textarea) return;
    textarea.value = await buildAutoPrompt();
    setTimeout(async () => {
      textarea.value = await buildAutoPrompt();
    }, 1500);
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
          window.getSignal();
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
    chat.innerHTML += `<div id="${loadingId}" class="message" style="color:#94a3b8;"><strong>${escapeHtml(
      coinName
    )}:</strong> AI is analyzing 1H charts & liquidity pools... 🧠⚙️</div>`;
    chat.scrollTop = chat.scrollHeight;

    try {
      let promptText = await buildAutoPrompt();

      // Analiz anında çekilen yeni prompt'u textarea'ya yaz
      const textarea = document.getElementById("user-input");
      if (textarea) textarea.value = promptText;

      // Manuel liquidation inputs (parse toleranslı)
      const upperRaw = document.getElementById("upper-liq")
        ? document.getElementById("upper-liq").value.trim()
        : "";
      const lowerRaw = document.getElementById("lower-liq")
        ? document.getElementById("lower-liq").value.trim()
        : "";
      const upperLiq = parseLooseNumber(upperRaw);
      const lowerLiq = parseLooseNumber(lowerRaw);

      if (upperLiq !== "" || lowerLiq !== "") {
        promptText += `\n\n🚨 COMMANDER OVERRIDE INTELLIGENCE:\n`;
        promptText += `User 1H Liquidation Map data:\n`;
        if (upperLiq !== "") promptText += `- Upper Pool: ${upperLiq}\n`;
        if (lowerLiq !== "") promptText += `- Lower Pool: ${lowerLiq}\n`;
        promptText += `\nINSTRUCTION: If LONG, set 'tp' slightly below ${
          upperLiq || "the upper pool"
        }. If SHORT, set 'tp' slightly above ${
          lowerLiq || "the lower pool"
        }. Adjust 'sl' for RR >= 1.5.\n`;
      }

      const r = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: promptText,
          coin: coin,
          upper_liq: upperLiq,
          lower_liq: lowerLiq,
        }),
      });

      const j = await r.json();
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      if (j.error) {
        chat.innerHTML += `<div class="message"><strong>Error:</strong> <span style="color:#ff4444;">${escapeHtml(
          j.error
        )}</span></div>`;
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
        entry: escapeHtml(j.entry ?? "Pending"),
        partial_tp: escapeHtml(j.partial_tp ?? "-"),
        tp: escapeHtml(j.tp ?? "-"),
        sl: escapeHtml(j.sl ?? "-"),
        rr: escapeHtml(j.rr ?? "-"),
        risk: escapeHtml(j.risk ?? "-"),
        liquidity_target: escapeHtml(j.liquidity_target !== null ? j.liquidity_target : "N/A"),
        what_to_watch_for: escapeHtml(j.what_to_watch_for ?? ""),
        market_summary: escapeHtml(j.market_summary ?? "-"),
        why_html:
          Array.isArray(j.why) && j.why.length > 0
            ? j.why.map((x) => `• ${escapeHtml(x)}`).join("<br/>")
            : "No specific reasoning provided.",
        cancel_html:
          j.direction !== "HOLD" && Array.isArray(j.cancel_conditions) && j.cancel_conditions.length > 0
            ? j.cancel_conditions.map((x) => `• ${escapeHtml(x)}`).join("<br/>")
            : "",
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

          <div style="background: rgba(239, 68, 68, 0.1); border: 1px dashed #ef4444; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;">
            <b>🎯 Whale Target (TP):</b> <span style="color:#f87171; font-size: 1.1em; font-weight: bold;">${s.liquidity_target}</span>
          </div>

          ${j.direction !== "HOLD" ? `
          <div style="margin-bottom: 15px;">
            Risk: <b>${s.risk}</b> | RR (Risk/Reward): <b>${s.rr}</b><br/>
            Entry: <b style="color:#fff;">${s.entry}</b><br/>
            Safe Profit (Partial TP): <b style="color:#eab308;">${s.partial_tp}</b><br/>
            Take Profit (Final TP): <b style="color:#22c55e;">${s.tp}</b> | Stop Loss (SL): <b style="color:#ef4444;">${s.sl}</b>
          </div>
          ` : ""}

          <b style="color:#e2e8f0;">Market Summary & Session:</b><br/>
          <span style="color:#cbd5e1; font-style: italic;">"${s.market_summary}"</span><br/><br/>

          ${j.direction === "HOLD" && j.what_to_watch_for ? `
          <div style="background: rgba(234, 179, 8, 0.1); border-left: 3px solid #eab308; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
            <b style="color:#eab308;">Tactic (What to watch for):</b><br/>
            <span style="color:#cbd5e1;">${s.what_to_watch_for}</span>
          </div>
          ` : ""}

          <b style="color:#e2e8f0;">AI Reasoning:</b><br/>
          <span style="color:#cbd5e1;">
            ${s.why_html}
          </span><br/><br/>

          ${s.cancel_html ? `
          <b style="color:#e2e8f0;">Cancel/Stop Conditions:</b><br/>
          <span style="color:#cbd5e1;">${s.cancel_html}</span>
          ` : ""}
        </div>
      `;

      chat.scrollTop = chat.scrollHeight;
    } catch (e) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      chat.innerHTML += `<div class="message"><strong>System Error:</strong> <span style="color:#ff4444;">${escapeHtml(
        e.message
      )}</span></div>`;
    }
  };
})();
