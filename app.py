import os
import streamlit as st
from dotenv import load_dotenv
from app.database import Database
from app.granite_service import GraniteService
from app.task_manager import TaskManager
from datetime import datetime

# Set page configuration - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Error404 Productivity Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables from .env file
load_dotenv()

# Initialize session state for navigation if it doesn't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Tasks'

# Hide Streamlit's default menu and footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for Linear-like design with horizontal nav
st.markdown("""
    <style>
    /* Main layout */
    .main {
        background-color: #13141C;
        color: #E2E2E2;
    }
    
    /* Header and Navigation */
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        background-color: #13141C;
        border-bottom: 1px solid #2D2D3D;
        position: sticky;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        margin: -5rem -5rem 2rem -5rem;
    }
    
    .nav-container {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    

    .nav-links {
        display: flex;
        gap: 1rem;
    }
    
    .nav-button {
        background: none;
        border: none;
        color: #A0A0A0;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.2s;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-button:hover {
        background-color: #2D2D3D;
        color: #E2E2E2;
    }
    
    .nav-button.active {
        background-color: #5E5EFF;
        color: white;
    }
    
    .right-nav {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Search bar */
    .search-box {
        background-color: #1C1C27;
        border: 1px solid #2D2D3D;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        color: #E2E2E2;
        width: 240px;
    }
    
    /* Content padding for fixed header */
    .content {
        margin-top: 5rem;
        padding: 2rem;
    }
    
    /* Task cards */
    .task-card {
        background-color: #1C1C27;
        border: 1px solid #2D2D3D;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    .task-card:hover {
        transform: translateY(-2px);
        border-color: #4A4A5C;
    }
    
    /* Priority badges */
    .priority {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    .priority-high { background-color: #3D1A1A; color: #FF4D4D; }
    .priority-medium { background-color: #3D3A1A; color: #FFD84D; }
    .priority-low { background-color: #1A3D1A; color: #4DFF4D; }
    
    /* Buttons */
    .stButton>button {
        background-color: #5E5EFF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #4B4BFF;
    }
    
    /* Modal */
    .task-modal {
        background-color: #1C1C27;
        border-radius: 12px;
        border: 1px solid #2D2D3D;
        padding: 2rem;
        max-width: 600px;
        margin: 2rem auto;
    }
    </style>
    
    <script>
        // JavaScript to handle navigation
        document.addEventListener('DOMContentLoaded', function() {
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const page = this.getAttribute('data-page');
                    window.location.search = `?page=${page}`;
                });
            });
        });
    </script>
    

  
    
    <div class="content">
    """, unsafe_allow_html=True)

# Add this at the end of your app to close the content div
st.markdown("</div>", unsafe_allow_html=True)

