import streamlit as st
import json
import hashlib
import random
import pandas as pd
import datetime
import os

# ==========================================
# 0. ULTRA-SMOOTH APPLE UI (CSS INJECTION)
# ==========================================
def apply_ultra_smooth_design():
    st.markdown("""
    <style>
    /* 1. Import Apple-style Web Font (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* 2. Smoothie-Smooth Page Fade-In Animation */
    .stApp {
        animation: smoothFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    @keyframes smoothFade {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* 3. Apple Blue Pill Buttons with Soft Bounce */
    div[data-testid="stButton"] > button {
        background-color: #0071e3 !important;
        color: #ffffff !important;
        border-radius: 980px !important; 
        border: none !important;
        font-weight: 500 !important;
        padding: 6px 20px !important;
        transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #0077ED !important;
        transform: scale(1.03) !important;
        box-shadow: 0 6px 15px rgba(0, 113, 227, 0.2) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: scale(0.97) !important;
    }

    /* 4. Fix Inputs (Keeps the Password Eye Icon visible) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #0071e3 !important;
        box-shadow: 0 0 0 2px rgba(0, 113, 227, 0.2) !important;
    }
    
    /* 5. Apple Wallet Style Image Banners */
    [data-testid="stImage"] img {
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px !important;
    }
    
    /* 6. Hide annoying default Streamlit headers */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. DATA MANAGEMENT
# ==========================================
DATA_FILE = 'bank_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        default_data = {
            "user1": {"password": hash_password("password123"), "balance": 5000.0, "history": [], "locked": False},
            "user2": {"password": hash_password("password123"), "balance": 2000.0, "history": [], "locked": False}
        }
        save_data(default_data)
        return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def record_transaction(username, data, transaction_type, amount, details=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {"date": timestamp, "type": transaction_type, "amount": amount, "details": details, "balance_after": data[username]['balance']}
    data[username]['history'].append(record)
    save_data(data)

# ==========================================
# 2. SESSION INITIALIZATION
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.login_attempts = {}
    st.session_state.otp = None
    st.session_state.pending_action = None

# ==========================================
# 3. USER INTERFACE
# ==========================================
st.set_page_config(page_title="Apple Card", page_icon="", layout="centered")
apply_ultra_smooth_design()

data = load_data()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'> Card</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sign in to your account.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Continue", use_container_width=True)

            if submit_button:
                if username in data:
                    if data[username].get('locked', False):
                        st.error("Account locked.")
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
                            st.error("Account locked.")
                        else:
                            st.error(f"Incorrect password. {3 - attempts} attempts left.")
                else:
                    st.error("Account not found.")

# --- MAIN DASHBOARD ---
else:
    user = st.session_state.current_user
    user_data = data[user]

    # GIANT BALANCE AT TOP
    colA, colB = st.columns([3, 1])
    with colA:
        st.caption(f"Welcome back, {user.capitalize()}")
        st.markdown(f"<h1 style='font-size: 3.5rem; margin-top: -15px;'>RM {user_data['balance']:,.2f}</h1>", unsafe_allow_html=True)
    with colB:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
            
    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Services", "Activity", "Statements", "Security"])

    # --- TAB 1: Action Center (WITH IMAGES) ---
    with tab1:
        action = st.segmented_control(
            "Actions",
            ["💸 Send Money", "🧾 Pay Bill", "💳 Card Payment", "📥 Add Funds"],
            default="💸 Send Money",
            label_visibility="collapsed"
        )
        st.write("<br>", unsafe_allow_html=True)

        if action == "💸 Send Money":
            st.image("https://images.unsplash.com/photo-1613243555988-441166d4d6fd?auto=format&fit=crop&w=800&q=80", use_container_width=True)
            target_user = st.text_input("To (Username)")
            transfer_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            if st.button("Review Transfer"):
                if target_user not in data: st.error("Recipient not found.")
                elif target_user == user: st.error("Cannot send to yourself.")
                elif transfer_amount > user_data['balance']: st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "transfer", "target": target_user, "amount": transfer_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "🧾 Pay Bill":
            st.image("https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=800&q=80", use_container_width=True)
            biller = st.selectbox("Biller", ["TNB", "Syabas", "Unifi", "Maxis"])
            bill_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            if st.button("Review Payment"):
                if bill_amount > user_data['balance']: st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "bill", "biller": biller, "amount": bill_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "💳 Card Payment":
            st.image("https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=800&q=80", use_container_width=True)
            card_num = st.text_input("Card Number (Last 4)", max_chars=4)
            cc_amount = st.number_input("Amount (RM)", min_value=1.0, step=10.0)
            if st.button("Review Payment"):
                if len(card_num) != 4: st.error("Enter the last 4 digits.")
                elif cc_amount > user_data['balance']: st.error("Insufficient balance.")
                else:
                    st.session_state.otp = generate_otp()
                    st.session_state.pending_action = {"type": "credit_card", "card": card_num, "amount": cc_amount}
                    st.success(f"Verification code sent: {st.session_state.otp}. Enter it in the Security tab.")

        elif action == "📥 Add Funds":
            st.image("https://images.unsplash.com/photo-1580048915913-4f8f5cb481c4?auto=format&fit=crop&w=800&q=80", use_container_width=True)
            deposit_amount = st.number_input("Amount (RM)", min_value=1.0, step=50.0)
            if st.button("Add to Apple Cash"):
                data[user]['balance'] += deposit_amount
                record_transaction(user, data, "Deposit", deposit_amount, "Added Funds")
                st.success(f"Added RM {deposit_amount:,.2f}")
                st.rerun()

    # --- TAB 2: Activity ---
    with tab2:
        if user_data['history']:
            df = pd.DataFrame(user_data['history']).set_index('date')
            st.line_chart(df['balance_after'], color="#0071e3")
        else:
            st.info("No recent transactions.")

    # --- TAB 3: Statements ---
    with tab3:
        if user_data['history']:
            df_history = pd.DataFrame(user_data['history'])
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name=f"{user}_statement.csv", mime="text/csv")
        else:
            st.info("No activity yet.")

    # --- TAB 4: OTP Verification ---
    with tab4:
        if st.session_state.otp and st.session_state.pending_action:
            action_data = st.session_state.pending_action
            if action_data['type'] == 'transfer': st.markdown(f"**Send RM {action_data['amount']} to {action_data['target']}?**")
            elif action_data['type'] == 'bill': st.markdown(f"**Pay RM {action_data['amount']} to {action_data['biller']}?**")
            elif action_data['type'] == 'credit_card': st.markdown(f"**Pay RM {action_data['amount']} for Card ending in {action_data['card']}?**")

            entered_otp = st.text_input("Enter Verification Code")
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
            st.info("No payments require authorization.")
