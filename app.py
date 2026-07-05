"""
Zomato x DPDP - "Consent, Clearly"
A clickable, deployable prototype of a DPDP-aligned consent & data-rights experience.

Run locally:   pip install -r requirements.txt  &&  streamlit run streamlit_app.py
Deploy:        push this folder to GitHub, then create an app at share.streamlit.io
"""

import streamlit as st

# ------------------------------------------------------------------ config
st.set_page_config(page_title="Zomato x DPDP - Consent, Clearly",
                   page_icon="🛡️", layout="centered", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ data
OPTIONALS = [
    ("personalise", "Personalised recommendations", "Uses your order history to suggest dishes you'll like."),
    ("marketing",   "Marketing messages",           "Offers and updates by email & SMS."),
    ("contacts",    "Find friends",                 "Reads your contacts to help you refer friends."),
    ("bgLocation",  "Precise background location",  "Faster ETAs by reading location in the background."),
]
LABELS = {k: label for k, label, _ in OPTIONALS}

I18N = {
    "en": dict(title="Your data, your rules",
               sub="Choose what Zomato uses, and why. You can change any of this later in 2 taps.",
               ess="To take & deliver your order",
               esssub="Location while ordering · Payment · Contact for delivery",
               optlabel="OPTIONAL — OFF BY DEFAULT",
               cont="Accept essentials & continue"),
    "hi": dict(title="आपका डेटा, आपके नियम",
               sub="चुनें कि Zomato क्या इस्तेमाल करे और क्यों। आप इसे बाद में 2 टैप में बदल सकते हैं।",
               ess="आपका ऑर्डर लेने और पहुँचाने के लिए",
               esssub="ऑर्डर के दौरान लोकेशन · भुगतान · डिलीवरी संपर्क",
               optlabel="वैकल्पिक — डिफ़ॉल्ट रूप से बंद",
               cont="ज़रूरी चीज़ें स्वीकार करें और आगे बढ़ें"),
}

STEP = {"splash": 1, "language": 1, "age": 1, "childVerify": 1, "childDone": 1, "consent": 1,
        "order": 2, "profile": 3, "privacy": 3,
        "manage": 4, "rights": 4, "data": 4, "grievance": 4}
STEP_NAMES = {1: "CONSENT", 2: "ORDER", 3: "PRIVACY CENTER", 4: "YOUR RIGHTS"}

INFO = {
 "splash":     ("Welcome", "A redesigned consent & data experience for Zomato. Tap through the happy path; this panel explains the DPDP thinking behind each screen.", [], ""),
 "language":   ("Notice in your language", "Consent is only valid if it's understood. Language choice comes first.", ["Notice offered in English + 22 scheduled languages"], "DPDP · plain-language notice"),
 "age":        ("Age assurance", "A single bright line: under-18 is a child. We check age with the lightest touch that works, escalating only on risk signals.", ["Age verification before processing", "Data minimisation — no extra collection"], "DPDP Rule 10"),
 "childVerify":("Verifiable parental consent", "For a minor, a parent must approve — and we must verify they're a real, identifiable adult.", ["DigiLocker / existing adult-account path", "Parent identity checked, nothing more"], "DPDP Rule 10"),
 "childDone":  ("Protection by default", "With parental consent, the account runs in a protected mode.", ["No behavioural tracking or profiling", "No targeted advertising to minors"], "DPDP Rule 10"),
 "consent":    ("Itemised, unbundled consent", "Essentials are grouped and clearly labelled. Every optional use is a separate, specific purpose — and OFF by default.", ["Itemised notice, one purpose per use", "Free & specific — no pre-ticked boxes", "Essential separated from optional"], "DPDP Rule 3"),
 "order":      ("The happy path is fast", "Because ordering needs only essentials, the core journey has almost no consent friction. Location is used only while the order is live.", ["Purpose limitation", "Data minimisation"], "DPDP · purpose limitation"),
 "profile":    ("Two taps from home", "Profile → Privacy & Data. Controls are discoverable, never buried in a policy.", ["Accessible controls", "Discoverable by design"], "DPDP · easy access"),
 "privacy":    ("The Privacy Center", "One home for consents, rights, transparency and grievance — the trust surface of the product.", ["Consent management", "Rights & grievance in one place"], "DPDP · Rules 3, 13, 14"),
 "manage":     ("Withdrawal parity", "Turn any optional use off in exactly one tap — as easy as turning it on. Essentials show an honest consequence instead of silently breaking.", ["Withdraw as easily as you consent", "Honest consequence copy, no dark patterns"], "DPDP · consent withdrawal"),
 "rights":     ("Data-principal rights", "Access, correction, erasure and nomination — all self-serve, no support ticket needed.", ["Access · Correction · Erasure", "Right to nominate"], "DPDP Rule 14"),
 "data":       ("Right to access", "A plain-language summary of what's held, for how long, and who sees it.", ["Summary of data & purposes", "Retention & recipients disclosed"], "DPDP Rule 14"),
 "grievance":  ("Grievance redressal", "A readily-available channel to the Data Protection Officer, with a published SLA.", ["Accessible grievance mechanism", "Published resolution timeline"], "DPDP · Rule 13"),
}

# ------------------------------------------------------------------ state + callbacks
def init():
    ss = st.session_state
    ss.setdefault("screen", "splash")
    ss.setdefault("lang", "en")
    ss.setdefault("is_child", False)
    ss.setdefault("consents", {k: False for k, _, _ in OPTIONALS})
    ss.setdefault("grievance_done", False)
    ss.setdefault("dialog", None)
    ss.setdefault("erase_req", False)
    ss.setdefault("pending_toast", None)

def nav(target, toast=None):
    st.session_state.screen = target
    st.session_state.dialog = None
    if target == "manage":                       # re-seed manage toggles from source of truth
        for k, _, _ in OPTIONALS:
            st.session_state[f"m_{k}"] = st.session_state.consents[k]
    if toast:
        st.session_state.pending_toast = toast

def set_lang_from_radio():
    st.session_state.lang = "en" if st.session_state.lang_radio.startswith("English") else "hi"

def set_age(is_child):
    st.session_state.is_child = is_child
    if is_child:
        st.session_state.screen = "childVerify"
    else:
        for k, _, _ in OPTIONALS:                # seed consent toggles
            st.session_state[f"c_{k}"] = st.session_state.consents[k]
        st.session_state.screen = "consent"

def go_consent():
    for k, _, _ in OPTIONALS:
        st.session_state[f"c_{k}"] = st.session_state.consents[k]
    st.session_state.screen = "consent"

def sync_consent(k):
    st.session_state.consents[k] = st.session_state[f"c_{k}"]

def sync_manage(k):
    st.session_state.consents[k] = st.session_state[f"m_{k}"]
    on = st.session_state.consents[k]
    st.session_state.pending_toast = f"{'Turned on' if on else 'Turned off'} · {LABELS[k]} · receipt sent"

def finish_consent():
    n = sum(bool(v) for v in st.session_state.consents.values())
    st.session_state.screen = "order"
    st.session_state.pending_toast = (f"Consent saved · {n} optional on · receipt sent"
                                       if n else "Essentials accepted · receipt sent")

def open_dlg(name):
    st.session_state.dialog = name
    if name == "erase":
        st.session_state.erase_req = False

def close_dlg(toast=None):
    st.session_state.dialog = None
    st.session_state.erase_req = False
    if toast:
        st.session_state.pending_toast = toast

def erase_request():
    st.session_state.erase_req = True

def submit_grievance():
    st.session_state.grievance_done = True
    st.session_state.pending_toast = "Grievance #ZG-2048 raised · SLA 7 days"

def leave_grievance():
    st.session_state.grievance_done = False
    st.session_state.screen = "privacy"

def restart():
    for k in ("screen", "lang", "is_child", "consents", "grievance_done", "dialog", "erase_req", "pending_toast"):
        st.session_state.pop(k, None)
    for k, _, _ in OPTIONALS:
        st.session_state.pop(f"c_{k}", None)
        st.session_state.pop(f"m_{k}", None)

# ------------------------------------------------------------------ styling
CSS = """
<style>
.stApp { background: radial-gradient(1200px 600px at 15% -10%, #2a2b31 0, #17181A 55%, #0f1012 100%); }
.block-container { max-width: 500px; background:#fff; border-radius:26px; padding:26px 30px 40px !important;
    margin-top:14px; box-shadow:0 30px 70px rgba(0,0,0,.45); }
#MainMenu, footer, header { visibility:hidden; }
h1,h2,h3,h4,p,div,span,label { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; }
.z-brand { display:flex; align-items:center; gap:11px; margin-bottom:4px; }
.z-logo { width:36px;height:36px;border-radius:10px;background:#E23744;color:#fff;display:grid;place-items:center;
    font-weight:800;font-size:20px;box-shadow:0 4px 14px rgba(226,55,68,.4); }
.z-steps { display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 4px; }
.z-chip { font-size:10.5px;color:#8a9099;background:#f2f3f5;border-radius:20px;padding:4px 10px;font-weight:700;letter-spacing:.3px; }
.z-chip.active { color:#fff;background:#E23744; }
.z-chip.done { color:#fff;background:#1BA672; }
.z-title { font-size:25px;font-weight:800;letter-spacing:-.4px;margin:10px 0 4px;color:#17181A;line-height:1.15; }
.z-sub { color:#5A5F66;font-size:14.5px;line-height:1.5;margin:0 0 8px; }
.z-card { background:#fff;border:1px solid #E7E8EB;border-radius:16px;padding:15px 16px;margin:12px 0;box-shadow:0 8px 22px rgba(20,20,25,.06); }
.z-card.ess { border-color:#f3c6cc;background:#fffafb; }
.z-flat { background:#F5F6F7;border-radius:14px;padding:13px 15px;margin:9px 0; }
.z-badge { display:inline-block;font-size:9.5px;font-weight:800;letter-spacing:.6px;padding:3px 9px;border-radius:20px;text-transform:uppercase; }
.z-badge.req { background:#E23744;color:#fff; } .z-badge.opt { background:#eef0f2;color:#5A5F66; }
.z-note { background:#E7F6EF;border-radius:12px;padding:12px 14px;font-size:12.5px;color:#0e7a52;line-height:1.55;margin:12px 0; }
.z-note.amber { background:#FBEFDA;color:#8a5a10; }
.z-fine { font-size:11.5px;color:#8A9099;text-align:center;line-height:1.5;margin:6px 0; }
.z-muted { color:#8A9099;font-size:12.5px; }
.z-receipt { background:#F5F6F7;border-radius:12px;padding:13px 15px;font-size:12.5px;color:#5A5F66;
    font-family:ui-monospace,Menlo,monospace;line-height:1.9; }
.z-lab b { font-size:14.5px;color:#17181A; } .z-lab span { font-size:12.5px;color:#5A5F66; }
.z-optlabel { font-size:11px;font-weight:800;letter-spacing:.8px;color:#8A9099;text-transform:uppercase;margin:14px 2px 0; }
div.stButton > button { border-radius:13px;font-weight:700;padding:11px 14px;border:1px solid #E7E8EB;font-size:15px; }
div.stButton > button[kind="primary"] { background:#E23744;border:none;box-shadow:0 8px 20px rgba(226,55,68,.28); }
div.stButton > button[kind="primary"]:hover { background:#c92c39; }
div[data-testid="column"] div.stButton > button { padding:6px 10px; }
section[data-testid="stSidebar"] { background:#121315; }
section[data-testid="stSidebar"] * { color:#e7e8eb; }
.ip-ey { font-size:11px;font-weight:800;letter-spacing:1.4px;color:#ff6b74; }
.ip-title { font-size:20px;font-weight:800;margin:6px 0 8px;color:#fff;line-height:1.2; }
.ip-desc { font-size:13.5px;color:#c9cbd1;line-height:1.55; }
.ip-h { font-size:10.5px;font-weight:800;letter-spacing:.8px;color:#8A9099;text-transform:uppercase;margin:16px 0 8px; }
.ip-item { font-size:12.8px;color:#e7e8eb;line-height:1.45;margin-bottom:8px;padding-left:20px;position:relative; }
.ip-item::before { content:"✓";position:absolute;left:0;color:#1BA672;font-weight:800; }
.ip-rule { display:inline-block;background:#E23744;color:#fff;font-size:11px;font-weight:700;padding:5px 11px;border-radius:20px;margin-top:8px; }
</style>
"""

# ------------------------------------------------------------------ dialogs
@st.dialog("Turn off essential data?")
def dlg_essential():
    st.write("This powers taking and delivering your order. **Turn it off and we can't deliver to your live "
             "location — ordering will pause.** We're telling you straight, no guilt-trips.")
    c1, c2 = st.columns(2)
    c1.button("Keep it on", use_container_width=True, key="dlg_ess_keep", on_click=close_dlg)
    c2.button("Turn off anyway", type="primary", use_container_width=True, key="dlg_ess_off",
              on_click=close_dlg, kwargs={"toast": "Ordering paused · you can re-enable anytime"})

@st.dialog("Download my data")
def dlg_download():
    st.write("We'll package everything we hold about you — profile, orders, consents and receipts — and email a secure copy.")
    st.markdown('<div class="z-receipt">Request&nbsp;&nbsp;Access / data export<br>'
                'Format&nbsp;&nbsp;&nbsp;Machine-readable (JSON + PDF)<br>'
                'Delivery&nbsp;within DPDP timeline<br>'
                'Receipt&nbsp;&nbsp;sent to your inbox</div>', unsafe_allow_html=True)
    st.button("Request my copy", type="primary", use_container_width=True, key="dlg_dl_go",
              on_click=close_dlg, kwargs={"toast": "Data export requested · receipt sent"})

@st.dialog("Correct my info")
def dlg_correct():
    name = "Meera M." if st.session_state.is_child else "Ananya M."
    st.text_input("Name", value=name, key="dlg_cf_name")
    st.text_input("Email", value="a.mohapatra@email.com", key="dlg_cf_mail")
    c1, c2 = st.columns(2)
    c1.button("Cancel", use_container_width=True, key="dlg_cf_cancel", on_click=close_dlg)
    c2.button("Save changes", type="primary", use_container_width=True, key="dlg_cf_save",
              on_click=close_dlg, kwargs={"toast": "Details updated · receipt sent"})

@st.dialog("Nominate someone")
def dlg_nominate():
    st.write("Name a person you trust to exercise your data rights if you're unable to (illness or incapacity).")
    st.text_input("Nominee name", placeholder="e.g. Rohan Mohapatra", key="dlg_nm_name")
    st.text_input("Relationship", placeholder="e.g. Sibling", key="dlg_nm_rel")
    c1, c2 = st.columns(2)
    c1.button("Cancel", use_container_width=True, key="dlg_nm_cancel", on_click=close_dlg)
    c2.button("Add nominee", type="primary", use_container_width=True, key="dlg_nm_save",
              on_click=close_dlg, kwargs={"toast": "Nominee added · they can act if you can't"})

@st.dialog("Erase my data")
def dlg_erase():
    if not st.session_state.erase_req:
        st.write("This deletes your account and personal data — **except records the law requires us to keep** "
                 "(like tax invoices). This can't be undone.")
        st.markdown('<div class="z-note amber">You\'ll get a confirmation and a receipt. Anything retained is only '
                    'what a legal obligation demands, and only for as long as required.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("Cancel", use_container_width=True, key="dlg_er_cancel", on_click=close_dlg)
        c2.button("Request erasure", type="primary", use_container_width=True, key="dlg_er_go", on_click=erase_request)
    else:
        st.success("Erasure requested")
        st.markdown('<div class="z-receipt">Request&nbsp;&nbsp;Erasure (account + data)<br>'
                    'Status&nbsp;&nbsp;&nbsp;In progress<br>'
                    'Retained&nbsp;tax invoices only (legal)<br>'
                    'Receipt&nbsp;&nbsp;sent to your inbox</div>', unsafe_allow_html=True)
        st.button("Done", type="primary", use_container_width=True, key="dlg_er_done",
                  on_click=close_dlg, kwargs={"toast": "Erasure request logged · receipt sent"})

@st.dialog("Full privacy notice")
def dlg_notice():
    st.markdown(
        "**Who we are:** Zomato is the Data Fiduciary for your data.\n\n"
        "**What & why (itemised):** Location — to deliver, only while ordering. Payment — to charge you. "
        "Contact — to reach you about your order. Optional uses are listed separately and off by default.\n\n"
        "**Who sees it:** delivery partner, payment processor, restaurant. We don't sell personal data.\n\n"
        "**Your rights:** access, correction, erasure, nomination, grievance — all in Privacy & Data.\n\n"
        "**Contact:** Data Protection Officer · dpo@zomato.com. You may also complain to the Data Protection Board of India.")
    st.button("Close", type="primary", use_container_width=True, key="dlg_notice_close", on_click=close_dlg)

DIALOGS = {"essential": dlg_essential, "download": dlg_download, "correct": dlg_correct,
           "nominate": dlg_nominate, "erase": dlg_erase, "notice": dlg_notice}

# ------------------------------------------------------------------ chrome
def render_header():
    cur = STEP[st.session_state.screen]
    st.markdown('<div class="z-brand"><div class="z-logo">z</div>'
                '<div><div style="font-weight:800;font-size:15px">Zomato × DPDP — Consent, Clearly</div>'
                '<div class="z-muted" style="font-size:11.5px">Clickable prototype · aligned to the DPDP Act 2023 &amp; Rules 2025</div></div></div>',
                unsafe_allow_html=True)
    chips = ""
    for n in (1, 2, 3, 4):
        cls = "done" if n < cur else ("active" if n == cur else "")
        chips += f'<span class="z-chip {cls}">{n} · {STEP_NAMES[n].title()}</span>'
    st.markdown(f'<div class="z-steps">{chips}</div><div style="height:6px"></div>', unsafe_allow_html=True)

def render_sidebar():
    t, d, bullets, rule = INFO[st.session_state.screen]
    s = STEP[st.session_state.screen]
    html = f'<div class="ip-ey">STEP {s} · {STEP_NAMES[s]}</div><div class="ip-title">{t}</div><div class="ip-desc">{d}</div>'
    if bullets:
        html += '<div class="ip-h">DPDP alignment</div>'
        for b in bullets:
            html += f'<div class="ip-item">{b}</div>'
        if rule:
            html += f'<span class="ip-rule">{rule}</span>'
    st.sidebar.markdown(html, unsafe_allow_html=True)
    st.sidebar.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.sidebar.button("↻ Restart prototype", use_container_width=True, key="restart", on_click=restart)

def nav_row(title, desc, target, key, icon="›"):
    with st.container(border=True):
        c1, c2 = st.columns([6, 1])
        c1.markdown(f'<div class="z-lab"><b>{title}</b><br><span>{desc}</span></div>', unsafe_allow_html=True)
        c2.button(icon, key=key, use_container_width=True, on_click=nav, args=(target,))

# ------------------------------------------------------------------ screens
def sc_splash():
    st.markdown('<div class="z-title" style="font-size:30px">zomato</div>'
                '<div class="z-sub">Order food &amp; more, near you.</div>'
                '<div class="z-note">New consent experience, redesigned for India\'s Digital Personal '
                'Data Protection rules. Tap through the happy path — the sidebar explains the DPDP thinking on every screen.</div>',
                unsafe_allow_html=True)
    st.button("Get started", type="primary", use_container_width=True, key="sp_start", on_click=nav, args=("language",))

def sc_language():
    st.markdown('<div class="z-title">Choose your language</div>'
                '<div class="z-sub">Your consent notice and controls will be shown in the language you pick.</div>',
                unsafe_allow_html=True)
    st.radio("Language", ["English", "हिन्दी (Hindi)"], index=0 if st.session_state.lang == "en" else 1,
             key="lang_radio", label_visibility="collapsed", on_change=set_lang_from_radio)
    st.markdown('<div class="z-flat" style="text-align:center"><span class="z-muted">+ 20 more Indian languages available</span><br>'
                '<span class="z-muted" style="font-size:11px">DPDP: notice must be offered in English &amp; all 22 scheduled languages</span></div>',
                unsafe_allow_html=True)
    st.button("Continue", type="primary", use_container_width=True, key="lang_cont", on_click=nav, args=("age",))

def sc_age():
    st.markdown('<div class="z-title">One quick check</div>'
                '<div class="z-sub">India\'s DPDP rules give extra protection to anyone under 18. Please confirm your age — '
                'we only use this to protect you, nothing else.</div>', unsafe_allow_html=True)
    st.button("I'm 18 or older", type="primary", use_container_width=True, key="age_adult", on_click=set_age, args=(False,))
    st.button("I'm under 18", use_container_width=True, key="age_child", on_click=set_age, args=(True,))
    st.markdown('<div class="z-fine">Self-declared, with risk-based re-checks. If needed, we verify a parent through '
                'DigiLocker — never by collecting more than required.</div>', unsafe_allow_html=True)

def sc_childVerify():
    st.markdown('<span class="z-badge req">Under-18 account</span>'
                '<div class="z-title" style="margin-top:8px">We need a parent\'s OK</div>'
                '<div class="z-sub">Before using any of your data, a parent or guardian must approve. Choose how to verify them:</div>',
                unsafe_allow_html=True)
    nav_row("Verify via DigiLocker", "Aadhaar-linked, Government of India", "childDone", "cv_digi")
    nav_row("My parent already uses Zomato", "Approve from their verified adult account", "childDone", "cv_parent")
    st.markdown('<div class="z-note">Only a parent\'s age &amp; identity are checked — we don\'t over-collect. (DPDP Rule 10)</div>',
                unsafe_allow_html=True)

def sc_childDone():
    st.markdown('<div class="z-title">Parent verified: Sunita M.</div>'
                '<div class="z-sub">Verifiable parental consent granted. Here\'s how Meera\'s account is protected:</div>'
                '<div class="z-note">✓ No behavioural tracking or profiling<br>✓ No targeted or personalised advertising<br>'
                '✓ Only data essential to fulfil an order is used</div>', unsafe_allow_html=True)
    st.button("Continue safely", type="primary", use_container_width=True, key="cd_cont", on_click=go_consent)

def sc_consent():
    t = I18N[st.session_state.lang]
    st.markdown(f'<div class="z-title">{t["title"]}</div><div class="z-sub">{t["sub"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="z-card ess"><span class="z-badge req">Required</span>'
                f'<div style="margin-top:8px"><b style="font-size:15px">{t["ess"]}</b><br>'
                f'<span class="z-muted">{t["esssub"]}</span></div>'
                f'<div class="z-muted" style="margin-top:8px;font-size:12px">Needed to provide the service you asked for. '
                f'Itemised, not bundled with anything optional.</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="z-optlabel">{t["optlabel"]}</div>', unsafe_allow_html=True)
    if st.session_state.is_child:
        st.markdown('<div class="z-note">Personalisation, marketing and contact access are switched off for under-18 '
                    'accounts and can\'t be turned on. (DPDP Rule 10)</div>', unsafe_allow_html=True)
    else:
        for k, label, desc in OPTIONALS:
            st.session_state.setdefault(f"c_{k}", st.session_state.consents[k])
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                c1.markdown(f'<div class="z-lab"><b>{label}</b><br><span>{desc}</span></div>', unsafe_allow_html=True)
                c2.toggle(label, key=f"c_{k}", label_visibility="collapsed", on_change=sync_consent, args=(k,))
    st.button(t["cont"], type="primary", use_container_width=True, key="c_cont", on_click=finish_consent)
    st.button("View full notice & who sees your data", use_container_width=True, key="c_notice",
              on_click=open_dlg, args=("notice",))
    st.markdown('<div class="z-fine">Withdrawing is as easy as giving — one tap, anytime, in Privacy &amp; Data.</div>',
                unsafe_allow_html=True)

def sc_order():
    name = "Meera" if st.session_state.is_child else "Ananya"
    st.markdown(f'<div class="z-title" style="font-size:22px">Order placed 🎉</div>'
                f'<div class="z-sub">Delivering to {name} · HSR Layout</div>'
                f'<div class="z-card"><div style="display:flex;justify-content:space-between">'
                f'<b>Paradise Biryani · ₹480</b><span class="z-badge" style="background:#E7F6EF;color:#0e7a52">On the way</span></div>'
                f'<div class="z-muted" style="margin-top:8px">Arriving in <b style="color:#17181A">28 min</b> · '
                f'location used only while your order is active.</div></div>', unsafe_allow_html=True)
    nav_row("Go to your profile", "Manage account, privacy & data", "profile", "or_profile")
    st.markdown('<div class="z-fine">Tip: your privacy controls are just 2 taps away — Profile → Privacy &amp; Data.</div>',
                unsafe_allow_html=True)

def sc_profile():
    name = "Meera M." if st.session_state.is_child else "Ananya M."
    av = "M" if st.session_state.is_child else "A"
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">'
                f'<div style="width:50px;height:50px;border-radius:50%;background:#E23744;color:#fff;display:grid;'
                f'place-items:center;font-weight:800;font-size:20px">{av}</div>'
                f'<div><b style="font-size:17px">{name}</b><br><span class="z-muted">+91 98•••••210 · verified</span></div></div>',
                unsafe_allow_html=True)
    st.button("‹ Back", key="pf_back", on_click=nav, args=("order",))
    st.caption("Your orders  ·  Payments  ·  Help & support")
    nav_row("🔒 Privacy & Data", "Consents, your rights, grievance", "privacy", "pf_privacy")

def sc_privacy():
    on = sum(bool(v) for v in st.session_state.consents.values())
    off = 0 if st.session_state.is_child else (len(OPTIONALS) - on)
    count = "1 required · minor-protected" if st.session_state.is_child else f"1 required · {on} on · {off} off"
    st.markdown('<div class="z-title">Privacy &amp; Data</div>'
                '<div class="z-sub">Everything about your data in one place. See it, control it, or ask us to act on it.</div>',
                unsafe_allow_html=True)
    nav_row("Consents &amp; purposes", count, "manage", "pv_manage")
    nav_row("Your rights", "Download · Correct · Erase · Nominate", "rights", "pv_rights")
    nav_row("Data &amp; activity", "What we hold · retention · who sees it", "data", "pv_data")
    nav_row("Grievance", "Raise &amp; track a concern · SLA 7 days", "grievance", "pv_griev")
    st.markdown('<div class="z-note">Every change here is timestamped and a receipt is sent to you — your record and ours.</div>',
                unsafe_allow_html=True)
    st.button("‹ Back to profile", key="pv_back", on_click=nav, args=("profile",))

def sc_manage():
    st.markdown('<div class="z-title">Consents &amp; purposes</div>'
                '<div class="z-sub">Turn any optional use on or off. Off is off — instantly.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        c1, c2 = st.columns([6, 1])
        c1.markdown('<div class="z-lab"><b>Take &amp; deliver your order</b><br>'
                    '<span>Location while ordering · Payment · Contact</span></div>', unsafe_allow_html=True)
        c2.button("🔒", key="m_ess", use_container_width=True, on_click=open_dlg, args=("essential",))
    if st.session_state.is_child:
        st.markdown('<div class="z-note">Optional uses are disabled for under-18 accounts (no tracking or ads).</div>',
                    unsafe_allow_html=True)
    else:
        for k, label, desc in OPTIONALS:
            st.session_state.setdefault(f"m_{k}", st.session_state.consents[k])
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                c1.markdown(f'<div class="z-lab"><b>{label}</b><br><span>{desc}</span></div>', unsafe_allow_html=True)
                c2.toggle(label, key=f"m_{k}", label_visibility="collapsed", on_change=sync_manage, args=(k,))
    st.markdown('<div class="z-fine">Withdrawal parity: turning a use off is exactly one tap, the same as turning it on.</div>',
                unsafe_allow_html=True)
    st.button("‹ Back", key="m_back", on_click=nav, args=("privacy",))

def sc_rights():
    st.markdown('<div class="z-title">Your rights</div>'
                '<div class="z-sub">Under the DPDP Act you can act on your data anytime. Pick one:</div>', unsafe_allow_html=True)
    st.button("⬇  Download my data — right to access", use_container_width=True, key="r_dl", on_click=open_dlg, args=("download",))
    st.button("✎  Correct my info", use_container_width=True, key="r_correct", on_click=open_dlg, args=("correct",))
    st.button("👤  Nominate someone", use_container_width=True, key="r_nom", on_click=open_dlg, args=("nominate",))
    st.button("🗑  Erase my data — right to erasure", use_container_width=True, key="r_erase", on_click=open_dlg, args=("erase",))
    st.button("‹ Back", key="r_back", on_click=nav, args=("privacy",))

def sc_data():
    st.markdown('<div class="z-title">Data &amp; activity</div>'
                '<div class="z-sub">A plain-language summary of what we hold and why — the right to access, always on.</div>',
                unsafe_allow_html=True)
    rows = [("Contact & account", "Name, phone, email", "kept while active"),
            ("Order history", "Restaurants, items, amounts", "24 months"),
            ("Location", "Only while an order is active", "not stored after"),
            ("Payment", "Tokenised — we don't store card numbers", "per RBI rules")]
    for a, b, c in rows:
        st.markdown(f'<div class="z-flat"><div style="display:flex;justify-content:space-between">'
                    f'<div><b>{a}</b><br><span class="z-muted">{b}</span></div>'
                    f'<span class="z-muted">{c}</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="z-note"><b>Who sees it:</b> delivery partner (your location, during delivery), '
                'payment processor (to charge you), and the restaurant (your order). No selling of personal data.</div>',
                unsafe_allow_html=True)
    st.button("‹ Back", key="d_back", on_click=nav, args=("privacy",))

def sc_grievance():
    st.markdown('<div class="z-title">Grievance</div>', unsafe_allow_html=True)
    if st.session_state.grievance_done:
        st.success("Concern raised")
        st.markdown('<div class="z-receipt">Ticket&nbsp;&nbsp;#ZG-2048<br>Status&nbsp;&nbsp;Pending · assigned to DPO<br>'
                    'SLA&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Resolve by +7 days<br>DPO&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dpo@zomato.com</div>',
                    unsafe_allow_html=True)
        st.button("Back to Privacy & Data", type="primary", use_container_width=True, key="g_back2", on_click=leave_grievance)
    else:
        st.markdown('<div class="z-sub">Something wrong with how we handle your data? Tell our Data Protection Officer.</div>',
                    unsafe_allow_html=True)
        st.selectbox("What's it about?", ["Consent not honoured", "Data I didn't expect being used",
                     "Access / download issue", "Erasure request", "Other"], key="g_cat")
        st.text_area("Describe it", placeholder="Tell us what happened…", key="g_txt")
        st.button("Submit to DPO", type="primary", use_container_width=True, key="g_submit", on_click=submit_grievance)
        st.markdown('<div class="z-fine">Published SLA: acknowledged instantly, resolved within 7 days.</div>',
                    unsafe_allow_html=True)
        st.button("‹ Back", key="g_back", on_click=nav, args=("privacy",))

SCREENS = {"splash": sc_splash, "language": sc_language, "age": sc_age, "childVerify": sc_childVerify,
           "childDone": sc_childDone, "consent": sc_consent, "order": sc_order, "profile": sc_profile,
           "privacy": sc_privacy, "manage": sc_manage, "rights": sc_rights, "data": sc_data, "grievance": sc_grievance}

def main():
    init()
    st.markdown(CSS, unsafe_allow_html=True)
    if st.session_state.pending_toast:
        st.toast(st.session_state.pending_toast, icon="✅")
        st.session_state.pending_toast = None
    render_sidebar()
    render_header()
    if st.session_state.dialog in DIALOGS:
        DIALOGS[st.session_state.dialog]()
    SCREENS[st.session_state.screen]()

main()
