import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64
import textwrap
import streamlit.components.v1 as components
import pydeck as pdk
from io import BytesIO
from PIL import Image

# =========================================================
# Page Setup
# =========================================================
st.set_page_config(
    page_title="Nervenschutz AI",
    page_icon="NS",
    layout="wide"
)

# =========================================================
# Helper Functions
# =========================================================
def image_to_base64(image_path, normalize_icon=False):
    if normalize_icon:
        with Image.open(image_path).convert("RGBA") as image:
            alpha_bbox = image.getchannel("A").getbbox()
            if alpha_bbox:
                image = image.crop(alpha_bbox)

            icon_canvas_size = 96
            icon_artwork_size = 72
            image.thumbnail((icon_artwork_size, icon_artwork_size), Image.Resampling.LANCZOS)

            canvas = Image.new("RGBA", (icon_canvas_size, icon_canvas_size), (255, 255, 255, 0))
            x = (icon_canvas_size - image.width) // 2
            y = (icon_canvas_size - image.height) // 2
            canvas.paste(image, (x, y), image)

            image_buffer = BytesIO()
            canvas.save(image_buffer, format="PNG")
            return base64.b64encode(image_buffer.getvalue()).decode()

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def get_icon_html(icon_path, fallback_text):
    path = Path(icon_path)
    if path.exists():
        icon_base64 = image_to_base64(path, normalize_icon=True)
        return f"""
        <img src="data:image/png;base64,{icon_base64}"
             class="stage-icon">
        """
    return f"""
    <div class="stage-icon-fallback">
        {fallback_text}
    </div>
    """


# =========================================================
# Styling
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #021738;
    color: #EAF2FF;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    color: #EAF2FF;
}

h1 {
    letter-spacing: 0.6px;
    text-shadow: 0 0 22px rgba(40, 215, 255, 0.18);
}

h2, h3 {
    letter-spacing: 0.3px;
}

[data-testid="stMetricValue"] {
    color: #28D7FF;
}

[data-testid="stMetricLabel"] {
    color: #EAF2FF;
}

section[data-testid="stSidebar"] {
    background-color: #0D1B2F;
    border-right: 1px solid #1B3557;
}

div[data-testid="stDataFrame"] {
    background-color: #0D1B2F;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.96), rgba(7, 17, 31, 0.96));
    border: 1px solid #1B3557;
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: inset 0 1px 0 rgba(234, 242, 255, 0.06), 0 0 24px rgba(40, 215, 255, 0.08);
}

.signal-box {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.98), rgba(7, 17, 31, 0.98));
    border: 1px solid #1B3557;
    border-left: 6px solid #EF4444;
    padding: 18px;
    border-radius: 8px;
    color: #EAF2FF;
    box-shadow: 0 0 26px rgba(239, 68, 68, 0.14);
}

.info-box {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.96), rgba(7, 17, 31, 0.96));
    border: 1px solid #1B3557;
    padding: 18px;
    border-radius: 8px;
    color: #EAF2FF;
    box-shadow: inset 0 1px 0 rgba(234, 242, 255, 0.06), 0 0 24px rgba(40, 215, 255, 0.06);
}

.module-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin: 14px 0 22px;
}

.cyber-card {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.96), rgba(7, 17, 31, 0.98));
    border: 1px solid #1B3557;
    border-top: 1px solid #28D7FF;
    border-radius: 8px;
    padding: 16px;
    min-height: 118px;
    box-shadow: inset 0 1px 0 rgba(234, 242, 255, 0.06), 0 0 24px rgba(40, 215, 255, 0.08);
}

.cyber-card-title {
    color: #28D7FF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.cyber-card-value {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 5px;
}

.cyber-card-copy {
    color: #AFC2D8;
    font-size: 12px;
    line-height: 1.45;
}

.flow-strip {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 8px;
    margin: 12px 0 20px;
}

.flow-step {
    position: relative;
    background: #07111F;
    border: 1px solid #233B5E;
    border-radius: 8px;
    padding: 12px;
    min-height: 96px;
}

.flow-step::after {
    content: "";
    position: absolute;
    top: 50%;
    right: -9px;
    width: 10px;
    height: 2px;
    background: #28D7FF;
    box-shadow: 0 0 12px rgba(40, 215, 255, 0.7);
}

.flow-step:last-child::after {
    display: none;
}

.flow-index {
    color: #67FFE1;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 8px;
}

.flow-title {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 6px;
}

.flow-copy {
    color: #AFC2D8;
    font-size: 11px;
    line-height: 1.35;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 78px;
    height: 24px;
    padding: 0 10px;
    border: 1px solid #28D7FF;
    border-radius: 999px;
    color: #28D7FF;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    background: rgba(40, 215, 255, 0.08);
}

.status-chip.high {
    border-color: #F2A93B;
    color: #F2A93B;
    background: rgba(242, 169, 59, 0.09);
}

.status-chip.critical {
    border-color: #EF4444;
    color: #EF4444;
    background: rgba(239, 68, 68, 0.1);
}

.playbook-card {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.97), rgba(7, 17, 31, 0.97));
    border: 1px solid #233B5E;
    border-left: 4px solid #67FFE1;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 0 22px rgba(103, 255, 225, 0.06);
}

.playbook-meta {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-top: 12px;
}

.mini-label {
    color: #7E94AA;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

.mini-value {
    color: #EAF2FF;
    font-size: 12px;
    font-weight: 700;
    margin-top: 4px;
}

.scenario-hero {
    background: linear-gradient(135deg, rgba(13, 27, 47, 0.98), rgba(7, 17, 31, 0.98));
    border: 1px solid #28D7FF;
    border-radius: 8px;
    padding: 22px;
    margin: 8px 0 18px;
    box-shadow: 0 0 28px rgba(40, 215, 255, 0.12);
}

.scenario-kicker {
    color: #67FFE1;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.scenario-title {
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 800;
    margin-top: 6px;
}

.scenario-copy {
    color: #AFC2D8;
    font-size: 14px;
    line-height: 1.55;
    margin-top: 8px;
    max-width: 900px;
}

.scenario-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0 22px;
}

