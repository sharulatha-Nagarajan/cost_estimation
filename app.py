import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Context Cost Calculator",
    page_icon="⚡",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark mono background */
.stApp {
    background-color: #0f0f11;
    color: #e8e8ea;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: -0.02em;
}

/* Hero strip */
.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2a2a3e;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}
.hero h1 {
    font-size: 2rem;
    color: #e0aaff;
    margin: 0 0 0.25rem 0;
}
.hero p {
    color: #8888aa;
    font-size: 0.9rem;
    margin: 0;
}

/* Section headers */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #e0aaff;
    margin-bottom: 0.75rem;
    border-left: 2px solid #e0aaff;
    padding-left: 0.6rem;
}

/* Cost card */
.cost-card {
    background: #1a1a2e;
    border: 1px solid #2a2a3e;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.cost-card .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: #8888aa;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.cost-card .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    color: #c77dff;
}
.cost-card .sub {
    font-size: 0.8rem;
    color: #6666aa;
    margin-top: 0.2rem;
}

/* Breakdown table */
.breakdown {
    background: #12121e;
    border: 1px solid #2a2a3e;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.breakdown-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid #1e1e30;
    font-size: 0.88rem;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-row .bname { color: #aaaacc; }
.breakdown-row .bval {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    color: #e0aaff;
}

/* Metric pill */
.metric-pill {
    display: inline-block;
    background: #1e1e30;
    border: 1px solid #2e2e48;
    border-radius: 6px;
    padding: 0.3rem 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: #c0b0ff;
    margin-bottom: 0.5rem;
}

/* Slider label overrides */
[data-testid="stSlider"] label {
    font-size: 0.85rem !important;
    color: #aaaacc !important;
}

/* Selectbox */
[data-testid="stSelectbox"] label {
    font-size: 0.85rem !important;
    color: #aaaacc !important;
}

/* Number input */
[data-testid="stNumberInput"] label {
    font-size: 0.85rem !important;
    color: #aaaacc !important;
}

/* Divider */
hr { border-color: #2a2a3e !important; }

/* Warning / info boxes */
[data-testid="stAlert"] {
    background: #1a1a2e !important;
    border: 1px solid #3a2a5e !important;
    color: #c0b0ff !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Model pricing (input $/1M tokens, output $/1M tokens) ────────────────────
MODELS = {
    # Anthropic
    "Claude 3.5 Haiku":        {"provider": "Anthropic", "input": 0.80,  "output": 4.00,  "ctx": 200_000},
    "Claude 3.5 Sonnet":       {"provider": "Anthropic", "input": 3.00,  "output": 15.00, "ctx": 200_000},
    "Claude 3 Opus":           {"provider": "Anthropic", "input": 15.00, "output": 75.00, "ctx": 200_000},
    "Claude Sonnet 4":         {"provider": "Anthropic", "input": 3.00,  "output": 15.00, "ctx": 200_000},
    "Claude Opus 4":           {"provider": "Anthropic", "input": 15.00, "output": 75.00, "ctx": 200_000},
    # OpenAI
    "GPT-4o":                  {"provider": "OpenAI",    "input": 2.50,  "output": 10.00, "ctx": 128_000},
    "GPT-4o mini":             {"provider": "OpenAI",    "input": 0.15,  "output": 0.60,  "ctx": 128_000},
    "GPT-4 Turbo":             {"provider": "OpenAI",    "input": 10.00, "output": 30.00, "ctx": 128_000},
    "o1":                      {"provider": "OpenAI",    "input": 15.00, "output": 60.00, "ctx": 200_000},
    "o3-mini":                 {"provider": "OpenAI",    "input": 1.10,  "output": 4.40,  "ctx": 200_000},
    # Google
    "Gemini 1.5 Flash":        {"provider": "Google",    "input": 0.075, "output": 0.30,  "ctx": 1_000_000},
    "Gemini 1.5 Pro":          {"provider": "Google",    "input": 3.50,  "output": 10.50, "ctx": 2_000_000},
    "Gemini 2.0 Flash":        {"provider": "Google",    "input": 0.10,  "output": 0.40,  "ctx": 1_000_000},
    # Meta / Open
    "Llama 3.1 70B (hosted)":  {"provider": "Meta/OSS",  "input": 0.90,  "output": 0.90,  "ctx": 128_000},
    "Llama 3.1 405B (hosted)": {"provider": "Meta/OSS",  "input": 3.00,  "output": 3.00,  "ctx": 128_000},
    # Mistral
    "Mistral Large 2":         {"provider": "Mistral",   "input": 2.00,  "output": 6.00,  "ctx": 128_000},
    "Mistral Small 3":         {"provider": "Mistral",   "input": 0.10,  "output": 0.30,  "ctx": 128_000},
}

PROVIDER_COLORS = {
    "Anthropic": "#c77dff",
    "OpenAI":    "#74c0fc",
    "Google":    "#69db7c",
    "Meta/OSS":  "#ffa94d",
    "Mistral":   "#f783ac",
}

def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)

def calc_cost(input_tokens, output_tokens, calls, model_info):
    input_cost  = (input_tokens  / 1_000_000) * model_info["input"]  * calls
    output_cost = (output_tokens / 1_000_000) * model_info["output"] * calls
    return input_cost, output_cost, input_cost + output_cost

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚡ Context Cost Calculator</h1>
  <p>Estimate LLM API costs by configuring your context window, output size, call volume, and model.</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    # — Model selection --------------------------------------------------------
    st.markdown('<div class="section-label">Model</div>', unsafe_allow_html=True)
    
    provider_filter = st.selectbox(
        "Filter by provider",
        ["All"] + sorted(set(v["provider"] for v in MODELS.values())),
        label_visibility="collapsed",
    )
    
    filtered = {k: v for k, v in MODELS.items()
                if provider_filter == "All" or v["provider"] == provider_filter}
    
    model_name = st.selectbox("Model", list(filtered.keys()), label_visibility="collapsed")
    model = filtered[model_name]
    
    pc = PROVIDER_COLORS.get(model["provider"], "#aaaacc")
    st.markdown(f"""
    <span class="metric-pill" style="color:{pc}; border-color:{pc}44; background:{pc}11">
      {model['provider']} &nbsp;·&nbsp; Max ctx: {fmt_tokens(model['ctx'])} tokens &nbsp;·&nbsp;
      In: ${model['input']}/1M &nbsp;·&nbsp; Out: ${model['output']}/1M
    </span>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # — Context breakdown sliders --------------------------------------------
    st.markdown('<div class="section-label">Context Window Breakdown</div>', unsafe_allow_html=True)
    
    max_ctx = model["ctx"]
    
    system_prompt = st.slider(
        "System prompt (tokens)",
        min_value=0, max_value=min(8_000, max_ctx),
        value=500, step=50,
    )
    
    retrieved_docs = st.slider(
        "Retrieved / RAG documents (tokens)",
        min_value=0, max_value=min(100_000, max_ctx),
        value=2_000, step=500,
    )
    
    conversation_history = st.slider(
        "Conversation history (tokens)",
        min_value=0, max_value=min(50_000, max_ctx),
        value=1_000, step=500,
    )
    
    user_message = st.slider(
        "User message (tokens)",
        min_value=0, max_value=min(10_000, max_ctx),
        value=200, step=50,
    )
    
    total_input = system_prompt + retrieved_docs + conversation_history + user_message
    ctx_pct = min(total_input / max_ctx * 100, 100)

    # capacity bar
    bar_color = "#c77dff" if ctx_pct < 70 else ("#ffa94d" if ctx_pct < 90 else "#ff6b6b")
    st.markdown(f"""
    <div style="margin: 0.5rem 0 1.5rem 0;">
      <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#8888aa; margin-bottom:4px;">
        <span>Context used: <b style="color:{bar_color}">{fmt_tokens(total_input)}</b></span>
        <span style="color:{bar_color}">{ctx_pct:.1f}% of {fmt_tokens(max_ctx)}</span>
      </div>
      <div style="background:#1e1e30; border-radius:4px; height:6px; overflow:hidden;">
        <div style="width:{ctx_pct:.1f}%; background:{bar_color}; height:100%; border-radius:4px; transition:width 0.3s;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if total_input > max_ctx:
        st.error(f"⚠️ Input ({fmt_tokens(total_input)}) exceeds model context limit ({fmt_tokens(max_ctx)}).")

    st.markdown('<div class="section-label">Output & Volume</div>', unsafe_allow_html=True)

    output_tokens = st.slider(
        "Output tokens per call",
        min_value=50, max_value=8_000,
        value=500, step=50,
    )

    calls = st.number_input(
        "API calls per month",
        min_value=1, max_value=10_000_000,
        value=1_000, step=100,
    )

with right:
    input_cost, output_cost, total_cost = calc_cost(total_input, output_tokens, calls, model)
    per_call = total_cost / calls if calls else 0
    total_input_tokens_month  = total_input  * calls
    total_output_tokens_month = output_tokens * calls

    # — Top metrics -------------------------------------------------------
    st.markdown('<div class="section-label">Estimated Monthly Cost</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("💰 Total Cost", f"${total_cost:,.4f}")
    with c2:
        st.metric("📞 Per Call", f"${per_call:.6f}")

    st.divider()

    # — Cost Breakdown table (native) --------------------------------------
    st.markdown('<div class="section-label">Cost Breakdown</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Token Usage**")
        st.markdown(f"""
| | Tokens |
|---|---|
| Input / call | `{fmt_tokens(total_input)}` |
| Output / call | `{fmt_tokens(output_tokens)}` |
| Input / month | `{fmt_tokens(total_input_tokens_month)}` |
| Output / month | `{fmt_tokens(total_output_tokens_month)}` |
""")
    with col_b:
        st.markdown("**Costs**")
        st.markdown(f"""
| | USD |
|---|---|
| Input cost | `${input_cost:,.4f}` |
| Output cost | `${output_cost:,.4f}` |
| **Total** | **`${total_cost:,.4f}`** |
| Per call | `${per_call:.6f}` |
""")

    st.divider()

    # — Context composition (native progress bars) ------------------------
    st.markdown('<div class="section-label">Context Composition</div>', unsafe_allow_html=True)

    parts = {
        "🟣  System prompt":   system_prompt,
        "🔵  RAG / docs":      retrieved_docs,
        "🟢  History":         conversation_history,
        "🟠  User message":    user_message,
    }

    for label, val in parts.items():
        pct = (val / total_input) if total_input else 0
        col_l, col_r = st.columns([3, 1])
        with col_l:
            st.progress(pct, text=label)
        with col_r:
            st.markdown(f"<div style='text-align:right; padding-top:6px; font-family:monospace; font-size:0.85rem;'>{fmt_tokens(val)}<br><span style='color:#888;font-size:0.75rem;'>{pct*100:.0f}%</span></div>", unsafe_allow_html=True)

    st.divider()

    # — Scale projections (native) ----------------------------------------
    st.markdown('<div class="section-label">Scale Projections</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    for col, (label, mult) in zip([s1, s2, s3], [("10×", 10), ("100×", 100), ("1K×", 1_000)]):
        with col:
            st.metric(
                label=f"{label} calls",
                value=f"${total_cost * mult:,.2f}",
                help=f"{fmt_tokens(calls * mult)} calls/month"
            )