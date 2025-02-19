import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import altair as alt
from PIL import Image
from datetime import datetime
import os

# ---------- 1) Thread-safe SQLite connection ----------
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('industry_4_0_app.db', check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()

# ---------- 2) Session State Management ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- 3) Create necessary tables ----------
def create_tables():
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, 
            password TEXT, 
            role TEXT,
            department TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            department_name TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            year TEXT, 
            jjm_strategic_pillars TEXT,
            target_main_category TEXT,
            target_sub_category TEXT,
            target_16_dimensions TEXT,
            jjm_action_plan TEXT,
            start_date TEXT, 
            end_date TEXT, 
            roadmap_captain TEXT,
            project_leaders TEXT,
            project_owners TEXT,
            task_status TEXT,
            task_completion_rate REAL, 
            jjm_comments TEXT,
            target_remark TEXT,
            manager TEXT
        )
    ''')
    
    # If "manager" column was missing in older DB, add it
    c.execute("PRAGMA table_info(projects)")
    columns_info = c.fetchall()
    existing_cols = [col[1] for col in columns_info]
    if "manager" not in existing_cols:
        c.execute("ALTER TABLE projects ADD COLUMN manager TEXT;")
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dimensions (
            dimension_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            dimension_name TEXT,
            dimension_score INTEGER,
            timestamp TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS training_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            description TEXT, 
            schedule TEXT, 
            material_path TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER, 
            session_id INTEGER,
            status TEXT,
            FOREIGN KEY(session_id) REFERENCES training_sessions(session_id)
        )
    ''')
    conn.commit()

create_tables()

# ---------- 4) User Authentication Functions ----------
def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, password))
    return c.fetchone()

def add_user(username, password, role, department):
    c.execute('INSERT INTO users (username, password, role, department) VALUES (?, ?, ?, ?)',
              (username, password, role, department))
    conn.commit()

def get_all_users():
    c.execute('SELECT * FROM users')
    return c.fetchall()

def get_all_departments():
    c.execute('SELECT * FROM departments')
    return c.fetchall()

def add_department(department_name):
    c.execute('INSERT INTO departments (department_name) VALUES (?)', (department_name,))
    conn.commit()