.scenario-step {
    background: #07111F;
    border: 1px solid #233B5E;
    border-top: 2px solid #28D7FF;
    border-radius: 8px;
    padding: 13px;
    min-height: 132px;
}

.scenario-step-number {
    color: #67FFE1;
    font-size: 11px;
    font-weight: 800;
}

.scenario-step-title {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    margin-top: 8px;
}

.scenario-step-copy {
    color: #AFC2D8;
    font-size: 11px;
    line-height: 1.4;
    margin-top: 8px;
}

@media (max-width: 900px) {
    .module-grid,
    .flow-strip,
    .playbook-meta,
    .scenario-grid {
        grid-template-columns: 1fr;
    }

    .flow-step::after {
        display: none;
    }
}

.progress-panel {
    background: #111827;
    border: 1px solid #233B5E;
    border-radius: 18px;
    padding: 24px 26px;
    margin-top: 10px;
    margin-bottom: 28px;
}

.progress-title {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.4px;
    margin-bottom: 18px;
}

.progress-top {
    display: flex;
    align-items: center;
    gap: 26px;
    margin-bottom: 24px;
}

.progress-donut {
    width: 118px;
    height: 118px;
    border-radius: 50%;
    background: conic-gradient(#28D7FF var(--progress), #26364D 0deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 28px rgba(40, 215, 255, 0.18);
}

.progress-donut-inner {
    width: 82px;
    height: 82px;
    background: #111827;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-percent {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 800;
}

.progress-copy {
    color: #AFC2D8;
    font-size: 13px;
    line-height: 1.45;
    max-width: 720px;
}

.progress-bar-shell {
    width: 100%;
    height: 24px;
    border: 2px solid #35516F;
    border-radius: 6px;
    padding: 3px;
    background: #0A1322;
    margin-bottom: 28px;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #39E6FF, #2F80ED);
    position: relative;
}

.progress-bar-label {
    position: absolute;
    right: -48px;
    top: -2px;
    color: #EAF2FF;
    font-size: 12px;
    font-weight: 700;
}

.stage-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    position: relative;
    margin-top: 8px;
}

.stage-line {
    position: absolute;
    top: 24px;
    left: 7%;
    right: 7%;
    height: 3px;
    background: #34526F;
    z-index: 0;
}

