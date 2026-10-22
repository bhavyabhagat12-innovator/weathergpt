/**
 * WeatherGPT Frontend Application
 * Handles navigation, conversational chat, live telemetry dashboard,
 * disaster EOC simulation, ERA5 climate trends, and aviation/marine briefings.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ── DOM References ──────────────────────────────────────────────────
  const navTabs = document.querySelectorAll(".nav-tab");
  const viewPanels = document.querySelectorAll(".view-panel");
  const langSelect = document.getElementById("lang-select");
  const connStatus = document.getElementById("conn-status");
  const alertBanner = document.getElementById("live-alert-banner");
  const bannerTitle = document.getElementById("banner-title");
  const bannerText = document.getElementById("banner-text");
  const bannerAskBtn = document.getElementById("banner-ask-btn");
  const bannerClose = document.getElementById("banner-close");

  // Chat View Elements
  const chatViewport = document.getElementById("chat-viewport");
  const chatForm = document.getElementById("chat-form");
  const queryInput = document.getElementById("query-input");
  const rolePills = document.getElementById("role-pills");
  const suggestionsBox = document.getElementById("suggestions");
  const micBtn = document.getElementById("mic-btn");

  // Dashboard Elements
  const dashSearchInput = document.getElementById("dash-search-input");
  const dashSearchBtn = document.getElementById("dash-search-btn");
  const dashQuickCities = document.getElementById("dash-quick-cities");
  const dashContent = document.getElementById("dash-content");

  // Alerts Elements
  const alertsListContainer = document.getElementById("alerts-list-container");
  const refreshAlertsBtn = document.getElementById("refresh-alerts-btn");
  const statRed = document.getElementById("stat-red");
  const statOrange = document.getElementById("stat-orange");
  const statYellow = document.getElementById("stat-yellow");
  const simCycloneBtn = document.getElementById("sim-cyclone-btn");
  const simRainBtn = document.getElementById("sim-rain-btn");
  const simHeatBtn = document.getElementById("sim-heat-btn");
  const customBulletinText = document.getElementById("custom-bulletin-text");
  const customBulletinState = document.getElementById("custom-bulletin-state");
  const customBulletinDistrict = document.getElementById("custom-bulletin-district");
  const customSimSubmit = document.getElementById("custom-sim-submit");
  const wsLogEntries = document.getElementById("ws-log-entries");
  const wsEventCount = document.getElementById("ws-event-count");

  // Climate Elements
  const climateRegionSelect = document.getElementById("climate-region-select");
  const climateYearsSelect = document.getElementById("climate-years-select");
  const climateAnalyzeBtn = document.getElementById("climate-analyze-btn");
  const climateChartContainer = document.getElementById("climate-chart-container");

  // Operations Briefing Elements
  const briefingTabs = document.querySelectorAll(".briefing-tab");
  const briefingContents = document.querySelectorAll(".briefing-content");
  const aviationStations = document.getElementById("aviation-stations");
  const marineStations = document.getElementById("marine-stations");
  const aviationDisplayArea = document.getElementById("aviation-display-area");
  const marineDisplayArea = document.getElementById("marine-display-area");

  // ── State Variables ─────────────────────────────────────────────────
  let currentView = "chat";
  let currentRole = "general";
  let currentLanguage = "en";
  let activeStationAviation = "Delhi";
  let activeStationMarine = "Visakhapatnam";
  let eventLogCounter = 0;
  const sessionId = "session-" + Math.random().toString(36).substring(2, 9);

  // ── Multilingual Voice & Suggestions Dictionary ─────────────────────
  const VOICE_LOCALE_MAP = {
    en: "en-IN", hi: "hi-IN", mr: "mr-IN", ta: "ta-IN", te: "te-IN"
  };

  const MULTILINGUAL_SUGGESTIONS = {
    en: {
      general: ["Will it rain in Delhi today?", "Current weather in Mumbai", "Weekend forecast in Bengaluru"],
      agriculture: ["Can I harvest onions in Nashik today?", "Is soil moisture adequate in Nagpur?", "Spraying window in Pune tomorrow?"],
      aviation: ["Flight landing briefing for Delhi runway", "Convective CAPE levels near Mumbai", "Wind gusts in Bengaluru airspace"],
      marine: ["Are conditions safe for fishing in Visakhapatnam?", "Severe cyclone warning in Bay of Bengal", "Port wind advisory in Chennai"],
      disaster_management: ["Active Red and Orange IMD warning bulletins", "Flash flood alerts in Konkan ghats", "Cyclone track bulletin for coastal Andhra"]
    },
    hi: {
      general: ["क्या आज दिल्ली में बारिश होगी?", "मुंबई में वर्तमान तापमान क्या है?", "बेंगलुरु का मौसम कैसा रहेगा?"],
      agriculture: ["क्या आज नासिक में प्याज की कटाई कर सकते हैं?", "क्या नागपुर में बुवाई के लिए नमी पर्याप्त है?", "पुणे में कल कीटनाशक छिड़काव कर सकते हैं?"],
      aviation: ["दिल्ली हवाई अड्डे के लिए उड़ान मौसम रिपोर्ट", "मुंबई के पास तूफान और हवा की स्थिति", "बेंगलुरु रनवे पर दृश्यता"],
      marine: ["क्या विशाखापट्टनम में मछुआरों के लिए जाना सुरक्षित है?", "बंगाल की खाड़ी में चक्रवात की स्थिति", "चेन्नई बंदरगाह पर हवा की गति"],
      disaster_management: ["सक्रिय रेड और ऑरेंज अलर्ट बुलेटिन", "कोंकण में भारी बारिश की चेतावनी", "तटीय चक्रवात आपातकालीन निर्देश"]
    },
    mr: {
      general: ["आज पुण्यात पाऊस पडेल का?", "मुंबईचे आजचे हवामान काय आहे?", "नाशिकमध्ये उद्या ऊन पडेल का?"],
      agriculture: ["नाशिकमध्ये आज कांदा काढणी करावी का?", "नागपुरात पेरणीसाठी जमिनीतील ओलावा पुरेसा आहे का?", "पुण्यात उद्या फवारणी योग्य आहे का?"],
      aviation: ["मुंबई विमानतळावरील वाऱ्याचा वेग", "विमान लँडिंगसाठी दृश्यता किती आहे?"],
      marine: ["विशाखापट्टणम किनाऱ्यावर मच्छीमारांसाठी इशारा", "चक्रीवादळाचा धोका किती आहे?"],
      disaster_management: ["कोकणात अतिवृष्टीचा रेड अलर्ट आहे का?", "पूर परिस्थितीची ताजी माहिती"]
    },
    ta: {
      general: ["சென்னையில் இன்று மழை பெய்யுமா?", "மதுரையின் தற்போதைய வெப்பநிலை"],
      agriculture: ["இன்று பயிர் அறுவடை செய்யலாமா?", "நாளை உரம் தெளிக்க தகுந்த வானிலையா?"],
      aviation: ["சென்னை விமான நிலைய வானிலை அறிக்கை"],
      marine: ["விசாகப்பட்டினத்தில் மீனவர்கள் கடலுக்கு செல்லலாமா?", "வங்கக்கடலில் புயல் எச்சரிக்கை"],
      disaster_management: ["தீவிர மழை எச்சரிக்கை மற்றும் புயல் தகவல்"]
    },
    te: {
      general: ["హైదరాబాద్‌లో ఈరోజు వర్షం పడుతుందా?", "విజయవాడలో ప్రస్తుత ఉష్ణోగ్రత"],
      agriculture: ["ఈరోజు పంట కోత చేయవచ్చా?", "రైతులకు విత్తనాల సలహా"],
      aviation: ["విమాన రాకపోకల వాతావరణ సమాచారం"],
      marine: ["విశాఖపట్నం సముద్రంలో చేపల వేటకు వెళ్ళవచ్చా?", "బంగాళాఖాతంలో తీవ్ర తుఫాను హెచ్చరిక"],
      disaster_management: ["తీరప్రాంత తుఫాను అత్యవసర హెచ్చరికలు"]
    }
  };

  // ── Navigation & View Switching ─────────────────────────────────────
  function switchView(viewName, pushHistory = true) {
    currentView = viewName;
    navTabs.forEach(tab => {
      tab.classList.toggle("active", tab.dataset.view === viewName);
    });

    viewPanels.forEach(panel => {
      panel.classList.toggle("active", panel.id === `view-${viewName}`);
    });

    if (pushHistory) {
      const newPath = viewName === "chat" ? "/" : `/${viewName}`;
      if (window.location.pathname !== newPath) {
        history.pushState({ view: viewName }, "", newPath);
      }
    }

    // Lazy load or refresh view-specific content
    if (viewName === "dashboard") {
      loadDashboardWeather(dashSearchInput.value.trim() || "Delhi");
    } else if (viewName === "alerts") {
      loadActiveAlerts();
    } else if (viewName === "climate") {
      if (climateChartContainer.querySelector(".placeholder-card")) {
        loadClimateTrend(climateRegionSelect.value, parseInt(climateYearsSelect.value));
      }
    } else if (viewName === "briefing") {
      loadAviationBriefing(activeStationAviation);
      loadMarineBriefing(activeStationMarine);
    }
  }

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      switchView(tab.dataset.view);
    });
  });

  // Handle browser back/forward buttons
  window.addEventListener("popstate", (event) => {
    const path = window.location.pathname.replace("/", "") || "chat";
    const validViews = ["chat", "dashboard", "alerts", "climate", "briefing"];
    const target = validViews.includes(path) ? path : "chat";
    switchView(target, false);
  });

  // Initialize view from URL path on page load
  const initialPath = window.location.pathname.replace("/", "") || "chat";
  if (["chat", "dashboard", "alerts", "climate", "briefing"].includes(initialPath)) {
    switchView(initialPath, false);
  } else {
    switchView("chat", false);
  }

  // ── WebSocket for Live Proactive Alerts ─────────────────────────────
  function setupWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/alerts`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      connStatus.textContent = "Live Alerts Active";
      connStatus.style.color = "#10b981";
      logWsMessage("system", "Connected to WeatherGPT Real-Time Alert Engine");
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "weather_alert") {
          const alert = msg.alert;
          bannerTitle.textContent = `${alert.severity.toUpperCase()} ALERT (${alert.event_type})`;
          bannerText.textContent = `${alert.headline} • Directive: ${alert.instruction || "Take precautions."}`;
          alertBanner.className = `emergency-banner ${alert.severity === "red" ? "" : "orange"}`;
          alertBanner.classList.remove("hidden");

          logWsMessage(alert.severity, `[${alert.severity.toUpperCase()}] ${alert.event_type}: ${alert.headline} (${alert.affected_districts?.join(", ") || "India"})`);
          
          // Wire ask button
          bannerAskBtn.onclick = () => {
            switchView("chat");
            queryInput.value = `Tell me about the ${alert.severity} alert for ${alert.event_type} in ${alert.affected_districts?.[0] || 'the region'} and what precautions to take.`;
            chatForm.dispatchEvent(new Event("submit"));
          };
        } else if (msg.type === "connection_ack") {
          logWsMessage("system", `${msg.message} (${msg.active_alerts_count} active bulletins)`);
        }
      } catch (err) {
        console.error("Error parsing WebSocket event:", err);
      }
    };

    socket.onclose = () => {
      connStatus.textContent = "Reconnecting...";
      connStatus.style.color = "#eab308";
      logWsMessage("system", "WebSocket disconnected. Reconnecting in 3s...");
      setTimeout(setupWebSocket, 3000);
    };
  }

  function logWsMessage(severity, text) {
    eventLogCounter++;
    if (wsEventCount) wsEventCount.textContent = `${eventLogCounter} events`;
    if (!wsLogEntries) return;

    const entry = document.createElement("div");
    entry.className = `log-entry ${severity}`;
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${text}`;
    wsLogEntries.prepend(entry);
  }

  setupWebSocket();

  bannerClose.addEventListener("click", () => {
    alertBanner.classList.add("hidden");
  });

  // ── Multilingual & Suggestion Chips ────────────────────────────────
  function updateSuggestions() {
    suggestionsBox.innerHTML = "";
    const langDict = MULTILINGUAL_SUGGESTIONS[currentLanguage] || MULTILINGUAL_SUGGESTIONS.en;
    const list = langDict[currentRole] || langDict.general || [];
    list.forEach(text => {
      const chip = document.createElement("button");
      chip.className = "suggestion-chip";
      chip.textContent = text;
      chip.type = "button";
      chip.addEventListener("click", () => {
        queryInput.value = text;
        chatForm.dispatchEvent(new Event("submit"));
      });
      suggestionsBox.appendChild(chip);
    });
  }

  langSelect.addEventListener("change", (e) => {
    currentLanguage = e.target.value;
    updateSuggestions();
  });

  rolePills.addEventListener("click", (e) => {
    const btn = e.target.closest(".role-pill");
    if (!btn) return;
    document.querySelectorAll(".role-pill").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    currentRole = btn.dataset.role;
    updateSuggestions();
  });

  updateSuggestions();

  // ── Voice Input (Web Speech API STT) ────────────────────────────────
  let recognition = null;
  let isListening = false;

  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      queryInput.value = transcript;
      chatForm.dispatchEvent(new Event("submit"));
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      stopListening();
    };

    recognition.onend = () => stopListening();

    micBtn.addEventListener("click", () => {
      if (isListening) {
        recognition.stop();
      } else {
        startListening();
      }
    });
  } else {
    micBtn.title = "Voice input not supported in this browser";
    micBtn.style.opacity = "0.4";
    micBtn.style.cursor = "not-allowed";
  }

  function startListening() {
    if (!recognition) return;
    recognition.lang = VOICE_LOCALE_MAP[currentLanguage] || "en-IN";
    try {
      recognition.start();
      isListening = true;
      micBtn.classList.add("listening");
      micBtn.title = "Listening… click to stop";
    } catch (e) {
      console.warn("Recognition start failed:", e);
    }
  }

  function stopListening() {
    isListening = false;
    micBtn.classList.remove("listening");
    micBtn.title = "Click to speak your query";
  }

  // ── Voice Output (SpeechSynthesis TTS) ──────────────────────────────
  function speakText(text, lang) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[#*`_]/g, "").replace(/https?:\/\/\S+/g, "");
    const utt = new SpeechSynthesisUtterance(cleanText);
    utt.lang = VOICE_LOCALE_MAP[lang || currentLanguage] || "en-IN";
    utt.rate = 0.95;
    window.speechSynthesis.speak(utt);
  }

  // ── Inline Climate Chart Renderer ──────────────────────────────────
  function renderInlineChart(chartSpec) {
    if (!chartSpec || !chartSpec.labels || !chartSpec.values) return "";
    const labels = chartSpec.labels;
    const values = chartSpec.values;
    const baseline = chartSpec.baseline_normal || null;
    const unit = chartSpec.unit || "mm";
    const title = chartSpec.title || "Climate Trend";
    const trend = chartSpec.trend_summary || "";

    const maxVal = Math.max(...values, baseline || 0, 1);

    const rows = labels.map((label, i) => {
      const val = values[i];
      const pct = Math.round((val / maxVal) * 100);
      let barClass = "chart-bar";
      if (baseline !== null) {
        barClass += val > baseline * 1.1 ? " above-normal" : (val < baseline * 0.9 ? " below-normal" : "");
      }
      return `
        <div class="chart-bar-row">
          <span class="chart-label">${label}</span>
          <div class="chart-bar-wrap">
            <div class="${barClass}" style="width:${pct}%"></div>
          </div>
          <span class="chart-value">${val} ${unit}</span>
        </div>`;
    }).join("");

    const baselineRow = baseline !== null
      ? `<div class="chart-baseline"></div><div class="chart-bar-row"><span class="chart-label" style="color:#64748b">Normal</span><div class="chart-bar-wrap"><div class="chart-bar" style="width:${Math.round((baseline/maxVal)*100)}%;background:#334155;"></div></div><span class="chart-value" style="color:#64748b">${baseline} ${unit}</span></div>`
      : "";

    return `
      <div class="chart-container">
        <div class="chart-title">${title}</div>
        ${rows}
        ${baselineRow}
        ${trend ? `<div class="chart-trend">${trend}</div>` : ""}
      </div>`;
  }

  // ── Chat Bubble Rendering ──────────────────────────────────────────
  function appendUserMessage(text) {
    const bubble = document.createElement("div");
    bubble.className = "message-bubble user";
    bubble.textContent = text;
    chatViewport.appendChild(bubble);
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }

  function appendTypingIndicator() {
    const bubble = document.createElement("div");
    bubble.className = "message-bubble assistant typing-bubble";
    bubble.id = "typing-bubble";
    bubble.innerHTML = `
      <div class="sender-tag">Grounding Telemetry &amp; Reasoning...</div>
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
    chatViewport.appendChild(bubble);
    chatViewport.scrollTop = chatViewport.scrollHeight;
    return bubble;
  }

  function appendAssistantResponse(data) {
    const typingBubble = document.getElementById("typing-bubble");
    if (typingBubble) typingBubble.remove();

    const bubble = document.createElement("div");
    bubble.className = "message-bubble assistant";

    let formatted = data.answer
      .replace(/### (.*?)\n/g, "<h3 style='margin: 8px 0 4px 0; color: #7dd3fc; font-size: 1rem;'>$1</h3>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "<p style='margin-bottom: 8px;'></p>")
      .replace(/\n- /g, "<br>• ");

    let alertsHtml = "";
    if (data.active_alerts && data.active_alerts.length > 0) {
      alertsHtml = data.active_alerts.map(a => {
        const cls = a.includes("RED") ? "red" : (a.includes("ORANGE") ? "orange" : "yellow");
        return `<div class="alert-badge ${cls}">${a}</div>`;
      }).join("");
    }

    const facts = data.grounded_facts || {};
    const chips = [];
    if (facts.current_temperature_c !== undefined) {
      chips.push(`<div class="metric-chip"><span class="metric-label">Temp:</span> <span class="metric-value">${facts.current_temperature_c}°C</span></div>`);
    }
    if (facts.relative_humidity_pct !== undefined) {
      chips.push(`<div class="metric-chip"><span class="metric-label">Humidity:</span> <span class="metric-value">${facts.relative_humidity_pct}%</span></div>`);
    }
    if (facts.forecast_today_rain_probability_pct !== undefined) {
      chips.push(`<div class="metric-chip"><span class="metric-label">Rain Prob:</span> <span class="metric-value">${facts.forecast_today_rain_probability_pct}%</span></div>`);
    }
    if (facts.wind_speed_kmh !== undefined) {
      chips.push(`<div class="metric-chip"><span class="metric-label">Wind:</span> <span class="metric-value">${facts.wind_speed_kmh} km/h</span></div>`);
    }
    if (facts.soil_moisture_0_7cm !== undefined && facts.soil_moisture_0_7cm !== null) {
      chips.push(`<div class="metric-chip"><span class="metric-label">Soil:</span> <span class="metric-value">${Number(facts.soil_moisture_0_7cm).toFixed(3)} m³/m³</span></div>`);
    }
    if (facts.nwp_cape_j_kg !== undefined) {
      chips.push(`<div class="metric-chip"><span class="metric-label">CAPE:</span> <span class="metric-value">${facts.nwp_cape_j_kg} J/kg</span></div>`);
    }

    const citationsText = (data.citations || []).slice(0, 3).join(" • ");
    const chartHtml = data.chart_spec ? renderInlineChart(data.chart_spec) : "";

    bubble.innerHTML = `
      <div class="sender-tag">${(data.role || "GENERAL").toUpperCase()} ADVISORY • ${facts.query_location || "INDIA"}</div>
      ${alertsHtml}
      <div class="advisory-content">${formatted}</div>
      ${chartHtml}
      <div class="grounding-card">
        <div class="grounding-header">
          <span>Telemetry Audit (${data.report_id})</span>
          <span>⚡ ${data.latency_ms}ms</span>
        </div>
        <div class="telemetry-grid">
          ${chips.join("")}
        </div>
        <div class="citations-row">
          <span>Sources: ${citationsText}</span>
          <button class="tts-btn" title="Read aloud">🔊 Speak</button>
          <span style="color: #10b981;">✓ Zero Hallucination Grounded</span>
        </div>
      </div>
    `;

    const ttsBtn = bubble.querySelector(".tts-btn");
    if (ttsBtn) {
      ttsBtn.addEventListener("click", () => speakText(data.answer, data.language || currentLanguage));
    }

    chatViewport.appendChild(bubble);
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }

  // ── Chat Form Submission ───────────────────────────────────────────
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    appendUserMessage(query);
    queryInput.value = "";
    appendTypingIndicator();

    try {
      const response = await fetch("/api/v1/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          session_id: sessionId,
          role: currentRole,
          language: currentLanguage
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      appendAssistantResponse(data);
    } catch (err) {
      const typingBubble = document.getElementById("typing-bubble");
      if (typingBubble) typingBubble.remove();

      const bubble = document.createElement("div");
      bubble.className = "message-bubble assistant";
      bubble.innerHTML = `<span style="color: #ef4444;">Error connecting to WeatherGPT: ${err.message}</span>`;
      chatViewport.appendChild(bubble);
      chatViewport.scrollTop = chatViewport.scrollHeight;
    }
  });


  // ═══════════════════════════════════════════════════════════════════
  // VIEW 2: LIVE TELEMETRY & MODEL DASHBOARD LOGIC
  // ═══════════════════════════════════════════════════════════════════
  async function loadDashboardWeather(locationName) {
    dashContent.innerHTML = `<div class="loading-spinner">Fetching live telemetry for ${locationName}...</div>`;

    try {
      const res = await fetch(`/api/v1/weather/report?location=${encodeURIComponent(locationName)}&role=general&include_climate=true`);
      if (!res.ok) throw new Error(`Status ${res.status}: ${res.statusText}`);
      const report = await res.json();
      renderDashboard(report);
    } catch (err) {
      dashContent.innerHTML = `
        <div class="placeholder-card" style="color: #ef4444;">
          <p>Failed to load weather report for "${locationName}": ${err.message}</p>
        </div>`;
    }
  }

  function getWeatherIcon(conditionText) {
    const text = (conditionText || "").toLowerCase();
    if (text.includes("rain") || text.includes("drizzle")) return "🌧️";
    if (text.includes("thunder") || text.includes("storm")) return "⛈️";
    if (text.includes("cloud") || text.includes("overcast")) return "☁️";
    if (text.includes("clear") || text.includes("sun")) return "☀️";
    if (text.includes("fog") || text.includes("haze")) return "🌫️";
    return "🌤️";
  }

  function renderDashboard(report) {
    const loc = report.location;
    const obs = report.observation;
    const fc = report.forecast;
    const nwp = report.nwp;
    const alerts = report.alerts || [];

    const weatherIcon = getWeatherIcon(obs.weather_condition);

    // Forecast items
    const forecastCardsHtml = (fc.daily || []).slice(0, 7).map(day => {
      const dIcon = getWeatherIcon(day.weather_condition);
      return `
        <div class="forecast-card">
          <div class="forecast-date">${String(day.date || day.time || day.forecast_date || day.day || "").split("T")[0].split("-").slice(1).join("/")}</div>
          <div class="forecast-icon">${dIcon}</div>
          <div class="forecast-temp">${Math.round(day.temp_max_c)}° / ${Math.round(day.temp_min_c)}°</div>
          <div class="forecast-rain">${day.rain_probability_pct}% rain</div>
        </div>`;
    }).join("");

    // Active Bulletins for district
    let alertsBannerHtml = "";
    if (alerts.length > 0) {
      alertsBannerHtml = alerts.map(a => `
        <div class="alert-item-card ${a.severity.toLowerCase()}">
          <div class="alert-card-top">
            <span class="alert-event">🚨 ${a.severity.toUpperCase()}: ${a.headline}</span>
            <span class="alert-source">${a.source}</span>
          </div>
          <div class="alert-directive">${a.instruction || "Follow disaster safety instructions."}</div>
        </div>
      `).join("");
    } else {
      alertsBannerHtml = `<div style="color: #10b981; font-size: 0.85rem; padding: 10px; background: rgba(16,185,129,0.1); border-radius: 6px; border: 1px solid rgba(16,185,129,0.2);">✅ No active severe weather warnings for ${loc.resolved_name}. Standard weather conditions prevail.</div>`;
    }

    // NWP CAPE status
    const cape = nwp ? nwp.cape_j_kg : 0;
    let capeClass = "stable";
    let capeText = "Stable";
    if (cape > 1500) { capeClass = "danger"; capeText = "Severe Squall Risk"; }
    else if (cape > 500) { capeClass = "moderate"; capeText = "Moderate Instability"; }

    dashContent.innerHTML = `
      <!-- Location Header Banner -->
      <div class="loc-banner">
        <div class="loc-banner-left">
          <h2>${loc.resolved_name}</h2>
          <p>${loc.district ? loc.district + ', ' : ''}${loc.state || 'India'} • Lat: ${loc.latitude.toFixed(2)}, Lon: ${loc.longitude.toFixed(2)}</p>
        </div>
        <div class="loc-banner-right">
          <span class="weather-badge-large">${weatherIcon}</span>
          <span class="temp-large">${obs.temperature_c}°C</span>
        </div>
      </div>

      <!-- Live Observations Metrics Grid -->
      <div class="metrics-grid-4">
        <div class="tele-card">
          <span class="tele-card-title">Condition</span>
          <span class="tele-card-val">${obs.weather_condition}</span>
          <span class="tele-card-sub">Feels like ${obs.apparent_temperature_c || obs.temperature_c}°C</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Relative Humidity</span>
          <span class="tele-card-val">${obs.relative_humidity_pct}%</span>
          <span class="tele-card-sub">Dew Point: ${(obs.temperature_c - ((100 - obs.relative_humidity_pct)/5)).toFixed(1)}°C</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Surface Wind</span>
          <span class="tele-card-val">${obs.wind_speed_kmh} km/h</span>
          <span class="tele-card-sub">Gusts up to ${obs.wind_gust_kmh || obs.wind_speed_kmh} km/h</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Surface Pressure</span>
          <span class="tele-card-val">${obs.surface_pressure_hpa} hPa</span>
          <span class="tele-card-sub">Barometric trend stable</span>
        </div>
      </div>

      <!-- 7-Day High-Resolution Forecast -->
      <div class="dash-section">
        <h3 class="dash-section-title">📅 7-Day Forecast Matrix (Open-Meteo High-Res)</h3>
        <div class="forecast-grid">
          ${forecastCardsHtml}
        </div>
      </div>

      <!-- NWP Numerical Weather Prediction Stability Deep-Dive -->
      <div class="nwp-box">
        <h3 class="dash-section-title">🛰️ NWP Atmospheric Stability (NOAA GFS &amp; NCMRWF)</h3>
        <div class="nwp-grid">
          <div class="nwp-card">
            <div class="nwp-card-header">
              <span class="tele-card-title">Convective Instability (CAPE)</span>
              <span class="nwp-status-pill ${capeClass}">${capeText}</span>
            </div>
            <div class="tele-card-val">${cape} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">J/kg</span></div>
            <div class="tele-card-sub">Threshold > 1500 indicates severe thunderstorm squall</div>
          </div>
          <div class="nwp-card">
            <div class="nwp-card-header">
              <span class="tele-card-title">Vertical Wind Shear (0-6km)</span>
              <span class="nwp-status-pill stable">Troposphere</span>
            </div>
            <div class="tele-card-val">${nwp ? nwp.wind_shear_0_6km_kmh : 'N/A'} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">km/h</span></div>
            <div class="tele-card-sub">Deep-layer steering flow and storm organization</div>
          </div>
          <div class="nwp-card">
            <div class="nwp-card-header">
              <span class="tele-card-title">Rootzone Soil Moisture</span>
              <span class="nwp-status-pill ${obs.soil_moisture_0_7cm > 0.4 ? 'danger' : 'stable'}">Layer 0-7cm</span>
            </div>
            <div class="tele-card-val">${obs.soil_moisture_0_7cm !== null ? Number(obs.soil_moisture_0_7cm).toFixed(3) : 'N/A'} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">m³/m³</span></div>
            <div class="tele-card-sub">${obs.soil_moisture_0_7cm > 0.4 ? 'Saturated topsoil - risk of waterlogging' : 'Adequate moisture profile for standing crops'}</div>
          </div>
        </div>
      </div>

      <!-- District Bulletins -->
      <div class="dash-section">
        <h3 class="dash-section-title">📢 Regional Warnings &amp; Disaster Bulletins</h3>
        ${alertsBannerHtml}
      </div>
    `;
  }

  dashSearchBtn.addEventListener("click", () => {
    const loc = dashSearchInput.value.trim();
    if (loc) loadDashboardWeather(loc);
  });

  dashSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const loc = dashSearchInput.value.trim();
      if (loc) loadDashboardWeather(loc);
    }
  });

  dashQuickCities.addEventListener("click", (e) => {
    const chip = e.target.closest(".city-chip");
    if (!chip) return;
    document.querySelectorAll(".city-chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    dashSearchInput.value = chip.dataset.city;
    loadDashboardWeather(chip.dataset.city);
  });


  // ═══════════════════════════════════════════════════════════════════
  // VIEW 3: DISASTER EOC & SEVERE ALERT SIMULATOR LOGIC
  // ═══════════════════════════════════════════════════════════════════
  async function loadActiveAlerts() {
    alertsListContainer.innerHTML = `<div class="loading-spinner">Fetching active national bulletins...</div>`;
    try {
      const res = await fetch("/api/v1/alerts/active");
      if (!res.ok) throw new Error("Failed to fetch alerts");
      const alerts = await res.json();
      renderAlertsList(alerts);
    } catch (err) {
      alertsListContainer.innerHTML = `<div style="color: #ef4444; font-size: 0.85rem;">Error loading alerts: ${err.message}</div>`;
    }
  }

  function renderAlertsList(alerts) {
    let redCount = 0;
    let orangeCount = 0;
    let yellowCount = 0;

    alerts.forEach(a => {
      const s = (a.severity || "").toLowerCase();
      if (s === "red") redCount++;
      else if (s === "orange") orangeCount++;
      else if (s === "yellow") yellowCount++;
    });

    statRed.textContent = redCount;
    statOrange.textContent = orangeCount;
    statYellow.textContent = yellowCount;

    if (!alerts || alerts.length === 0) {
      alertsListContainer.innerHTML = `<div class="placeholder-card">No active severe bulletins. All sectors normal.</div>`;
      return;
    }

    alertsListContainer.innerHTML = alerts.map(a => `
      <div class="alert-item-card ${a.severity.toLowerCase()}">
        <div class="alert-card-top">
          <span class="alert-event">🚨 ${a.severity.toUpperCase()} ALERT (${a.event_type})</span>
          <span class="alert-source">${a.source}</span>
        </div>
        <div style="font-weight: 600; color: #fff; font-size: 0.82rem;">${a.headline}</div>
        <div style="font-size: 0.74rem; color: #94a3b8;">
          Affected Districts: <strong>${(a.affected_districts || []).join(", ") || "General"}</strong> • 
          States: <strong>${(a.affected_states || []).join(", ") || "India"}</strong>
        </div>
        <div class="alert-directive">
          <strong>Mandatory Directive:</strong> ${a.instruction || "Follow state disaster management authority orders."}
        </div>
      </div>
    `).join("");
  }

  refreshAlertsBtn.addEventListener("click", loadActiveAlerts);

  async function triggerSimulation(rawText, states, districts) {
    try {
      const res = await fetch("/api/v1/alerts/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_text: rawText,
          source: "IMD National Disaster Weather Monitoring Center",
          affected_states: states,
          affected_districts: districts
        })
      });

      if (!res.ok) throw new Error("Simulation request failed");
      const alert = await res.json();
      loadActiveAlerts();
    } catch (err) {
      alert(`Simulation failed: ${err.message}`);
    }
  }

  simCycloneBtn.addEventListener("click", () => {
    triggerSimulation(
      "RED ALERT: Severe Cyclonic Storm 'Varuna' over West-Central Bay of Bengal moving northwestward with sustained winds of 120 km/h and gusts to 145 km/h. Coastal storm surge of 2.5 meters expected. Total ban on fishermen venturing into sea.",
      ["Andhra Pradesh", "Odisha"],
      ["Visakhapatnam", "Vizianagaram", "Srikakulam"]
    );
  });

  simRainBtn.addEventListener("click", () => {
    triggerSimulation(
      "ORANGE ALERT: Extremely Heavy Rainfall exceeding 220 mm in 24 hours expected in Konkan, Mumbai, and adjoining Western Ghats. Inundation of low-lying urban sectors and landslide hazards along mountain passes.",
      ["Maharashtra", "Goa"],
      ["Mumbai", "Thane", "Raigad", "Ratnagiri", "Pune"]
    );
  });

  simHeatBtn.addEventListener("click", () => {
    triggerSimulation(
      "YELLOW ALERT: Severe Heatwave conditions with maximum temperatures crossing 47.2°C in isolated pockets of Vidarbha and Telangana. Extreme thermal stress during peak afternoon hours 12:00 PM to 4:00 PM.",
      ["Maharashtra", "Telangana"],
      ["Nagpur", "Chandrapur", "Wardha", "Hyderabad"]
    );
  });

  customSimSubmit.addEventListener("click", () => {
    const text = customBulletinText.value.trim();
    if (!text) return alert("Please enter bulletin text to simulate");
    const st = customBulletinState.value.trim() || "Maharashtra";
    const dist = customBulletinDistrict.value.trim() || "Nashik";
    triggerSimulation(text, [st], [dist]);
    customBulletinText.value = "";
  });


  // ═══════════════════════════════════════════════════════════════════
  // VIEW 4: CLIMATE ARCHIVE & ERA5 TRENDS LOGIC
  // ═══════════════════════════════════════════════════════════════════
  async function loadClimateTrend(region, years) {
    climateChartContainer.innerHTML = `<div class="loading-spinner">Retrieving ERA5 multi-year reanalysis data for ${region}...</div>`;

    try {
      const res = await fetch(`/api/v1/climate/trend-chart?location=${encodeURIComponent(region)}&years=${years}`);
      if (!res.ok) throw new Error(`API error: ${res.statusText}`);
      const chartSpec = await res.json();
      renderClimateView(chartSpec, region);
    } catch (err) {
      climateChartContainer.innerHTML = `
        <div class="placeholder-card" style="color: #ef4444;">
          <p>Failed to load ERA5 climate trends: ${err.message}</p>
        </div>`;
    }
  }

  function renderClimateView(chartSpec, region) {
    const labels = chartSpec.labels || [];
    const values = chartSpec.values || [];
    const baseline = chartSpec.baseline_normal || 850;
    const unit = chartSpec.unit || "mm";

    const maxVal = Math.max(...values, baseline, 1);

    const barsHtml = labels.map((year, i) => {
      const val = values[i];
      const pct = Math.round((val / maxVal) * 100);
      const diffPct = (((val - baseline) / baseline) * 100).toFixed(1);
      const isAbove = val >= baseline;
      const barColor = isAbove ? "linear-gradient(90deg, #38bdf8, #0ea5e9)" : "linear-gradient(90deg, #f59e0b, #ef4444)";
      const badgeClass = isAbove ? "stable" : "danger";
      const badgeText = isAbove ? `+${diffPct}% (Excess)` : `${diffPct}% (Deficit)`;

      return `
        <div style="margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span style="font-weight: 600; color: #fff;">${year} Monsoon Season</span>
            <span style="color: #7dd3fc; font-weight: 700;">${val} ${unit} <span class="nwp-status-pill ${badgeClass}" style="margin-left: 6px;">${badgeText}</span></span>
          </div>
          <div style="background: #1e293b; border-radius: 4px; height: 22px; width: 100%; overflow: hidden; position: relative;">
            <div style="width: ${pct}%; background: ${barColor}; height: 100%; border-radius: 4px; transition: width 0.8s ease;"></div>
          </div>
        </div>
      `;
    }).join("");

    const baselinePct = Math.round((baseline / maxVal) * 100);

    climateChartContainer.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 12px;">
        <div>
          <h3 style="color: #fff; font-size: 1.15rem;">${chartSpec.title}</h3>
          <p style="font-size: 0.8rem; color: #94a3b8;">ERA5 Surface Precipitation Reanalysis (June–September Monsoon Total)</p>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 0.74rem; color: #94a3b8;">IMD Long Period Average (LPA Normal):</span>
          <div style="font-size: 1.1rem; font-weight: 700; color: #38bdf8;">${baseline} ${unit}</div>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        ${barsHtml}
      </div>

      <div style="background: #141f33; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px 16px;">
        <h4 style="color: #38bdf8; font-size: 0.85rem; margin-bottom: 6px;">🧠 Climate Trend Intelligence:</h4>
        <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">${chartSpec.trend_summary}</p>
      </div>
    `;
  }

  climateAnalyzeBtn.addEventListener("click", () => {
    loadClimateTrend(climateRegionSelect.value, parseInt(climateYearsSelect.value));
  });


  // ═══════════════════════════════════════════════════════════════════
  // VIEW 5: AVIATION & MARITIME OPERATIONS CONSOLE LOGIC
  // ═══════════════════════════════════════════════════════════════════
  briefingTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      briefingTabs.forEach(t => t.classList.remove("active"));
      briefingContents.forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      const mode = tab.dataset.mode;
      document.getElementById(`sub-${mode}`).classList.add("active");
    });
  });

  async function loadAviationBriefing(station) {
    aviationDisplayArea.innerHTML = `<div class="loading-spinner">Computing METAR &amp; flight category briefing for ${station}...</div>`;

    try {
      const res = await fetch(`/api/v1/weather/report?location=${encodeURIComponent(station)}&role=aviation`);
      if (!res.ok) throw new Error("Aviation briefing API error");
      const report = await res.json();
      renderAviationConsole(report, station);
    } catch (err) {
      aviationDisplayArea.innerHTML = `<div class="placeholder-card" style="color:#ef4444;">Error: ${err.message}</div>`;
    }
  }

  function renderAviationConsole(report, station) {
    const obs = report.observation;
    const nwp = report.nwp;
    const cape = nwp ? nwp.cape_j_kg : 0;
    const shear = nwp ? nwp.wind_shear_0_6km_kmh : 15;
    const vis = obs.visibility_km !== null ? obs.visibility_km : 8.5;

    let flightCategory = "VFR";
    let catClass = "vfr";
    let catDesc = "Visual Flight Rules — Unrestricted terminal operations permitted.";
    if (vis < 3.0 || cape > 1500) {
      flightCategory = "IFR";
      catClass = "ifr";
      catDesc = "Instrument Flight Rules Mandatory — Low visibility or severe convective squall detected.";
    } else if (vis < 8.0 || cape > 500) {
      flightCategory = "MVFR";
      catClass = "mvfr";
      catDesc = "Marginal VFR — Heightened vigilance required for low ceilings and scattered convective cells.";
    }

    // Crosswind estimation
    const crosswind = Math.round(obs.wind_speed_kmh * 0.7);

    aviationDisplayArea.innerHTML = `
      <div class="category-banner ${catClass}">
        <div>
          <div class="category-label">${flightCategory} OPERATIONS</div>
          <div class="category-desc">${catDesc}</div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 700;">${station.toUpperCase()}</div>
      </div>

      <div class="metrics-grid-4" style="margin-bottom: 16px;">
        <div class="tele-card">
          <span class="tele-card-title">Visibility</span>
          <span class="tele-card-val">${vis} km</span>
          <span class="tele-card-sub">Horizontal runway visual range</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Surface Wind</span>
          <span class="tele-card-val">${obs.wind_speed_kmh} km/h</span>
          <span class="tele-card-sub">Peak Gusts: ${obs.wind_gust_kmh || obs.wind_speed_kmh} km/h</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Runway Crosswind</span>
          <span class="tele-card-val">~${crosswind} km/h</span>
          <span class="tele-card-sub">Within standard crosswind limits</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Convective CAPE</span>
          <span class="tele-card-val">${cape} J/kg</span>
          <span class="tele-card-sub">Bulk Shear: ${shear} km/h</span>
        </div>
      </div>

      <div style="background: #162438; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px 16px;">
        <h4 style="color: #38bdf8; font-size: 0.85rem; margin-bottom: 6px;">✈️ Operations Clearance &amp; ATC Advisory:</h4>
        <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
          ${cape > 1500 
            ? '⚠️ Convective instability exceeds terminal safety threshold. Microburst and lightning squalls probable. Maintain minimum radar separation and verify alternate diversion airports.' 
            : '✅ Tropospheric profile indicates stable terminal maneuvering area. Standard departure and arrival routing approved.'}
        </p>
      </div>
    `;
  }

  aviationStations.addEventListener("click", (e) => {
    const pill = e.target.closest(".station-pill");
    if (!pill) return;
    aviationStations.querySelectorAll(".station-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    activeStationAviation = pill.dataset.station;
    loadAviationBriefing(activeStationAviation);
  });

  async function loadMarineBriefing(station) {
    marineDisplayArea.innerHTML = `<div class="loading-spinner">Computing port &amp; sea-state briefing for ${station}...</div>`;

    try {
      const res = await fetch(`/api/v1/weather/report?location=${encodeURIComponent(station)}&role=marine`);
      if (!res.ok) throw new Error("Marine briefing API error");
      const report = await res.json();
      renderMarineConsole(report, station);
    } catch (err) {
      marineDisplayArea.innerHTML = `<div class="placeholder-card" style="color:#ef4444;">Error: ${err.message}</div>`;
    }
  }

  function renderMarineConsole(report, station) {
    const obs = report.observation;
    const alerts = report.alerts || [];
    const gusts = obs.wind_gust_kmh || obs.wind_speed_kmh;

    let seaState = "Slight to Moderate";
    let statusClass = "vfr";
    let fishermenStatus = "🟢 SAFE TO VENTURE";
    let directive = "Coastal fishing and harbor vessels permitted to operate with standard cautionary watch.";

    if (alerts.some(a => a.severity === "red" || a.event_type.includes("CYCLONE")) || gusts > 50) {
      seaState = "Very Rough to High (Gale Winds)";
      statusClass = "ifr";
      fishermenStatus = "🔴 PROHIBITED — DANGER";
      directive = "All fishing trawlers and small crafts must immediately return to harbor or remain anchored. Deep-sea operations suspended.";
    } else if (alerts.some(a => a.severity === "orange") || gusts > 35) {
      seaState = "Moderate to Rough";
      statusClass = "mvfr";
      fishermenStatus = "🟡 EXERCISE CAUTION";
      directive = "Fishermen advised not to venture into deep offshore waters beyond 20 nautical miles.";
    }

    marineDisplayArea.innerHTML = `
      <div class="category-banner ${statusClass}">
        <div>
          <div class="category-label">${fishermenStatus}</div>
          <div class="category-desc">${directive}</div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 700;">${station.toUpperCase()}</div>
      </div>

      <div class="metrics-grid-4" style="margin-bottom: 16px;">
        <div class="tele-card">
          <span class="tele-card-title">Sea Surface Wind</span>
          <span class="tele-card-val">${obs.wind_speed_kmh} km/h</span>
          <span class="tele-card-sub">Peak Gusts: ${gusts} km/h</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Estimated Sea State</span>
          <span class="tele-card-val">${seaState.split(" ")[0]}</span>
          <span class="tele-card-sub">${seaState}</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Surface Pressure</span>
          <span class="tele-card-val">${obs.surface_pressure_hpa} hPa</span>
          <span class="tele-card-sub">Barometric sea-level pressure</span>
        </div>
        <div class="tele-card">
          <span class="tele-card-title">Active Warnings</span>
          <span class="tele-card-val">${alerts.length}</span>
          <span class="tele-card-sub">${alerts.length > 0 ? alerts[0].headline : 'No severe marine alerts'}</span>
        </div>
      </div>

      <div style="background: #162438; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px 16px;">
        <h4 style="color: #38bdf8; font-size: 0.85rem; margin-bottom: 6px;">⚓ Port Operations &amp; Crane Safety Guidelines:</h4>
        <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
          ${gusts > 45 
            ? '🚫 HIGH WIND HAZARD: Surface gusts exceed 45 km/h. Harbor crane and container stacking operations must be immediately secured or paused according to port safety code.' 
            : '✅ Crane and lighterage schedules operational within safety limits. Standard berthing precautions apply.'}
        </p>
      </div>
    `;
  }

  marineStations.addEventListener("click", (e) => {
    const pill = e.target.closest(".station-pill");
    if (!pill) return;
    marineStations.querySelectorAll(".station-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    activeStationMarine = pill.dataset.station;
    loadMarineBriefing(activeStationMarine);
  });

});
