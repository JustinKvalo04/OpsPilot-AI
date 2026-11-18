import os
from dotenv import load_dotenv
import html
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed",
)


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("OPSPILOT_API_KEY", "")


DB_PATH = Path(
    os.getenv(
        "OPSPILOT_DB_PATH",
        str(BASE_DIR / "opspilot.db")
    )
)

API_URL = os.getenv(
    "OPSPILOT_API_URL",
    "http://127.0.0.1:8000"
)


BG = "#090D14"
CARD = "#151B27"
BORDER = "#293244"
BLUE = "#3B82F6"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


# ============================================================
# DARK THEME AND CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {
        background: #090D14 !important;
        color: #F8FAFC !important;
    }

    /* Remove sidebar completely */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Main content width */
    .block-container {
    max-width: 1600px;
    padding-top: 5rem !important;
    padding-bottom: 3rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

    /* Typography */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {
        color: #FFFFFF !important;
    }

    .stApp p,
    .stApp label {
        color: #E2E8F0;
    }

    /* Header branding */
    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 6px;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        background: #2563EB;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
        font-weight: 800;
    }

    .brand-name {
        color: #FFFFFF;
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -0.7px;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: #94A3B8;
        font-size: 12px;
        margin-top: 3px;
    }

    /* Top navigation */
    div[data-testid="stSegmentedControl"] {
        margin-top: 15px;
        margin-bottom: 12px;
    }

    div[data-testid="stSegmentedControl"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 9px 22px !important;
    }

    /* Page headings */
    .page-title {
        color: #FFFFFF;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-top: 12px;
        margin-bottom: 5px;
    }

    .page-description {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* KPI cards */
    .metric-card {
        background: #151B27;
        border: 1px solid #293244;
        border-radius: 14px;
        padding: 24px;
        min-height: 145px;
    }

    .metric-label {
        color: #A6B4CA;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .metric-footer {
        color: #94A3B8;
        font-size: 12px;
        margin-top: 10px;
    }

    /* Section headings */
    .section-title {
        color: #FFFFFF;
        font-size: 21px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 6px;
    }

    .section-description {
        color: #94A3B8;
        font-size: 13px;
        margin-bottom: 18px;
    }

    /* Policy cards */
    .policy-card {
        background: #151B27;
        border: 1px solid #293244;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .policy-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .policy-content {
        color: #CBD5E1;
        font-size: 13px;
        line-height: 1.7;
    }

    .policy-id {
        color: #60A5FA;
        font-size: 11px;
        margin-top: 12px;
    }

    /* Inputs */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background: #1C2533 !important;
        border-color: #334155 !important;
        color: #FFFFFF !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="input"] input {
        color: #FFFFFF !important;
    }

    [data-baseweb="tag"] {
        background: #2563EB !important;
    }

    [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    /* Charts */
    div[data-testid="stPlotlyChart"] {
        background: #151B27;
        border: 1px solid #293244;
        border-radius: 14px;
        padding: 12px;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #293244;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Buttons */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 9px !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: #1D4ED8 !important;
    }

    hr {
        border-color: #293244 !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .page-title {
            font-size: 27px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE AND API FUNCTIONS
# ============================================================

def load_data():
    if not DB_PATH.exists():
        st.error("OpsPilot database not found.")
        st.stop()

    try:
        with sqlite3.connect(DB_PATH) as connection:
            tickets = pd.read_sql_query(
                "SELECT * FROM tickets",
                connection,
            )

            history = pd.read_sql_query(
                """
                SELECT *
                FROM audit_logs
                ORDER BY id DESC
                """,
                connection,
            )

        return tickets, history

    except sqlite3.Error as error:
        st.error(f"Database error: {error}")
        st.stop()



def api_request(method, endpoint, payload=None):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=25,
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        detail = str(error)

        if error.response is not None:
            try:
                detail = error.response.json().get(
                    "detail",
                    detail,
                )
            except (ValueError, AttributeError):
                pass

        st.error(f"API error: {detail}")
        return None


def format_label(value):
    if value is None:
        return "Unassigned"

    try:
        if pd.isna(value):
            return "Unassigned"
    except (TypeError, ValueError):
        pass

    return str(value).replace("_", " ").title()


def safe_text(value):
    return html.escape(str(value))


def page_header(title, description):
    st.markdown(
        f'<div class="page-title">'
        f'{safe_text(title)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="page-description">'
        f'{safe_text(description)}</div>',
        unsafe_allow_html=True,
    )


def section_header(title, description=""):
    st.markdown(
        f'<div class="section-title">'
        f'{safe_text(title)}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.markdown(
            f'<div class="section-description">'
            f'{safe_text(description)}</div>',
            unsafe_allow_html=True,
        )


def metric_card(label, value, footer):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                {safe_text(label)}
            </div>
            <div class="metric-value">
                {value:,}
            </div>
            <div class="metric-footer">
                {safe_text(footer)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        height=340,
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20,
        ),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(
            color="#E2E8F0",
            size=12,
        ),
        title=None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(gridcolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


def show_policies(policies):
    if not policies:
        st.info("No matching policies found.")
        return

    for policy in policies:
        title = safe_text(policy.get("title", "Policy"))
        content = safe_text(policy.get("content", ""))
        policy_id = safe_text(policy.get("id", ""))

        st.markdown(
            f"""
            <div class="policy-card">
                <div class="policy-title">
                    {title}
                </div>
                <div class="policy-content">
                    {content}
                </div>
                <div class="policy-id">
                    {policy_id}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TOP HEADER AND NAVIGATION
# ============================================================

header_left, header_right = st.columns([5, 1])

with header_left:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">O</div>
            <div>
                <div class="brand-name">OpsPilot</div>
                <div class="brand-subtitle">
                    AI Operations Platform
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



with header_right:
    try:
        health_response = requests.get(
            f"{API_URL}/health",
            headers={"X-API-Key": API_KEY},
            timeout=2,
        )
        backend_online = health_response.ok
    except requests.exceptions.RequestException:
        backend_online = False

    if backend_online:
        st.markdown("🟢 **System Online**")
    else:
        st.markdown("🔴 **System Offline**")

    if st.button(
        "↻ Refresh",
        use_container_width=True,
    ):
        st.rerun()



page = st.segmented_control(
    "Navigation",
    options=[
        "Overview",
        "Tickets",
        "Knowledge Base",
        "Activity",
    ],
    default="Overview",
    key="main_navigation",
    label_visibility="collapsed",
)

if page is None:
    page = "Overview"

st.divider()


# ============================================================
# LOAD DATABASE
# ============================================================

tickets, history = load_data()


# ============================================================
# PAGE 1: OPERATIONS OVERVIEW
# ============================================================

if page == "Overview":

    page_header(
        "Operations Overview",
        "Monitor support activity, workflow performance, "
        "and team workloads.",
    )

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    section_header(
        "System Status",
        "Current status of OpsPilot's core services.",
    )


    api_online = False

    try:
        health_check = requests.get(
            f"{API_URL}/health",
            headers={"X-API-Key": API_KEY},
            timeout=3,
        )
        api_online = health_check.ok
    except requests.exceptions.RequestException:
        pass

    database_online = False

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("SELECT 1")
            database_online = True
    except sqlite3.Error:
        pass

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "API Server",
            "Online" if api_online else "Offline",
        )

    with s2:
        st.metric(
            "Database",
            "Connected" if database_online else "Offline",
        )

    with s3:
        st.metric(
            "AI Automation",
            "Available" if api_online else "Unavailable",
        )

    st.caption(
        "AI Automation availability reflects API connectivity, "
        "not the status of external AI providers."
    )

    st.divider()

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    filter1, filter2, filter3 = st.columns(3)

    department_options = sorted(
        tickets["assigned_department"]
        .fillna("Unassigned")
        .unique()
        .tolist()
    )

    status_options = sorted(
        tickets["status"]
        .dropna()
        .unique()
        .tolist()
    )

    priority_options = sorted(
        tickets["priority"]
        .fillna("Unassigned")
        .unique()
        .tolist()
    )

    with filter1:
        selected_departments = st.multiselect(
            "Department",
            department_options,
            default=department_options,
            format_func=format_label,
        )

    with filter2:
        selected_statuses = st.multiselect(
            "Status",
            status_options,
            default=status_options,
            format_func=format_label,
        )

    with filter3:
        selected_priorities = st.multiselect(
            "Priority",
            priority_options,
            default=priority_options,
            format_func=format_label,
        )

    filtered = tickets.copy()

    if not filtered.empty:
        filtered = filtered[
            filtered["assigned_department"]
            .fillna("Unassigned")
            .isin(selected_departments)
            &
            filtered["status"].isin(selected_statuses)
            &
            filtered["priority"]
            .fillna("Unassigned")
            .isin(selected_priorities)
        ]

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    total = len(filtered)

    pending = int(
        (filtered["status"] == "pending_approval").sum()
    )

    high = int(
        (filtered["priority"] == "high").sum()
    )

    approved = int(
        (filtered["status"] == "approved").sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Tickets",
            total,
            "Matching current filters",
        )

    with c2:
        metric_card(
            "Pending Approval",
            pending,
            "Awaiting human review",
        )

    with c3:
        metric_card(
            "High Priority",
            high,
            "Requires attention",
        )

    with c4:
        metric_card(
            "Approved Tickets",
            approved,
            "Completed reviews",
        )

    # --------------------------------------------------------
    # AUTOMATION AND RESPONSE METRICS
    # --------------------------------------------------------

    section_header(
        "Automation & Response Performance",
        "Live workflow and customer response metrics.",
    )

    automated_tickets = int(
        (history["action"] == "ticket_automated").sum()
    ) if not history.empty else 0

    with sqlite3.connect(DB_PATH) as conn:
        response_metrics = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS total_responses,
                SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) AS drafts,
                SUM(CASE WHEN status = 'pending_review' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved,
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) AS sent
            FROM customer_responses
            """,
            conn,
        ).fillna(0)

    metrics = response_metrics.iloc[0]


    a1, a2, a3, a4, a5 = st.columns(5)

    with a1:
        metric_card(
            "Automated Tickets",
            automated_tickets,
            "Completed automated workflows",
        )

    with a2:
        metric_card(
            "Response Drafts",
            int(metrics["drafts"]),
            "Saved drafts awaiting submission",
        )

    with a3:
        metric_card(
            "Awaiting Review",
            int(metrics["pending"]),
            "Responses requiring approval",
        )

    with a4:
        metric_card(
            "Approved Responses",
            int(metrics["approved"]),
            "Approved and ready to send",
        )

    with a5:
        metric_card(
            "Simulated Sends",
            int(metrics["sent"]),
            "Delivery simulations completed",
        )


    st.divider()


    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    section_header(
        "Ticket Analytics",
        "Ticket distribution and department workload.",
    )

    left, right = st.columns(2)

    with left:
        st.markdown("**Tickets by Status**")

        if filtered.empty:
            st.info("No matching tickets.")
        else:
            counts = (
                filtered["status"]
                .value_counts()
                .reset_index()
            )

            counts.columns = ["Status", "Count"]

            counts["Status"] = counts["Status"].map(
                format_label
            )

            fig = px.bar(
                counts,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_sequence=[
                    "#2563EB",
                    "#60A5FA",
                    "#93C5FD",
                    "#1D4ED8",
                    "#BFDBFE",
                ],
            )

            fig.update_layout(showlegend=False)
            show_chart(fig)

    with right:
        st.markdown("**Department Workload**")

        if filtered.empty:
            st.info("No matching tickets.")
        else:
            counts = (
                filtered["assigned_department"]
                .fillna("Unassigned")
                .value_counts()
                .reset_index()
            )

            counts.columns = ["Department", "Count"]

            counts["Department"] = counts[
                "Department"
            ].map(format_label)

            fig = px.pie(
                counts,
                names="Department",
                values="Count",
                hole=0.6,
                color_discrete_sequence=[
                    "#2563EB",
                    "#60A5FA",
                    "#93C5FD",
                    "#64748B",
                ],
            )

            show_chart(fig)

    left, right = st.columns(2)

    with left:
        st.markdown("**Priority Distribution**")

        if filtered.empty:
            st.info("No matching tickets.")
        else:
            counts = (
                filtered["priority"]
                .fillna("Unassigned")
                .value_counts()
                .reset_index()
            )

            counts.columns = ["Priority", "Count"]

            counts["Priority"] = counts[
                "Priority"
            ].map(format_label)

            fig = px.bar(
                counts,
                x="Priority",
                y="Count",
                color="Priority",
                color_discrete_map={
                    "High": "#EF4444",
                    "Medium": "#F59E0B",
                    "Low": "#10B981",
                    "Unassigned": "#64748B",
                },
            )

            fig.update_layout(showlegend=False)
            show_chart(fig)

    with right:
        st.markdown("**Workflow Activity**")

        if history.empty:
            st.info("No workflow activity.")
        else:
            counts = (
                history["action"]
                .value_counts()
                .reset_index()
            )

            counts.columns = ["Action", "Count"]

            counts["Action"] = counts["Action"].map(
                format_label
            )

            fig = px.bar(
                counts,
                x="Count",
                y="Action",
                orientation="h",
                color_discrete_sequence=[BLUE],
            )

            show_chart(fig)

    # --------------------------------------------------------
    # RESPONSE APPROVAL PIPELINE
    # --------------------------------------------------------

    section_header(
        "Response Approval Pipeline",
        "Track customer responses through the review process.",
    )

    with sqlite3.connect(DB_PATH) as conn:
        response_pipeline = pd.read_sql_query(
            """
            SELECT status, COUNT(*) AS count
            FROM customer_responses
            GROUP BY status
            """,
            conn,
        )

    pipeline_stages = [
        "draft",
        "pending_review",
        "approved",
        "rejected",
        "sent",
    ]

    pipeline_counts = {
        row["status"]: int(row["count"])
        for _, row in response_pipeline.iterrows()
    }

    pipeline_data = pd.DataFrame({
        "Stage": [
            "Draft",
            "Pending Review",
            "Approved",
            "Rejected",
            "Sent",
        ],
        "Responses": [
            pipeline_counts.get(stage, 0)
            for stage in pipeline_stages
        ],
    })

    fig = px.bar(
        pipeline_data,
        x="Stage",
        y="Responses",
        color="Stage",
        color_discrete_map={
            "Draft": "#64748B",
            "Pending Review": "#F59E0B",
            "Approved": "#3B82F6",
            "Rejected": "#EF4444",
            "Sent": "#10B981",
        },
        text="Responses",
    )

    fig.update_layout(
        showlegend=False,
        yaxis=dict(dtick=1),
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
    )

    show_chart(fig)


    # --------------------------------------------------------
    # RECENT AUTOMATION ACTIVITY
    # --------------------------------------------------------

    section_header(
        "Recent Automation Activity",
        "Latest tickets processed by OpsPilot automation.",
    )

    if history.empty:
        st.info("No automation activity recorded yet.")

    else:
        automation_history = history[
            history["action"] == "ticket_automated"
        ].copy()

        if automation_history.empty:
            st.info(
                "No automated workflows yet. "
                "Run an automated workflow to see activity here."
            )

        else:
            automation_history = automation_history.head(10)

            automation_history["Ticket"] = (
                automation_history["ticket_id"].astype(str).str[:8]
            )

            ticket_subjects = tickets.set_index("id")[
                "subject"
            ].to_dict()

            automation_history["Subject"] = (
                automation_history["ticket_id"]
                .map(ticket_subjects)
                .fillna("Unknown Ticket")
            )

            automation_history["Activity"] = (
                "Automated Workflow Completed"
            )

            display_columns = [
                "Ticket",
                "Subject",
                "Activity",
            ]

            if "timestamp" in automation_history.columns:
                automation_history["Time"] = (
                    automation_history["timestamp"]
                )
                display_columns.append("Time")

            st.dataframe(
                automation_history[display_columns],
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    # --------------------------------------------------------
    # RECENT TICKETS
    # --------------------------------------------------------

    section_header(
        "Recent Tickets",
        "Current support tickets matching your filters.",
    )

    display_tickets = filtered[
        [
            "id",
            "subject",
            "status",
            "assigned_department",
            "priority",
        ]
    ].copy()

    for column in [
        "status",
        "assigned_department",
        "priority",
    ]:
        display_tickets[column] = (
            display_tickets[column].map(format_label)
        )

    st.dataframe(
        display_tickets,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PAGE 2: TICKET MANAGEMENT
# ============================================================

elif page == "Tickets":

    page_header(
        "Ticket Management",
        "Review, process, and manage customer support tickets.",
    )

    # --------------------------------------------------------
    # CREATE NEW TICKET
    # --------------------------------------------------------

    with st.expander("＋ Create New Ticket"):

        with st.form("create_ticket_form"):
            new_subject = st.text_input(
                "Ticket Subject",
                placeholder="Example: Refund request",
            )

            new_message = st.text_area(
                "Customer Message",
                placeholder="Describe the customer's issue...",
            )


            submitted = st.form_submit_button(
                "✓ Ticket Created"
                if st.session_state.get("ticket_created_success")
                else "Create Ticket",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.get(
                    "ticket_created_success", False
                ),
            )


            if submitted:
                if (
                    len(new_subject.strip()) < 3
                    or len(new_message.strip()) < 10
                ):
                    st.warning(
                        "Subject must have at least 3 characters "
                        "and message at least 10 characters."
                    )
                else:
                    result = api_request(
                        "POST",
                        "/tickets",
                        {
                            "subject": new_subject.strip(),
                            "message": new_message.strip(),
                        },
                    )


                    if result is not None:
                        st.session_state["newly_created_ticket_id"] = result["id"]
                        st.session_state["ticket_created_success"] = True
                        st.rerun()


    st.divider()

    # --------------------------------------------------------
    # SEARCH AND SELECT TICKET
    # --------------------------------------------------------

    api_tickets = api_request("GET", "/tickets")

    if api_tickets is not None:

        search = st.text_input(
            "Search Tickets",
            placeholder="Search by subject or ticket ID...",
        )

        matching = [
            ticket
            for ticket in api_tickets
            if (
                search.lower() in ticket["subject"].lower()
                or search.lower() in ticket["id"].lower()
            )
        ]

        if not matching:
            st.info("No matching tickets found.")

        else:
            options = {
                (
                    f"{ticket['subject']} "
                    f"— {format_label(ticket['status'])} "
                    f"({ticket['id'][:8]})"
                ): ticket["id"]
                for ticket in matching
            }


            new_ticket_id = st.session_state.pop(
                "newly_created_ticket_id", None
            )

            ticket_labels = list(options.keys())

            if new_ticket_id:
                matching_label = next(
                    (
                        label
                        for label, ticket_id in options.items()
                        if ticket_id == new_ticket_id
                    ),
                    None,
                )

                if matching_label:
                    st.session_state["selected_ticket_label"] = matching_label

            selected_label = st.selectbox(
                "Select Ticket",
                ticket_labels,
                key="selected_ticket_label",
            )


            if st.session_state.get("ticket_created_success", False):

                st.success(
                    "Ticket created successfully! "
                    "Your new ticket is selected below."
                )


            selected_id = options[selected_label]

            ticket = next(
                item
                for item in matching
                if item["id"] == selected_id
            )

            st.divider()

            # ------------------------------------------------
            # TICKET DETAILS
            # ------------------------------------------------

            section_header("Ticket Details")

            left, right = st.columns(2)

            with left:
                st.write(
                    "**Subject:**",
                    ticket["subject"],
                )

                st.write(
                    "**Status:**",
                    format_label(ticket["status"]),
                )

                st.write(
                    "**Priority:**",
                    format_label(ticket["priority"]),
                )

            with right:
                st.write(
                    "**Department:**",
                    format_label(
                        ticket["assigned_department"]
                    ),
                )

                st.write(
                    "**Ticket ID:**",
                    ticket["id"],
                )

            st.markdown("**Customer Message**")
            st.info(ticket["message"])

            st.divider()

            # ------------------------------------------------
            # ONE-CLICK WORKFLOW AUTOMATION
            # ------------------------------------------------

            st.divider()

            section_header(
                "Workflow Automation",
                "Automatically classify, route, and prepare a response.",
            )

            if ticket["status"] == "new":
                if st.button(
                    "Run Automated Workflow",
                    type="primary",
                    use_container_width=True,
                    key=f"automate_{selected_id}",
                ):
                    with st.spinner("Running automated workflow..."):
                        result = api_request(
                            "POST",
                            f"/tickets/{selected_id}/automate",
                        )

                    if result is not None:
                        st.session_state["last_analysis"] = result
                        st.session_state["resolution_result"] = result

                        saved_response = result["saved_response"]

                        st.session_state[
                            f"draft_subject_{selected_id}"
                        ] = saved_response["subject"]

                        st.session_state[
                            f"draft_body_{selected_id}"
                        ] = saved_response["body"]

                        st.session_state[
                            f"draft_reviewed_{selected_id}"
                        ] = False

                        st.session_state[
                            f"draft_metadata_{selected_id}"
                        ] = result["response_draft"]

                        st.success(
                            "Workflow completed! Ticket classified, "
                            "department assigned, resolution generated, "
                            "and customer response saved."
                        )

                        st.rerun()
            else:
                st.info(
                    "This ticket has already been processed. "
                    "Automation is available for new tickets only."
                )

            # ------------------------------------------------
            # PROCESS TICKET WITH AI
            # ------------------------------------------------

            if ticket["status"] == "new":

                st.markdown("### AI Processing")

                st.caption(
                    "Classify this ticket, assign a department, "
                    "and determine whether human approval is needed."
                )

                if st.button(
                    "Process Ticket with AI",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.spinner("Processing ticket..."):
                        result = api_request(
                            "POST",
                            f"/tickets/{selected_id}/process",
                        )

                    if result is not None:
                        st.session_state[
                            "last_analysis"
                        ] = result

                        st.success(
                            "Ticket processed successfully."
                        )

                        st.rerun()

            # ------------------------------------------------
            # HUMAN APPROVAL
            # ------------------------------------------------

            elif ticket["status"] == "pending_approval":

                st.markdown("### Human Review Required")

                st.warning(
                    "This ticket requires approval before "
                    "the workflow can continue."
                )

                with st.form(
                    f"review_form_{selected_id}"
                ):
                    reviewer = st.text_input(
                        "Reviewer Name",
                    )

                    reason = st.text_area(
                        "Decision Reason",
                    )

                    decision = st.radio(
                        "Decision",
                        ["Approve", "Reject"],
                        horizontal=True,
                    )

                    submit_review = st.form_submit_button(
                        "Submit Review",
                        type="primary",
                        use_container_width=True,
                    )

                    if submit_review:
                        if (
                            not reviewer.strip()
                            or not reason.strip()
                        ):
                            st.warning(
                                "Reviewer and reason are required."
                            )
                        else:
                            result = api_request(
                                "POST",
                                f"/tickets/{selected_id}/approve",
                                {
                                    "approved": (
                                        decision == "Approve"
                                    ),
                                    "reviewer": reviewer.strip(),
                                    "reason": reason.strip(),
                                },
                            )

                            if result is not None:
                                st.success(
                                    f"Ticket {decision.lower()}d."
                                    if decision == "Approve"
                                    else "Ticket rejected."
                                )
                                st.rerun()

            else:
                st.info(
                    "This ticket has already been processed "
                    "or reviewed."
                )

            # ------------------------------------------------
            # AI ANALYSIS
            # ------------------------------------------------

            last_analysis = st.session_state.get(
                "last_analysis"
            )

            if (
                isinstance(last_analysis, dict)
                and last_analysis.get("ticket_id")
                == selected_id
            ):
                with st.expander(
                    "Latest AI Analysis",
                    expanded=True,
                ):
                    st.markdown("**Classification**")
                    st.json(
                        last_analysis.get("analysis", {})
                    )

                    st.markdown("**Workflow Decision**")
                    st.json(
                        last_analysis.get("workflow", {})
                    )

            # ------------------------------------------------
            # AI-ASSISTED RESOLUTION RECOMMENDATION
            # ------------------------------------------------

            st.divider()

            section_header(
                "AI-Assisted Resolution",
                "Suggested actions based on ticket classification "
                "and company policies.",
            )

            st.caption(
                "Recommendations are advisory only. "
                "No customer actions are executed automatically."
            )

            if st.button(
                "Generate Resolution Recommendation",
                type="primary",
                use_container_width=True,
                key=f"recommend_{selected_id}",
            ):
                with st.spinner("Generating recommendation..."):
                    result = api_request(
                        "GET",
                        f"/tickets/{selected_id}/recommendation",
                    )

                if result is not None:
                    st.session_state[
                        "resolution_result"
                    ] = result

            saved_result = st.session_state.get(
                "resolution_result"
            )

            if (
                isinstance(saved_result, dict)
                and saved_result.get("ticket_id") == selected_id
            ):
                recommendation = saved_result.get(
                    "resolution_recommendation", {}
                )

                st.markdown(
                    "### " + recommendation.get(
                        "recommendation_title",
                        "Resolution Recommendation",
                    )
                )

                r1, r2, r3 = st.columns(3)

                with r1:
                    st.metric(
                        "Department",
                        format_label(
                            recommendation.get(
                                "recommended_department"
                            )
                        ),
                    )

                with r2:
                    st.metric(
                        "Priority",
                        format_label(
                            recommendation.get("priority")
                        ),
                    )

                with r3:
                    st.metric(
                        "Human Approval",
                        "Required"
                        if recommendation.get(
                            "requires_human_approval"
                        )
                        else "Not Flagged",
                    )

                st.markdown("**Recommended Steps**")

                for number, step in enumerate(
                    recommendation.get(
                        "recommended_steps", []
                    ),
                    start=1,
                ):
                    st.write(f"{number}. {step}")

                st.markdown("**Reasoning**")
                st.write(
                    recommendation.get(
                        "reasoning",
                        "No reasoning available.",
                    )
                )

                st.markdown("**Referenced Policies**")

                policy_ids = recommendation.get(
                    "referenced_policies", []
                )

                if policy_ids:
                    st.write(", ".join(policy_ids))
                else:
                    st.info(
                        "No matching company policies found."
                    )

                if recommendation.get(
                    "requires_human_approval"
                ):
                    st.warning(
                        "Human approval is required before "
                        "performing sensitive actions."
                    )

                st.caption(
                    recommendation.get("disclaimer", "")
                )

            # ------------------------------------------------
            # CUSTOMER RESPONSE DRAFTING
            # ------------------------------------------------

            st.divider()

            section_header(
                "Customer Response Draft",
                "Generate, edit, and review a customer-facing reply.",
            )

            st.caption(
                "Drafts are not sent automatically. "
                "Review and verify all details before use."
            )

            if st.button(
                "Generate Customer Response",
                type="primary",
                use_container_width=True,
                key=f"generate_response_{selected_id}",
            ):
                with st.spinner("Preparing response draft..."):
                    result = api_request(
                        "GET",
                        f"/tickets/{selected_id}/response-draft",
                    )

                if result is not None:
                    draft = result.get("draft", {})

                    st.session_state[
                        f"draft_subject_{selected_id}"
                    ] = draft.get("subject", "")

                    st.session_state[
                        f"draft_body_{selected_id}"
                    ] = draft.get("body", "")

                    st.session_state[
                        f"draft_metadata_{selected_id}"
                    ] = draft

                    st.session_state[
                        f"draft_reviewed_{selected_id}"
                    ] = False

                    st.rerun()

            draft_key = f"draft_body_{selected_id}"
            subject_key = f"draft_subject_{selected_id}"
            reviewed_key = f"draft_reviewed_{selected_id}"
            metadata_key = f"draft_metadata_{selected_id}"

            # Automatically restore a saved response when opening a ticket
            if draft_key not in st.session_state:
                existing_result = api_request(
                    "GET",
                    f"/tickets/{selected_id}/saved-response",
                )

                if existing_result is not None:
                    existing_response = existing_result.get("response")

                    if existing_response:
                        st.session_state[subject_key] = (
                            existing_response["subject"]
                        )
                        st.session_state[draft_key] = (
                            existing_response["body"]
                        )
                        st.session_state[reviewed_key] = False
                        st.session_state[metadata_key] = {
                            "referenced_policies": [],
                            "review_notes": (
                                "This response was restored from "
                                "the saved database record."
                            ),
                        }

            if draft_key in st.session_state:

                metadata = st.session_state.get(
                    metadata_key, {}
                )

                st.markdown("### Response Editor")

                def clear_draft_review():
                    st.session_state[reviewed_key] = False

                response_result = api_request(
                    "GET",
                    f"/tickets/{selected_id}/saved-response",
                )

                current_response = (
                    response_result.get("response")
                    if response_result else None
                )

                response_locked = (
                    current_response is not None
                    and current_response["status"] in (
                        "approved",
                        "sent",
                    )
                )

                if response_locked:
                    st.info(
                        "This response is approved or sent "
                        "and cannot be edited."
                    )


                edited_subject = st.text_input(
                    "Email Subject",
                    key=subject_key,
                    on_change=clear_draft_review,
                    disabled=response_locked,
                )



                edited_body = st.text_area(
                    "Customer Response",
                    key=draft_key,
                    height=300,
                    on_change=clear_draft_review,
                    disabled=response_locked,
                )


                st.markdown("**Internal Review Information**")

                policy_ids = metadata.get(
                    "referenced_policies", []
                )

                st.write(
                    "Referenced policies:",
                    ", ".join(policy_ids)
                    if policy_ids else "None found",
                )

                if metadata.get(
                    "requires_human_approval", False
                ):
                    st.warning(
                        "The ticket workflow requires human "
                        "approval before restricted actions."
                    )

                st.info(
                    metadata.get(
                        "review_notes",
                        "Verify the draft before use.",
                    )
                )

                # Any edit must be reviewed again.
                # The review checkbox is an acknowledgement,
                # not a backend authorization.

                reviewed = st.checkbox(
                    "I have reviewed the response and verified "
                    "that it is appropriate for this customer.",
                    key=reviewed_key,
                )

                if reviewed:
                    st.success(
                        "Draft marked as reviewed in this session."
                    )

                    st.caption(
                        "This does not change ticket approval "
                        "status or send the response."
                    )

                    response_text = (
                        f"Subject: {edited_subject}\n\n"
                        f"{edited_body}"
                    )

                    st.code(
                        response_text,
                        language=None,
                    )

                    st.caption(
                        "Copy the text above to use it in "
                        "your customer communication system."
                    )

                else:
                    st.caption(
                        "Review the draft and select the "
                        "checkbox before using it."
                    )

            # ------------------------------------------------
            # RESPONSE MANAGEMENT
            # ------------------------------------------------

            st.divider()

            section_header(
                "Response Management",
                "Save drafts, approve responses, and simulate delivery.",
            )

            actor = st.text_input(
                "Employee / Reviewer Name",
                value="Demo Operator",
                key=f"response_actor_{selected_id}",
            )

            saved_result = api_request(
                "GET",
                f"/tickets/{selected_id}/saved-response",
            )

            saved_response = (
                saved_result.get("response")
                if saved_result else None
            )

            if saved_response:
                status = saved_response["status"]

                st.markdown(
                    f"**Current Response Status:** "
                    f"`{status.upper().replace('_', ' ')}`"
                )

                st.caption(
                    f"Last updated: {saved_response['updated_at']}"
                )

                if saved_response.get("reviewer"):
                    st.write(
                        "Reviewer:",
                        saved_response["reviewer"],
                    )
            else:
                status = None
                st.info("No saved response for this ticket yet.")

            draft_subject_key = f"draft_subject_{selected_id}"
            draft_body_key = f"draft_body_{selected_id}"

            if (
                draft_subject_key in st.session_state
                and draft_body_key in st.session_state
                and status != "sent"
            ):
                if st.button(
                    "Save Response Draft",
                    use_container_width=True,
                    key=f"save_response_{selected_id}",
                ):
                    result = api_request(
                        "POST",
                        f"/tickets/{selected_id}/saved-response",
                        {
                            "subject": st.session_state[draft_subject_key],
                            "body": st.session_state[draft_body_key],
                            "actor": actor,
                        },
                    )

                    if result is not None:
                        st.success("Response saved to SQLite.")
                        st.rerun()

            if status == "draft":
                if st.button(
                    "Submit for Review",
                    use_container_width=True,
                    key=f"submit_response_{selected_id}",
                ):
                    result = api_request(
                        "POST",
                        f"/tickets/{selected_id}/response-action/submit",
                        {
                            "actor": actor,
                        },
                    )

                    if result is not None:
                        st.rerun()

            elif status == "pending_review":
                review_reason = st.text_input(
                    "Review Notes",
                    key=f"response_reason_{selected_id}",
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Approve Response",
                        use_container_width=True,
                        key=f"approve_response_{selected_id}",
                    ):
                        result = api_request(
                            "POST",
                            f"/tickets/{selected_id}/response-action/approve",
                            {
                                "actor": actor,
                                "reason": review_reason,
                            },
                        )

                        if result is not None:
                            st.rerun()

                with col2:
                    if st.button(
                        "Reject Response",
                        use_container_width=True,
                        key=f"reject_response_{selected_id}",
                    ):
                        result = api_request(
                            "POST",
                            f"/tickets/{selected_id}/response-action/reject",
                            {
                                "actor": actor,
                                "reason": review_reason,
                            },
                        )

                        if result is not None:
                            st.rerun()

            elif status == "rejected":
                if st.button(
                    "Reopen Draft",
                    use_container_width=True,
                    key=f"reopen_response_{selected_id}",
                ):
                    result = api_request(
                        "POST",
                        f"/tickets/{selected_id}/response-action/reopen",
                        {
                            "actor": actor,
                        },
                    )

                    if result is not None:
                        st.rerun()

            elif status == "approved":
                st.warning(
                    "This action only simulates delivery. "
                    "No real email will be sent."
                )

                if st.button(
                    "Simulate Send",
                    use_container_width=True,
                    key=f"simulate_send_{selected_id}",
                ):
                    result = api_request(
                        "POST",
                        f"/tickets/{selected_id}/response-action/simulate_send",
                        {
                            "actor": actor,
                        },
                    )

                    if result is not None:
                        st.success("Delivery simulated successfully.")
                        st.rerun()

            elif status == "sent":
                st.success(
                    "Response marked as sent (simulation only)."
                )

            with st.expander("Response Audit History"):
                history_result = api_request(
                    "GET",
                    f"/tickets/{selected_id}/response-history",
                )

                if history_result is not None:
                    response_history = history_result.get(
                        "history", []
                    )

                    if response_history:
                        st.dataframe(
                            pd.DataFrame(response_history),
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.caption("No response activity recorded.")

            # ------------------------------------------------
            # RELEVANT POLICIES
            # ------------------------------------------------

            with st.expander(
                "Relevant Company Policies"
            ):
                policies = api_request(
                    "GET",
                    f"/tickets/{selected_id}/knowledge",
                )

                if policies is not None:
                    show_policies(
                        policies.get(
                            "relevant_policies",
                            [],
                        )
                    )

            # ------------------------------------------------
            # TICKET AUDIT HISTORY
            # ------------------------------------------------

            with st.expander(
                "Ticket Audit History"
            ):
                audit = api_request(
                    "GET",
                    f"/tickets/{selected_id}/history",
                )

                if audit is not None:
                    if isinstance(audit, list):
                        audit_rows = audit
                    else:
                        audit_rows = audit.get(
                            "history",
                            [],
                        )

                    if audit_rows:
                        st.dataframe(
                            pd.DataFrame(audit_rows),
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.info(
                            "No audit history available."
                        )


# ============================================================
# PAGE 3: KNOWLEDGE BASE
# ============================================================

elif page == "Knowledge Base":

    page_header(
        "Knowledge Base",
        "Search internal company policies and "
        "support documentation.",
    )

    st.markdown(
        "Find company policies related to refunds, "
        "account management, technical support, "
        "and customer communication."
    )

    query = st.text_input(
        "Search Company Policies",
        placeholder=(
            "Try: refund, password reset, technical error..."
        ),
    )

    if query.strip():

        try:
            response = requests.get(
                f"{API_URL}/knowledge/search",
                params={"query": query.strip()},
                headers={"X-API-Key": API_KEY},
                timeout=20,
            )

            response.raise_for_status()
            result = response.json()

            st.caption(
                f"{result.get('total_results', 0)} "
                "matching policies"
            )

            show_policies(
                result.get("results", [])
            )

        except requests.exceptions.RequestException as error:
            st.error(
                f"Knowledge base search failed: {error}"
            )

    else:
        st.info(
            "Enter a search term to find relevant "
            "company policies."
        )


# ============================================================
# PAGE 4: ACTIVITY AND AUDIT LOGS
# ============================================================

elif page == "Activity":

    page_header(
        "Activity & Audit Logs",
        "Monitor recorded ticket actions, "
        "approvals, and workflow events.",
    )

    total_events = len(history)

    approvals = int(
        (history["action"] == "ticket_approved").sum()
    )

    rejections = int(
        (history["action"] == "ticket_rejected").sum()
    )

    # --------------------------------------------------------
    # ACTIVITY METRICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Total Events",
            total_events,
            "All recorded workflow activity",
        )

    with c2:
        metric_card(
            "Approvals",
            approvals,
            "Approved review decisions",
        )

    with c3:
        metric_card(
            "Rejections",
            rejections,
            "Rejected review decisions",
        )

    # --------------------------------------------------------
    # AUDIT HISTORY
    # --------------------------------------------------------

    section_header(
        "Audit History",
        "Complete record of ticket actions "
        "and workflow decisions.",
    )

    if history.empty:
        st.info("No audit activity recorded.")

    else:
        action_options = sorted(
            history["action"].unique().tolist()
        )

        selected_actions = st.multiselect(
            "Filter by Action",
            action_options,
            default=action_options,
            format_func=format_label,
        )

        filtered_history = history[
            history["action"].isin(selected_actions)
        ].copy()

        filtered_history["action"] = (
            filtered_history["action"].map(
                format_label
            )
        )

        st.dataframe(
            filtered_history,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_left, footer_right = st.columns([4, 1])

with footer_left:
    st.caption(
        "OpsPilot AI | Python • FastAPI • SQLite • "
        "Streamlit • Plotly"
    )

with footer_right:
    st.caption("Version 0.5 | Local")
