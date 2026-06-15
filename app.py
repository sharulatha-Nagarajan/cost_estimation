import streamlit as st

st.set_page_config(page_title="Context Cost Calculator", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0d0d12; color: #e8e8ea; }
h1,h2,h3 { font-family: 'IBM Plex Mono', monospace !important; letter-spacing:-0.02em; }

.hero {
    background: linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
    border:1px solid #2a2a3e; border-radius:12px; padding:1.8rem 2.5rem; margin-bottom:1.5rem;
}
.hero h1 { font-size:1.8rem; color:#e0aaff; margin:0 0 0.2rem 0; }
.hero p  { color:#8888aa; font-size:0.88rem; margin:0; }

.section-label {
    font-family:'IBM Plex Mono',monospace; font-size:0.65rem; letter-spacing:0.12em;
    text-transform:uppercase; color:#e0aaff; margin-bottom:0.6rem;
    border-left:2px solid #e0aaff; padding-left:0.6rem;
}

.metric-pill {
    display:inline-block; border-radius:6px; padding:0.3rem 0.75rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.78rem; margin-bottom:0.5rem;
}

/* Provider comparison cards */
.prov-card {
    border-radius:10px; padding:1.1rem 1.3rem; margin-bottom:0.75rem;
    border:1px solid; position:relative;
}
.prov-card.winner { border-width:2px; }
.prov-badge {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem; letter-spacing:0.1em;
    text-transform:uppercase; border-radius:4px; padding:2px 7px; display:inline-block;
    margin-bottom:0.4rem;
}
.prov-name { font-size:1rem; font-weight:600; margin-bottom:0.1rem; }
.prov-cost { font-family:'IBM Plex Mono',monospace; font-size:1.6rem; font-weight:700; }
.prov-sub  { font-size:0.75rem; color:#8888aa; margin-top:0.15rem; }
.prov-fee  { font-size:0.78rem; margin-top:0.5rem; padding-top:0.5rem; border-top:1px solid #2a2a3e; }

hr { border-color:#2a2a3e !important; }
[data-testid="stSlider"] label  { font-size:0.85rem !important; color:#aaaacc !important; }
[data-testid="stSelectbox"] label { font-size:0.85rem !important; color:#aaaacc !important; }
[data-testid="stNumberInput"] label { font-size:0.85rem !important; color:#aaaacc !important; }
[data-testid="stAlert"] {
    background:#1a1a2e !important; border:1px solid #3a2a5e !important;
    color:#c0b0ff !important; border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

# Base model pricing (Direct API, $/1M tokens)
MODELS = {
    # Anthropic
    "Claude 3.5 Haiku":        {"family":"Anthropic","input":0.80,  "output":4.00,  "ctx":200_000, "openai_compat":False},
    "Claude 3.5 Sonnet":       {"family":"Anthropic","input":3.00,  "output":15.00, "ctx":200_000, "openai_compat":False},
    "Claude Sonnet 4":         {"family":"Anthropic","input":3.00,  "output":15.00, "ctx":200_000, "openai_compat":False},
    "Claude Opus 4":           {"family":"Anthropic","input":15.00, "output":75.00, "ctx":200_000, "openai_compat":False},
    # OpenAI — available on all platforms
    "GPT-5":                   {"family":"OpenAI",  "input":1.25,  "output":10.00, "ctx":272_000, "openai_compat":True},
    "GPT-5 Mini":              {"family":"OpenAI",  "input":0.25,  "output":2.00,  "ctx":272_000, "openai_compat":True},
    "GPT-5 Nano":              {"family":"OpenAI",  "input":0.05,  "output":0.40,  "ctx":272_000, "openai_compat":True},
    "GPT-5 Chat Latest":       {"family":"OpenAI",  "input":1.25,  "output":10.00, "ctx":272_000, "openai_compat":True},
    "GPT-5.5":                 {"family":"OpenAI",  "input":5.00,  "output":30.00, "ctx":270_000, "openai_compat":True},
    "GPT-5.5 Pro":             {"family":"OpenAI",  "input":30.00, "output":180.00,"ctx":270_000, "openai_compat":True},
    "GPT-5.4":                 {"family":"OpenAI",  "input":2.50,  "output":15.00, "ctx":270_000, "openai_compat":True},
    "GPT-5.4 Mini":            {"family":"OpenAI",  "input":0.75,  "output":4.50,  "ctx":270_000, "openai_compat":True},
    "GPT-5.4 Nano":            {"family":"OpenAI",  "input":0.20,  "output":1.25,  "ctx":270_000, "openai_compat":True},
    "GPT-5.4 Pro":             {"family":"OpenAI",  "input":30.00, "output":180.00,"ctx":270_000, "openai_compat":True},
    "GPT-5.3 Codex":           {"family":"OpenAI",  "input":1.75,  "output":14.00, "ctx":270_000, "openai_compat":True},
    "ChatGPT Latest":          {"family":"OpenAI",  "input":5.00,  "output":30.00, "ctx":270_000, "openai_compat":True},
    "GPT-4o":                  {"family":"OpenAI",  "input":2.50,  "output":10.00, "ctx":128_000, "openai_compat":True},
    "GPT-4o mini":             {"family":"OpenAI",  "input":0.15,  "output":0.60,  "ctx":128_000, "openai_compat":True},
    "GPT-4 Turbo":             {"family":"OpenAI",  "input":10.00, "output":30.00, "ctx":128_000, "openai_compat":True},
    "o1":                      {"family":"OpenAI",  "input":15.00, "output":60.00, "ctx":200_000, "openai_compat":True},
    "o3-mini":                 {"family":"OpenAI",  "input":1.10,  "output":4.40,  "ctx":200_000, "openai_compat":True},
    # Google
    "Gemini 1.5 Flash":        {"family":"Google",  "input":0.075, "output":0.30,  "ctx":1_000_000,"openai_compat":False},
    "Gemini 1.5 Pro":          {"family":"Google",  "input":3.50,  "output":10.50, "ctx":2_000_000,"openai_compat":False},
    "Gemini 2.0 Flash":        {"family":"Google",  "input":0.10,  "output":0.40,  "ctx":1_000_000,"openai_compat":False},
    # Meta/OSS
    "Llama 3.1 70B (hosted)":  {"family":"Meta/OSS","input":0.90,  "output":0.90,  "ctx":128_000, "openai_compat":False},
    "Llama 3.1 405B (hosted)": {"family":"Meta/OSS","input":3.00,  "output":3.00,  "ctx":128_000, "openai_compat":False},
    # Mistral
    "Mistral Large 2":         {"family":"Mistral", "input":2.00,  "output":6.00,  "ctx":128_000, "openai_compat":False},
    "Mistral Small 3":         {"family":"Mistral", "input":0.10,  "output":0.30,  "ctx":128_000, "openai_compat":False},
}

FAMILY_COLORS = {
    "Anthropic":"#c77dff","OpenAI":"#74c0fc","Google":"#69db7c",
    "Meta/OSS":"#ffa94d","Mistral":"#f783ac",
}

# Platform configs for cloud model comparison
# markup: multiplier on token price (e.g. 1.10 = +10%)
# flat_per_call: $ per API call
# monthly_fee: fixed $/month
# notes: displayed as fee breakdown
PLATFORMS = {
    "Direct API": {
        "color":"#74c0fc","icon":"🔷",
        "markup":1.00, "flat_per_call":0.0, "monthly_fee":0,
        "tier_label":"Pay-as-you-go",
        "notes":"No platform overhead. Direct vendor API pricing for the selected model family.",
        "families":["Anthropic", "OpenAI", "Google", "Meta/OSS", "Mistral"],
        "fees":[],
    },
    "Azure OpenAI": {
        "color":"#00bfff","icon":"☁️",
        "markup":1.00, "flat_per_call":0.0, "monthly_fee":0,
        "tier_label":"Token price parity + infra cost",
        "notes":"Same token prices as Direct OpenAI. Costs come from Azure infra (PTU commitments, networking, storage).",
        "families":["OpenAI"],
        "fees":[
            ("Azure infra / networking (est.)", 50, "month"),
            ("Private endpoint (optional)", 10, "month"),
        ],
    },
    "AWS Bedrock": {
        "color":"#ff9900","icon":"🟠",
        "markup":1.00, "flat_per_call":0.0, "monthly_fee":0,
        "tier_label":"Token price parity + Bedrock overhead",
        "notes":"AWS Bedrock can host selected model families. Additional costs come from data transfer, CloudWatch logging, and optional provisioned throughput.",
        "families":["Anthropic", "Meta/OSS", "Mistral"],
        "fees":[
            ("CloudWatch / logging (est.)", 15, "month"),
            ("Data transfer out (est.)", 10, "month"),
            ("Bedrock API overhead", 0.001, "call"),
        ],
    },
    "Gloo AI Gateway": {
        "color":"#a78bfa","icon":"🔮",
        "markup":1.00, "flat_per_call":0.002, "monthly_fee":299,
        "tier_label":"Gateway fee + token pass-through",
        "notes":"Gloo adds a per-call gateway fee plus a monthly platform subscription. Token prices are passed through for supported upstream providers.",
        "families":["Anthropic", "OpenAI", "Google", "Meta/OSS", "Mistral"],
        "fees":[
            ("Platform subscription", 299, "month"),
            ("Per-call gateway fee", 0.002, "call"),
        ],
    },
}

def fmt_tokens(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)

def fmt_usd(v, decimals=4):
    return f"${v:,.{decimals}f}"

def calc_token_cost(input_tok, output_tok, calls, model_info, markup=1.0):
    ic = (input_tok  / 1_000_000) * model_info["input"]  * markup * calls
    oc = (output_tok / 1_000_000) * model_info["output"] * markup * calls
    return ic, oc

def calc_platform_total(input_tok, output_tok, calls, model_info, platform):
    p = PLATFORMS[platform]
    ic, oc = calc_token_cost(input_tok, output_tok, calls, model_info, p["markup"])
    token_total = ic + oc
    # fixed monthly fees from fee list
    monthly_fixed = sum(amt for _, amt, freq in p["fees"] if freq == "month")
    per_call_fees = sum(amt for _, amt, freq in p["fees"] if freq == "call") * calls
    grand = token_total + monthly_fixed + per_call_fees
    return {
        "input_cost": ic, "output_cost": oc, "token_total": token_total,
        "monthly_fixed": monthly_fixed, "per_call_fees": per_call_fees,
        "grand": grand, "per_call": grand / calls if calls else 0,
    }

def available_platforms_for(model_info):
    return {
        name: info for name, info in PLATFORMS.items()
        if model_info["family"] in info["families"]
    }

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚡ Context Cost Calculator</h1>
  <p>Estimate and compare LLM API costs across providers — including Azure, AWS Bedrock, Gloo, and direct cloud APIs.</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Single Model Calculator", "🔀 Provider Comparison"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single model calculator
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="section-label">Model</div>', unsafe_allow_html=True)
        family_filter = st.selectbox("Filter by family", ["All"] + sorted(set(v["family"] for v in MODELS.values())), key="t1_fam")
        filtered = {k:v for k,v in MODELS.items() if family_filter=="All" or v["family"]==family_filter}
        model_name = st.selectbox("Model", list(filtered.keys()), key="t1_model")
        model = filtered[model_name]

        pc = FAMILY_COLORS.get(model["family"], "#aaaacc")
        st.markdown(f"""<span class="metric-pill" style="color:{pc};border:1px solid {pc}44;background:{pc}11">
          {model['family']} &nbsp;·&nbsp; ctx {fmt_tokens(model['ctx'])} &nbsp;·&nbsp;
          In ${model['input']}/1M &nbsp;·&nbsp; Out ${model['output']}/1M
        </span>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Context Window</div>', unsafe_allow_html=True)
        max_ctx = model["ctx"]

        sys_p  = st.slider("System prompt (tokens)",        0, min(8_000,max_ctx),   500,  50,  key="t1_sys")
        rag    = st.slider("RAG / retrieved docs (tokens)", 0, min(100_000,max_ctx), 2000, 500, key="t1_rag")
        hist   = st.slider("Conversation history (tokens)", 0, min(50_000,max_ctx),  1000, 500, key="t1_hist")
        usr    = st.slider("User message (tokens)",         0, min(10_000,max_ctx),   200,  50,  key="t1_usr")
        total_input = sys_p + rag + hist + usr
        ctx_pct = min(total_input / max_ctx * 100, 100)
        bar_col = "#c77dff" if ctx_pct<70 else ("#ffa94d" if ctx_pct<90 else "#ff6b6b")
        st.markdown(f"""<div style="margin:0.4rem 0 1.2rem 0;">
          <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#8888aa;margin-bottom:4px;">
            <span>Context used: <b style="color:{bar_col}">{fmt_tokens(total_input)}</b></span>
            <span style="color:{bar_col}">{ctx_pct:.1f}% of {fmt_tokens(max_ctx)}</span>
          </div>
          <div style="background:#1e1e30;border-radius:4px;height:6px;overflow:hidden;">
            <div style="width:{ctx_pct:.1f}%;background:{bar_col};height:100%;border-radius:4px;"></div>
          </div></div>""", unsafe_allow_html=True)
        if total_input > max_ctx:
            st.error(f"⚠️ Input ({fmt_tokens(total_input)}) exceeds model limit ({fmt_tokens(max_ctx)}).")

        st.markdown('<div class="section-label">Output & Volume</div>', unsafe_allow_html=True)
        out_tok = st.slider("Output tokens per call", 50, 8_000, 500, 50, key="t1_out")
        calls   = st.number_input("API calls per month", 1, 10_000_000, 1_000, 100, key="t1_calls")

    with right:
        ic, oc = calc_token_cost(total_input, out_tok, calls, model)
        total_cost = ic + oc
        per_call   = total_cost / calls if calls else 0

        st.markdown('<div class="section-label">Monthly Cost</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("💰 Total", fmt_usd(total_cost, 4))
        m2.metric("📞 Per Call", fmt_usd(per_call, 6))
        st.divider()

        st.markdown('<div class="section-label">Cost Breakdown</div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**Token Usage**")
            st.markdown(f"""| | |
|---|---|
| Input / call | `{fmt_tokens(total_input)}` |
| Output / call | `{fmt_tokens(out_tok)}` |
| Input / month | `{fmt_tokens(total_input*calls)}` |
| Output / month | `{fmt_tokens(out_tok*calls)}` |
""")
        with cb:
            st.markdown("**Costs**")
            st.markdown(f"""| | |
|---|---|
| Input cost | `{fmt_usd(ic,4)}` |
| Output cost | `{fmt_usd(oc,4)}` |
| **Total** | **`{fmt_usd(total_cost,4)}`** |
| Per call | `{fmt_usd(per_call,6)}` |
""")
        st.divider()

        st.markdown('<div class="section-label">Context Composition</div>', unsafe_allow_html=True)
        for emoji, label, val in [("🟣","System prompt",sys_p),("🔵","RAG / docs",rag),("🟢","History",hist),("🟠","User msg",usr)]:
            pct = (val/total_input) if total_input else 0
            cl, cr = st.columns([3,1])
            with cl: st.progress(pct, text=f"{emoji}  {label}")
            with cr: st.markdown(f"<div style='text-align:right;padding-top:6px;font-family:monospace;font-size:0.82rem;'>{fmt_tokens(val)}<br><span style='color:#888;font-size:0.72rem;'>{pct*100:.0f}%</span></div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="section-label">Scale Projections</div>', unsafe_allow_html=True)
        s1,s2,s3 = st.columns(3)
        for col,(lbl,mult) in zip([s1,s2,s3],[("10×",10),("100×",100),("1K×",1000)]):
            col.metric(lbl, fmt_usd(total_cost*mult,2), help=f"{fmt_tokens(calls*mult)} calls/mo")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Provider Comparison
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Compare supported cloud models across Direct API, Azure, AWS Bedrock, and Gloo")
    st.caption("Choose any supported model. The comparison only shows platforms mapped to that model family.")
    st.markdown("")

    # Config row
    cfg1, cfg2, cfg3 = st.columns([1.2, 1, 1])
    with cfg1:
        cmp_model_name = st.selectbox("Cloud Model", list(MODELS.keys()), key="cmp_model")
        cmp_model = MODELS[cmp_model_name]
        available_platforms = available_platforms_for(cmp_model)
    with cfg2:
        cmp_calls = st.number_input("API calls / month", 1, 10_000_000, 10_000, 1000, key="cmp_calls")
    with cfg3:
        cmp_out = st.slider("Output tokens / call", 50, 8_000, 500, 50, key="cmp_out")

    st.markdown('<div class="section-label">Context Window (shared)</div>', unsafe_allow_html=True)
    cc1, cc2, cc3, cc4 = st.columns(4)
    cmp_sys  = cc1.slider("System prompt",  0, 8_000,   500, 50,  key="cmp_sys")
    cmp_rag  = cc2.slider("RAG docs",       0, 100_000, 2000, 500, key="cmp_rag")
    cmp_hist = cc3.slider("History",        0, 50_000,  1000, 500, key="cmp_hist")
    cmp_usr  = cc4.slider("User message",   0, 10_000,  200,  50,  key="cmp_usr")
    cmp_input = cmp_sys + cmp_rag + cmp_hist + cmp_usr
    if cmp_input > cmp_model["ctx"]:
        st.error(f"⚠️ Input ({fmt_tokens(cmp_input)}) exceeds model limit ({fmt_tokens(cmp_model['ctx'])}).")

    st.markdown("")

    # Custom overrides expander
    with st.expander("⚙️ Customise platform fees (optional)"):
        st.caption("Override the default fee estimates below. Changes apply immediately to the comparison.")
        ov1, ov2, ov3, ov4 = st.columns(4)
        azure_infra   = ov1.number_input("Azure infra $/mo",    0.0, 10000.0, 50.0,  5.0,  key="az_infra")
        azure_ep      = ov1.number_input("Azure endpoint $/mo", 0.0, 500.0,   10.0,  5.0,  key="az_ep")
        aws_cw        = ov2.number_input("AWS CloudWatch $/mo", 0.0, 1000.0,  15.0,  5.0,  key="aws_cw")
        aws_dt        = ov2.number_input("AWS data transfer $/mo",0.0,1000.0, 10.0,  5.0,  key="aws_dt")
        aws_per_call  = ov2.number_input("AWS per-call fee $",  0.0, 0.1,     0.001, 0.001,key="aws_pc", format="%.4f")
        gloo_sub      = ov3.number_input("Gloo subscription $/mo",0.0,5000.0,299.0, 50.0, key="gloo_sub")
        gloo_per_call = ov3.number_input("Gloo per-call fee $", 0.0, 0.1,    0.002, 0.001,key="gloo_pc", format="%.4f")

    # Recalc with custom fees
    def custom_calc(platform_key):
        ic, oc = calc_token_cost(cmp_input, cmp_out, cmp_calls, cmp_model)
        token_total = ic + oc
        if platform_key == "Direct API":
            mf, pcf = 0, 0
        elif platform_key == "Azure OpenAI":
            mf  = azure_infra + azure_ep
            pcf = 0
        elif platform_key == "AWS Bedrock":
            mf  = aws_cw + aws_dt
            pcf = aws_per_call * cmp_calls
        else:  # Gloo
            mf  = gloo_sub
            pcf = gloo_per_call * cmp_calls
        grand = token_total + mf + pcf
        return {"ic":ic,"oc":oc,"token_total":token_total,"mf":mf,"pcf":pcf,
                "grand":grand,"per_call":grand/cmp_calls if cmp_calls else 0}

    results = {p: custom_calc(p) for p in available_platforms}
    sorted_platforms = sorted(results.items(), key=lambda x: x[1]["grand"])
    cheapest = sorted_platforms[0][0]
    cheapest_cost = sorted_platforms[0][1]["grand"]

    # ── Cards ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Provider Cost Comparison</div>', unsafe_allow_html=True)

    card_cols = st.columns(len(available_platforms))
    for col, (pname, pinfo) in zip(card_cols, available_platforms.items()):
        r = results[pname]
        is_winner = pname == cheapest
        savings = r["grand"] - cheapest_cost
        color = pinfo["color"]
        bg = f"{color}18"
        border = f"{color}99" if is_winner else f"{color}44"

        fee_lines = ""
        if r["mf"] > 0:
            fee_lines += f"<div>📋 Platform fees: <b>{fmt_usd(r['mf'],2)}/mo</b></div>"
        if r["pcf"] > 0:
            fee_lines += f"<div>🔁 Per-call fees: <b>{fmt_usd(r['pcf'],2)}/mo</b></div>"
        if r["mf"] == 0 and r["pcf"] == 0:
            fee_lines = "<div style='color:#6688aa'>No additional platform fees</div>"

        winner_badge = ""
        if is_winner:
            winner_badge = f'<div class="prov-badge" style="background:{color}33;color:{color}">✓ Cheapest</div>'
        else:
            pct_more = ((r["grand"]/cheapest_cost)-1)*100 if cheapest_cost > 0 else 0
            winner_badge = f'<div class="prov-badge" style="background:#2a2a3e;color:#8888aa">+{pct_more:.1f}% vs cheapest</div>'

        with col:
            st.markdown(f"""
<div class="prov-card {'winner' if is_winner else ''}"
     style="background:{bg};border-color:{border};">
  {winner_badge}
  <div class="prov-name" style="color:{color}">{pinfo['icon']} {pname}</div>
  <div class="prov-cost" style="color:{color}">{fmt_usd(r['grand'],2)}</div>
  <div class="prov-sub">per month · {fmt_usd(r['per_call'],5)}/call</div>
  <div class="prov-fee" style="color:#aaaacc">{fee_lines}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Detailed breakdown table ──────────────────────────────────────────────
    st.markdown('<div class="section-label">Detailed Cost Breakdown</div>', unsafe_allow_html=True)

    # Build comparison dataframe-style using markdown table
    rows_data = [
        ("Input token cost",    {p: fmt_usd(results[p]["ic"],4)        for p in available_platforms}),
        ("Output token cost",   {p: fmt_usd(results[p]["oc"],4)        for p in available_platforms}),
        ("Token subtotal",      {p: fmt_usd(results[p]["token_total"],4) for p in available_platforms}),
        ("Platform fees/mo",    {p: fmt_usd(results[p]["mf"],2)        for p in available_platforms}),
        ("Per-call fees/mo",    {p: fmt_usd(results[p]["pcf"],2)       for p in available_platforms}),
        ("**Total/month**",     {p: f"**{fmt_usd(results[p]['grand'],2)}**" for p in available_platforms}),
        ("Per call",            {p: fmt_usd(results[p]["per_call"],5)  for p in available_platforms}),
    ]

    header = "| Metric | " + " | ".join(f"{available_platforms[p]['icon']} {p}" for p in available_platforms) + " |"
    sep    = "|---|" + "---|"*len(available_platforms)
    table_rows = "\n".join(
        f"| {label} | " + " | ".join(vals[p] for p in available_platforms) + " |"
        for label, vals in rows_data
    )
    st.markdown(f"{header}\n{sep}\n{table_rows}")

    st.divider()

    # ── Fee info expander per provider ────────────────────────────────────────
    st.markdown('<div class="section-label">Platform Fee Notes</div>', unsafe_allow_html=True)
    note_cols = st.columns(len(available_platforms))
    for col, (pname, pinfo) in zip(note_cols, available_platforms.items()):
        color = pinfo["color"]
        with col:
            st.markdown(f"**{pinfo['icon']} {pname}**")
            st.caption(pinfo["notes"])

    st.divider()

    # ── Scale projections for comparison ─────────────────────────────────────
    st.markdown('<div class="section-label">Scale Projections (All Providers)</div>', unsafe_allow_html=True)
    sc_cols = st.columns(len(available_platforms))
    for col, (pname, pinfo) in zip(sc_cols, available_platforms.items()):
        r = results[pname]
        color = pinfo["color"]
        with col:
            st.markdown(f"<div style='font-size:0.8rem;font-weight:600;color:{color};margin-bottom:0.4rem'>{pinfo['icon']} {pname}</div>", unsafe_allow_html=True)
            for lbl, mult in [("10×", 10), ("100×", 100), ("1K×", 1000)]:
                # scale only the variable parts; fixed fees stay fixed
                scaled = r["token_total"]*mult + r["mf"] + r["pcf"]*mult
                st.markdown(f"<div style='display:flex;justify-content:space-between;font-size:0.82rem;padding:3px 0;border-bottom:1px solid #1e1e30'><span style='color:#8888aa'>{lbl} calls</span><span style='font-family:monospace;color:{color}'>{fmt_usd(scaled,2)}</span></div>", unsafe_allow_html=True)
