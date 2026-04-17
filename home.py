# home.py - CareerBridge AI — Design ULTRA PREMIUM Futuriste
import streamlit as st


def render_home():
    """Page d'accueil ultra premium — hackathon winner level"""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ═══════════════════════════════════════
       BASE & RESET
    ═══════════════════════════════════════ */
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ═══════════════════════════════════════
       BACKGROUND ANIMÉ
    ═══════════════════════════════════════ */
    .stApp {
        background: #020817;
        overflow-x: hidden;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: -40%;
        left: -20%;
        width: 80%;
        height: 80%;
        background: radial-gradient(ellipse, rgba(99,102,241,0.18) 0%, transparent 65%);
        pointer-events: none;
        z-index: 0;
        animation: driftA 12s ease-in-out infinite alternate;
    }

    .stApp::after {
        content: '';
        position: fixed;
        bottom: -30%;
        right: -15%;
        width: 70%;
        height: 70%;
        background: radial-gradient(ellipse, rgba(139,92,246,0.14) 0%, transparent 65%);
        pointer-events: none;
        z-index: 0;
        animation: driftB 15s ease-in-out infinite alternate;
    }

    @keyframes driftA {
        from { transform: translate(0, 0) scale(1); }
        to   { transform: translate(6%, 8%) scale(1.08); }
    }
    @keyframes driftB {
        from { transform: translate(0, 0) scale(1); }
        to   { transform: translate(-5%, -6%) scale(1.06); }
    }

    /* ═══════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════ */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 2px; }

    /* ═══════════════════════════════════════
       BADGE PULSE
    ═══════════════════════════════════════ */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 100px;
        padding: 6px 18px;
        font-size: 12px;
        font-weight: 500;
        color: #a5b4fc;
        margin-bottom: 1.5rem;
        letter-spacing: 0.02em;
    }

    .badge-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #6366f1;
        box-shadow: 0 0 0 0 rgba(99,102,241,0.6);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(99,102,241,0.7); }
        70%  { box-shadow: 0 0 0 8px rgba(99,102,241,0); }
        100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
    }

    /* ═══════════════════════════════════════
       HERO
    ═══════════════════════════════════════ */
    .hero-wrapper {
        position: relative;
        padding: 5rem 2rem 4rem;
        text-align: center;
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .hero-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -60%);
        width: 600px;
        height: 300px;
        background: radial-gradient(ellipse, rgba(99,102,241,0.22) 0%, transparent 70%);
        pointer-events: none;
        filter: blur(20px);
        animation: glowPulse 4s ease-in-out infinite;
    }

    @keyframes glowPulse {
        0%, 100% { opacity: 0.7; transform: translate(-50%, -60%) scale(1); }
        50%       { opacity: 1;   transform: translate(-50%, -60%) scale(1.08); }
    }

    .hero-eyebrow {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.18em;
        color: #6366f1;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: clamp(2.2rem, 5vw, 3.4rem);
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -0.03em;
        color: #f1f5f9;
        margin-bottom: 0.6rem;
    }

    .hero-title .brand {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 40%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 20px rgba(99,102,241,0.5));
    }

    .hero-subtitle {
        font-size: 16px;
        font-weight: 400;
        color: #64748b;
        line-height: 1.7;
        max-width: 520px;
        margin: 0 auto 2.5rem;
    }

    .hero-subtitle strong {
        color: #94a3b8;
        font-weight: 500;
    }

    /* ═══════════════════════════════════════
       SÉPARATEUR LUMINEUX
    ═══════════════════════════════════════ */
    .luminous-divider {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(99,102,241,0.4) 30%,
            rgba(139,92,246,0.6) 50%,
            rgba(99,102,241,0.4) 70%,
            transparent 100%
        );
        margin: 0.5rem 0 2.5rem;
    }

    /* ═══════════════════════════════════════
       SECTION LABEL
    ═══════════════════════════════════════ */
    .section-label {
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6366f1;
        margin-bottom: 1rem;
        padding-left: 2rem;
    }

    /* ═══════════════════════════════════════
       FEATURE CARDS — GLASS
    ═══════════════════════════════════════ */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
        padding: 0 2rem 2rem;
    }

    .feature-card {
        position: relative;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 20px;
        padding: 2rem 1.75rem;
        overflow: hidden;
        transition: transform 0.35s cubic-bezier(.22,.68,0,1.2),
                    box-shadow 0.35s ease,
                    border-color 0.35s ease;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .feature-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(99,102,241,0.06) 0%, transparent 60%);
        border-radius: 20px;
        opacity: 0;
        transition: opacity 0.35s ease;
    }

    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(99,102,241,0.45);
        box-shadow:
            0 20px 50px rgba(99,102,241,0.2),
            0 0 0 1px rgba(99,102,241,0.12) inset,
            0 0 30px rgba(99,102,241,0.08) inset;
    }

    .feature-card:hover::before { opacity: 1; }

    .feature-card-glow {
        position: absolute;
        top: -30px;
        right: -30px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.35s ease;
    }

    .feature-card:hover .feature-card-glow { opacity: 1; }

    .feature-icon-wrap {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 1.25rem;
        transition: background 0.3s ease, border-color 0.3s ease;
    }

    .feature-card:hover .feature-icon-wrap {
        background: rgba(99,102,241,0.25);
        border-color: rgba(99,102,241,0.4);
    }

    .feature-title {
        font-size: 15px;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .feature-desc {
        font-size: 13px;
        color: #475569;
        line-height: 1.65;
    }

    /* ═══════════════════════════════════════
       STATS
    ═══════════════════════════════════════ */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        padding: 0 2rem 2.5rem;
    }

    .stat-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99,102,241,0.12);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        backdrop-filter: blur(12px);
    }

    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99,102,241,0.35);
        box-shadow: 0 12px 30px rgba(99,102,241,0.15);
    }

    .stat-number {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #818cf8, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        font-size: 10px;
        font-weight: 600;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
    }

    /* ═══════════════════════════════════════
       AGENTS PILLS
    ═══════════════════════════════════════ */
    .agents-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 0 2rem 2.5rem;
    }

    .agent-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 100px;
        padding: 7px 16px;
        font-size: 12.5px;
        font-weight: 500;
        color: #a5b4fc;
        transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease;
        cursor: default;
    }

    .agent-pill:hover {
        background: rgba(99,102,241,0.18);
        border-color: rgba(99,102,241,0.45);
        color: #c7d2fe;
    }

    .agent-num {
        font-size: 10px;
        font-weight: 700;
        color: #6366f1;
        background: rgba(99,102,241,0.15);
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ═══════════════════════════════════════
       TESTIMONIALS
    ═══════════════════════════════════════ */
    .testimonial-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 14px;
        padding: 0 2rem 2.5rem;
    }

    .testimonial-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        backdrop-filter: blur(12px);
    }

    .testimonial-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99,102,241,0.3);
        box-shadow: 0 15px 35px rgba(99,102,241,0.12);
    }

    .t-stars { color: #fbbf24; font-size: 12px; margin-bottom: 10px; letter-spacing: 2px; }

    .t-text {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.65;
        margin-bottom: 14px;
        font-style: italic;
    }

    .t-author-wrap { display: flex; align-items: center; gap: 10px; }

    .t-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }

    .t-name { font-size: 13px; font-weight: 600; color: #e2e8f0; }
    .t-role { font-size: 11px; color: #475569; }

    /* ═══════════════════════════════════════
       BOUTON CTA STREAMLIT
    ═══════════════════════════════════════ */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #818cf8 100%) !important;
        color: white !important;
        border-radius: 100px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: none !important;
        letter-spacing: -0.01em !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 0 30px rgba(99,102,241,0.35), 0 4px 15px rgba(99,102,241,0.25) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.015) !important;
        box-shadow: 0 0 50px rgba(99,102,241,0.5), 0 8px 25px rgba(99,102,241,0.35) !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* ═══════════════════════════════════════
       CTA SECTION WRAPPER
    ═══════════════════════════════════════ */
    .cta-section {
        padding: 0 2rem 1rem;
        max-width: 480px;
        margin: 0 auto;
    }

    /* ═══════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════ */
    .footer {
        text-align: center;
        padding: 2rem 2rem 3rem;
        margin-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.04);
    }

    .footer-inner {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #334155;
        font-weight: 500;
    }

    .footer-dot { width: 3px; height: 3px; border-radius: 50%; background: #6366f1; }

    /* ═══════════════════════════════════════
       ANIMATIONS APPARITION
    ═══════════════════════════════════════ */
    .fade-up {
        animation: fadeUp 0.7s cubic-bezier(.22,.68,0,1.2) both;
    }

    .fade-up-1 { animation-delay: 0.05s; }
    .fade-up-2 { animation-delay: 0.15s; }
    .fade-up-3 { animation-delay: 0.25s; }
    .fade-up-4 { animation-delay: 0.35s; }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ═══════════════════════════════════════
       RESPONSIVE
    ═══════════════════════════════════════ */
    @media (max-width: 768px) {
        .hero-wrapper { padding: 3.5rem 1rem 2.5rem; }
        .feature-grid, .stats-grid, .testimonial-grid { padding: 0 1rem 2rem; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        .agents-wrap { padding: 0 1rem 2rem; }
        .section-label { padding-left: 1rem; }
        .cta-section { padding: 0 1rem 1rem; }
        .footer { padding: 1.5rem 1rem 2.5rem; }
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrapper fade-up fade-up-1">
        <div class="hero-glow"></div>

        <div class="hero-eyebrow">Propulsé par l'intelligence artificielle</div>

        <div class="hero-badge">
            <div class="badge-dot"></div>
            Orientation intelligente · Marché marocain 2024
        </div>

        <div class="hero-title">
            Trouvez votre voie<br>avec <span class="brand">CareerBridge AI</span>
        </div>

        <p class="hero-subtitle">
            Un conseiller propulsé par <strong>6 agents IA spécialisés</strong>,
            conçu exclusivement pour les étudiants marocains — données réelles,
            recommandations sur-mesure.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="luminous-divider"></div>', unsafe_allow_html=True)

    # ── FEATURES ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label fade-up fade-up-2">Fonctionnalités</div>', unsafe_allow_html=True)

    features = [
        ("🎓", "Orientation personnalisée",
         "Recommandations adaptées à votre profil, vos passions et vos compétences uniques."),
        ("🤖", "6 agents IA spécialisés",
         "Guardrail · Profiler · Retriever · Scorer · Generator · Evaluator — un pipeline complet."),
        ("📊", "Données marché réelles",
         "Salaires, écoles, tendances 2024 — toutes les infos pour choisir avec confiance."),
    ]

    st.markdown('<div class="feature-grid fade-up fade-up-2">', unsafe_allow_html=True)
    for icon, title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-card-glow"></div>
            <div class="feature-icon-wrap">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── STATS ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label fade-up fade-up-3">Chiffres clés</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stats-grid fade-up fade-up-3">
        <div class="stat-card">
            <div class="stat-number">6+</div>
            <div class="stat-label">Secteurs analysés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">105k+</div>
            <div class="stat-label">Postes disponibles</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">+17%</div>
            <div class="stat-label">Croissance moyenne</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">14k</div>
            <div class="stat-label">MAD salaire Bac+5</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AGENTS ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label fade-up fade-up-3">Pipeline IA</div>', unsafe_allow_html=True)
    agents = ["Guardrail", "Profiler", "Retriever", "Scorer", "Generator", "Evaluator"]
    pills_html = '<div class="agents-wrap fade-up fade-up-3">'
    for i, agent in enumerate(agents, 1):
        pills_html += f'<div class="agent-pill"><span class="agent-num">{i}</span>{agent}</div>'
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)

    # ── TESTIMONIALS ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label fade-up fade-up-4">Ce qu\'ils en disent</div>', unsafe_allow_html=True)
    testimonials = [
        ("YE", "⭐⭐⭐⭐⭐",
         "Grâce à CareerBridge AI, j'ai trouvé ma voie dans la data science. Les recommandations étaient parfaitement adaptées à mon profil !",
         "Youssef El Mansouri", "Data Scientist · Casablanca"),
        ("FZ", "⭐⭐⭐⭐⭐",
         "L'interface est magnifique et les conseils très précis. J'ai orienté mon fils vers la cybersécurité sereinement.",
         "Fatima Zahra", "Parent d'élève · Rabat"),
    ]

    st.markdown('<div class="testimonial-grid fade-up fade-up-4">', unsafe_allow_html=True)
    for initials, stars, text, name, role in testimonials:
        st.markdown(f"""
        <div class="testimonial-card">
            <div class="t-stars">{stars}</div>
            <div class="t-text">"{text}"</div>
            <div class="t-author-wrap">
                <div class="t-avatar">{initials}</div>
                <div>
                    <div class="t-name">{name}</div>
                    <div class="t-role">{role}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── CTA ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="cta-section">', unsafe_allow_html=True)
    if st.button("🚀 Commencer mon orientation", use_container_width=True, type="primary"):
        st.session_state.page = "Chat"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        <div class="footer-inner">
            <span>CareerBridge AI</span>
            <div class="footer-dot"></div>
            <span>L'orientation intelligente pour les étudiants marocains</span>
            <div class="footer-dot"></div>
            <span>🇲🇦</span>
        </div>
    </div>
    """, unsafe_allow_html=True)