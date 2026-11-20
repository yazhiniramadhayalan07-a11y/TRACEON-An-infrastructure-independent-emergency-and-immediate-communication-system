# ================================================================
# TRACEON - DISASTER RESCUE AND COMMUNICATION SYSTEM
# Streamlit single-file dashboard
# Libraries: Streamlit, NumPy, Pandas, Matplotlib, Seaborn
# Note: Folium is intentionally not used because TRACEON is GPS-free.
# ================================================================

from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(
    page_title="TRACEON | Rescue Command Centre",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "traceon_data"
DATA_DIR.mkdir(exist_ok=True)

SOS_FILE = DATA_DIR / "sos_alerts.csv"
FAMILY_FILE = DATA_DIR / "families.csv"
NODE_FILE = DATA_DIR / "nodes.csv"
ROUTE_FILE = DATA_DIR / "routes.csv"
TEAM_FILE = DATA_DIR / "rescue_teams.csv"

# -------------------- STARTER DATA --------------------
# These records are demonstration data based on the current TRACEON
# prototype context. They are not live hardware readings.
def create_csv_if_missing(path, rows, columns):
    if not path.exists():
        pd.DataFrame(rows, columns=columns).to_csv(path, index=False)

create_csv_if_missing(
    FAMILY_FILE,
    [
        ["FAM-001", "H-104", "DEV-001", "North Street, Zone A", 4, "9876500001"],
        ["FAM-002", "H-212", "DEV-002", "River Road, Zone B", 5, "9876500002"],
        ["FAM-003", "H-305", "DEV-003", "Market Street, Zone A", 3, "9876500003"],
        ["FAM-004", "H-118", "DEV-004", "Lake Road, Zone C", 2, "9876500004"],
        ["FAM-005", "H-221", "DEV-005", "Hill View, Zone B", 6, "9876500005"],
    ],
    ["family_id", "house_id", "device_id", "location_description", "people_count", "contact"]
)

create_csv_if_missing(
    SOS_FILE,
    [
        ["SOS-2026-010", "FAM-002", "H-212", "DEV-002", "SOS", "HIGH", "IN_PROGRESS", "Team Charlie", "2026-11-13 18:20"],
        ["SOS-2026-009", "FAM-001", "H-104", "DEV-001", "HELP", "LOW", "RESCUED", "", "2026-11-13 17:45"],
        ["SOS-2026-008", "FAM-001", "H-104", "DEV-001", "HELP", "MEDIUM", "RESCUED", "", "2026-11-13 16:30"],
        ["SOS-2026-007", "FAM-001", "H-104", "DEV-001", "SOS", "HIGH", "IN_PROGRESS", "Team Bravo", "2026-11-13 15:10"],
        ["SOS-000006", "FAM-001", "H-104", "DEV-001", "SOS", "HIGH", "RESCUED", "Team Alpha", "2026-11-13 14:05"],
        ["SOS-2026-005", "FAM-005", "H-221", "DEV-005", "SOS", "HIGH", "IN_PROGRESS", "Team Alpha", "2026-11-13 13:20"],
        ["SOS-2026-004", "FAM-004", "H-118", "DEV-004", "HELP", "LOW", "RESCUED", "Team Alpha", "2026-11-13 12:40"],
        ["SOS-2026-003", "FAM-003", "H-305", "DEV-003", "SOS", "MEDIUM", "PENDING", "", "2026-11-13 11:15"],
        ["SOS-2026-002", "FAM-002", "H-212", "DEV-002", "SOS", "HIGH", "PENDING", "", "2026-11-13 10:30"],
        ["SOS-2026-001", "FAM-001", "H-104", "DEV-001", "SOS", "HIGH", "RESCUED", "Team Alpha", "2026-11-13 09:00"],
    ],
    ["sos_id", "family_id", "house_id", "device_id", "alert_type", "priority", "rescue_status", "assigned_team", "created_at"]
)

create_csv_if_missing(
    NODE_FILE,
    [
        ["N01", "ACTIVE", "2026-11-13 18:20", 125],
        ["N02", "ACTIVE", "2026-11-13 18:18", 98],
        ["N03", "ACTIVE", "2026-11-13 18:15", 76],
        ["N04", "INACTIVE", "2026-11-13 16:02", 42],
        ["N05", "ACTIVE", "2026-11-13 18:19", 111],
        ["N06", "ACTIVE", "2026-11-13 18:17", 63],
    ],
    ["node_id", "node_status", "last_heartbeat", "messages_forwarded"]
)

create_csv_if_missing(
    ROUTE_FILE,
    [
        ["R-001", "N01", "N02", "ACTIVE", "Primary communication path"],
        ["R-002", "N02", "N03", "ACTIVE", "Primary communication path"],
        ["R-003", "N03", "N04", "BLOCKED", "N04 inactive; verify alternate path"],
        ["R-004", "N02", "N05", "ACTIVE", "Alternate communication path"],
        ["R-005", "N05", "N06", "ACTIVE", "Alternate communication path"],
    ],
    ["route_id", "from_node", "to_node", "route_status", "notes"]
)

create_csv_if_missing(
    TEAM_FILE,
    [
        ["Team Alpha", "BUSY", "SOS-2026-005"],
        ["Team Bravo", "BUSY", "SOS-2026-007"],
        ["Team Charlie", "BUSY", "SOS-2026-010"],
    ],
    ["team_name", "team_status", "current_sos_id"]
)

# -------------------- DATA ACCESS --------------------
@st.cache_data
def read_all_data():
    """Read persistent CSV datasets using Pandas."""
    sos_df = pd.read_csv(SOS_FILE)
    family_df = pd.read_csv(FAMILY_FILE)
    node_df = pd.read_csv(NODE_FILE)
    route_df = pd.read_csv(ROUTE_FILE)
    team_df = pd.read_csv(TEAM_FILE)
    sos_df["created_at"] = pd.to_datetime(sos_df["created_at"], errors="coerce")
    return sos_df, family_df, node_df, route_df, team_df

def save_sos(df):
    output = df.copy()
    output["created_at"] = pd.to_datetime(output["created_at"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")
    output.to_csv(SOS_FILE, index=False)
    read_all_data.clear()

def save_teams(df):
    df.to_csv(TEAM_FILE, index=False)
    read_all_data.clear()

sos, families, nodes, routes, teams = read_all_data()

# -------------------- VISUAL THEME --------------------
st.markdown("""
<style>
    .stApp { background: #F3F6FA; }
    [data-testid="stSidebar"] { background: #10243A; }
    [data-testid="stSidebar"] * { color: #F4F7FB !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { font-weight: 600; }
    .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E3EAF2;
        padding: 15px 17px; border-radius: 13px;
        box-shadow: 0 2px 8px rgba(16,36,58,0.045);
    }
    div[data-testid="stMetricLabel"] { color: #61758A; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #10243A; font-weight: 800; }
    .traceon-subtitle { color: #687B8F; margin-top: -12px; margin-bottom: 22px; }
    .status-note { background: #EAF1F8; padding: 12px 15px; border-radius: 10px; color: #29445F; }
    div.stButton > button { border-radius: 9px; font-weight: 650; }
</style>
""", unsafe_allow_html=True)

# -------------------- COMMON FUNCTIONS --------------------
def page_header(title, subtitle):
    st.title(title)
    st.markdown(f'<div class="traceon-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def metric_cards(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)

def show_df(df, height=390):
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)

def priority_colour(priority):
    return {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}.get(priority, "⚪")

# -------------------- SIDEBAR NAVIGATION --------------------
with st.sidebar:
    st.markdown("# 🛟 TRACEON")
    st.caption("DISASTER RESCUE & COMMUNICATION")
    st.divider()
    selected_page = st.radio(
        "MAIN NAVIGATION",
        [
            "Command Dashboard",
            "SOS & HELP Alerts",
            "Family Management",
            "Communication Nodes",
            "Route Monitoring",
            "Rescue Progress",
            "Rescue Teams",
            "Reports & Analytics",
            "System Information"
        ],
        label_visibility="visible"
    )
    st.divider()
    st.markdown("### SYSTEM STATUS")
    st.success("Dashboard application active")
    st.warning("Hardware not connected")
    st.caption("Prototype mode • No GPS • No AI/ML")
    st.caption("Data source: CSV files")

# -------------------- 1. COMMAND DASHBOARD --------------------
if selected_page == "Command Dashboard":
    page_header("Rescue Command Dashboard", "Live-style overview of emergency alerts, rescue operations and communication network.")

    total_alerts = len(sos)
    high_count = int((sos["priority"] == "HIGH").sum())
    pending_count = int((sos["rescue_status"] == "PENDING").sum())
    progress_count = int((sos["rescue_status"] == "IN_PROGRESS").sum())
    rescued_count = int((sos["rescue_status"] == "RESCUED").sum())
    help_count = int((sos["alert_type"] == "HELP").sum())
    sos_count = int((sos["alert_type"] == "SOS").sum())

    metric_cards([
        ("TOTAL ALERTS", total_alerts),
        ("HIGH PRIORITY", high_count),
        ("SOS ALERTS", sos_count),
        ("HELP REQUESTS", help_count),
        ("PENDING CASES", pending_count),
    ])
    st.write("")
    metric_cards([
        ("IN PROGRESS", progress_count),
        ("RESCUED", rescued_count),
        ("ACTIVE NODES", int((nodes["node_status"] == "ACTIVE").sum())),
        ("BLOCKED ROUTES", int((routes["route_status"] == "BLOCKED").sum())),
        ("AVAILABLE TEAMS", int((teams["team_status"] == "AVAILABLE").sum())),
    ])

    st.divider()
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Emergency Priority Overview")
        priority_order = ["HIGH", "MEDIUM", "LOW"]
        priority_values = sos["priority"].value_counts().reindex(priority_order, fill_value=0)
        fig, ax = plt.subplots(figsize=(7, 3.6))
        sns.barplot(x=priority_values.index, y=priority_values.values, ax=ax)
        ax.set_xlabel("Priority Level")
        ax.set_ylabel("Number of Alerts")
        ax.set_title("Alerts grouped by priority")
        ax.grid(axis="y", alpha=0.2)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with right:
        st.subheader("Rescue Case Distribution")
        status_order = ["PENDING", "IN_PROGRESS", "RESCUED"]
        status_values = sos["rescue_status"].value_counts().reindex(status_order, fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 3.6))
        ax.pie(status_values.values, labels=status_values.index, autopct="%1.0f%%",
               startangle=90, wedgeprops={"width": 0.42})
        ax.set_title("Current rescue status")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.subheader("Latest Emergency Activity")
    latest = sos.sort_values("created_at", ascending=False).head(6).copy()
    latest["priority"] = latest["priority"].apply(lambda x: f"{priority_colour(x)} {x}")
    show_df(latest[["sos_id", "house_id", "alert_type", "priority", "rescue_status", "assigned_team", "created_at"]])

# -------------------- 2. SOS & HELP ALERTS --------------------
elif selected_page == "SOS & HELP Alerts":
    page_header("SOS & HELP Alert Centre", "Monitor distress alerts and assistance requests. Priority is assigned by rescue operators.")

    metric_cards([
        ("SOS DISTRESS ALERTS", int((sos["alert_type"] == "SOS").sum())),
        ("HELP REQUESTS", int((sos["alert_type"] == "HELP").sum())),
        ("HIGH PRIORITY", int((sos["priority"] == "HIGH").sum())),
        ("AWAITING ASSIGNMENT", int((sos["rescue_status"] == "PENDING").sum())),
    ])
    st.info("SOS indicates an emergency distress alert. HELP indicates an assistance request. The victim does not select priority; the rescue-side operator assigns it.")

    with st.expander("＋ Register a demonstration SOS / HELP alert"):
        with st.form("new_alert_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            family_ids = families["family_id"].astype(str).tolist()
            selected_family = c1.selectbox("Family ID", family_ids)
            alert_type = c2.selectbox("Alert type", ["SOS", "HELP"])
            priority = c3.selectbox("Rescue-side priority", ["HIGH", "MEDIUM", "LOW"])
            submit_alert = st.form_submit_button("Register Alert", type="primary")

            if submit_alert:
                fam = families[families["family_id"].astype(str) == selected_family].iloc[0]
                new_number = len(sos) + 1
                new_id = f"TRACEON-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                new_row = {
                    "sos_id": new_id,
                    "family_id": fam["family_id"],
                    "house_id": fam["house_id"],
                    "device_id": fam["device_id"],
                    "alert_type": alert_type,
                    "priority": priority,
                    "rescue_status": "PENDING",
                    "assigned_team": "",
                    "created_at": datetime.now()
                }
                updated = pd.concat([sos, pd.DataFrame([new_row])], ignore_index=True)
                save_sos(updated)
                st.success(f"{alert_type} alert registered for {fam['house_id']} as PENDING.")
                st.rerun()

    st.subheader("Filter Alerts")
    f1, f2, f3 = st.columns(3)
    priority_filter = f1.multiselect("Priority", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
    type_filter = f2.multiselect("Alert Type", ["SOS", "HELP"], default=["SOS", "HELP"])
    status_filter = f3.multiselect("Rescue Status", ["PENDING", "IN_PROGRESS", "RESCUED"],
                                   default=["PENDING", "IN_PROGRESS", "RESCUED"])
    filtered = sos[
        sos["priority"].isin(priority_filter)
        & sos["alert_type"].isin(type_filter)
        & sos["rescue_status"].isin(status_filter)
    ].sort_values("created_at", ascending=False)
    show_df(filtered)

# -------------------- 3. FAMILY MANAGEMENT --------------------
elif selected_page == "Family Management":
    page_header("Family & House Management", "View registered households using Family ID, House ID and Device ID. No GPS coordinates are used.")
    metric_cards([
        ("REGISTERED FAMILIES", len(families)),
        ("TOTAL PEOPLE", int(families["people_count"].sum())),
        ("UNIQUE HOUSE IDs", families["house_id"].nunique()),
    ])
    search = st.text_input("Search by Family ID, House ID, Device ID or area")
    view = families.copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    show_df(view)
    st.caption("Contact details are demonstration values. Replace them with authorised project data before any real deployment.")

# -------------------- 4. COMMUNICATION NODES --------------------
elif selected_page == "Communication Nodes":
    page_header("Communication Node Monitoring", "Monitor the prototype communication network's node status and message forwarding.")
    metric_cards([
        ("TOTAL NODES", len(nodes)),
        ("ACTIVE NODES", int((nodes["node_status"] == "ACTIVE").sum())),
        ("INACTIVE NODES", int((nodes["node_status"] == "INACTIVE").sum())),
        ("MESSAGES FORWARDED", int(nodes["messages_forwarded"].sum())),
    ])
    show_df(nodes)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    sns.barplot(data=nodes, x="node_id", y="messages_forwarded", hue="node_status", ax=ax)
    ax.set_title("Message forwarding by node (sample data)")
    ax.set_xlabel("Node ID")
    ax.set_ylabel("Messages forwarded")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.warning("Node status and message counts are sample records. Hardware is not connected, so these are not live readings.")

# -------------------- 5. ROUTE MONITORING --------------------
elif selected_page == "Route Monitoring":
    page_header("Communication Route Monitoring", "Inspect active, blocked and alternate logical paths between communication nodes.")
    metric_cards([
        ("TOTAL ROUTES", len(routes)),
        ("ACTIVE ROUTES", int((routes["route_status"] == "ACTIVE").sum())),
        ("BLOCKED ROUTES", int((routes["route_status"] == "BLOCKED").sum())),
    ])
    show_df(routes)
    blocked = routes[routes["route_status"] == "BLOCKED"]
    if not blocked.empty:
        st.error("Blocked route detected. Verify an alternate communication path before relying on this route.")
        st.write("Blocked route(s):", ", ".join(blocked["route_id"].astype(str)))
        st.info("Available alternate paths in this sample: N02 → N05 → N06.")
    st.caption("This is a logical node-network representation, not a geographic map.")

# -------------------- 6. RESCUE PROGRESS --------------------
elif selected_page == "Rescue Progress":
    page_header("Rescue Progress Tracking", "Track cases awaiting assignment, currently in progress and successfully rescued.")
    pending = int((sos["rescue_status"] == "PENDING").sum())
    active = int((sos["rescue_status"] == "IN_PROGRESS").sum())
    rescued = int((sos["rescue_status"] == "RESCUED").sum())
    metric_cards([("PENDING", pending), ("IN PROGRESS", active), ("RESCUED", rescued)])

    st.subheader("Update Case Status")
    case_ids = sos["sos_id"].astype(str).tolist()
    selected_case = st.selectbox("Select SOS / HELP case", case_ids)
    selected_row = sos[sos["sos_id"].astype(str) == selected_case].iloc[0]
    st.write(f"House: **{selected_row['house_id']}**  |  Priority: **{selected_row['priority']}**  |  Current status: **{selected_row['rescue_status']}**")

    new_status = st.selectbox("New rescue status", ["PENDING", "IN_PROGRESS", "RESCUED"])
    if st.button("Save Status Update", type="primary"):
        updated = sos.copy()
        row_index = updated.index[updated["sos_id"].astype(str) == selected_case][0]

        if new_status == "IN_PROGRESS":
            already_assigned = str(updated.loc[row_index, "assigned_team"]).strip()
            if already_assigned:
                updated.loc[row_index, "rescue_status"] = "IN_PROGRESS"
                save_sos(updated)
                st.success(f"Case updated. Assigned team: {already_assigned}")
                st.rerun()
            else:
                available = teams[teams["team_status"] == "AVAILABLE"]
                if available.empty:
                    updated.loc[row_index, "rescue_status"] = "PENDING"
                    updated.loc[row_index, "assigned_team"] = ""
                    save_sos(updated)
                    st.error("No rescue team is available. Case remains PENDING — Awaiting Assignment.")
                    st.rerun()
                else:
                    team_name = available.iloc[0]["team_name"]
                    updated.loc[row_index, "rescue_status"] = "IN_PROGRESS"
                    updated.loc[row_index, "assigned_team"] = team_name
                    team_updated = teams.copy()
                    team_idx = team_updated.index[team_updated["team_name"] == team_name][0]
                    team_updated.loc[team_idx, "team_status"] = "BUSY"
                    team_updated.loc[team_idx, "current_sos_id"] = selected_case
                    save_teams(team_updated)
                    save_sos(updated)
                    st.success(f"{team_name} assigned. Case is now IN_PROGRESS.")
                    st.rerun()

        elif new_status == "RESCUED":
            assigned = str(updated.loc[row_index, "assigned_team"]).strip()
            updated.loc[row_index, "rescue_status"] = "RESCUED"
            if assigned:
                team_updated = teams.copy()
                match = team_updated["team_name"] == assigned
                team_updated.loc[match, "team_status"] = "AVAILABLE"
                team_updated.loc[match, "current_sos_id"] = ""
                save_teams(team_updated)
                updated.loc[row_index, "assigned_team"] = assigned
            save_sos(updated)
            st.success("Case marked RESCUED. Any assigned team has been released.")
            st.rerun()
        else:
            assigned = str(updated.loc[row_index, "assigned_team"]).strip()
            if assigned:
                team_updated = teams.copy()
                match = team_updated["team_name"] == assigned
                team_updated.loc[match, "team_status"] = "AVAILABLE"
                team_updated.loc[match, "current_sos_id"] = ""
                save_teams(team_updated)
            updated.loc[row_index, "rescue_status"] = "PENDING"
            updated.loc[row_index, "assigned_team"] = ""
            save_sos(updated)
            st.success("Case moved to PENDING — Awaiting Assignment.")
            st.rerun()

    st.subheader("All Rescue Cases")
    show_df(sos.sort_values("created_at", ascending=False)[
        ["sos_id", "family_id", "house_id", "alert_type", "priority", "rescue_status", "assigned_team", "created_at"]
    ])

# -------------------- 7. RESCUE TEAMS --------------------
elif selected_page == "Rescue Teams":
    page_header("Rescue Team Management", "View team availability and current case assignments.")
    metric_cards([
        ("TOTAL TEAMS", len(teams)),
        ("AVAILABLE", int((teams["team_status"] == "AVAILABLE").sum())),
        ("BUSY", int((teams["team_status"] == "BUSY").sum())),
    ])
    show_df(teams)

# -------------------- 8. REPORTS & ANALYTICS --------------------
elif selected_page == "Reports & Analytics":
    page_header("Reports & Data Analytics", "Analyse alert priority, emergency type, rescue outcomes and operational patterns.")
    total = len(sos)
    if total:
        priority_counts = sos["priority"].value_counts().reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
        status_counts = sos["rescue_status"].value_counts().reindex(["PENDING", "IN_PROGRESS", "RESCUED"], fill_value=0)

        # NumPy: calculate percentage share of each priority.
        priority_percent = np.round((priority_counts.to_numpy() / max(total, 1)) * 100, 1)
        st.subheader("Priority Distribution")
        priority_table = pd.DataFrame({
            "Priority": priority_counts.index,
            "Alerts": priority_counts.to_numpy(),
            "Share (%)": priority_percent
        })
        show_df(priority_table)

        c1, c2 = st.columns(2)
        with c1:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(x=priority_counts.index, y=priority_counts.values, ax=ax)
            ax.set_title("Alert count by priority")
            ax.set_xlabel("Priority")
            ax.set_ylabel("Count")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with c2:
            cross = pd.crosstab(sos["priority"], sos["alert_type"]).reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(cross, annot=True, fmt="d", cmap="Blues", linewidths=0.5, ax=ax)
            ax.set_title("Priority vs SOS / HELP")
            ax.set_xlabel("Alert Type")
            ax.set_ylabel("Priority")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.subheader("Rescue Status Summary")
        status_summary = pd.DataFrame({
            "Rescue Status": status_counts.index,
            "Cases": status_counts.values
        })
        show_df(status_summary)

        report_csv = sos.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download SOS / HELP Report (CSV)",
            data=report_csv,
            file_name="TRACEON_SOS_HELP_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("No alert data is available for analysis.")

# -------------------- 9. SYSTEM INFORMATION --------------------
elif selected_page == "System Information":
    page_header("System Information & Data Source", "Technical details of the TRACEON Streamlit dashboard.")
    st.subheader("Development Components")
    st.markdown("""
    - **Streamlit:** interactive dashboard, sidebar navigation, tables, forms and metrics.
    - **Pandas:** reads and manages CSV datasets using `pd.read_csv()`.
    - **NumPy:** numerical calculations and percentage analysis.
    - **Matplotlib:** dashboard charts.
    - **Seaborn:** priority charts, heatmaps and node analysis.
    - **Folium:** not enabled in this GPS-free prototype because no geographic coordinates are collected.
    """)
    st.subheader("Data Storage")
    st.code(
        "TRACEON Streamlit App\n"
        "  └── traceon_data/\n"
        "       ├── sos_alerts.csv\n"
        "       ├── families.csv\n"
        "       ├── nodes.csv\n"
        "       ├── routes.csv\n"
        "       └── rescue_teams.csv",
        language="text"
    )
    st.warning("The CSV files are the dashboard's local prototype data store. They are not the existing TRACEON SQLite database.")
    st.subheader("Prototype Limitations")
    st.markdown("""
    - Hardware / LoRa nodes are not connected.
    - Node and route values are sample data, not real-time telemetry.
    - No GPS tracking or victim coordinates are used.
    - No AI / ML prediction is used.
    - This starter dashboard is for demonstration; add authentication and database security before real deployment.
    """)

# -------------------- FOOTER --------------------
st.divider()
st.caption("TRACEON | Disaster Rescue and Communication System | Streamlit Prototype | Hardware not connected | No GPS | No AI/ML")
