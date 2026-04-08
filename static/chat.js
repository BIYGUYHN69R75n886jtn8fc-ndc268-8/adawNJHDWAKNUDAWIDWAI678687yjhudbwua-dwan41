// static/chat.js
(function () {
    const TWELVE_API_KEY = "d3123a9d9d344ce99c9e05fa75e32b78";
    const INTERVAL = "1h"; 
  
    function getCoinInfo() {
      const body = document.body;
      const coinAttr = body.getAttribute("data-coin");
      const coinNameAttr = body.getAttribute("data-coin-name");
      if (coinAttr && coinNameAttr) return { coin: coinAttr, coinName: coinNameAttr };
  
      const file = (window.location.pathname.split("/").pop() || "").toLowerCase();
      const map = {
        "bitcoin.html": { coin: "BTC", coinName: "Bitcoin" },
        "ethereum.html": { coin: "ETH", coinName: "Ethereum" },
        "ada.html": { coin: "ADA", coinName: "Cardano (ADA)" },
        "avax.html": { coin: "AVAX", coinName: "Avalanche (AVAX)" },
        "mana.html": { coin: "MANA", coinName: "Decentraland (MANA)" },
        "bnb.html": { coin: "BNB", coinName: "BNB" },
        "xrp.html": { coin: "XRP", coinName: "XRP" },
        "solana.html": { coin: "SOL", coinName: "Solana (SOL)" },
        "doge.html": { coin: "DOGE", coinName: "Dogecoin (DOGE)" },
        "trx.html": { coin: "TRX", coinName: "TRON (TRX)" },
        "index.html": { coin: "ETH", coinName: "Ethereum" },
      };
      return map[file] || { coin: "ETH", coinName: "Ethereum" };
    }
  
    function readIndicatorText(id) {
      const el = document.querySelector(`#${id} p`);
      if (!el) return "N/A";
      const parts = (el.textContent || "").split(":");
      return (parts[1] || "").trim() || "N/A";
    }
  
    async function fetchCurrentPrice(coin) {
      const url = `https://api.twelvedata.com/price?apikey=${TWELVE_API_KEY}&symbol=${coin}/USD`;
      try {
        const r = await fetch(url);
        const j = await r.json();
        return (j && j.price) ? j.price : "N/A";
      } catch { return "N/A"; }
    }

    // 🔥 MACRO TREND FILTER (1D EMA 200) 🔥
    async function fetchDailyMacroTrend(coin) {
      // 1 Günlük grafikte 200 periyotluk EMA'yı çekiyoruz
      const url = `https://api.twelvedata.com/ema?apikey=${TWELVE_API_KEY}&symbol=${coin}/USD&interval=1day&time_period=200`;
      try {
        const r = await fetch(url);
        const j = await r.json();
        if (j && j.values && j.values[0]) {
            return parseFloat(j.values[0].ema);
        }
        return null;
      } catch { return null; }
    }

    // 🔥 TIER-1 HEDGE FUND DETERMINISTIC ENGINE (WEIGHTED SCORING v2.0) 🔥
    function calculateHardMath(values, currentPriceStr) {
        let p = parseFloat(currentPriceStr);
        let bull = 0, bear = 0, neutral = 0;
        if (isNaN(p)) return { bull: 0, bear: 0, neutral: 15 };

        const parseVal = (str) => parseFloat((str || "").replace(/[^0-9.-]/g, ''));

        // 🔥 PROFESYONEL AĞIRLIKLANDIRMA ÇARPANLARI
        const W_VOLUME = 3;   // Akıllı Para & Hacim
        const W_TREND = 2;    // Ana Trend Yönü
        const W_MOMENTUM = 1; // Kısa Vadeli Osilatörler

        // --- AĞIR SIKLET (HACİM) ---
        // 1. VWAP
        let vwap = parseVal(values.VWAP);
        if (!isNaN(vwap)) { if (p > vwap) bull += W_VOLUME; else if (p < vwap) bear += W_VOLUME; else neutral++; }

        // 2. OBV
        let obv = parseVal(values.OBV);
        if (!isNaN(obv)) { if (obv > 0) bull += W_VOLUME; else if (obv < 0) bear += W_VOLUME; else neutral++; } else { neutral++; }

        // --- ORTA SIKLET (TREND) ---
        // 3. EMA
        let ema = parseVal(values.EMA);
        if (!isNaN(ema)) { if (p > ema) bull += W_TREND; else if (p < ema) bear += W_TREND; else neutral++; }

        // 4. SUPERTREND
        let st = parseVal(values.Supertrend);
        if (!isNaN(st)) { if (p > st) bull += W_TREND; else if (p < st) bear += W_TREND; else neutral++; }

        // 5. MACD
        let macd = parseVal(values.MACD);
        if (!isNaN(macd)) { if (macd > 0) bull += W_TREND; else if (macd < 0) bear += W_TREND; else neutral++; }

        // 6. ICHIMOKU
        if (values.ICHIMOKU && values.ICHIMOKU.includes('|')) {
            let parts = values.ICHIMOKU.split('|');
            let tenkan = parseVal(parts[0]), kijun = parseVal(parts[1]);
            if (p > tenkan && p > kijun) bull += W_TREND; else if (p < tenkan && p < kijun) bear += W_TREND; else neutral++;
        }

        // 7. SAR
        let sar = parseVal(values.SAR);
        if (!isNaN(sar)) { if (p > sar) bull += W_TREND; else if (p < sar) bear += W_TREND; else neutral++; }

        // 8. ADX (Sadece momentum onayı olarak kullanıyoruz)
        let adx = parseVal(values.ADX);
        if (!isNaN(adx)) {
            if (adx > 25) { 
                let currentEma = parseVal(values.EMA);
                if (p > currentEma) bull += W_TREND; else if (p < currentEma) bear += W_TREND; else neutral++; 
            } else { neutral++; }
        } else { neutral++; }


        // --- HAFİF SIKLET (OSİLATÖR VE BANTLAR) ---
        // 9. RSI
        let rsi = parseVal(values.RSI);
        if (!isNaN(rsi)) { if (rsi <= 30) bull += W_MOMENTUM; else if (rsi >= 70) bear += W_MOMENTUM; else neutral++; }

        // 10. MFI
        let mfi = parseVal(values.MFI);
        if (!isNaN(mfi)) { if (mfi <= 20) bull += W_MOMENTUM; else if (mfi >= 80) bear += W_MOMENTUM; else neutral++; }

        // 11. CCI
        let cci = parseVal(values.CCI);
        if (!isNaN(cci)) { if (cci <= -100) bull += W_MOMENTUM; else if (cci >= 100) bear += W_MOMENTUM; else neutral++; }

        // 12. STOCH
        if (values.STOCH && values.STOCH.includes('/')) {
            let parts = values.STOCH.split('/');
            let k = parseVal(parts[0]), d = parseVal(parts[1]);
            if (k <= 20 && d <= 20) bull += W_MOMENTUM; else if (k >= 80 && d >= 80) bear += W_MOMENTUM; else neutral++;
        }

        // 13. BBANDS
        if (values.BBANDS && values.BBANDS.includes('/')) {
            let parts = values.BBANDS.split('/');
            let upper = parseVal(parts[0]), lower = parseVal(parts[1]);
            if (p <= lower) bull += W_MOMENTUM; else if (p >= upper) bear += W_MOMENTUM; else neutral++;
        }

        // 14. KELTNER
        if (values.KELTNER && values.KELTNER.includes('|')) {
            let parts = values.KELTNER.split('|');
            let upper = parseVal(parts[0]), lower = parseVal(parts[1]);
            if (p <= lower) bull += W_MOMENTUM; else if (p >= upper) bear += W_MOMENTUM; else neutral++;
        }

        // 15. ATR (Sadece volatilite ölçer, yön belirtmez)
        neutral++;

        return { bull, bear, neutral };
    }
  
    async function buildAutoPrompt() {
      const { coin, coinName } = getCoinInfo();
      const values = {
        RSI: readIndicatorText("rsi"), EMA: readIndicatorText("ema"), MACD: readIndicatorText("macd"),
        BBANDS: readIndicatorText("bbands"), ATR: readIndicatorText("atr"), STOCH: readIndicatorText("stoch"),
        ADX: readIndicatorText("adx"), ICHIMOKU: readIndicatorText("ichimoku"), OBV: readIndicatorText("obv"),
        KELTNER: readIndicatorText("keltner"), SAR: readIndicatorText("sar"), VWAP: readIndicatorText("vwap"),
        MFI: readIndicatorText("mfi"), Supertrend: readIndicatorText("supertrend"), CCI: readIndicatorText("cci"),
      };
      const price = await fetchCurrentPrice(coin);

      window.deterministicScores = calculateHardMath(values, price);
  
      return (
  `I am now providing you with ${coinName} 1H data:
  Current price: ${price}
  
  RSI: ${values.RSI}
  EMA: ${values.EMA}
  MACD: ${values.MACD}
  BBANDS: ${values.BBANDS}
  ATR: ${values.ATR}
  STOCH: ${values.STOCH}
  ADX: ${values.ADX}
  ICHIMOKU: ${values.ICHIMOKU}
  OBV: ${values.OBV}
  KELTNER: ${values.KELTNER}
  SAR: ${values.SAR}
  VWAP: ${values.VWAP}
  MFI: ${values.MFI}
  Supertrend: ${values.Supertrend}
  CCI: ${values.CCI}
  
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
          widget.classList.toggle("expanded"); widget.classList.toggle("collapsed");
          this.innerHTML = widget.classList.contains("expanded") ? "&#x2923;" : "&#x2922;";
        });
      }
      const input = document.getElementById("user-input");
      if (input) {
        input.addEventListener("keydown", function (e) {
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (typeof window.getSignal === "function") window.getSignal(); }
        });
      }
    }
  
    document.addEventListener("DOMContentLoaded", () => { hookChatUI(); autoFillChat(); });
  
  // 🔥 PROFESSIONAL SIGNAL ENGINE DISPLAY
  window.getSignal = async function () {
    const { coinName } = getCoinInfo();
    const chat = document.getElementById("chat-messages");
    if (!chat) return;
  
    const loadingId = "loading-" + Date.now();
    chat.innerHTML += `<div id="${loadingId}" class="message" style="color:#94a3b8;"><strong>${coinName}:</strong> AI is analyzing 1H charts & liquidity pools... 🧠⚙️</div>`;
    chat.scrollTop = chat.scrollHeight;
  
    try {
      let promptText = await buildAutoPrompt();
      
      // 🔥 HAYALET BUG ÇÖZÜMÜ: Analiz anında çekilen YENİ fiyatı ekrana yansıt ki kullanıcı görsün.
      const textarea = document.getElementById("user-input");
      if (textarea) textarea.value = promptText;
      
      const upperLiq = document.getElementById('upper-liq') ? document.getElementById('upper-liq').value.trim() : "";
      const lowerLiq = document.getElementById('lower-liq') ? document.getElementById('lower-liq').value.trim() : "";
      
     if (upperLiq !== "" || lowerLiq !== "") {
          promptText += `\n\n💧 SMART MONEY LIQUIDITY DATA:\n`;
          promptText += `User High-Timeframe Liquidation Pools:\n`;
          if (upperLiq !== "") promptText += `- Upper Pool: ${upperLiq}\n`;
          if (lowerLiq !== "") promptText += `- Lower Pool: ${lowerLiq}\n`;
          promptText += `\nCRITICAL SURVIVAL RULES FOR TP/SL:\n`;
          promptText += `1. FRONT-RUN TARGETS: Market makers sweep these pools. To ensure fills, place the TP *slightly before* the target pool (e.g., if LONG, TP just below Upper Pool; if SHORT, TP just above Lower Pool).\n`;
          promptText += `2. STOP HUNT KEVLAR (SL BUFFER): Retail places stops exactly ON the pools and gets liquidated by wicks. You MUST place the SL significantly *BEYOND* the opposing liquidity pool. Use the current ATR value in the data above as a mathematical buffer distance to survive sudden sweeps.\n`;
          promptText += `3. DO NOT let these pools dictate the LONG/SHORT direction. Follow the Hardcoded Bull/Bear Score for direction.\n`;
      }
  
      const r = await fetch("/chat", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ input: promptText })
      });
  
      const j = await r.json();
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
  
      if (j.error) {
        chat.innerHTML += `<div class="message"><strong>Error:</strong> <span style="color:#ff4444;">${j.error}</span></div>`;
        return;
      }
  
      let directionColor = "#eab308"; 
      if (j.direction === "LONG") directionColor = "#22c55e"; 
      if (j.direction === "SHORT") directionColor = "#ef4444"; 
  
      let bullCount = window.deterministicScores ? window.deterministicScores.bull : 0;
      let bearCount = window.deterministicScores ? window.deterministicScores.bear : 0;
      let neutralCount = window.deterministicScores ? window.deterministicScores.neutral : 15;
  
      chat.innerHTML += `
        <div class="message" style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid ${directionColor}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong style="font-size: 1.2em; color: #fff;">${coinName} 1H Signal</strong> 
            <div style="background: #0f172a; padding: 4px 10px; border-radius: 6px; border: 1px solid ${directionColor};">
                <b style="color: ${directionColor}; font-size: 1.2em;">${j.direction}</b> 
                <span style="color:#94a3b8; font-size: 0.9em;">(${j.confidence || 0}%)</span>
            </div>
          </div>
          
          <div style="background: #0f172a; padding: 10px; border-radius: 6px; font-size: 0.9em; margin-bottom: 10px; border: 1px solid #334155;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                  <div><b>📊 Market:</b> <span style="color:#38bdf8;">${j.market_regime ?? "Unknown"}</span></div>
                  <div><b>🎯 Score:</b> <span style="color:#a78bfa;">${j.confluence_score ?? "-"}</span></div>
                  <div><b>📈 Resistance:</b> <span style="color:#f472b6;">${j.resistance_level ?? "N/A"}</span></div>
                  <div><b>📉 Support:</b> <span style="color:#34d399;">${j.support_level ?? "N/A"}</span></div>
              </div>
              
              <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed #334155; text-align: center;">
                 <span style="color: #22c55e;">🟢 ${bullCount} Bull</span> &nbsp;|&nbsp; 
                 <span style="color: #94a3b8;">⚪ ${neutralCount} Neutral</span> &nbsp;|&nbsp; 
                 <span style="color: #ef4444;">🔴 ${bearCount} Bear</span>
              </div>
          </div>
  
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px dashed #ef4444; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;">
              <b>🎯 Whale Target (TP):</b> <span style="color:#f87171; font-size: 1.1em; font-weight: bold;">${j.liquidity_target !== null ? j.liquidity_target : "N/A"}</span>
          </div>
  
          ${j.direction !== "HOLD" ? `
          <div style="margin-bottom: 15px;">
              Risk: <b>${j.risk ?? "-"}</b> | RR (Risk/Reward): <b>${j.rr ?? "-"}</b><br/>
              Entry: <b style="color:#fff;">${j.entry ?? "Pending"}</b><br/>
              Safe Profit (Partial TP): <b style="color:#eab308;">${j.partial_tp ?? "-"}</b><br/>
              Take Profit (Final TP): <b style="color:#22c55e;">${j.tp ?? "-"}</b> | Stop Loss (SL): <b style="color:#ef4444;">${j.sl ?? "-"}</b>
          </div>
          ` : ''}
          
          <b style="color:#e2e8f0;">Market Summary & Session:</b><br/>
          <span style="color:#cbd5e1; font-style: italic;">"${j.market_summary ?? "-"}"</span><br/><br/>
  
          ${j.direction === "HOLD" && j.what_to_watch_for ? `
          <div style="background: rgba(234, 179, 8, 0.1); border-left: 3px solid #eab308; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
              <b style="color:#eab308;">Tactic (What to watch for):</b><br/>
              <span style="color:#cbd5e1;">${j.what_to_watch_for}</span>
          </div>
          ` : ''}
          
          <b style="color:#e2e8f0;">AI Reasoning:</b><br/>
          <span style="color:#cbd5e1;">
          ${Array.isArray(j.why) && j.why.length > 0 ? j.why.map(x => `• ${x}`).join("<br/>") : "No specific reasoning provided."}
          </span><br/><br/>
          
          ${j.direction !== "HOLD" && Array.isArray(j.cancel_conditions) && j.cancel_conditions.length > 0 ? `
          <b style="color:#e2e8f0;">Cancel/Stop Conditions:</b><br/>
          <span style="color:#cbd5e1;">${j.cancel_conditions.map(x => `• ${x}`).join("<br/>")}</span>
          ` : ''}
        </div>
      `;
      chat.scrollTop = chat.scrollHeight;
    } catch (e) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      chat.innerHTML += `<div class="message"><strong>System Error:</strong> <span style="color:#ff4444;">${e.message}</span></div>`;
    }
  };
    
  })();

// 🔥 DİNAMİK SEANS MOTORU 🔥
function updateSessionClock() {
    const timerEl = document.getElementById('session-timer');
    const timeEl = document.getElementById('session-time');
    const textEl = document.getElementById('session-text');
    
    if(!timerEl || !timeEl || !textEl) return;

    // Bilgisayarın yerel saatini al
    const now = new Date();
    const hours = now.getHours();
    const mins = now.getMinutes().toString().padStart(2, '0');
    
    // Ekrana saati yaz (Örn: 11:05)
    timeEl.textContent = `${hours.toString().padStart(2, '0')}:${mins}`;

    // Kaptanın Kuralları: Saat 11 (Londra) veya 18 (New York) ise YEŞİL yap
    if (hours === 11) {
        timerEl.className = 'session-active';
        textEl.textContent = 'London Session Open';
    } else if (hours === 18) {
        timerEl.className = 'session-active';
        textEl.textContent = 'New York Session Open';
    } else {
        // Diğer tüm saatlerde KIRMIZI yap
        timerEl.className = 'session-inactive';
        textEl.textContent = 'Do Not Enter';
    }
}

// Her 1 saniyede bir saati güncelle
setInterval(updateSessionClock, 1000);
// Sayfa yüklenir yüklenmez ilk çağrıyı yap
document.addEventListener("DOMContentLoaded", updateSessionClock);



