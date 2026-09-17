import streamlit as st
import json
import hashlib
import random
import pandas as pd
import datetime
import os

# ==========================================
# 1. DATA MANAGEMENT (JSON Persistence)
# ==========================================
DATA_FILE = 'bank_data.json'

def load_data():
    """Load user data from JSON file or create default data if not exists."""
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
    """Save user data to JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# ==========================================
# 2. SECURITY & AUTHENTICATION
# ==========================================
def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def record_transaction(username, data, transaction_type, amount, details=""):
    """Record transaction history with timestamp."""
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
st.set_page_config(page_title="Secure Virtual Bank", page_icon="🏦", layout="wide")

data = load_data()

# --- LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🏦 Secure Virtual Banking System")
    st.markdown("### Login Portal")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username in data:
                if data[username].get('locked', False):
                    st.error("Account locked due to multiple failed login attempts. Contact support.")
                elif data[username]['password'] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.login_attempts[username] = 0
                    st.success("Login successful!")
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
    
    st.info("💡 Hint: Default accounts are 'user1' and 'user2'. Password is 'password123'.")

# --- MAIN DASHBOARD ---
else:
    user = st.session_state.current_user
    user_data = data[user]

    # Sidebar
    with st.sidebar:
        st.header(f"Welcome, {user.capitalize()}! 👋")
        st.metric(label="Current Balance", value=f"RM {user_data['balance']:.2f}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.otp = None
            st.rerun()

    st.title("Main Dashboard")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", "💸 Transfer & Deposit", "🧾 Pay Bills & Cards", "📝 History & Export", "🔐 OTP Pending"
    ])

    # --- TAB 1: Dashboard (Charts) ---
    with tab1:
        st.subheader("Financial Overview")
        if user_data['history']:
            df = pd.DataFrame(user_data['history'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            st.markdown("**Balance Over Time**")
            st.line_chart(df['balance_after'])
        else:
            st.info("No transaction history available to display charts.")

    # --- TAB 2: Transfer & Deposit ---
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Transfer Funds")
            target_user = st.text_input("Recipient Username")
            transfer_amount = st.number_input("Amount to Transfer (RM)", min_value=1.0, step=10.0)
            
            if st.button("Initiate Transfer"):
                if target_user not in data:
                    st.error("Recipient does not exist.")
                elif target_user == user:
                    st.error("Cannot transfer to yourself.")
                elif transfer_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {
                        "type": "transfer",
                        "target": target_user,
                        "amount": transfer_amount
                    }
                    st.info(f"OTP generated: {st.session_state.otp} (Check the OTP tab to complete)")

        with col2:
            st.subheader("Deposit Funds")
            deposit_amount = st.number_input("Amount to Deposit (RM)", min_value=1.0, step=50.0)
            
            if st.button("Deposit"):
                data[user]['balance'] += deposit_amount
                record_transaction(user, data, "Deposit", deposit_amount, "Self Deposit")
                st.success(f"Successfully deposited RM {deposit_amount:.2f}")
                st.rerun()

    # --- TAB 3: Bill & Credit Card Payments ---
    with tab3:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Pay Bills")
            biller = st.selectbox("Select Biller", ["TNB", "Syabas", "Unifi", "Maxis"])
            bill_amount = st.number_input("Bill Amount (RM)", min_value=1.0, step=10.0, key="bill_amt")
            
            if st.button("Initiate Bill Payment"):
                if bill_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {
                        "type": "bill",
                        "biller": biller,
                        "amount": bill_amount
                    }
                    st.info(f"OTP generated: {st.session_state.otp} (Check the OTP tab to complete)")

        with col4:
            st.subheader("Credit Card Payment")
            card_num = st.text_input("Credit Card Number (Last 4 digits)", max_chars=4)
            cc_amount = st.number_input("Payment Amount (RM)", min_value=1.0, step=10.0, key="cc_amt")
            
            if st.button("Initiate CC Payment"):
                if len(card_num) != 4:
                    st.error("Please enter the last 4 digits.")
                elif cc_amount > user_data['balance']:
                    st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {
                        "type": "credit_card",
                        "card": card_num,
                        "amount": cc_amount
                    }
                    st.info(f"OTP generated: {st.session_state.otp} (Check the OTP tab to complete)")

    # --- TAB 4: History & Export ---
    with tab4:
        st.subheader("Transaction History")
        if user_data['history']:
            df_history = pd.DataFrame(user_data['history'])
            st.dataframe(df_history, use_container_width=True)
            
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Transaction Report (CSV)",
                data=csv,
                file_name=f"{user}_transactions.csv",
                mime="text/csv",
            )
        else:
            st.info("No transactions found.")

    # --- TAB 5: OTP Verification ---
    with tab5:
        st.subheader("Security Verification")
        if st.session_state.otp and st.session_state.pending_action:
            st.warning("A transaction is pending. Please verify your OTP.")
            action = st.session_state.pending_action
            
            if action['type'] == 'transfer':
                st.write(f"**Action:** Transfer RM {action['amount']} to {action['target']}")
            elif action['type'] == 'bill':
                st.write(f"**Action:** Pay RM {action['amount']} to {action['biller']}")
            elif action['type'] == 'credit_card':
                st.write(f"**Action:** Pay RM {action['amount']} for Card ending in {action['card']}")

            entered_otp = st.text_input("Enter 6-digit OTP")
            
            if st.button("Confirm Transaction"):
                if entered_otp == st.session_state.otp:
                    amt = action['amount']
                    data[user]['balance'] -= amt
                    
                    if action['type'] == 'transfer':
                        data[action['target']]['balance'] += amt
                        record_transaction(user, data, "Transfer Out", -amt, f"To {action['target']}")
                        record_transaction(action['target'], data, "Transfer In", amt, f"From {user}")
                    elif action['type'] == 'bill':
                        record_transaction(user, data, "Bill Payment", -amt, action['biller'])
                    elif action['type'] == 'credit_card':
                        record_transaction(user, data, "CC Payment", -amt, f"Card *{action['card']}")
                    
                    st.session_state.otp = None
                    st.session_state.pending_action = None
                    st.success("Transaction Completed Successfully!")
                    st.rerun()
                else:
                    st.error("Invalid OTP. Transaction failed.")
        else:
            st.info("No pending transactions requiring OTP.")