def task_list(task_manager, tasks):
    # Status and priority filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", 
                                    ["All", "Pending", "In Progress", "Completed"])
    with col2:
        priority_filter = st.multiselect("Filter by Priority",
                                       ["High", "Medium", "Low"])
    
    # Apply additional filters
    filtered_tasks = [
        t for t in tasks
        if (status_filter == "All" or t.get('status') == status_filter) and
        (not priority_filter or t.get('priority') in priority_filter)
    ]
    
    # Display tasks with enhanced status visualization
    for task in filtered_tasks:
        status_color = {
            'Pending': '#ff4b4b',
            'In Progress': '#f0ab00',
            'Completed': '#00c853'
        }.get(task.get('status', 'Pending'), '#ff4b4b')
        
        with st.container():
            st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; 
                            border-left: 4px solid {status_color};
                            background: #1C1C27; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <h4>{task['title']}</h4>
                        <span style="color: {status_color}">● {task.get('status', 'Pending')}</span>
                    </div>
                    <p style="color: #888; margin: 0.5rem 0;">{task.get('description', '')}</p>
                    <div style="display: flex; gap: 1rem; font-size: 0.9em;">
                        <div>📅 {task.get('deadline', 'No deadline')}</div>
                        <div>🏷️ {task.get('category', 'Uncategorized')}</div>
                        <div>🔖 {task.get('labels', 'Uncategorized')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Quick actions
            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                new_status = st.selectbox("Update Status",
                                       ["Pending", "In Progress", "Completed"],
                                       key=f"status_{task['id']}")
            with col2:
                if st.button("Update", key=f"update_{task['id']}"):
                    task_manager.update_task_status(task['id'], new_status)
                    st.rerun()

    # Cleanup completed tasks button
    if st.button("🗑️ Cleanup Completed Tasks", type="primary"):
        deleted_count = task_manager.cleanup_completed_tasks()
        if deleted_count > 0:
            st.success(f"Successfully deleted {deleted_count} completed tasks!")
            st.rerun()
        else:
            st.info("No completed tasks to delete.")

def add_task_modal(task_manager):
    with st.form("new_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title*")
            description = st.text_area("Description")
            category = st.selectbox("Category", ["Work", "Personal", "Study", "Health", "Uncategorized"])
        
        with col2:
            priority = st.selectbox("Priority*", ["High", "Medium", "Low"])
            labels = st.multiselect("Labels", ["Urgent", "Meeting", "Project", "Review"])
            deadline = st.date_input("Deadline")
        
        if st.form_submit_button("Add Task"):
            if title:
                task_manager.add_task(
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    labels=",".join(labels) if labels else "Uncategorized",
                    deadline=str(deadline) if deadline else None
                )
                st.session_state.show_modal = False
                st.rerun()
            else:
                st.error("Title is required")

def show_productivity_insights(task_manager):
    st.title("📊 Productivity Insights")
    
    try:
        with st.spinner("Analyzing overall productivity..."):
            insights = task_manager.get_insights()
            
            if not insights:
                st.info("🌟 Add tasks to unlock insights!")
                return

            # Main insights grid
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Priority Distribution")
                st.markdown("---")
                
                # Priority Distribution Chart
                if 'priority_distribution' in insights:
                    priority_data = insights['priority_distribution']
                    
                    # Pie Chart
                    st.write("### Task Priority Breakdown")
                    pie_chart = create_pie_chart(priority_data)
                    if pie_chart:
                        st.pyplot(pie_chart)
                    
                    # Text Analysis
                    total_tasks = sum(priority_data.values())
                    if total_tasks > 0:
                        st.write("#### Analysis:")
                        st.write(f"- **High Priority Tasks:** {priority_data['High']} ({priority_data['High']/total_tasks*100:.1f}%)")
                        st.write(f"- **Medium Priority Tasks:** {priority_data['Medium']} ({priority_data['Medium']/total_tasks*100:.1f}%)")
                        st.write(f"- **Low Priority Tasks:** {priority_data['Low']} ({priority_data['Low']/total_tasks*100:.1f}%)")
                        
                        if priority_data['High'] > total_tasks * 0.5:
                            st.warning("⚠️ Over 50% of tasks are high priority - consider delegating or rescheduling some tasks")
                else:
                    st.info("No priority data available")
                
                st.subheader("⏱ Time Management")
                st.markdown("---")
                
                # Time Management Analysis
                if 'time_management' in insights:
                    st.write("### Time Management Analysis")
                    st.write(insights['time_management'])
                    
                    # Add more detailed analysis
                    if "deadline_clustering" in insights:
                        st.warning(f"⚠️ Deadline clustering detected: {insights['deadline_clustering']} tasks share the same due date")
                else:
                    st.info("No time management data available")
            
            with col2:
                st.subheader("Task Completion Trends")
                st.markdown("---")
                
                # Task Completion Analysis
                if 'completion_trends' in insights:
                    completion_data = insights['completion_trends']
                    
                    # Line Chart
                    st.write("### Completion Trends Over Time")
                    st.line_chart(completion_data)
                    
                    # Text Analysis
                    total_completed = sum(completion_data.values())
                    if total_completed > 0:
                        st.write("#### Analysis:")
                        st.write(f"- **Total Completed Tasks:** {total_completed}")
                        best_week = max(completion_data, key=completion_data.get)
                        st.write(f"- **Most Productive Week:** {best_week} ({completion_data[best_week]} tasks completed)")
                else:
                    st.info("No completion trends available")
                
                st.subheader("Recommendations")
                st.markdown("---")
                if insights.get("recommendations"):
                    st.write("### Actionable Recommendations")
                    for rec in insights["recommendations"]:
                        st.markdown(f"▸ {rec}")
                else:
                    st.write("No recommendations available")
            
            st.markdown("---")
            st.subheader("Productivity Overview")
            st.write(insights.get("productivity_analysis", "Analysis unavailable"))

    except Exception as e:
        st.error("Failed to generate insights")
        print(f"Productivity insights error: {str(e)}")

def create_pie_chart(data):
    try:
        import matplotlib.pyplot as plt
        
        labels = list(data.keys())
        sizes = list(data.values())
        
        # Custom colors for the pie chart
        colors = ['#ff4b4b', '#f0ab00', '#00c853']  # Red, Orange, Green
        
        fig, ax = plt.subplots()
        wedges, _, autotexts = ax.pie(
            sizes,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
            textprops={'color': 'white', 'weight': 'bold'}
        )
        
        # Add a legend
        ax.legend(
            wedges,
            labels,
            title="Priorities",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # Make the pie chart circular
        ax.axis('equal')
        
        return fig
    except ImportError:
        st.error("Matplotlib is not installed. Please install it to view charts.")
        return None

def show_task_analysis(task_manager):
    st.title("🔍 Task Analysis Guide")
    
    try:
        with st.spinner("Loading tasks..."):
            tasks = task_manager.get_tasks()
            
            if not tasks:
                st.info("🌟 Add tasks to analyze!")
                return
                
            selected_task = st.selectbox(
                "Select a Task for Detailed Analysis",
                options=tasks,
                format_func=lambda x: f"{x['title']} ({x.get('priority', 'No Priority')})",
                key="task_analysis_select"
            )
            
            task_insights = task_manager.get_task_insights(selected_task)
            detailed_guide = task_manager.get_task_guide(selected_task)

            col1, col2 = st.columns([1, 2])
            
            with col1:
                if selected_task:
                    st.subheader("Task Details")
                    st.markdown("---")
                    st.write(f"📅 **Deadline:** {selected_task.get('deadline', 'Not set')}")
                    st.write(f"🔖 **Priority:** {selected_task.get('priority', 'Not set')}")
                    st.write(f"🏷️ **Category:** {selected_task.get('category', 'Uncategorized')}")
                    st.write(f"🏷️ **Labels:** {selected_task.get('labels', 'None')}")
                    
                    st.markdown("---")
                    st.subheader("Quick Recommendations")
                    if task_insights.get('recommendations'):
                        for rec in task_insights['recommendations']:
                            st.markdown(f"▸ {rec}")
                else:
                    st.info("Please select a task to analyze")

                st.markdown("---")
                st.subheader("Description Analysis")
                if selected_task and selected_task.get('description'):
                    st.write(task_insights.get('description_analysis', ''))

            with col2:
                st.subheader("Completion Guide")
                st.markdown("---")
                
                with st.expander("📘 Comprehensive Completion Guide", expanded=True):
                    # AI-Generated Steps
                    st.markdown("### Steps to Complete the Task")
                    steps = task_manager.granite.generate_task_steps(selected_task)
                    for step in steps:
                        st.markdown(step)
                    
                    # Time Management Strategy
                    st.markdown("### ⏰ Time Management Strategy")
                    st.write(f"**Technique:** {detailed_guide.get('time_management', {}).get('technique', '')}")
                    st.write(f"**Daily Focus:** {detailed_guide.get('time_management', {}).get('daily_allocation', '')}")
                    
                    if detailed_guide.get('time_management', {}).get('milestones'):
                        st.markdown("**Key Milestones:**")
                        for milestone in detailed_guide['time_management']['milestones']:
                            st.markdown(f"- {milestone}")
                    
                    # Tools and Resources
                    st.markdown("---")
                    st.markdown("### 🛠️ Recommended Tools & Resources")
                    if detailed_guide.get('tools'):
                        st.markdown("**Essential Tools:**")
                        for tool in detailed_guide['tools']:
                            st.markdown(f"- {tool}")
                    
                    if detailed_guide.get('resources'):
                        st.markdown("**Reference Materials:**")
                        for res in detailed_guide['resources']:
                            st.markdown(f"- 📚 {res}")
                    
                    # Methodology
                    st.markdown("---")
                    st.markdown("### 📐 Suggested Frameworks")
                    if detailed_guide.get('frameworks'):
                        for framework in detailed_guide['frameworks']:
                            st.markdown(f"- {framework}")
                    else:
                        st.write("Standard task management approach recommended")
                    
                    # Step-by-Step Plan
                    st.markdown("---")
                    st.markdown("### 📝 Action Plan")
                    for step in detailed_guide.get('steps', []):
                        st.markdown(f"- {step}")
                    
                    # Potential Challenges
                    st.markdown("---")
                    st.markdown("### ⚠️ Anticipated Challenges")
                    if detailed_guide.get('potential_challenges'):
                        for challenge in detailed_guide['potential_challenges']:
                            st.markdown(f"- {challenge}")
                    else:
                        st.write("No significant challenges anticipated")
                
                st.markdown("---")
                st.subheader("Description Analysis")
                if selected_task and selected_task.get('description'):
                    st.write(task_insights.get('description_analysis', ''))

    except Exception as e:
        st.error("Failed to analyze task")
        print(f"Task analysis error: {str(e)}")

def show_reminders_page(task_manager):
    st.title("⏰ Upcoming Reminders")
    
    try:
        with st.spinner("Checking upcoming deadlines..."):
            reminders = task_manager.get_reminders(days_ahead=7)
            
            if not reminders:
                st.success("🎉 No urgent deadlines in the next 7 days!")
                return
                
            st.subheader(f"Found {len(reminders)} upcoming tasks")
            
            for task in reminders:
                days_left = (datetime.strptime(task['deadline'], '%Y-%m-%d').date() - datetime.today().date()).days
                
                with st.container():
                    st.markdown(f"""
                        <div style="padding:1rem; margin:0.5rem 0; 
                                    background:#1C1C27; border-radius:8px;
                                    border-left:4px solid {'#ff4b4b' if days_left < 3 else '#f0ab00'}">
                            <div style="display:flex; justify-content:space-between; align-items:center">
                                <h3>{task['title']}</h3>
                                <span style="color:{'#ff4b4b' if days_left < 3 else '#f0ab00'}">
                                    {days_left} days left
                                </span>
                            </div>
                            <div style="display:flex; gap:2rem; margin-top:0.5rem">
                                <div>📅 {task['deadline']}</div>
                                <div>🔖 {task.get('priority', 'No priority')}</div>
                                <div>📌 {task.get('category', 'Uncategorized')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
    except Exception as e:
        st.error("Failed to load reminders")
        print(f"Reminders error: {str(e)}")

def show_project_page(task_manager):
    st.title("📊 Projects")
    
    # Get all tasks
    tasks = task_manager.get_tasks()
    
    # Filter tasks with a 'Project' tag (singular)
    project_tasks = [task for task in tasks if 'Project' in task.get('labels', '')]
    
    if not project_tasks:
        st.info("🌟 No projects found. Add a 'Project' tag to tasks to see them here.")
        return
    
    # Display project tasks
    for task in project_tasks:
        status_color = {
            'Pending': '#ff4b4b',
            'In Progress': '#f0ab00',
            'Completed': '#00c853'
        }.get(task.get('status', 'Pending'), '#ff4b4b')
        
        with st.container():
            st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; 
                            border-left: 4px solid {status_color};
                            background: #1C1C27; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <h4>{task['title']}</h4>
                        <span style="color: {status_color}">● {task.get('status', 'Pending')}</span>
                    </div>
                    <p style="color: #888; margin: 0.5rem 0;">{task.get('description', '')}</p>
                    <div style="display: flex; gap: 1rem; font-size: 0.9em;">
                        <div>📅 {task.get('deadline', 'No deadline')}</div>
                        <div>🏷️ {task.get('category', 'Uncategorized')}</div>
                        <div>🔖 {task.get('priority', 'No priority')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Quick actions
            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                new_status = st.selectbox("Update Status",
                                       ["Pending", "In Progress", "Completed"],
                                       key=f"status_{task['id']}")
            with col2:
                if st.button("Update", key=f"update_{task['id']}"):
                    task_manager.update_task_status(task['id'], new_status)
                    st.rerun()

def main():
    # Initialize core services
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, 'data', 'error404.db')
    db = Database(db_path)
    granite = GraniteService()
    task_manager = TaskManager(db, granite)

    # Get all tasks at the beginning
    tasks = task_manager.get_tasks()
    
    # Display centered name without logo
    col1, col2, col3 = st.columns([3, 6, 3])  # Create three columns for centering
    with col2:  # Use the middle column
        st.markdown("""
            <div style="text-align: center;">
                <h2 style="margin: 0; color: #E2E2E2;">Error404</h2>
            </div>
        """, unsafe_allow_html=True)

    # Custom CSS for the navigation bar
    st.markdown(f"""
        <style>
            .navbar {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #1C1C27;
                padding: 0.5rem 2rem;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }}
            
            .navbar-content {{
                display: flex;
                align-items: center;
                gap: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .navbar-brand {{
                display: flex;
                align-items: center;
                color: #00C853;
                font-size: 1.25rem;
                font-weight: bold;
                white-space: nowrap;
            }}
            
            .nav-tabs {{
                display: flex;
                align-items: center;
                flex: 1;
                gap: 0.5rem;
            }}
            
            .nav-tabs .stRadio {{
                width: 100%;
            }}
            
            .nav-tabs .stRadio > div {{
                display: flex;
                gap: 0.5rem;
                align-items: center;
            }}
            
            .nav-tabs label {{
                color: #B0B0B0;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.3s ease;
                cursor: pointer;
                white-space: nowrap;
                font-weight: 500;
            }}
            
            .nav-tabs label:hover {{
                color: white;
                background: rgba(255,255,255,0.1);
            }}
            
            .nav-tabs input:checked + label {{
                color: white;
                background: #00C853;
                box-shadow: 0 2px 8px rgba(0,200,83,0.3);
            }}
            
            .main-content {{
                margin-top: 4rem;
                padding: 1rem;
            }}
            
            /* Hide Streamlit branding */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tabs = {
        "📋 Tasks": "Tasks",
        "📈 Insights": "Productivity Insights",
        "🔍 Task Analysis": "Task Analysis",
        "⏰ Reminders": "Reminders",
        "📊 Projects": "Project",
        "🚨 Urgent": "Urgent",
        "👥 Meeting": "Meeting",
        "📝 Review": "Review"
    }
    
    page = st.radio("Navigation", list(tabs.keys()), horizontal=True, key="nav", label_visibility="collapsed")
    selected_page = tabs[page]
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)

    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if selected_page == "Tasks":
        st.title("📋 Tasks")
        if st.button("+ New Task"):
            st.session_state.show_modal = True
        
        if st.session_state.get('show_modal', False):
            add_task_modal(task_manager)
        
        # Filter tasks based on labels
        all_labels = set()
        for task in tasks:
            if task.get('labels'):
                all_labels.update(task['labels'].split(','))
        
        # Filter tasks based on selected label
        filtered_tasks = tasks
        if all_labels:
            selected_label = st.radio("Filter by Label", ["All Tasks"] + sorted(list(all_labels)), horizontal=True)
            if selected_label != "All Tasks":
                filtered_tasks = [task for task in tasks if selected_label in task.get('labels', '')]
        
        task_list(task_manager, filtered_tasks)
    
    elif selected_page == "Productivity Insights":
        show_productivity_insights(task_manager)
    
    elif selected_page == "Task Analysis":
        show_task_analysis(task_manager)
    
    elif selected_page == "Reminders":
        show_reminders_page(task_manager)
    
    elif selected_page in ["Project", "Urgent", "Meeting", "Review"]:  # Handle tag-specific pages
        st.title(f"🏷️ {selected_page} Tasks")
        
        # Filter tasks for the selected tag
        tag_tasks = [task for task in tasks if selected_page in task.get('labels', '')]
        
        if not tag_tasks:
            st.info(f"🌟 No tasks found with the '{selected_page}' tag. Add a task with the '{selected_page}' tag to see it here.")
            return
        
        # Display tasks for the selected tag
        for task in tag_tasks:
            status_color = {
                'Pending': '#ff4b4b',
                'In Progress': '#f0ab00',
                'Completed': '#00c853'
            }.get(task.get('status', 'Pending'), '#ff4b4b')
            
            with st.container():
                st.markdown(f"""
                    <div style="padding: 1rem; margin: 0.5rem 0; 
                                border-left: 4px solid {status_color};
                                background: #1C1C27; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between;">
                            <h4>{task['title']}</h4>
                            <span style="color: {status_color}">● {task.get('status', 'Pending')}</span>
                        </div>
                        <p style="color: #888; margin: 0.5rem 0;">{task.get('description', '')}</p>
                        <div style="display: flex; gap: 1rem; font-size: 0.9em;">
                            <div>📅 {task.get('deadline', 'No deadline')}</div>
                            <div>🏷️ {task.get('category', 'Uncategorized')}</div>
                            <div>🔖 {task.get('priority', "No priority")}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Quick actions
                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    new_status = st.selectbox("Update Status",
                                           ["Pending", "In Progress", "Completed"],
                                           key=f"status_{task['id']}")
                with col2:
                    if st.button("Update", key=f"update_{task['id']}"):
                        task_manager.update_task_status(task['id'], new_status)
                        st.rerun()
    
    elif selected_page == "Settings":
        st.title("⚙️ Settings")
        st.write("Settings page coming soon...")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 