# ---------- 5) Project Management ----------
def add_project(project_name, year, jjm_strategic_pillars, target_main_category,
                target_sub_category, target_16_dimensions, jjm_action_plan,
                start_date, end_date, roadmap_captain, project_leaders,
                project_owners, task_status, task_completion_rate, jjm_comments,
                target_remark, manager):
    c.execute('''
        INSERT INTO projects (
            project_name, year, jjm_strategic_pillars, target_main_category,
            target_sub_category, target_16_dimensions, jjm_action_plan,
            start_date, end_date, roadmap_captain, project_leaders, project_owners,
            task_status, task_completion_rate, jjm_comments, target_remark, manager
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
        project_name, year, jjm_strategic_pillars, target_main_category,
        target_sub_category, target_16_dimensions, jjm_action_plan, str(start_date),
        str(end_date), roadmap_captain, project_leaders, project_owners,
        task_status, task_completion_rate, jjm_comments, target_remark, manager
    ))
    conn.commit()

def update_project(project_id, project_name, year, jjm_strategic_pillars, target_main_category,
                   target_sub_category, target_16_dimensions, jjm_action_plan,
                   start_date, end_date, roadmap_captain, project_leaders,
                   project_owners, task_status, task_completion_rate, jjm_comments,
                   target_remark, manager):
    c.execute('''
        UPDATE projects
        SET project_name=?,
            year=?,
            jjm_strategic_pillars=?,
            target_main_category=?,
            target_sub_category=?,
            target_16_dimensions=?,
            jjm_action_plan=?,
            start_date=?,
            end_date=?,
            roadmap_captain=?,
            project_leaders=?,
            project_owners=?,
            task_status=?,
            task_completion_rate=?,
            jjm_comments=?,
            target_remark=?,
            manager=?
        WHERE project_id=?
    ''',
    (
        project_name, year, jjm_strategic_pillars, target_main_category,
        target_sub_category, target_16_dimensions, jjm_action_plan, str(start_date),
        str(end_date), roadmap_captain, project_leaders, project_owners,
        task_status, task_completion_rate, jjm_comments, target_remark, manager, project_id
    ))
    conn.commit()

def get_all_projects():
    c.execute('SELECT * FROM projects')
    return c.fetchall()

def get_project_by_name(project_name):
    c.execute('SELECT * FROM projects WHERE project_name = ?', (project_name,))
    return c.fetchone()

def update_project_status(project_id, new_status):
    c.execute('UPDATE projects SET task_status = ? WHERE project_id = ?', (new_status, project_id))
    conn.commit()

def get_project_status():
    c.execute("SELECT task_status, COUNT(*) FROM projects GROUP BY task_status")
    return c.fetchall()

# ---------- 6) Progress / Training ----------
def get_user_progress(user_id):
    c.execute('SELECT session_id, status FROM user_progress WHERE user_id = ?', (user_id,))
    return c.fetchall()

# ---------- 7) Excel Processing: Soft error handling ----------
def process_excel_file(uploaded_file):
    """
    Reads Excel, skipping rows that are missing 'Project Name' entirely.
    'Start Date'/'End Date' are attempted best-effort. 
    Missing columns won't cause a crash; we fill with None or skip if absolutely necessary.
    """
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.warning(f"Failed to read Excel: {e}")
        return

    # Map Excel columns to DB fields. If any column is missing, we won't error out.
    mapping = {
        "Project Name": "project_name",
        "Year": "year",
        "JJM Strategic Pillars": "jjm_strategic_pillars",
        "Target Main Category": "target_main_category",
        "Target Sub Category": "target_sub_category",
        "Target 16 Dimensions": "target_16_dimensions",
        "JJM Action Plan": "jjm_action_plan",
        "Start Date": "start_date",
        "End Date": "end_date",
        "Roadmap Captain": "roadmap_captain",
        "Project Leaders": "project_leaders",
        "Project Owners": "project_owners",
        "Task Status": "task_status",
        "Task Completion Rate": "task_completion_rate",
        "JJM Comments": "jjm_comments",
        "Target Remark": "target_remark",
        "Manager": "manager",
    }

    for idx, row in df.iterrows():
        # Construct a dict from the row
        row_data = {}
        for excel_col, db_field in mapping.items():
            if excel_col in df.columns:
                # If the row doesn't have a valid value, store None
                row_data[db_field] = row.get(excel_col, None)
            else:
                # This column missing in Excel, store None
                row_data[db_field] = None

        p_name = row_data.get("project_name", "")
        if not p_name or pd.isna(p_name):
            st.warning(f"Skipping row {idx+1}: no Project Name.")
            continue

        # Attempt to parse start_date / end_date as string
        start_date_val = row_data.get("start_date")
        end_date_val = row_data.get("end_date")

        # Convert if it's a Timestamp
        if pd.notnull(start_date_val) and hasattr(start_date_val, "strftime"):
            start_date_val = start_date_val.strftime("%Y-%m-%d")
        else:
            # If it's NaN or missing, store blank
            start_date_val = "" if not start_date_val else str(start_date_val)

        if pd.notnull(end_date_val) and hasattr(end_date_val, "strftime"):
            end_date_val = end_date_val.strftime("%Y-%m-%d")
        else:
            end_date_val = "" if not end_date_val else str(end_date_val)

        # Convert numeric
        tcr_val = 0.0
        try:
            tcr_val = float(row_data.get("task_completion_rate") or 0.0)
        except:
            tcr_val = 0.0

        # Check if project exists
        existing = get_project_by_name(p_name)
        if existing:
            # Update
            pid = existing[0]
            update_project(
                project_id=pid,
                project_name=p_name,
                year=row_data.get("year", ""),
                jjm_strategic_pillars=row_data.get("jjm_strategic_pillars", ""),
                target_main_category=row_data.get("target_main_category", ""),
                target_sub_category=row_data.get("target_sub_category", ""),
                target_16_dimensions=row_data.get("target_16_dimensions", ""),
                jjm_action_plan=row_data.get("jjm_action_plan", ""),
                start_date=start_date_val,
                end_date=end_date_val,
                roadmap_captain=row_data.get("roadmap_captain", ""),
                project_leaders=row_data.get("project_leaders", ""),
                project_owners=row_data.get("project_owners", ""),
                task_status=row_data.get("task_status", "Not Started"),
                task_completion_rate=tcr_val,
                jjm_comments=row_data.get("jjm_comments", ""),
                target_remark=row_data.get("target_remark", ""),
                manager=row_data.get("manager", "")
            )
            st.success(f"Updated project '{p_name}' from Excel row {idx+1}.")
        else:
            # Insert
            add_project(
                project_name=p_name,
                year=row_data.get("year", ""),
                jjm_strategic_pillars=row_data.get("jjm_strategic_pillars", ""),
                target_main_category=row_data.get("target_main_category", ""),
                target_sub_category=row_data.get("target_sub_category", ""),
                target_16_dimensions=row_data.get("target_16_dimensions", ""),
                jjm_action_plan=row_data.get("jjm_action_plan", ""),
                start_date=start_date_val,
                end_date=end_date_val,
                roadmap_captain=row_data.get("roadmap_captain", ""),
                project_leaders=row_data.get("project_leaders", ""),
                project_owners=row_data.get("project_owners", ""),
                task_status=row_data.get("task_status", "Not Started"),
                task_completion_rate=tcr_val,
                jjm_comments=row_data.get("jjm_comments", ""),
                target_remark=row_data.get("target_remark", ""),
                manager=row_data.get("manager", "")
            )
            st.success(f"Inserted new project '{p_name}' from Excel row {idx+1}.")

# ---------- 8) Visualization / Reporting ----------
def visualize_projects():
    st.subheader("Project Dashboard Overview")

    # Fetch DB
    projects = get_all_projects()
    df = pd.DataFrame(projects, columns=[
        "ID", "Project Name", "Year", "JJM Strategic Pillars", "Target Main Category",
        "Target Sub Category", "Target 16 Dimensions", "JJM Action Plan", "Start Date",
        "End Date", "Roadmap Captain", "Project Leaders", "Project Owners",
        "Task Status", "Task Completion Rate", "JJM Comments", "Target Remark",
        "Manager"
    ])

    # Convert date columns to datetime for analysis
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["End Date"]   = pd.to_datetime(df["End Date"], errors="coerce")

    # ========== Number Cards with multiple statuses ==========
    colA, colB, colC, colD = st.columns(4)
    total_projects = len(df)
    colA.metric("Total Projects", total_projects)

    # Let's also show Completed
    completed_projects = len(df[df["Task Status"] == "Completed"])
    colB.metric("Completed", completed_projects)

    # In Progress
    in_progress_projects = len(df[df["Task Status"] == "In Progress"])
    colC.metric("In Progress", in_progress_projects)

    # Delayed: EndDate < now, not completed
    now = datetime.now()
    delayed_projects = df[
        (df["End Date"].notnull()) &
        (df["End Date"] < now) &
        (df["Task Status"] != "Completed")
    ]
    colD.metric("Delayed", len(delayed_projects))

    # Another row for other statuses
    st.write("## Additional Status Counts:")
    colX, colY, colZ = st.columns(3)
    trial_done = len(df[df["Task Status"] == "Trial Done"])
    colX.metric("Trial Done", trial_done)

    in_testing = len(df[df["Task Status"] == "In Testing"])
    colY.metric("In Testing", in_testing)

    deployed = len(df[df["Task Status"] == "Production Deployed"])
    colZ.metric("Deployed", deployed)

    # ========== Project Status Visualization (Plotly bar) ==========
    status_counts = df["Task Status"].value_counts()
    status_df = pd.DataFrame({"Task Status": status_counts.index, "Count": status_counts.values})
    fig_status_bar = px.bar(
        status_df, x="Task Status", y="Count",
        title="Project Status Overview",
        color="Task Status"
    )
    st.plotly_chart(fig_status_bar, use_container_width=True)

    # ========== Completion Rate Visualization (Altair) ==========
    df["Task Completion Rate"] = pd.to_numeric(df["Task Completion Rate"], errors="coerce").fillna(0)
    chart = alt.Chart(df).mark_line().encode(
        x='JJM Strategic Pillars',
        y='Task Completion Rate',
        color='Target Main Category'
    ).properties(
        title="Task Completion Rate Across Projects"
    )
    st.altair_chart(chart, use_container_width=True)

    # ========== Milestone Visualization (Altair bar) ==========
    mile_df = df.groupby("Target Main Category")["Task Completion Rate"].mean().reset_index()
    milestone_chart = alt.Chart(mile_df).mark_bar().encode(
        x='Target Main Category',
        y='Task Completion Rate',
        color='Target Main Category'
    ).properties(
        title="Milestone Progress by Category"
    )
    st.altair_chart(milestone_chart, use_container_width=True)

    # ========== Scatter of Completion Rate vs. Strategic Pillars (Plotly) ==========
    scatter_fig = px.scatter(
        df, x="JJM Strategic Pillars", y="Task Completion Rate",
        color="Target Main Category", hover_data=["Project Name"],
        title="Completion Rate vs. JJM Strategic Pillars"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    # ========== Kanban Board Visualization ==========
    st.subheader("Kanban Board")
    kanban_df = df[["Project Name", "Task Status"]].copy()
    status_order = [
        "Not Started", "In Progress", "Trial Done",
        "In Testing", "Production Deployed", "Running", "Completed"
    ]
    # We'll create columns for each status
    kanban_cols = st.columns(len(status_order))
    for i, status in enumerate(status_order):
        with kanban_cols[i]:
            st.markdown(f"### {status}")
            subset = kanban_df[kanban_df["Task Status"] == status]
            for _, row in subset.iterrows():
                # Show each project as a "card"
                st.info(f"**{row['Project Name']}**")

    # ========== Additional Visualizations ==========

    # Bar chart for JJM Strategic Pillars (# of projects, # completed)
    st.subheader("Projects by JJM Strategic Pillars")
    pillar_group = df.groupby('JJM Strategic Pillars').agg(
        Total_Projects=('Project Name', 'count'),
        Completed_Projects=('Task Status', lambda x: (x == 'Completed').sum())
    ).reset_index()

    # Ensure both columns are of the same numeric type (e.g., int)
    pillar_group['Total_Projects'] = pillar_group['Total_Projects'].astype(int)
    pillar_group['Completed_Projects'] = pillar_group['Completed_Projects'].astype(int)

    fig_pillars = px.bar(
        pillar_group,
        x='JJM Strategic Pillars',
        y=['Total_Projects', 'Completed_Projects'],
        labels={'value': 'Number of Projects', 'variable': 'Project Status'},
        title='Projects by JJM Strategic Pillars',
        barmode='group'
    )
    st.plotly_chart(fig_pillars, use_container_width=True)

    # Pie chart for Target Main Category
    st.subheader("Projects by Target Main Category")
    category_counts = df['Target Main Category'].value_counts(dropna=True)
    fig_category = px.pie(
        names=category_counts.index,
        values=category_counts.values,
        title='Distribution of Projects by Main Category'
    )
    st.plotly_chart(fig_category, use_container_width=True)

    # Bar chart for Target 16 Dimensions
    st.subheader("Projects by Target 16 Dimensions")
    dims_counts = df['Target Sub Category'].value_counts()
    dims_df = pd.DataFrame({'Target Sub Category': dims_counts.index, 'Count': dims_counts.values})
    fig_dimensions = px.bar(
        dims_df,
        x='Target Sub Category',
        y='Count',
        labels={'x': 'Target Sub Category', 'y': 'Count'},
        title='Number of Projects by Sub Category'
    )
    st.plotly_chart(fig_dimensions, use_container_width=True)

    # Grouped bar for Task Status by Manager
    st.subheader("Task Status by Manager")
    status_by_manager = df.groupby(['Manager', 'Task Status']).size().unstack(fill_value=0)
    if not status_by_manager.empty:
        fig_manager_status = px.bar(
            status_by_manager,
            x=status_by_manager.index,
            y=status_by_manager.columns,
            labels={'value': 'Count', 'index': 'Manager'},
            title='Task Status by Manager'
        )
        st.plotly_chart(fig_manager_status, use_container_width=True)

    # ========== Gantt Chart ==========
    st.subheader("Gantt Chart")
    # For Gantt, we need 'Task', 'Start', 'Finish'
    # We'll color by "Task Status"
    # We'll skip rows missing Start or End
    gantt_df = df.dropna(subset=["Start Date", "End Date"]).copy()
    # Make sure they're strings recognized by px.timeline
    gantt_df["Start"] = gantt_df["Start Date"].dt.strftime("%Y-%m-%d")
    gantt_df["Finish"] = gantt_df["End Date"].dt.strftime("%Y-%m-%d")
    if len(gantt_df):
        fig_gantt = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Project Name",
            color="Task Status",
            hover_data=["Task Completion Rate", "Manager"],
            title="Project Gantt Chart"
        )
        # Reverse y-axis so earliest project is at top
        fig_gantt.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No valid Start/End dates to display a Gantt chart.")

    # ========== Correlation Matrix for numeric columns ==========
    st.subheader("Correlation Matrix for Numeric Columns")
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) > 1:
        corr_matrix = numeric_df.corr()
        fig_corr = px.imshow(
            corr_matrix,
            labels=dict(x="Columns", y="Columns", color="Correlation"),
            title="Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.write("Not enough numeric columns for correlation matrix.")


# ---------- 9) Sidebar with Logo and Text ----------
def display_sidebar():
    with st.sidebar:
        logo_path = r'C:\Users\brajb\OneDrive\Desktop\coding development\industry 4.0\Jay jay  (2).png'
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            st.image(logo, width=250)
        st.markdown("### Jay Jay Group Industry 4.0")
        st.markdown("---")
        if st.session_state.logged_in:
            st.write(f"Logged in as {st.session_state.role}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.page = "login"


# ---------- 10) User Authentication Page ----------
def login_page():
    display_sidebar()
    st.title("Industry 4.0 Project Management App")
    menu = ["Login", "Sign Up", "Tutorial"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")
        username = st.sidebar.text_input("User Name", key="login_username")
        password = st.sidebar.text_input("Password", type='password', key="login_password")
        if st.sidebar.button("Login"):
            result = login_user(username, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.user_id = result[0]
                st.session_state.role = result[3]
                st.session_state.page = "dashboard"
                st.success(f"Welcome {username}")
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        new_user = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type='password', key="signup_password")
        all_depts = get_all_departments()
        dept_names = [d[1] for d in all_depts] if all_depts else ["General"]
        department = st.selectbox("Select Department", dept_names, key="signup_department")
        role = st.selectbox("Select Role", ["Admin", "Manager", "User"], key="signup_role")

        if st.button("Sign Up"):
            if new_user and new_password:
                add_user(new_user, new_password, role, department)
                st.success("Account Created Successfully! Please Login.")
            else:
                st.warning("Please enter all details to sign up.")

    elif choice == "Tutorial":
        st.subheader("Industry 4.0 Project Management - Tutorial")
        st.write("""
        ### Key Sections:
        1. **User Authentication System**: Different roles (Admin, Manager, User).
        2. **Project Management with 16-Dimension Tool**: Add, update, and delete projects with a structured breakdown.
        3. **Dropdown Selections**: For Year, JJM Strategic Pillars, and categories to maintain consistency.
        4. **Interactive Dashboards**: Delayed projects, on-time projects, completion rates, milestone progress, Kanban board, Gantt chart, etc.
        5. **Learning Portal**: Admin can add training sessions; users can access and track progress.
        """)


def show_16_dimension_tool():
    st.subheader("16-Dimension Industry 4.0 Assessment Tool")
    st.write("Coming soon...")

# ---------- 11) Admin Dashboard ----------
def admin_dashboard(user_id):
    display_sidebar()
    st.title("Admin Dashboard")

    menu = [
        "Manage Departments",
        "Manage Users",
        "Manage Projects",
        "Manage Training",
        "View Reports",
        "16-Dimension Tool",
        "Update Project Status"
    ]
    choice = st.selectbox("Menu", menu)

    if choice == "Manage Departments":
        st.subheader("Department Management")
        department_name = st.text_input("Department Name", key="department_name")
        if st.button("Add Department"):
            add_department(department_name)
            st.success(f"Department {department_name} added successfully!")
        st.write(pd.DataFrame(get_all_departments(), columns=["ID", "Department Name"]))

    elif choice == "Manage Users":
        st.subheader("User Management")
        username = st.text_input("Username", key="admin_username")
        password = st.text_input("Password", type='password', key="admin_password")
        depts = get_all_departments()
        dept_names = [d[1] for d in depts] if depts else ["General"]
        department = st.selectbox("Select Department", dept_names, key="admin_department")
        role = st.selectbox("Role", ["Admin", "Manager", "User"], key="admin_role")

        if st.button("Add User"):
            if username and password:
                add_user(username, password, role, department)
                st.success(f"User {username} added successfully!")
            else:
                st.warning("Please provide all user details.")
        st.write(pd.DataFrame(get_all_users(), columns=["ID", "Username", "Password", "Role", "Department"]))

    elif choice == "Manage Projects":
        st.subheader("Project Management")

        # ========== Single-form for adding a new project ==========
        project_name = st.text_input("Project Name", key="project_name")
        year = st.selectbox("Year", ["2023-2024", "2025-2026", "2027-2028"], key="project_year")
        jjm_strategic_pillars = st.text_input("JJM Strategic Pillars", key="jjm_strategic_pillars")
        main_cat = ["E2E Supply Chain Visibility & Connectivity", "Real-Time Data & Analytics", "Organization Readiness"]
        target_main_category = st.selectbox("Target Main Category", main_cat, key="target_main_category")

        if target_main_category == "E2E Supply Chain Visibility & Connectivity":
            sub_cat_opts = ["Digitized Product Development", "Automation and Deskillment", "Seamless Connectivity"]
        elif target_main_category == "Real-Time Data & Analytics":
            sub_cat_opts = ["Predictive Analytics and Digitized Planning", "AI-Based Decision Making"]
        else:
            sub_cat_opts = ["Digital Performance Management", "Cross-Functional Digitization"]
        target_sub_category = st.selectbox("Target Sub Category", sub_cat_opts, key="target_sub_category")

        sixteen_dims = [
            "Management Mindset", "Strategy Roadmap", "Change Management Plan", "Technology Readiness",
            "Data-Driven Decision Making", "Organizational Structure", "Process Digitization", "Talent Readiness",
            "Supply Chain Integration", "Automation and Deskilling", "Predictive Analytics", "Customer Integration",
            "Digital Product Development", "Real-Time Analytics", "Security and Compliance", "Continuous Improvement"
        ]
        target_16_dimensions = st.selectbox("Target 16 Dimensions", sixteen_dims, key="target_16_dimensions")

        jjm_action_plan = st.text_area("JJM Action Plan and Tasks", key="jjm_action_plan")
        start_date = st.date_input("Start Date", key="start_date")
        end_date = st.date_input("End Date", key="end_date")
        roadmap_captain = st.text_input("Roadmap Captain", key="roadmap_captain")
        project_leaders = st.text_input("Project Leaders", key="project_leaders")
        project_owners = st.text_input("Project Owners", key="project_owners")

        task_status_list = [
            "Not Started", "In Progress", "Trial Done", "In Testing",
            "Production Deployed", "Running", "Completed"
        ]
        task_status = st.selectbox("Task Status", task_status_list, key="task_status")
        task_completion_rate = st.slider("Task Completion Rate", 0, 100, 0, key="task_completion_rate")
        jjm_comments = st.text_area("JJM Comments", key="jjm_comments")
        target_remark = st.text_area("Target Remark", key="target_remark")

        # Assign project manager (users with role == Manager)
        all_users = get_all_users()
        manager_opts = [u[1] for u in all_users if u[3] == "Manager"]
        manager = st.selectbox("Assign Project Manager", manager_opts, key="manager")

        if st.button("Add Project"):
            add_project(
                project_name, year, jjm_strategic_pillars, target_main_category,
                target_sub_category, target_16_dimensions, jjm_action_plan, start_date,
                end_date, roadmap_captain, project_leaders, project_owners, task_status,
                task_completion_rate, jjm_comments, target_remark, manager
            )
            st.success(f"Project '{project_name}' added successfully!")

        # ========== Section: Add/Update from Excel without crashing on missing columns ==========
        st.subheader("Add/Update Projects from Excel (Optional)")
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        if uploaded_file is not None:
            process_excel_file(uploaded_file)

        # ========== Section: Update Project by ID ==========
        st.subheader("Update Existing Project")
        all_projects = get_all_projects()
        if all_projects:
            project_id_list = [(p[0], p[1]) for p in all_projects]  # (ID, Name)
            sel_texts = [f"{pid} - {pname}" for pid, pname in project_id_list]
            selected_upd = st.selectbox("Select Project by ID", sel_texts)
            # Parse the selection
            if selected_upd:
                chosen_id = int(selected_upd.split(" - ")[0])
                if st.button("Update Project Details"):
                    update_project(
                        chosen_id,
                        project_name,
                        year,
                        jjm_strategic_pillars,
                        target_main_category,
                        target_sub_category,
                        target_16_dimensions,
                        jjm_action_plan,
                        start_date,
                        end_date,
                        roadmap_captain,
                        project_leaders,
                        project_owners,
                        task_status,
                        task_completion_rate,
                        jjm_comments,
                        target_remark,
                        manager
                    )
                    st.success(f"Project ID {chosen_id} updated successfully!")
        else:
            st.info("No projects in the database yet.")

        # Show Visualization
        visualize_projects()

    elif choice == "Update Project Status":
        st.subheader("Update Project Status")

        all_projects = get_all_projects()
        if all_projects:
            # We'll show the project name instead of ID
            name_dict = {p[1]: p[0] for p in all_projects}  # {Name:ID}
            selected_project_name = st.selectbox("Select Project", list(name_dict.keys()))
            st.info(f"Selected Project: **{selected_project_name}**")
            new_status_list = [
                "Not Started", "In Progress", "Trial Done", "In Testing",
                "Production Deployed", "Running", "Completed"
            ]
            new_status = st.selectbox("New Status", new_status_list)
            if st.button("Update Status"):
                pid = name_dict[selected_project_name]
                update_project_status(pid, new_status)
                st.success(f"Updated '{selected_project_name}' to status: {new_status}")
        else:
            st.info("No projects found to update.")

    elif choice == "Manage Training":
        st.subheader("Training Management")
        title = st.text_input("Training Title", key="training_title")
        description = st.text_area("Training Description", key="training_description")
        schedule = st.date_input("Schedule Date", key="training_schedule")
        material = st.file_uploader("Upload Training Material", type=["pdf", "docx", "pptx"], key="training_material")
        
        material_path = None
        if material is not None:
            material_path = f"training_materials/{material.name}"
            if not os.path.exists('training_materials'):
                os.makedirs('training_materials')
            with open(material_path, "wb") as f:
                f.write(material.getbuffer())
            st.success(f"Uploaded {material.name} successfully!")

        if st.button("Add Training"):
            if material_path:
                c.execute('''
                    INSERT INTO training_sessions (title, description, schedule, material_path)
                    VALUES (?, ?, ?, ?)
                ''', (title, description, str(schedule), material_path))
                conn.commit()
                st.success("Training Session Added!")
            else:
                st.error("Please upload the training material before adding the session.")

    elif choice == "View Reports":
        st.subheader("Reports and Analysis")
        projects = get_all_projects()
        df = pd.DataFrame(projects, columns=[
            "ID", "Project Name", "Year", "JJM Strategic Pillars",
            "Target Main Category", "Target Sub Category", "Target 16 Dimensions",
            "JJM Action Plan", "Start Date", "End Date", "Roadmap Captain",
            "Project Leaders", "Project Owners", "Task Status", "Task Completion Rate",
            "JJM Comments", "Target Remark", "Manager"
        ])
        st.dataframe(df)

        # Download button for CSV
        st.download_button(
            "Download as CSV",
            df.to_csv(index=False),
            file_name="project_report.csv",
            mime='text/csv'
        )

    elif choice == "16-Dimension Tool":
        show_16_dimension_tool()

# ---------- 12) Manager Dashboard ----------
def manager_dashboard(user_id):
    display_sidebar()
    st.title("Manager Dashboard")
    st.subheader("Project Management and Reporting")
    visualize_projects()

# ---------- 13) User Dashboard ----------
def user_dashboard(user_id):
    display_sidebar()
    st.title("User Dashboard")
    st.subheader("Your Assigned Tasks and Progress")
    progress = get_user_progress(user_id)
    if progress:
        for record in progress:
            st.write(f"Session {record[0]}: {record[1]}")
    else:
        st.write("No progress recorded yet.")

# ---------- 14) Main Function ----------
def main():
    if st.session_state.logged_in:
        if st.session_state.role == "Admin":
            admin_dashboard(st.session_state.user_id)
        elif st.session_state.role == "Manager":
            manager_dashboard(st.session_state.user_id)
        else:
            user_dashboard(st.session_state.user_id)
    else:
        login_page()

if __name__ == '__main__':
    main()
