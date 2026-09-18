import streamlit as st
import json
import hashlib
import random
import pandas as pd
import datetime
import os

# ==========================================
# 0. APPLE-INSPIRED UI DESIGN (CSS INJECTION)
# ==========================================
def apply_smooth_design():
    st.markdown("""
    <style>
    /* Force Apple system fonts everywhere */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Force smooth, rounded buttons with hover bounce */
    div[data-testid="stButton"] > button {
        border-radius: 20px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.15) !important;
        border-color: rgba(128, 128, 128, 0.5) !important;
    }

    /* Force input field rounding */
    div[data-baseweb="input"] > div {
        border-radius: 12px !important;
    }
    
    /* Clean up the radio button background */
    div[data-testid="stRadio"] > div {
        background-color: transparent !important;
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
st.set_page_config(page_title="Secure Virtual Bank", page_icon="", layout="centered")
apply_smooth_design() # Activate Apple Design

data = load_data()

# --- LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title(" Secure Virtual Bank")
    st.markdown("### Sign In")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Sign In")

        if submit_button:
            if username in data:
                if data[username].get('locked', False):
                    st.error("Account locked due to multiple failed login attempts.")
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
                        st.error("Account locked due to 3 failed attempts.")
                    else:
                        st.error(f"Invalid password. Attempts remaining: {3 - attempts}")
            else:
                st.error("Invalid username.")
    
    st.caption("Hint: Default accounts are 'user1' and 'user2'. Password is 'password123'.")

# --- MAIN DASHBOARD ---
else:
    user = st.session_state.current_user
    user_data = data[user]

    # Clean Sidebar Profile
    with st.sidebar:
        st.title(f"Hello, {user.capitalize()}")
        st.metric(label="Apple Card Balance", value=f"RM {user_data['balance']:.2f}")
        st.divider()
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.otp = None
            st.rerun()

    # Streamlined Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", "⚡ Quick Actions", "📝 History", "🔐 Security (OTP)"
    ])

    # --- TAB 1: Dashboard (Charts) ---
    with tab1:
        st.subheader("Spending Overview")
        if user_data['history']:
            df = pd.DataFrame(user_data['history'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            st.line_chart(df['balance_after'])
        else:
            st.info("No transaction history available.")

    # --- TAB 2: Dynamic Action Center (Click Icon to Reveal) ---
    with tab2:
        st.subheader("Select an Action")
        
        # Horizontal Segmented Control for Icons
        action = st.radio(
            "Actions",
            ["💸 Transfer", "🧾 Pay Bill", "💳 Credit Card", "📥 Deposit"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.divider()

        # Reveal specific form based on icon clicked
        if action == "💸 Transfer":
            st.markdown("#### Transfer Funds")
            target_user = st.text_input("Recipient Username")
            transfer_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Transfer"):
                if target_user not in data:
                    st.error("Recipient does not exist.")
                elif target_user == user:
                    st.error("Cannot transfer to yourself.")
                elif transfer_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "transfer", "target": target_user, "amount": transfer_amount}
                    st.success(f"OTP generated: {st.session_state.otp}. Go to the Security tab to confirm.")

        elif action == "🧾 Pay Bill":
            st.markdown("#### Bill Payment")
            biller = st.selectbox("Select Biller", ["TNB", "Syabas", "Unifi", "Maxis"])
            bill_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Payment"):
                if bill_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "bill", "biller": biller, "amount": bill_amount}
                    st.success(f"OTP generated: {st.session_state.otp}. Go to the Security tab to confirm.")

        elif action == "💳 Credit Card":
            st.markdown("#### Credit Card Payment")
            card_num = st.text_input("Card Number (Last 4 digits)", max_chars=4)
            cc_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            
            if st.button("Review Card Payment"):
                if len(card_num) != 4:
                    st.error("Please enter the last 4 digits.")
                elif cc_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "credit_card", "card": card_num, "amount": cc_amount}
                    st.success(f"OTP generated: {st.session_state.otp}. Go to the Security tab to confirm.")

        elif action == "📥 Deposit":
            st.markdown("#### Instant Deposit")
            deposit_amount = st.number_input("Deposit Amount (RM)", min_value=1.0, step=50.0)
            
            if st.button("Complete Deposit"):
                data[user]['balance'] += deposit_amount
                record_transaction(user, data, "Deposit", deposit_amount, "Self Deposit")
                st.success(f"Successfully deposited RM {deposit_amount:.2f}")
                st.rerun()

    # --- TAB 3: History & Export ---
    with tab3:
        st.subheader("Recent Transactions")
        if user_data['history']:
            df_history = pd.DataFrame(user_data['history'])
            st.dataframe(df_history, use_container_width=True)
            
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Export CSV", data=csv, file_name=f"{user}_statement.csv", mime="text/csv")
        else:
            st.info("No transactions found.")

    # --- TAB 4: OTP Verification ---
    with tab4:
        st.subheader("Two-Factor Authentication")
        if st.session_state.otp and st.session_state.pending_action:
            st.warning("Action required: Please verify your identity.")
            action_data = st.session_state.pending_action
            
            if action_data['type'] == 'transfer':
                st.write(f"**Request:** Transfer RM {action_data['amount']} to {action_data['target']}")
            elif action_data['type'] == 'bill':
                st.write(f"**Request:** Pay RM {action_data['amount']} to {action_data['biller']}")
            elif action_data['type'] == 'credit_card':
                st.write(f"**Request:** Pay RM {action_data['amount']} for Card *{action_data['card']}")

            entered_otp = st.text_input("Enter 6-digit OTP code")
            
            if st.button("Confirm & Authenticate"):
                if entered_otp == st.session_state.otp:
                    amt = action_data['amount']
                    data[user]['balance'] -= amt
                    
                    if action_data['type'] == 'transfer':
                        data[action_data['target']]['balance'] += amt
                        record_transaction(user, data, "Transfer Out", -amt, f"To {action_data['target']}")
                        record_transaction(action_data['target'], data, "Transfer In", amt, f"From {user}")
                    elif action_data['type'] == 'bill':
                        record_transaction(user, data, "Bill Payment", -amt, action_data['biller'])
                    elif action_data['type'] == 'credit_card':
                        record_transaction(user, data, "CC Payment", -amt, f"Card *{action_data['card']}")
                    
                    st.session_state.otp = None
                    st.session_state.pending_action = None
                    st.success("Verified successfully.")
                    st.rerun()
                else:
                    st.error("Invalid authentication code.")
        else:
            st.info("Your account is secure. No pending actions.")
