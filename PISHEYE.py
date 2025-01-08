from PIL import Image
import hashlib
import os
import streamlit as st
from urllib.parse import urlparse
from Algoritmaa import Node, DecisionTree, RandomForest
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
import re



st.set_page_config(page_title="PishEye", layout="wide")


if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def read_user_database(file="data_user.csv"):
    if not os.path.exists(file):
        return pd.DataFrame(columns=["email", "username", "password"])
    return pd.read_csv(file)

def about_page():
    st.title("About")
    st.write("Ini adalah halaman About.")

def history_page():
    # CSS styling
    
    
    st.markdown(
        """
        <style>
            html, body {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        
        <style>
        .hero {
            background-color: #0078d7;
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            top: 0;
            margin-top: -110px;
            height: 300px;
             

        }
        .hero h1 {
            font-size: 48px;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 18px;
            line-height: 1.6;
        }
    
        </style>
        <div class="hero">
            <h1> </h1>
            <p> </p>
        </div>
        """,
        unsafe_allow_html=True,
       
    )
    st.markdown(
        """
        <style>
        .card {
            margin: auto;
            width: 90%;
            background: #f9f9f9;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            margin-top: -250px; 
        }
      .card .table-wrapper {
        max-height: 300px; 
        overflow-y: auto; 
        overflow-x: auto; 

    }

    .card .table {
        width: 100%;
        border-collapse: collapse;
        white-space: nowrap; 
        
        

      
    }

    .card .table th, .card .table td {
        padding: 10px 15px; 
        text-align: left; 
        vertical-align: top; 
        border: 1px solid #ddd; 
 
    }

    .card .table th {
        background-color: #0078d7; 
        color: white; 
        text-align: center; 
    }
    .card .table td:nth-child(1), .card .table th:nth-child(1) {
        width: 12px; 
        white-space: nowrap; 
    }

    .card .table td {
        text-align: center; 
    }


    .card .table-wrapper {
        margin: 0 auto; 
    }

        </style>
        """,
        unsafe_allow_html=True
    )

    if "username" in st.session_state:
        username = st.session_state["username"]
        
        history = load_history(username)
        
        # Data Missing 
        history.fillna("0", inplace=True)

        if not history.empty:
            columns_to_format = [
                "url_length", "path_length", "fd_length", "count-", "count.", "count=", 
                "count-http", "count-https", "count-www", "count-digits", "count_dir", 
                "count_slashes", "count_subdomain", "short_url"
            ]

            # Mengubah tipe data kolom yang diperlukan menjadi integer
            history[columns_to_format] = history[columns_to_format].astype('int')

            selected_columns = history[["URL", "Result"] + columns_to_format + ["Timestamp"]]

            table_html = selected_columns.to_html(index=False, classes="table table-striped")

            st.markdown(
                f"""
                <div class="card" style="border: 1px solid #ccc; padding: 16px; border-radius: 8px; text-align: center;">
                    <h2>Recently Checked URLs</h2>
                    <div class="table-wrapper">
                        {table_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card", style="text-align: center;">
                    <h2>Recently Checked URLs</h2>
                    <p>Belum ada URL yang Anda periksa.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.error("Harap login terlebih dahulu untuk melihat history.")


def load_history(username):
    filename = "history.csv"

    try:

        df = pd.read_csv(filename)

        if df.empty:
            return pd.DataFrame(columns=["URL", "Result", "url_length","path_length","fd_length","count-","count.","count=","count-http","count-https","count-www","count-digits","count_dir","count_slashes","count_subdomain","short_url", "Timestamp"])
        
        user_history = df[df["Username"] == username]
        return user_history
    except FileNotFoundError:
        return pd.DataFrame(columns=[ "URL", "Result", "url_length","path_length","fd_length","count-","count.","count=","count-http","count-https","count-www","count-digits","count_dir","count_slashes","count_subdomain","short_url", "Timestamp"])
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["URL", "Result", "url_length","path_length","fd_length","count-","count.","count=","count-http","count-https","count-www","count-digits","count_dir","count_slashes","count_subdomain","short_url", "Timestamp"])

def profile_page():
    st.title("Profile")
    st.write("Ini adalah halaman Profile.")

def shortening_service(url):
    short_url_services = (
        r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
        r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
        r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
        r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
        r'db\.tt|qr\.ae|adf\.ly|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|'
        r'is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
        r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|'
        r'tweez\.me|v\.gd|tr\.im|link\.zip\.net'
    )

    match = re.search(short_url_services, url)
    return 1 if match else 0
def extract_features_from_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname if parsed_url.hostname else ""
    path = parsed_url.path if parsed_url.path else ""

    features = {
        'url_length': len(url),
        'path_length': len(path),
        'fd_length': len(parsed_url.netloc.split('.')[-1]) if parsed_url.netloc else 0,
        'count-': url.count('-'),
        'count.': url.count('.'),
        'count=': url.count('='),
        'count-http': url.count('http'),
        'count-https': url.count('https'),
        'count-www': url.count('www'),
        'count-digits': sum(c.isdigit() for c in url),
        'count_dir': path.count('/'),
        'count_slashes': url.count('/'),
        'count_subdomain': hostname.count('.') if hostname else 0,
        'short_url': shortening_service(url),
    }

    feature_order = [
        'url_length', 'path_length', 'fd_length', 'count-', 'count.', 'count=',
        'count-http', 'count-https', 'count-www', 'count-digits', 'count_dir',
        'count_slashes', 'count_subdomain', 'short_url'
    ]
    feature_values = [features[key] for key in feature_order]

    return np.array(feature_values).reshape(1, -1), features



def predict_url(model, url):
    url_features_array, _ = extract_features_from_url(url)

    print(f"Features shape: {url_features_array.shape}")
    expected_features = model.n_features_in_
    print(f"Expected features: {expected_features}")
    
    if url_features_array.shape[1] != expected_features:
        raise ValueError(f"Jumlah fitur tidak sesuai. Diharapkan {expected_features}, tetapi ditemukan {url_features_array.shape[1]}")

    prediction = model.predict(url_features_array)
    return prediction[0]

try:
    model = joblib.load('random_forest_model.pkl')
except FileNotFoundError:
    st.error("Model tidak ditemukan. Pastikan model sudah dilatih dan disimpan dengan benar.")
    exit()



def home_page():
    
    st.markdown("""
    <style>
        html, body { margin: 0; padding: 0; box-sizing: border-box; }
        .block-container { padding: 0 !important; margin: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        .hero {
            background-color: #0078d7;
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            top: 0;
            margin-top: -110px;
            height: 200px;
        }
        .hero h1 {
            font-size:68px;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 58px;
            line-height: 1.6;
        }
    </style>
    <div class="hero">
        <h1><div style="position: relative; top: -50px;">PishEye</h1>
        <p><div style="font-size: 28px; position: relative; top: -163px;"><b>Think Before You Click Stay Safe from Tricks<b></p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown('<div style="text-align: center">', unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 19px;margin-left: 12.5%;position: relative; font-weight: bold; top: -10px;">Check your URL is phishing or malicious :</div>
    """, unsafe_allow_html=True)

    url = st.text_input(" ", placeholder="https://example.com")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <style>
            div[data-baseweb="input"] {
                height: 50px;
                font-size: 16px;
                width: 75%;
                max-width: 75%;
                margin: 20px auto;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                position: relative;
                top: -45px;
            }
        </style>
    """, unsafe_allow_html=True)

  
    st.markdown(
        """
        <style>
        .warning-div {
            background-color: #ffdddd;
            padding: 15px;
            border-radius: 5px;
            margin-top: -190px;
            text-align: center; 
        }
        .success-div {
            background-color: #ddffdd;
            padding: 15px;
            border-radius: 5px;
            margin-top: -190px;
            text-align: center; 
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        check_button = st.button('Check')
        st.markdown("""
            <style>
                .stButton > button {
                    position: relative;
                    margin-left: 82%;
                    top: -175px;  /* Keep the button in this position */
                }
            </style>
        """, unsafe_allow_html=True)


    if check_button:
        if url:
            try:
        
                url_features_array, url_features_dict = extract_features_from_url(url)
                result = predict_url(model, url)

                result_text = "Phishing" if result == 1 else "Not Phishing"
            
                if "username" in st.session_state:
                    username = st.session_state["username"]
                    save_to_csv(username, url, result_text, url_features_dict)
                else:
                    st.error("Harap login terlebih dahulu sebelum menggunakan fitur ini.")
                
    
                if result == 1:
                    st.markdown(
                        f"<div class='warning-div'>⚠️'<b>{url}</b>' This URL may not be safe, potentially <b>Phishing</b></div>",
                    
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(

                        f"<div class='success-div'>✅'<b>{url}</b>'This URL is safe, please continue your browsing</div>",
                        unsafe_allow_html=True
                    )

            except ValueError as e:
                st.error(f"Error: {e}")
        else:
            st.error("Harap masukkan URL.")



def save_to_csv(username, submit, result_text, features):
    filename = "history.csv"
    new_data = {
        "Username": [username],
        "URL": [submit],
        "Result": [result_text],
        "Timestamp": [pd.Timestamp.now()]
    }
    

    for key, value in features.items():
        new_data[key] = [value]

    new_data = pd.DataFrame(new_data)

    try:
        df = pd.read_csv(filename)
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    
    df.to_csv(filename, index=False)


def login_page():
    st.markdown("<br>" * 1, unsafe_allow_html=True) 
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div style='text-align: center; position: relative; top: 75px; margin-top: 35px;font-weight: bold;'>", unsafe_allow_html=True)
        st.write("# **PishEye**")
        st.write("##### Think Before You Click Stay Safe from Tricks")
        if st.button("**Sign Up**"):
            st.session_state["show_signup"] = True
            st.session_state["logged_in"] = False

    with col2:
        try:
            image = Image.open("logo.png")
            st.image(image, width=400)
        except FileNotFoundError:
            st.error("Gambar tidak ditemukan. Pastikan path gambar sudah benar.")

    with col3:
        email = st.text_input("Email", key="login_email").strip().lower()
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            users = read_user_database()
            if not email or not password:
                st.error("Harap lengkapi semua informasi sebelum melanjutkan.")
            elif email in users["email"].str.lower().values:
                user = users[users["email"].str.lower() == email].iloc[0]
                if hash_password(password) == user["password"]:
                    st.session_state["logged_in"] = True
                    st.session_state["show_signup"] = False
                    st.session_state["username"] = user["username"]
                else:
                    st.error("Password salah.")
            else:
                st.error("Email tidak ditemukan. Silakan Sign Up terlebih dahulu.")

# Halaman sign up
def signup_page():
    st.markdown("<br>" * 1, unsafe_allow_html=True) 
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div style='text-align: center; position: relative; top: 75px; margin-top: 35px;'>", unsafe_allow_html=True)
        st.write("# **PishEye**")
        st.write("##### Think Before You Click Stay Safe from Tricks")
        if st.button("Login"):
            st.session_state["show_signup"] = False

    with col2:
        try:
            image = Image.open("logo.png")
            st.image(image, width=400)
        except FileNotFoundError:
            st.error("Gambar tidak ditemukan. Pastikan path gambar sudah benar.")

    with col3:
        email = st.text_input("Email", key="signup_email").strip().lower()
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Konfirmasi Password", type="password", key="signup_confirm_password")
        
        users = read_user_database()
        if st.button("Sign Up"):
            if not email or not username or not password or not confirm_password:
                st.error("Harap lengkapi semua informasi sebelum melanjutkan.")
            elif password != confirm_password:
                st.error("Password tidak sama.")
            elif email in users["email"].str.lower().values:
                st.error("Email sudah terdaftar.")
            elif username in users["username"].values:
                st.error("Username sudah digunakan.")
            else:
                new_user = pd.DataFrame({
                    "email": [email],
                    "username": [username],
                    "password": [hash_password(password)]
                })
                updated_users = pd.concat([users, new_user], ignore_index=True)
                updated_users.to_csv("data_user.csv", index=False)
                st.success("Daftar Akun Berhasil!")
                st.session_state["show_signup"] = False



if st.session_state["logged_in"]:
    col1, col2 = st.columns([6, 2])
    st.markdown(
        """
        <style>
            .stColumn {
                padding-top: 60px;
            }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(
        """
        <style>
            div[role="radiogroup"] {
                display: flex;
                justify-content: center; 
                align-items: center; 
                gap: 20px; 
            }

            div[role="radiogroup"] input[type="radio"] + div {
                background-color: #f0f0f0;
                border: 2px solid #dcdcdc;
                border-radius: 50%; 
                width: 50px;
                height: 50px;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            div[role="radiogroup"] input[type="radio"]:checked + div {
                background-color: #0078d7;
                border: 2px solid #0078d7;
                color: white;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
            div[role="radiogroup"] label {
                padding-top: 60px;
                margin-top: -100px;
                margin-left: -30px;
                position: relative;
                left: -395px;
                
            }

            div[role="radiogroup"] input[type="radio"] {
                position: relative;
                top: 5px; 
                left: 180px; 
                margin-left: -20px;
                position: relative;

            }

            div[role="radiogroup"] input[type="radio"] + div {
                background-color: #f0f0f0;
                border: 2px solid #dcdcdc; 
                border-radius: 10%; 
                width: 80px;
                height: 35px; 
            }

            /* Style untuk radio button yang dipilih */
            div[role="radiogroup"] input[type="radio"]:checked + div {
                background-color: #0078d7; 
                border: 2px solid #0078d7; 
                border-radius: 10%; 
                color: white; 
            }
        </style>
        """,
        unsafe_allow_html=True
    )


    st.markdown("""
        <style>
        .stExpander {
            position: absolute;
            z-index: 100;
            background: white;
            width: 280px; 
            white-space: nowrap; 
                
            
        }
        </style>
    """, unsafe_allow_html=True)

    with col1:
        menu = st.radio(
            "",
            ["Home", "History"],
            horizontal=True,
            key="top_menu"
        )

    with col2:

        st.markdown("""
            <style>
                .logout-button-container {
                    text-align: center;
                    margin-top: 180px;
                    top:100px;
                    position: relative;
                    left: 30px;
                    margin-left : 300px;
                }
                .logout-button {
                   
                    background-color: #FF4B4B;
                    color: white;
                    cursor: pointer;
                    font-size: 16px;
                    width: 100px;
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)

        with st.expander(st.session_state["username"]):
            st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
            logout_button = st.button("Log Out", key="logout_button")
            st.markdown('</div>', unsafe_allow_html=True)

            if logout_button:
                st.session_state["logged_in"] = False
                st.session_state["username"] = ""
                st.success("You have logged out successfully.")

    if menu == "Home":
        home_page()
    elif menu == "History":
        history_page()
else:
    login_page() if not st.session_state["show_signup"] else signup_page()


