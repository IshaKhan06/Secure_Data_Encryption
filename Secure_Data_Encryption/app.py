import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# ---------- Setup ----------

# FIXED key for consistent encryption/decryption (use the key generated once)
FERNET_KEY = b'NteAuihrQD2In_WLEbLOpCs1ygrZfSWbDAk3r3x3NIg='  # Replace with your own generated key
cipher = Fernet(FERNET_KEY)

# In-memory data storage and failed attempts
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}  # {"encrypted_text": {"encrypted_text": ..., "passkey": hashed_passkey}}
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False  # Initial login state should be False
if "login_success" not in st.session_state:
    st.session_state.login_success = False  # Fix for success message error

# ---------- Utility Functions ----------

# Function to hash passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)
    data = st.session_state.stored_data.get(encrypted_text)

    if data and data["passkey"] == hashed_passkey:
        st.session_state.failed_attempts = 0
        return cipher.decrypt(encrypted_text.encode()).decode()
    
    st.session_state.failed_attempts += 1
    return None

# ---------- Pages ----------

# Navigation Menu
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("🔎 Navigate", menu)

# ---------- Home Page ----------
if choice == "Home":
    st.title("🔐 Secure Data Encryption System")
    st.write("Welcome! This app helps you **encrypt and store text securely**, and retrieve it with your passkey.")
    st.info("Navigate using the sidebar ➡️")

# ---------- Store Data Page ----------
elif choice == "Store Data":
    st.header("📥 Store Data Securely")

    user_data = st.text_area("Enter your secret data:")
    passkey = st.text_input("Create a Passkey:", type="password")

    if st.button("Encrypt & Store"):
        if user_data and passkey:
            encrypted_text = encrypt_data(user_data)
            hashed_pass = hash_passkey(passkey)
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_pass
            }
            st.success("✅ Your data has been securely stored!")
            st.code(encrypted_text, language="text")
        else:
            st.warning("Please enter both data and passkey.")

# ---------- Retrieve Data Page ----------
elif choice == "Retrieve Data":
    st.header("🔍 Retrieve Encrypted Data")

    if not st.session_state.is_logged_in:
        st.warning("🔒 You are locked out. Please go to the Login page to reauthorize.")
    else:
        encrypted_input = st.text_area("Enter the Encrypted Text:")
        passkey_input = st.text_input("Enter Your Passkey:", type="password")

        if st.button("Decrypt"):
            if encrypted_input and passkey_input:
                result = decrypt_data(encrypted_input, passkey_input)

                if result:
                    st.success("✅ Decryption Successful!")
                    st.text_area("Your Original Data:", result, height=150)
                else:
                    remaining = 3 - st.session_state.failed_attempts
                    if remaining > 0:
                        st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")
                    else:
                        st.warning("🔐 Too many failed attempts! Redirecting to Login Page...")
                        st.session_state.is_logged_in = False
                        st.rerun()
            else:
                st.warning("Both fields are required!")

# ---------- Login Page ----------
elif choice == "Login":
    st.header("🔑 Reauthorization Required")

    login_pass = st.text_input("Enter Master Password :", type="password")
    
    if st.button("Login"):
        if login_pass == "admin123":
            st.session_state.failed_attempts = 0
            st.session_state.is_logged_in = True
            st.session_state.login_success = True
            st.rerun()
        else:
            st.error("❌ Incorrect password!")

    # ✅ Show success message *below* login button after rerun
    if st.session_state.login_success:
        st.success("✅ Reauthorized successfully! You can now retrieve data.")
        st.session_state.login_success = False  # Reset after showing once