.stage-line-fill {
    position: absolute;
    top: 24px;
    left: 7%;
    height: 3px;
    background: linear-gradient(90deg, #67FFE1, #28D7FF);
    z-index: 1;
}

.stage-item {
    position: relative;
    z-index: 2;
    width: 25%;
    text-align: center;
}

.stage-circle {
    margin: 0 auto;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    border: 2px solid #67FFE1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.stage-label {
    margin-top: 9px;
    font-size: 12px;
    font-weight: 700;
}

.good {
    color: #27C281;
    font-weight: 700;
}

.warning {
    color: #F2A93B;
    font-weight: 700;
}

.danger {
    color: #EF4444;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# Data
# =========================================================
incoterm_descriptions = {
    "EXW": "Ex Works - buyer collects goods from seller's premises.",
    "FCA": "Free Carrier - seller delivers goods to a named carrier or place.",
    "CPT": "Carriage Paid To - seller pays transport to named destination.",
    "CIP": "Carriage and Insurance Paid To - seller pays transport and insurance.",
    "DAP": "Delivered at Place - seller delivers to named destination, unloaded by buyer.",
    "DPU": "Delivered at Place Unloaded - seller delivers and unloads at destination.",
    "DDP": "Delivered Duty Paid - seller handles delivery, duties, and import clearance.",
    "FAS": "Free Alongside Ship - seller delivers alongside vessel.",
    "FOB": "Free On Board - seller delivers goods on board vessel.",
    "CFR": "Cost and Freight - seller pays freight to destination port.",
    "CIF": "Cost, Insurance and Freight - seller pays freight and insurance to destination port."
}

route_nodes = pd.DataFrame({
    "Stage": ["FAB", "SORT", "ASSY", "TEST", "DC", "Customer"],
    "Location": [
        "Hsinchu, Taiwan",
        "Hsinchu, Taiwan",
        "Penang, Malaysia",
        "Singapore",
        "Munich, Germany",
        "Stuttgart, Germany"
    ],
    "Latitude": [24.8138, 24.8138, 5.4164, 1.3521, 48.1351, 48.7758],
    "Longitude": [120.9675, 120.9675, 100.3327, 103.8198, 11.5820, 9.1829],
    "Risk Level": ["High", "High", "Medium", "Medium", "Low", "High"],
    "Risk Score": [90, 88, 65, 60, 25, 82]
})

route_edges = pd.DataFrame({
    "From": ["FAB", "SORT", "ASSY", "TEST", "DC"],
    "To": ["SORT", "ASSY", "TEST", "DC", "Customer"],
    "from_lat": [24.8138, 24.8138, 5.4164, 1.3521, 48.1351],
    "from_lon": [120.9675, 120.9675, 100.3327, 103.8198, 11.5820],
    "to_lat": [24.8138, 5.4164, 1.3521, 48.1351, 48.7758],
    "to_lon": [120.9675, 100.3327, 103.8198, 11.5820, 9.1829],
    "Risk": [90, 80, 60, 45, 70]
})

risk_signals = pd.DataFrame({
    "Signal Source": [
        "Trade restriction feed",
        "Port congestion index",
        "Supplier financial monitor",
        "Regional conflict indicator"
    ],
    "Signal": [
        "Taiwan Strait logistics restriction",
        "Penang port dwell time rising",
        "Backup SUBCON margin pressure",
        "Cross-border customs inspection surge"
    ],
    "Mapped Node / Route": [
        "FAB Taiwan -> SORT Taiwan",
        "SORT Taiwan -> ASSY Malaysia",
        "Backup SUBCON",
        "TEST Singapore -> DC Europe"
    ],
    "Severity": [92, 68, 54, 61],
    "Confidence": ["High", "Medium", "Medium", "Medium"],
    "Status": ["Active", "Watching", "Watching", "Watching"]
})

system_flow = [
    ("Risk Signal", "External disruption converted into numeric risk"),
    ("Network Impact", "Affected nodes, routes, and orders identified"),
    ("Fragility Score", "Route vulnerability ranked by Resilience DNA"),
    ("Antibody", "Pre-approved playbook selected"),
    ("Optimized Route", "Cost-time-risk trade-off calculated"),
    ("Customer Message", "ETA and trust response generated")
]


orders = pd.DataFrame({
    "Order ID": ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004"],
    "Customer": [
        "Automotive Customer A",
        "Industrial Customer B",
        "Consumer Customer C",
        "Automotive Customer D"
    ],
    "Product": [
        "Automotive Power Module",
        "Industrial Sensor IC",
        "Consumer Power IC",
        "Automotive Microcontroller"
    ],
    "Manufacturing Progress": [100, 100, 65, 100],
    "Shipment Ready": [1, 1, 0, 1],
    "Shipment Released": [1, 0, 0, 1],
    "Order Fulfilled": [0, 0, 0, 1],
    "DIC Days": [4, 8, 15, 20],
    "Disruption Risk": [85, 62, 35, 20],
    "Lead Time Remaining": [5, 7, 14, 0]
})

routes = pd.DataFrame({
    "Route": ["Normal Route", "Premium Freight", "Backup SUBCON", "Split Shipment"],
    "Cost Score": [90, 45, 70, 75],
    "Lead Time Score": [40, 95, 80, 88],
    "Risk Score": [30, 65, 85, 90],
    "Capacity Score": [85, 55, 70, 82],
    "Customer Priority Score": [60, 85, 88, 92]
})

weights = {
    "Cost Score": 0.25,
    "Lead Time Score": 0.25,
    "Risk Score": 0.20,
    "Capacity Score": 0.15,
    "Customer Priority Score": 0.15
}

routes["Overall Score"] = (
    routes["Cost Score"] * weights["Cost Score"] +
    routes["Lead Time Score"] * weights["Lead Time Score"] +
    routes["Risk Score"] * weights["Risk Score"] +
    routes["Capacity Score"] * weights["Capacity Score"] +
    routes["Customer Priority Score"] * weights["Customer Priority Score"]
).round(1)

best_route = routes.loc[routes["Overall Score"].idxmax()]

dna = pd.DataFrame({
    "Factor": [
        "Supplier concentration",
        "Country exposure",
        "Route redundancy",
        "DIC coverage",
        "Lead time sensitivity",
        "Customer criticality"
    ],
    "Risk Score": [85, 90, 60, 70, 78, 95]
})

overall_fragility = round(dna["Risk Score"].mean(), 1)

playbook = pd.DataFrame({
    "Component": [
        "Trigger condition",
        "Affected product",
        "Backup option",
        "Inventory action",
        "Approval owner",
        "Customer action"
    ],
    "Recommendation": [
        "Route risk score exceeds 80",
        "Automotive power module family",
        "Activate backup SUBCON and split shipment",
        "Increase DIC from 10 to 18 days",
        "Logistics lead and procurement lead",
        "Send revised ETA within 1 hour"
    ]
})

antibodies = pd.DataFrame({
    "Playbook": [
        "A1 Taiwan Logistics Bypass",
        "A2 Backup SUBCON Activation",
        "A3 Critical Customer Split Shipment"
    ],
    "Trigger": [
        "Route risk score exceeds 80",
        "Supplier capacity drops below 70%",
        "Trust risk exceeds 80"
    ],
    "Risk Type": [
        "Trade restriction",
        "Capacity constraint",
        "Customer delivery risk"
    ],
    "Affected Scope": [
        "FAB, SORT, ASSY, automotive power modules",
        "ASSY, TEST, downstream distribution",
        "High-priority automotive orders"
    ],
    "Response": [
        "Reroute via alternate logistics corridor",
        "Shift urgent volume to qualified backup SUBCON",
        "Split urgent order and reserve TEST capacity"
    ],
    "Cost Impact": ["+7%", "+6%", "+9%"],
    "Time Impact": ["+2 days", "+1 day", "-3 days vs normal disruption"],
    "Owner": [
        "Logistics lead",
        "Procurement lead",
        "Sales and planning lead"
    ],
    "Activation": ["Ready", "Ready", "Pending approval"]
})

customers = pd.DataFrame({
    "Customer": [
        "Automotive Customer A",
        "Industrial Customer B",
        "Consumer Customer C",
        "Automotive Customer D"
    ],
    "Delay Days": [5, 3, 1, 4],
    "Customer Priority": [95, 70, 35, 88],
    "Recovery Confidence": [55, 80, 90, 45],
    "Past Disruption History": [80, 45, 20, 70]
})

customers["Trust Risk Score"] = (
    customers["Delay Days"] * 8 +
    customers["Customer Priority"] * 0.35 +
    (100 - customers["Recovery Confidence"]) * 0.25 +
    customers["Past Disruption History"] * 0.15
).round(1)

customers_sorted = customers.sort_values("Trust Risk Score", ascending=False)
highest_risk_customer = customers_sorted.iloc[0]

operational_kpis = pd.DataFrame({
    "KPI": [
        "Recovery route selection time",
        "Customer notification time",
        "Premium freight reduction",
        "Revised ETA accuracy",
        "DIC stability",
        "Recovery confidence"
    ],
    "Value": ["11 min", "42 min", "18%", "86%", "74%", "82%"],
    "Target": ["< 30 min", "< 60 min", "> 15%", "> 85%", "> 70%", "> 80%"]
})

# =========================================================
# Predictive Logic
# =========================================================
def risk_category(score):
    if score >= 80:
        return "Critical"
    if score >= 61:
        return "High"
    if score >= 31:
        return "Medium"
    return "Low"


def response_severity(score, dic_days):
    if score >= 80 and dic_days <= 5:
        return "Redesign route/entity"
    if score >= 60:
        return "Reroute disrupted connection"
    return "Absorb delay"


def compute_route_scores(route_df, route_weights):
    scored_routes = route_df.copy()
    scored_routes["Overall Score"] = (
        scored_routes["Cost Score"] * route_weights["Cost Score"] +
        scored_routes["Lead Time Score"] * route_weights["Lead Time Score"] +
        scored_routes["Risk Score"] * route_weights["Risk Score"] +
        scored_routes["Capacity Score"] * route_weights["Capacity Score"] +
        scored_routes["Customer Priority Score"] * route_weights["Customer Priority Score"]
    ).round(1)
    return scored_routes.sort_values("Overall Score", ascending=False)


def render_html(html):
    cleaned_html = "\n".join(
        line.strip()
        for line in textwrap.dedent(html).splitlines()
        if line.strip()
    )
    st.markdown(cleaned_html, unsafe_allow_html=True)


def render_system_flow():
    flow_html = ['<div class="flow-strip">']
    for index, (title, copy) in enumerate(system_flow, start=1):
        flow_html.extend([
            '<div class="flow-step">',
            f'<div class="flow-index">L{index:02d}</div>',
            f'<div class="flow-title">{title}</div>',
            f'<div class="flow-copy">{copy}</div>',
            '</div>'
        ])
    flow_html.append("</div>")
    render_html("\n".join(flow_html))


def render_signal_cards(signals):
    card_html = ['<div class="module-grid">']
    for _, signal in signals.iterrows():
        category = risk_category(signal["Severity"])
        chip_class = "critical" if category == "Critical" else "high" if category == "High" else ""
        card_html.extend([
            '<div class="cyber-card">',
            f'<div class="cyber-card-title">{signal["Signal Source"]}</div>',
            f'<div class="cyber-card-value">{signal["Severity"]}/100</div>',
            f'<div class="cyber-card-copy">{signal["Signal"]}</div>',
            f'<div class="cyber-card-copy" style="margin-top:8px;">{signal["Mapped Node / Route"]}</div>',
            '<div style="margin-top:10px;">',
            f'<span class="status-chip {chip_class}">{category}</span>',
            '</div>',
            '</div>'
        ])
    card_html.append("</div>")
    render_html("\n".join(card_html))


def render_playbook_cards(playbooks):
    for _, playbook_row in playbooks.iterrows():
        activation = playbook_row["Activation"]
        chip_class = "" if activation == "Ready" else "high"
        render_html(
            f"""
            <div class="playbook-card">
                <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                    <div>
                        <div class="cyber-card-title">{playbook_row["Playbook"]}</div>
                        <div class="cyber-card-copy"><b style="color:#EAF2FF;">Trigger:</b> {playbook_row["Trigger"]}</div>
                        <div class="cyber-card-copy"><b style="color:#EAF2FF;">Response:</b> {playbook_row["Response"]}</div>
                    </div>
                    <span class="status-chip {chip_class}">{activation}</span>
                </div>
                <div class="playbook-meta">
                    <div><div class="mini-label">Risk Type</div><div class="mini-value">{playbook_row["Risk Type"]}</div></div>
                    <div><div class="mini-label">Scope</div><div class="mini-value">{playbook_row["Affected Scope"]}</div></div>
                    <div><div class="mini-label">Cost / Time</div><div class="mini-value">{playbook_row["Cost Impact"]} | {playbook_row["Time Impact"]}</div></div>
                    <div><div class="mini-label">Owner</div><div class="mini-value">{playbook_row["Owner"]}</div></div>
                </div>
            </div>
            """
        )


def render_scenario_steps():
    steps_html = ['<div class="scenario-grid">']
    for index, row in scenario_steps.iterrows():
        steps_html.extend([
            '<div class="scenario-step">',
            f'<div class="scenario-step-number">STEP {index + 1:02d}</div>',
            f'<div class="scenario-step-title">{row["Module"]}</div>',
            f'<div class="scenario-step-copy">{row["Scenario Action"]}</div>',
            '</div>'
        ])
    steps_html.append('</div>')
    render_html("\n".join(steps_html))



def predict_order_stage(order_row):
    if order_row["Order Fulfilled"] == 1:
        return "Order Fulfilled"

    if order_row["Shipment Released"] == 1:
        return "Shipment Released"

    if order_row["Shipment Ready"] == 1:
        return "Shipment Ready"

    return "Manufacturing"


def predict_progress_percentage(order_row):
    progress = 0
    progress += order_row["Manufacturing Progress"] * 0.40
    progress += order_row["Shipment Ready"] * 20
    progress += order_row["Shipment Released"] * 25
    progress += order_row["Order Fulfilled"] * 15
    return min(round(progress), 100)


def predict_delay_risk(order_row):
    risk_score = (
        order_row["Disruption Risk"] * 0.45 +
        max(0, 10 - order_row["DIC Days"]) * 4 +
        order_row["Lead Time Remaining"] * 2
    )

    if risk_score >= 75:
        delay_category = "High Delay Risk"
        eta_confidence = "Low"
    elif risk_score >= 45:
        delay_category = "Medium Delay Risk"
        eta_confidence = "Medium"
    else:
        delay_category = "Low Delay Risk"
        eta_confidence = "High"

    return round(risk_score, 1), delay_category, eta_confidence


def render_order_progress(current_stage, progress_percent):
    stages = [
        {"key": "Order Processed", "label": "Order Processed", "icon": "order_processed.png", "fallback": "ORD"},
        {"key": "Manufacturing", "label": "Manufacturing", "icon": "manufacturing.png", "fallback": "MFG"},
        {"key": "Shipment Ready", "label": "Shipment Ready", "icon": "shipment_ready.png", "fallback": "RDY"},
        {"key": "Shipment Released", "label": "Shipment Released", "icon": "shipment_release.png", "fallback": "REL"},
        {"key": "Order Fulfilled", "label": "Order Fulfilled", "icon": "order_fulfilled.png", "fallback": "FUL"}
    ]

    stage_keys = [stage["key"] for stage in stages]
    current_index = stage_keys.index(current_stage)

    progress_angle = progress_percent * 3.6
    stage_fill_width = (current_index / (len(stages) - 1)) * 86

    stage_html = ""

    for index, stage in enumerate(stages):
        completed = index <= current_index
        circle_bg = "#67FFE1" if completed else "#07111F"
        circle_border = "#67FFE1" if completed else "#34526F"
        label_color = "#EAF2FF" if completed else "#7E94AA"
        icon_html = get_icon_html(stage["icon"], stage["fallback"])

        stage_html += f"""
        <div class="stage-item">
            <div class="stage-circle" style="background:{circle_bg}; border-color:{circle_border};">
                {icon_html}
            </div>
            <div class="stage-label" style="color:{label_color};">
                {stage["label"]}
            </div>
        </div>
        """

    html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: Arial, sans-serif;
                color: #EAF2FF;
            }}

            .progress-panel {{
                background: #111827;
                border: 1px solid #233B5E;
                border-radius: 18px;
                padding: 24px 26px;
                box-sizing: border-box;
                width: 100%;
            }}

            .progress-title {{
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 0.4px;
                margin-bottom: 18px;
            }}

            .progress-top {{
                display: flex;
                align-items: center;
                gap: 26px;
                margin-bottom: 24px;
            }}

            .donut {{
                width: 118px;
                height: 118px;
                border-radius: 50%;
                background: conic-gradient(#28D7FF {progress_angle}deg, #26364D 0deg);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 28px rgba(40, 215, 255, 0.18);
                flex-shrink: 0;
            }}

            .donut-inner {{
                width: 82px;
                height: 82px;
                background: #111827;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .progress-percent {{
                color: #FFFFFF;
                font-size: 25px;
                font-weight: 800;
            }}

            .progress-copy {{
                color: #AFC2D8;
                font-size: 13px;
                line-height: 1.45;
                max-width: 780px;
            }}

            .progress-bar-shell {{
                width: 100%;
                height: 24px;
                border: 2px solid #35516F;
                border-radius: 6px;
                padding: 3px;
                background: #0A1322;
                margin-bottom: 28px;
                box-sizing: border-box;
            }}

            .progress-bar-fill {{
                height: 100%;
                border-radius: 3px;
                background: linear-gradient(90deg, #39E6FF, #2F80ED);
                position: relative;
            }}

            .progress-bar-label {{
                position: absolute;
                right: 8px;
                top: 1px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
            }}

            .stage-row {{
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                position: relative;
                margin-top: 8px;
            }}

            .stage-line {{
                position: absolute;
                top: 25px;
                left: 7%;
                right: 7%;
                height: 3px;
                background: #34526F;
                z-index: 0;
            }}

            .stage-line-fill {{
                position: absolute;
                top: 25px;
                left: 7%;
                height: 3px;
                background: linear-gradient(90deg, #67FFE1, #28D7FF);
                z-index: 1;
                width: {stage_fill_width}%;
            }}

            .stage-item {{
                position: relative;
                z-index: 2;
                width: 25%;
                text-align: center;
            }}

            .stage-circle {{
                margin: 0 auto;
                width: 52px;
                height: 52px;
                border-radius: 50%;
                border: 2px solid #67FFE1;
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
            }}

            .stage-icon {{
                display: block;
                width: 48px;
                height: 48px;
                object-fit: contain;
                flex: 0 0 48px;
            }}

            .stage-icon-fallback {{
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #07111F;
                font-size: 13px;
                font-weight: 800;
                line-height: 1;
            }}

            .stage-label {{
                margin-top: 9px;
                font-size: 12px;
                font-weight: 700;
            }}
        </style>
    </head>

    <body>
        <div class="progress-panel">
            <div class="progress-title">ORDER PROGRESS ANALYSIS</div>

            <div class="progress-top">
                <div class="donut">
                    <div class="donut-inner">
                        <div class="progress-percent">{progress_percent}%</div>
                    </div>
                </div>

                <div class="progress-copy">
                    <b style="color:#28D7FF;">{current_stage}</b>.
                </div>
            </div>

            <div class="progress-bar-shell">
                <div class="progress-bar-fill" style="width:{progress_percent}%;">
                    <div class="progress-bar-label">{progress_percent}%</div>
                </div>
            </div>

            <div class="stage-row">
                <div class="stage-line"></div>
                <div class="stage-line-fill"></div>
                {stage_html}
            </div>
        </div>
    </body>
    </html>
    """

    components.html(html, height=360, scrolling=False)

def risk_colour(score):
    if score >= 75:
        return [239, 68, 68, 220]
    if score >= 45:
        return [242, 169, 59, 220]
    return [39, 194, 129, 220]


def render_affected_route_map():
    map_nodes = route_nodes.copy()
    map_edges = route_edges.copy()

    map_nodes["Color"] = map_nodes["Risk Score"].apply(risk_colour)
    map_edges["Color"] = map_edges["Risk"].apply(risk_colour)

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=map_edges,
        get_source_position="[from_lon, from_lat]",
        get_target_position="[to_lon, to_lat]",
        get_source_color="Color",
        get_target_color="Color",
        get_width=5,
        pickable=True
    )

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_nodes,
        get_position="[Longitude, Latitude]",
        get_radius=70000,
        get_fill_color="Color",
        get_line_color=[234, 242, 255],
        line_width_min_pixels=2,
        pickable=True
    )

    text_layer = pdk.Layer(
        "TextLayer",
        data=map_nodes,
        get_position="[Longitude, Latitude]",
        get_text="Stage",
        get_size=16,
        get_color=[234, 242, 255],
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        get_pixel_offset=[0, -35]
    )

    view_state = pdk.ViewState(
        latitude=18,
        longitude=75,
        zoom=2,
        pitch=25
    )

    deck = pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK,
        initial_view_state=view_state,
        layers=[arc_layer, point_layer, text_layer],
        tooltip={
            "html": """
            <b>{Stage}</b><br/>
            Location: {Location}<br/>
            Risk Level: {Risk Level}<br/>
            Risk Score: {Risk Score}
            """,
            "style": {
                "backgroundColor": "#0D1B2F",
                "color": "#EAF2FF"
            }
        }
    )

    st.pydeck_chart(deck, use_container_width=True)
# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("NerveShield AI")
st.sidebar.caption("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Command Centre",
        "Route Optimizer",
        "Customer Trust",
        "Document Generator"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Current Scenario: Taiwan Strait logistics restriction")

# =========================================================
# Header
# =========================================================
logo_path = Path("infineon_logo.png")

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("Nervenschutz AI")
with header_right:
    if logo_path.exists():
        logo_base64 = image_to_base64(logo_path)
        render_html(
            f"""
            <div style="text-align:right;">
                <img src="data:image/png;base64,{logo_base64}" style="width:150px;">
            </div>
            """
        )
    else:
        render_html(
            """
            <div style="text-align:right;font-weight:800;color:#EAF2FF;font-size:20px;">
                INFINEON
            </div>
            """
        )

render_html("""
<div class="signal-box">
<b>Risk Signal Detected:</b> Taiwan Strait logistics restriction affecting high-priority semiconductor routes.
</div>
""")

st.write("")

# =========================================================
# Page 1: Command Centre
# =========================================================
if page == "Command Centre":
    st.subheader("Live Overview")

    selected_order_id = st.selectbox(
        "By Order",
        orders["Order ID"]
    )

    selected_order = orders[orders["Order ID"] == selected_order_id].iloc[0]

    predicted_stage = predict_order_stage(selected_order)
    progress_percent = predict_progress_percentage(selected_order)
    delay_score, delay_category, eta_confidence = predict_delay_risk(selected_order)
    selected_response = response_severity(delay_score, selected_order["DIC Days"])

    render_order_progress(predicted_stage, progress_percent)

    order_col1, order_col2, order_col3, order_col4 = st.columns(4)
    order_col1.metric("Predicted Stage", predicted_stage)
    order_col2.metric("Progress", f"{progress_percent}%")
    order_col3.metric("ETA Confidence", eta_confidence)
    order_col4.metric("Lead Time Remaining", f"{selected_order['Lead Time Remaining']} days")

    render_html(
        f"""
        <div class="info-box">
        <b>Recommended Response Class:</b> {selected_response}<br>
        <span style="color:#AFC2D8;">Based on disruption risk, DIC coverage, and remaining lead time for {selected_order["Order ID"]}.</span>
        </div>
        """
    )

    st.markdown("### Selected Order Details")

    selected_order_details = pd.DataFrame({
        "Field": [
            "Order ID",
            "Customer",
            "Product",
            "Manufacturing Progress",
            "Shipment Ready",
            "Shipment Released",
            "Order Fulfilled",
            "DIC Days",
            "Disruption Risk",
            "Delay Risk Category"
        ],
        "Value": [
            selected_order["Order ID"],
            selected_order["Customer"],
            selected_order["Product"],
            f"{selected_order['Manufacturing Progress']}%",
            "Yes" if selected_order["Shipment Ready"] == 1 else "No",
            "Yes" if selected_order["Shipment Released"] == 1 else "No",
            "Yes" if selected_order["Order Fulfilled"] == 1 else "No",
            selected_order["DIC Days"],
            selected_order["Disruption Risk"],
            delay_category
        ]
    })

    st.dataframe(selected_order_details, use_container_width=True)

    st.write("")
    st.subheader("Command Centre KPIs")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Disruptions", "3", "+2")
    col2.metric("High-Risk Routes", "12", "+5")
    col3.metric("Recovery Confidence", "82%", "+14%")
    col4.metric("Customers at Trust Risk", "5", "+3")

    st.write("")
    st.subheader("System Activation Flow")
    render_system_flow()

    st.write("")
    st.subheader("Layer 3: Risk Signal Ingestion")
    render_signal_cards(risk_signals)
    st.dataframe(risk_signals, use_container_width=True)

    st.write("")
    st.subheader("1. Supply Chain Nervous System")

    render_html("""
    <div class="info-box">
    <b>Affected Route:</b><br>
    FAB Taiwan -> SORT Taiwan -> ASSY Malaysia -> TEST Singapore -> Distribution Centre Europe -> Automotive Customer A
    </div>
    """)

    st.write("")

    render_affected_route_map()

    st.write("")
    st.subheader("2. Resilience DNA Engine")

    left, right = st.columns([1, 1])

    with left:
        st.metric("Overall Fragility Score", f"{overall_fragility}/100", "High Risk")
        st.dataframe(dna, use_container_width=True)

    with right:
        fig = px.bar(
            dna,
            x="Risk Score",
            y="Factor",
            orientation="h",
            color="Risk Score",
            color_continuous_scale=["#27C281", "#F2A93B", "#EF4444"],
            range_x=[0, 100],
            title="Resilience DNA Risk Profile"
        )
        fig.update_layout(
            paper_bgcolor="#07111F",
            plot_bgcolor="#07111F",
            font_color="#EAF2FF"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("3. Disruption Antibody Generator")
    render_playbook_cards(antibodies)
    st.markdown("### Legacy Playbook Matrix")
    st.dataframe(playbook, use_container_width=True)

    st.success("Activated Antibody: Split urgent order volume across backup SUBCON and alternative logistics route.")

    st.subheader("Operational KPIs")
    st.dataframe(operational_kpis, use_container_width=True)


# =========================================================
# Page 3: Route Optimizer
# =========================================================
elif page == "Route Optimizer":
    st.subheader("Adaptive Route Optimizer")

    render_html("""
    <div class="info-box">
    Tune the decision weights to match the disruption mode. The optimizer recalculates the best recovery action using cost, lead time, risk, capacity, and customer priority.
    </div>
    """)

    st.write("")
    st.markdown("### Adaptive Scoring Weights")

    slider_cols = st.columns(5)
    raw_weight_values = {}
    for slider_col, (criteria, default_weight) in zip(slider_cols, weights.items()):
        with slider_col:
            raw_weight_values[criteria] = st.slider(
                criteria.replace(" Score", ""),
                min_value=0,
                max_value=50,
                value=int(default_weight * 100),
                step=5
            )

    total_weight = sum(raw_weight_values.values()) or 1
    active_weights = {
        criteria: value / total_weight
        for criteria, value in raw_weight_values.items()
    }

    weight_df = pd.DataFrame({
        "Criteria": list(active_weights.keys()),
        "Normalized Weight": [round(value, 2) for value in active_weights.values()]
    })

    st.dataframe(weight_df, use_container_width=True)

    st.markdown("### Recovery Option Comparison")

    sorted_routes = compute_route_scores(routes.drop(columns=["Overall Score"], errors="ignore"), active_weights)
    active_best_route = sorted_routes.iloc[0]
    st.dataframe(sorted_routes, use_container_width=True)

    st.success(
        f"Recommended Recovery Action: {active_best_route['Route']} "
        f"with an overall score of {active_best_route['Overall Score']:.1f}/100."
    )

    render_html(
        f"""
        <div class="module-grid">
            <div class="cyber-card">
                <div class="cyber-card-title">Decision Mode</div>
                <div class="cyber-card-value">{response_severity(delay_score if "delay_score" in globals() else 85, 4)}</div>
                <div class="cyber-card-copy">Severity class selected from risk and DIC pressure.</div>
            </div>
            <div class="cyber-card">
                <div class="cyber-card-title">Best Option</div>
                <div class="cyber-card-value">{active_best_route['Route']}</div>
                <div class="cyber-card-copy">Highest weighted cost-time-risk recovery score.</div>
            </div>
            <div class="cyber-card">
                <div class="cyber-card-title">Recovery Confidence</div>
                <div class="cyber-card-value">High</div>
                <div class="cyber-card-copy">Capacity and customer priority remain within target range.</div>
            </div>
        </div>
        """
    )

    fig2 = px.bar(
        sorted_routes,
        x="Route",
        y="Overall Score",
        color="Overall Score",
        color_continuous_scale=["#EF4444", "#F2A93B", "#27C281"],
        range_y=[0, 100],
        title="Recovery Option Score"
    )
    fig2.update_layout(
        paper_bgcolor="#07111F",
        plot_bgcolor="#07111F",
        font_color="#EAF2FF"
    )
    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# Page 4: Customer Trust
# =========================================================
elif page == "Customer Trust":
    st.subheader("Customer Trust Layer")

    render_html("""
    <div class="info-box">
    This layer ranks customers based on delay severity, customer importance, recovery confidence,
    and past disruption history.
    </div>
    """)

    st.write("")
    customers_display = customers_sorted.copy()
    customers_display["Trust Category"] = customers_display["Trust Risk Score"].apply(risk_category)
    customers_display["Recommended Action"] = customers_display["Trust Category"].map({
        "Critical": "Personal account manager call",
        "High": "Prioritized sales update",
        "Medium": "Automated ETA and recovery note",
        "Low": "Standard notification"
    })
    st.dataframe(customers_display, use_container_width=True)

    st.error(
        f"Highest Trust Risk: {highest_risk_customer['Customer']} "
        f"with trust risk score {highest_risk_customer['Trust Risk Score']}/100."
    )

    trust_category = risk_category(highest_risk_customer["Trust Risk Score"])
    communication_action = customers_display.iloc[0]["Recommended Action"]

    render_html(
        f"""
        <div class="module-grid">
            <div class="cyber-card">
                <div class="cyber-card-title">Trust Category</div>
                <div class="cyber-card-value">{trust_category}</div>
                <div class="cyber-card-copy">Customer impact level based on delay, priority, confidence, and history.</div>
            </div>
            <div class="cyber-card">
                <div class="cyber-card-title">Communication Action</div>
                <div class="cyber-card-value">{communication_action}</div>
                <div class="cyber-card-copy">Recommended next step for customer-facing teams.</div>
            </div>
            <div class="cyber-card">
                <div class="cyber-card-title">Next Update Window</div>
                <div class="cyber-card-value">24 hrs</div>
                <div class="cyber-card-copy">Follow-up cadence linked to recovery confidence.</div>
            </div>
        </div>
        """
    )

    st.markdown("### Generated Customer Message")

    message = f"""
Dear {highest_risk_customer['Customer']},

Your scheduled delivery may experience a delay due to a logistics disruption affecting part of the semiconductor supply route.

To reduce impact, Infineon has activated the recommended recovery action: {best_route['Route']}.
The revised delay estimate is approximately {highest_risk_customer['Delay Days']} days.
Your case has been prioritized for {communication_action.lower()}.

We will provide the next update within 24 hours. For urgent production impact, your account team will coordinate the next recovery update directly.

Regards,
Infineon Supply Chain Team
"""

    st.text_area("Customer Update Draft", message, height=240)

    st.markdown("### Internal Team Action Plan")
    internal_actions = pd.DataFrame({
        "Team": ["Sales", "Customer Service", "Logistics", "Production Planning", "Procurement"],
        "Action": [
            "Prepare prioritized talking points for critical customer",
            "Send ETA update and schedule follow-up reminder",
            "Confirm selected route and shipment milestone",
            "Reserve TEST capacity for urgent orders",
            "Confirm backup SUBCON activation readiness"
        ]
    })
    st.dataframe(internal_actions, use_container_width=True)

# =========================================================
# Page 5: Document Generator
# =========================================================
elif page == "Document Generator":
    st.subheader("Document Generator")
    st.caption("Create formatted quotation orders, purchase orders, and order acknowledgement forms.")

    doc_type = st.selectbox(
        "Select Document Type",
        [
            "Quotation Order",
            "Purchase Order",
            "Order Acknowledgement Form"
        ]
    )

    st.write("")
    col_a, col_b = st.columns(2)

    with col_a:
        company_name = st.text_input("Buyer / Customer Name", "Automotive Customer A")
        supplier_name = st.text_input("Supplier Name", "Infineon Technologies")
        contact_person = st.text_input("Contact Person", "Procurement Manager")
        document_no = st.text_input("Document Number", "NS-PO-2026-001")
        document_date = st.date_input("Document Date")

    with col_b:
        product_name = st.text_input("Product / Part Name", "Automotive Power Module")
        part_number = st.text_input("Part Number", "APM-7842-X")
        quantity = st.number_input("Quantity", min_value=1, value=500)
        unit_price = st.number_input("Unit Price", min_value=0.0, value=42.50)
        currency = st.selectbox("Currency", ["SGD", "USD", "EUR", "MYR", "JPY"])

    st.markdown("### Shipping and Commercial Terms")

    col_c, col_d = st.columns(2)

    with col_c:
        incoterm = st.selectbox(
            "Incoterm",
            list(incoterm_descriptions.keys()),
            index=1
        )
        named_place = st.text_input("Named Place / Port", "Singapore")
        lead_time = st.number_input("Lead Time", min_value=1, value=14)
        lead_time_unit = st.selectbox("Lead Time Unit", ["calendar days", "working days", "weeks"])

    with col_d:
        payment_terms = st.selectbox(
            "Payment Terms",
            ["Net 30", "Net 45", "Net 60", "Advance Payment", "Upon Delivery"]
        )
        delivery_mode = st.selectbox(
            "Delivery Mode",
            ["Air Freight", "Sea Freight", "Road Transport", "Courier", "Multimodal"]
        )
        validity_period = st.number_input("Validity Period for Quotation", min_value=1, value=30)
        warranty_terms = st.text_input("Warranty / Quality Terms", "Subject to standard quality inspection")

    total_amount = quantity * unit_price

    st.info(f"Selected Incoterm: {incoterm} - {incoterm_descriptions[incoterm]}")

    if doc_type == "Quotation Order":
        title = "QUOTATION ORDER"
        intro = "We are pleased to provide the following quotation for your consideration."
        closing = "This quotation is valid subject to the stated validity period and commercial terms."
    elif doc_type == "Purchase Order":
        title = "PURCHASE ORDER"
        intro = "Please process the following purchase order according to the stated commercial and delivery terms."
        closing = "Kindly confirm acceptance of this purchase order and expected delivery schedule."
    else:
        title = "ORDER ACKNOWLEDGEMENT FORM"
        intro = "We acknowledge receipt and acceptance of the following order details."
        closing = "This acknowledgement confirms the order details subject to production and delivery availability."

    document_text = f"""
{title}

Document No.: {document_no}
Date: {document_date}

Buyer / Customer:
{company_name}
Contact Person: {contact_person}

Supplier:
{supplier_name}

Order Details:
Product / Part Name: {product_name}
Part Number: {part_number}
Quantity: {quantity}
Unit Price: {currency} {unit_price:,.2f}
Total Amount: {currency} {total_amount:,.2f}

Commercial Terms:
Incoterm: {incoterm} - {named_place}
Incoterm Meaning: {incoterm_descriptions[incoterm]}
Payment Terms: {payment_terms}
Delivery Mode: {delivery_mode}
Lead Time: {lead_time} {lead_time_unit}
Warranty / Quality Terms: {warranty_terms}

Remarks:
{intro}

Lead time will begin from the date of order confirmation, subject to material availability, capacity allocation, and final approval.

{closing}

"""

    st.markdown("### Generated Document Preview")
    st.text_area("Formatted Document", document_text, height=520)

    st.download_button(
        label="Download Document as TXT",
        data=document_text,
        file_name=f"{doc_type.lower().replace(' ', '_')}_{document_no}.txt",
        mime="text/plain"
    )
