import streamlit as st
import json
import hashlib
import random
import pandas as pd
import datetime
import os

# ==========================================
# 0. APPLE KEYNOTE UI DESIGN (ADVANCED CSS)
# ==========================================
def apply_apple_keynote_design():
    st.markdown("""
    <style>
    /* 1. Hide Streamlit's Default Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Authentic Apple Typography & Spacing */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif !important;
    }
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    p {
        font-weight: 400 !important;
        letter-spacing: -0.01em !important;
    }

    /* 3. Apple Blue Pill Buttons */
    div[data-testid="stButton"] > button {
        background-color: #0071e3 !important;
        color: #ffffff !important;
        border-radius: 980px !important; /* Perfect pill shape */
        border: none !important;
        font-weight: 500 !important;
        padding: 6px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #0077ED !important;
        transform: scale(1.02) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: scale(0.98) !important;
    }

    /* 4. iOS Style Inputs (Subtle Gray, No Hard Borders) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(142, 147, 150, 0.12) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    
    /* 5. Sidebar Glassmorphism (Blur Effect) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.02) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.1) !important;
    }
    
    /* 6. Clean up metric text (Balances) */
    [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.03em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. DATA MANAGEMENT (JSON Persistence)
# ==========================================
DATA_FILE = 'bank_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        default_data = {
            "user1": {
                "password": hash_password("password123"),
                "balance": 5000.0,
                "history": [],
                "locked": False
            },
            "user2": {
                "password": hash_password("password123"),
                "balance": 2000.0,
                "history": [],
                "locked": False
            }
        }
        save_data(default_data)
        return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# ==========================================
# 2. SECURITY & AUTHENTICATION
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def record_transaction(username, data, transaction_type, amount, details=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "date": timestamp,
        "type": transaction_type,
        "amount": amount,
        "details": details,
        "balance_after": data[username]['balance']
    }
    data[username]['history'].append(record)
    save_data(data)

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = {}
if 'otp' not in st.session_state:
    st.session_state.otp = None
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None

# ==========================================
# 4. USER INTERFACE & WORKFLOW
# ==========================================
st.set_page_config(page_title="Apple Card", page_icon="", layout="centered")
apply_apple_keynote_design() # Activate Full Apple Overhaul

data = load_data()

# --- LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'> Card</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sign in with your Apple ID to manage your finances.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Apple ID")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Continue", use_container_width=True)

            if submit_button:
                if username in data:
                    if data[username].get('locked', False):
                        st.error("Apple ID locked. Too many attempts.")
                    elif data[username]['password'] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.session_state.login_attempts[username] = 0
                        st.rerun()
                    else:
                        attempts = st.session_state.login_attempts.get(username, 0) + 1
                        st.session_state.login_attempts[username] = attempts
                        if attempts >= 3:
                            data[username]['locked'] = True
                            save_data(data)
                            st.error("Apple ID locked.")
                        else:
                            st.error(f"Incorrect password. {3 - attempts} attempts left.")
                else:
                    st.error("Apple ID not found.")
        
        st.caption("Testing? Use 'user1' and 'password123'.")

# --- MAIN DASHBOARD ---
else:
    user = st.session_state.current_user
    user_data = data[user]

    # Sidebar Profile
    with st.sidebar:
        st.write("<br>", unsafe_allow_html=True)
        st.markdown(f"###  {user.capitalize()}'s Mac")
        st.metric(label="Apple Card Balance", value=f"RM {user_data['balance']:,.2f}")
        st.write("<br><br><br>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.otp = None
            st.rerun()

    # Streamlined Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Activity", "Payments", "Statements", "Security"
    ])

    # --- TAB 1: Activity ---
    with tab1:
        st.markdown("### Spending")
        if user_data['history']:
            df = pd.DataFrame(user_data['history'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            st.line_chart(df['balance_after'], color="#0071e3")
        else:
            st.info("No recent transactions.")

    # --- TAB 2: Action Center ---
    with tab2:
        st.markdown("### Services")
        action = st.segmented_control(
            "Actions",
            ["💸 Send Money", "🧾 Pay Bill", "💳 Card Payment", "📥 Add Funds"],
            default="💸 Send Money",
            label_visibility="collapsed"
        )
        st.write("<br>", unsafe_allow_html=True)

        if action == "💸 Send Money":
            st.markdown("#### Apple Cash Transfer")
            target_user = st.text_input("To (Username)")
            transfer_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Transfer"):
                if target_user not in data:
                    st.error("Recipient not found on Apple Cash.")
                elif target_user == user:
                    st.error("Cannot send money to yourself.")
                elif transfer_amount > user_data['balance']:
                    st.error("Insufficient Apple Cash balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "transfer", "target": target_user, "amount": transfer_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "🧾 Pay Bill":
            st.markdown("#### Bill Pay")
            biller = st.selectbox("Biller", ["TNB", "Syabas", "Unifi", "Maxis"])
            bill_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Payment"):
                if bill_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "bill", "biller": biller, "amount": bill_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "💳 Card Payment":
            st.markdown("#### Pay Apple Card")
            card_num = st.text_input("Card Number (Last 4)", max_chars=4)
            cc_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Payment"):
                if len(card_num) != 4:
                    st.error("Enter the last 4 digits.")
                elif cc_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "credit_card", "card": card_num, "amount": cc_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "📥 Add Funds":
            st.markdown("#### Add Money")
            deposit_amount = st.number_input("Amount (RM)", min_value=1.0, step=50.0)
            
            if st.button("Add to Apple Cash"):
                data[user]['balance'] += deposit_amount
                record_transaction(user, data, "Deposit", deposit_amount, "Added Funds")
                st.success(f"Added RM {deposit_amount:,.2f} to your balance.")
                st.rerun()

    # --- TAB 3: Statements ---
    with tab3:
        st.markdown("### Latest Transactions")
        if user_data['history']:
            df_history = pd.DataFrame(user_data['history'])
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Statement (CSV)", data=csv, file_name=f"{user}_statement.csv", mime="text/csv")
        else:
            st.info("No activity yet.")

    # --- TAB 4: OTP Verification ---
    with tab4:
        st.markdown("### Two-Factor Authentication")
        if st.session_state.otp and st.session_state.pending_action:
            action_data = st.session_state.pending_action
            
            if action_data['type'] == 'transfer':
                st.markdown(f"**Send RM {action_data['amount']} to {action_data['target']}?**")
            elif action_data['type'] == 'bill':
                st.markdown(f"**Pay RM {action_data['amount']} to {action_data['biller']}?**")
            elif action_data['type'] == 'credit_card':
                st.markdown(f"**Pay RM {action_data['amount']} for Card ending in {action_data['card']}?**")

            entered_otp = st.text_input("Enter Apple ID Verification Code")
            
            if st.button("Authorize"):
                if entered_otp == st.session_state.otp:
                    amt = action_data['amount']
                    data[user]['balance'] -= amt
                    
                    if action_data['type'] == 'transfer':
                        data[action_data['target']]['balance'] += amt
                        record_transaction(user, data, "Transfer", -amt, f"To {action_data['target']}")
                        record_transaction(action_data['target'], data, "Received", amt, f"From {user}")
                    elif action_data['type'] == 'bill':
                        record_transaction(user, data, "Bill Pay", -amt, action_data['biller'])
                    elif action_data['type'] == 'credit_card':
                        record_transaction(user, data, "Card Payment", -amt, f"*{action_data['card']}")
                    
                    st.session_state.otp = None
                    st.session_state.pending_action = None
                    st.success("Payment authorized.")
                    st.rerun()
                else:
                    st.error("Incorrect verification code.")
        else:
            st.info("No payments require authorization at this time.")
