// static/chat.js
(function () {
    const TWELVE_API_KEY = "d3123a9d9d344ce99c9e05fa75e32b78";
    const INTERVAL = "15min";
  
    function getCoinInfo() {
      const body = document.body;
      const coinAttr = body.getAttribute("data-coin");
      const coinNameAttr = body.getAttribute("data-coin-name");
      if (coinAttr && coinNameAttr) {
        return { coin: coinAttr, coinName: coinNameAttr };
      }
  
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
      const text = el.textContent || "";
      const parts = text.split(":");
      return (parts[1] || "").trim() || "N/A";
    }
  
    async function fetchCurrentPrice(coin) {
      const url = `https://api.twelvedata.com/price?apikey=${TWELVE_API_KEY}&symbol=${coin}/USD`;
      try {
        const r = await fetch(url);
        const j = await r.json();
        if (j && j.price) return j.price;
        return "N/A";
      } catch {
        return "N/A";
      }
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
  
      return (
  `I am now providing you with ${coinName} data:
  
  ${coinName} Current price: ${price}
  
  RSI: ${values.RSI}
  EMA: ${values.EMA}
  MACD: ${values.MACD}
  BBANDS: ${values.BBANDS}
  ATR: ${values.ATR}
  STOCH Slow: ${values.STOCH}
  ADX: ${values.ADX}
  ICHIMOKU: ${values.ICHIMOKU}
  OBV: ${values.OBV}
  KELTNER: ${values.KELTNER}
  SAR: ${values.SAR}
  VWAP: ${values.VWAP}
  MFI: ${values.MFI}
  Supertrend: ${values.Supertrend}
  CCI: ${values.CCI}
  
  I’m about to open a position. Based on these data, give me direction and TP/SL.`
      );
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
            if (typeof window.getSignal === "function") window.getSignal();
          }
        });
      }
    }
  
    document.addEventListener("DOMContentLoaded", () => {
      hookChatUI();
      autoFillChat();
    });
  
 // 🔥 PROFESSIONAL SIGNAL ENGINE DISPLAY (SMART MONEY EDITION)
  window.getSignal = async function () {
    const { coinName } = getCoinInfo();
    const chat = document.getElementById("chat-messages");
    if (!chat) return;
  
    const loadingId = "loading-" + Date.now();
    chat.innerHTML += `<div id="${loadingId}" class="message" style="color:#94a3b8;"><strong>${coinName}:</strong> AI is analyzing 15m charts & liquidity pools... 🧠⚙️</div>`;
    chat.scrollTop = chat.scrollHeight;
  
    try {
      // 1. OTOMATİK İNDİKATÖR VERİLERİNİ ÇEKİYORUZ (Asla bozulmaz!)
      let promptText = await buildAutoPrompt();
      
      // 2. KUTULARDAKİ COINGLASS VERİLERİNİ YAKALIYORUZ
      const upperLiq = document.getElementById('upper-liq') ? document.getElementById('upper-liq').value.trim() : "";
      const lowerLiq = document.getElementById('lower-liq') ? document.getElementById('lower-liq').value.trim() : "";
      
      // 3. EĞER KUTULARA SAYI GİRİLDİYSE, EMRİ İNDİKATÖRLERİN ALTINA "EKLE" (+=)
      if (upperLiq !== "" || lowerLiq !== "") {
          promptText += `\n\n🚨 COMMANDER OVERRIDE INTELLIGENCE (CRITICAL):\n`;
          promptText += `The user has provided exact 12H Liquidation Map data from Coinglass:\n`;
          if (upperLiq !== "") promptText += `- Massive Upper Liquidity Pool: ${upperLiq}\n`;
          if (lowerLiq !== "") promptText += `- Massive Lower Liquidity Pool: ${lowerLiq}\n`;
          promptText += `\nINSTRUCTION: If your indicator analysis shows LONG, you MUST set 'liquidity_target' to ${upperLiq || "the upper pool"} and place TP slightly below it to front-run. If indicators show SHORT, target ${lowerLiq || "the lower pool"} and place TP slightly above it. Override your 15m default targets! Adjust SL to maintain a proper RR.\n`;
      }

      // 4. (Opsiyonel) Eski beyaz sohbet kutusuna not yazıldıysa onu da ekle
      const inputBox = document.querySelector('.chat-input textarea') || document.querySelector('.chat-input input[type="text"]');
      if (inputBox && inputBox.value.trim() !== "") {
          promptText += "\n\nAdditional User Note: " + inputBox.value.trim();
          // Gönderdikten sonra kutuyu temizle
          inputBox.value = "";
      }
  
      // 5. TÜM PAKETİ YAPAY ZEKAYA GÖNDER
      const r = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: promptText }),
      });
  
      const j = await r.json();
      
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
  
      if (j.error) {
        chat.innerHTML += `<div class="message"><strong>Error:</strong> <span style="color:#ff4444;">${j.error}</span></div>`;
        chat.scrollTop = chat.scrollHeight;
        return;
      }
  
      let directionColor = "#eab308"; 
      if (j.direction === "LONG") directionColor = "#22c55e"; 
      if (j.direction === "SHORT") directionColor = "#ef4444"; 

      let bullCount = 0, bearCount = 0, neutralCount = 0;
      if (j.indicator_votes) {
          Object.values(j.indicator_votes).forEach(vote => {
              if (vote === 'bullish') bullCount++;
              else if (vote === 'bearish') bearCount++;
              else neutralCount++;
          });
      }
  
      // 6. EKRANA YAZDIRMA KISMI (TASARIM)
      chat.innerHTML += `
        <div class="message" style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid ${directionColor}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
          
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong style="font-size: 1.2em; color: #fff;">${coinName} 15m Signal</strong>
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
              Take Profit (TP): <b style="color:#22c55e;">${j.tp ?? "-"}</b> | Stop Loss (SL): <b style="color:#ef4444;">${j.sl ?? "-"}</b>
          </div>
          ` : ''}
          
          <b style="color:#e2e8f0;">Market Summary & Session:</b><br/>
          <span style="color:#cbd5e1; font-style: italic;">"${j.market_summary ?? "-"}"</span>
          <br/><br/>

          ${j.direction === "HOLD" && j.what_to_watch_for ? `
          <div style="background: rgba(234, 179, 8, 0.1); border-left: 3px solid #eab308; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
              <b style="color:#eab308;">Tactic (What to watch for):</b><br/>
              <span style="color:#cbd5e1;">${j.what_to_watch_for}</span>
          </div>
          ` : ''}
          
          <b style="color:#e2e8f0;">AI Reasoning:</b><br/>
          <span style="color:#cbd5e1;">
          ${Array.isArray(j.why) && j.why.length > 0 ? j.why.map(x => `• ${x}`).join("<br/>") : "No specific reasoning provided."}
          </span>
          <br/><br/>
          
          ${j.direction !== "HOLD" && Array.isArray(j.cancel_conditions) && j.cancel_conditions.length > 0 ? `
          <b style="color:#e2e8f0;">Cancel/Stop Conditions:</b><br/>
          <span style="color:#cbd5e1;">
          ${j.cancel_conditions.map(x => `• ${x}`).join("<br/>")}
          </span>
          ` : ''}
        </div>
      `;
  
      chat.scrollTop = chat.scrollHeight;
  
    } catch (e) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      chat.innerHTML += `<div class="message"><strong>System Error:</strong> <span style="color:#ff4444;">${e.message}</span></div>`;
      chat.scrollTop = chat.scrollHeight;
    }
  };
  

  })();


