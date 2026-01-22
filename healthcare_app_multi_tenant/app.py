import streamlit as st
from database import Base, engine, get_db
from crud import *
from models import Tenant, User

# database setup
Base.metadata.create_all(bind=engine)
db = get_db()

# streamlit setup
st.set_page_config(
    page_title="Healthcare Multi-Tenant System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# session state
if "role" not in st.session_state:
    st.session_state.role = None
if "tenant" not in st.session_state:
    st.session_state.tenant = None
if "admin_action" not in st.session_state:
    st.session_state.admin_action = None
if "view_tenants" not in st.session_state:
    st.session_state.view_tenants = False

# admin login interface
if st.session_state.role is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Healthcare System")
        st.subheader("Admin Portal")
        st.divider()
        
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        st.write("")
        if st.button("Login", use_container_width=True, type="primary"):
            if admin_login(username, password):
                st.session_state.role = "admin"
                st.success("Admin logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")


elif st.session_state.role == "admin" and st.session_state.admin_action is None:

    with st.sidebar:
        st.header("Logout to Main Menu")
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.role = None
            st.session_state.admin_action = None
            st.session_state.view_tenants = False
            st.rerun()

    st.title("Admin Dashboard")
    st.subheader("Choose an action to continue")
    st.divider()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Create Tenant")
        st.write("Add a new healthcare facility")
        if st.button("Create Tenant", use_container_width=True, key="create_btn", type="primary"):
            st.session_state.admin_action = "create_tenant"
            st.session_state.view_tenants = False
            st.rerun()
    
    with col2:
        st.subheader("Tenant Login")
        st.write("Access facility dashboard")
        if st.button("Tenant Login", use_container_width=True, key="login_btn", type="primary"):
            st.session_state.admin_action = "tenant_login"
            st.session_state.view_tenants = False
            st.rerun()
    
    with col3:
        st.subheader("View Tenants")
        st.write("See all registered facilities")
        if st.button("View All Tenants", use_container_width=True, key="view_btn", type="primary"):
            st.session_state.view_tenants = True
            st.rerun()

    if st.session_state.view_tenants:
        st.divider()
        st.header("All Registered Tenants")
        tenants = get_all_tenants(db)
        if tenants:
            for t in tenants:
                with st.container(border=True):
                    st.write(f"**ID:** {t.id}  |  **Name:** {t.name}")
        else:
            st.info("No tenants created yet.")

# create tenant interface
if st.session_state.role == "admin" and st.session_state.admin_action == "create_tenant":
    with st.sidebar:
        st.header("Logout to Main Menu")
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.role = None
            st.session_state.admin_action = None
            st.session_state.view_tenants = False
            st.rerun()
    
    st.title("Create New Tenant")
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            name = st.text_input("Tenant Name", placeholder="e.g., City General Hospital")
            subdomain = st.text_input("Subdomain", placeholder="e.g., citygen")
            username = st.text_input("Tenant Username", placeholder="e.g., admin_citygen")
            password = st.text_input("Tenant Password", type="password", placeholder="Enter secure password")

            st.write("")
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Create Tenant", use_container_width=True, type="primary"):
                    tenant = create_tenant(db, name, subdomain, username, password)
                    if tenant:
                        st.success("Tenant created successfully!")
                    else:
                        st.error("Tenant already exists")
            
            with col_btn2:
                if st.button("Back", use_container_width=True, type="secondary"):
                    st.session_state.admin_action = None
                    st.rerun()

# tenant login interface
if st.session_state.role == "admin" and st.session_state.admin_action == "tenant_login":
    with st.sidebar:
        st.header("Logout to Main Menu")
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.role = None
            st.session_state.admin_action = None
            st.session_state.view_tenants = False
            st.rerun()
    
    st.title("Tenant Login")
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            tenant_username = st.text_input("Tenant Username", placeholder="Enter tenant username")
            tenant_password = st.text_input("Tenant Password", type="password", placeholder="Enter password")

            st.write("")
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Login as Tenant", use_container_width=True, type="primary"):
                    tenant = tenant_login(db, tenant_username, tenant_password)
                    if tenant:
                        st.session_state.role = "tenant"
                        st.session_state.tenant = tenant
                        st.session_state.admin_action = None
                        st.session_state.view_tenants = False
                        st.success("Tenant logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid tenant credentials")
            
            with col_btn2:
                if st.button("Back", use_container_width=True, type="secondary"):
                    st.session_state.admin_action = None
                    st.session_state.view_tenants = False
                    st.rerun()

# tenant dashboard
if st.session_state.role == "tenant":
    tenant = st.session_state.tenant

    with st.sidebar:
        st.header("Tenant Profile")
        st.divider()
        st.write(f"**Name:** {tenant.name}")
        st.write(f"**Username:** {tenant.username}")
        st.write(f"**Subdomain:** {tenant.subdomain if hasattr(tenant, 'subdomain') else 'N/A'}")
        
        st.divider()
        users = get_users(db, tenant.id)
        st.metric("Total Staff Users", len(users))
        
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.role = "admin"
            st.session_state.tenant = None
            st.session_state.admin_action = None
            st.rerun()

    st.title(f"{tenant.name} Dashboard")
    st.divider()

    tab1, tab2 = st.tabs(["Create User", "Manage Users"])

    # create user interface
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container(border=True):
                st.subheader("Create Staff User")
                
                name = st.text_input("Name", placeholder="Enter full name")
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                role = st.selectbox("Role", ["Doctor", "Nurse", "Surgeon", "Pharmacist", 
                                               "Lab Technician", "Radiologist", "Receptionist", 
                                               "Admin Staff", "EMT", "Therapist"])

                st.write("")
                if st.button("Create User", use_container_width=True, type="primary"):
                    existing_user = get_user_by_username(db, username, tenant.id)
                    if not existing_user:
                        create_user(db, name, username, password, role, tenant.id)
                        st.success("User created successfully!")
                        st.rerun()
                    # silently do nothing if username exists

    # manage users interface
    with tab2:
        st.subheader("Staff Users Management")
        st.divider()
        
        if users:
            for user in users:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**ID:** {user.id}")
                    
                    with col2:
                        st.write(f"**Name:** {user.name}")
                    
                    with col3:
                        st.write(f"**Current Role:** {user.role}")
                    
                    with col4:
                        new_role = st.selectbox(
                            "Change Role",
                            ["Doctor", "Nurse", "Surgeon", "Pharmacist", "Lab Technician", 
                             "Radiologist", "Receptionist", "Admin Staff", "EMT", "Therapist"],
                            index=["Doctor", "Nurse", "Surgeon", "Pharmacist", "Lab Technician", 
                                   "Radiologist", "Receptionist", "Admin Staff", "EMT", "Therapist"].index(user.role),
                            key=f"user_role_{user.id}"
                        )
                        
                        if st.button("Update", key=f"btn_{user.id}", use_container_width=True, type="primary"):
                            if new_role != user.role:
                                update_user_role(db, user.id, tenant.id, new_role)
                                st.success(f"Role for {user.name} updated to {new_role}!")
                                st.rerun()
        else:
            st.info("No staff users created yet. Create your first user in the 'Create User' tab.")
