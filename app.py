import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="🚄 Train Prioritization System",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# Sidebar Navigation
# ==============================
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "📤 Upload Data", "📊 Prioritization Results", "📈 Analytics"])

# ==============================
# Home Page
# ==============================
if page == "🏠 Home":
    st.title("🚄 AI-Powered Train Prioritization")
    st.markdown("""
    Welcome to the **AI Train Traffic Management System**.  
    This system uses **Fuzzy Logic** to compute the urgency of trains based on:
    - 🚆 Train Type (Rajdhani, Duronto, Shatabdi, etc.)
    - ⏱️ Climatic Delays
    - ⚡ Train Priority & Duration

    Use the sidebar to upload train data and view results.
    """)

    st.image("https://i.gifer.com/origin/28/28d44d10d27f13e54f47e49a8ae0c3f4_w200.gif", caption="Smart Train Scheduling", use_column_width=True)

# ==============================
# Upload Data Page
# ==============================
elif page == "📤 Upload Data":
    st.title("📤 Upload Train Data")
    uploaded_file = st.file_uploader("Upload Train Dataset (CSV or PKL)", type=["csv", "pkl"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_pickle(uploaded_file)

        # Normalize columns
        df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]

        st.success("✅ Data Uploaded Successfully!")
        st.write("Preview of Uploaded Data:")
        st.dataframe(df.head())

        # Store data in session for other pages
        st.session_state["train_data"] = df

# ==============================
# Prioritization Results Page
# ==============================
elif page == "📊 Prioritization Results":
    st.title("📊 Train Prioritization Results")

    if "train_data" not in st.session_state:
        st.warning("⚠️ Please upload data first (Go to Upload Data tab).")
    else:
        df = st.session_state["train_data"]

        # Filter controls
        train_types = st.multiselect("Select Train Types:", options=df["TRAIN_TYPE"].unique(),
                                     default=list(df["TRAIN_TYPE"].unique()))
        min_urgency = st.slider("Minimum Urgency Score:", 0, 10, 0)

        df_filtered = df[df["TRAIN_TYPE"].isin(train_types)]
        if "URGENCY_SCORE" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["URGENCY_SCORE"] >= min_urgency]

        # Sort
        df_sorted = df_filtered.sort_values(by=["URGENCY_SCORE", "TRAIN_PRIORITY"], ascending=[False, False])

        # Train Animation
        st.subheader("🚆 Animated Train Preview")
        top_trains = df_sorted.head(5)
        animation_placeholder = st.empty()
        for step in range(1, 8):
            display_text = ""
            for _, row in top_trains.iterrows():
                display_text += f"{'🚄'*step} {row['TRAIN_NAME']} | Urgency: {row.get('URGENCY_SCORE',0):.1f}\n"
            animation_placeholder.text(display_text)
            time.sleep(0.3)

        # Table
        st.subheader("📋 Train Table")
        st.dataframe(
            df_sorted[["TRAIN_NUMBER","TRAIN_NAME","TRAIN_TYPE",
                       "TRAIN_PRIORITY","CLIMATIC_DELAYS_MINS",
                       "URGENCY_SCORE","DURATION_MINS"]].style.background_gradient(
                           subset=["URGENCY_SCORE"], cmap="Reds"
                       )
        )

        # Top 3 trains
        st.subheader("🔥 Top 3 High Urgency Trains")
        for _, row in df_sorted.head(3).iterrows():
            st.markdown(f"<span style='color:red; font-size:18px'>🚄 {row['TRAIN_NAME']} | Urgency: {row['URGENCY_SCORE']:.1f}</span>", unsafe_allow_html=True)

# ==============================
# Analytics Page
# ==============================
elif page == "📈 Analytics":
    st.title("📈 Analytics Dashboard")

    if "train_data" not in st.session_state:
        st.warning("⚠️ Please upload data first (Go to Upload Data tab).")
    else:
        df = st.session_state["train_data"]

        # Plot urgency distribution
        st.subheader("Urgency Score Distribution")
        fig, ax = plt.subplots()
        df["URGENCY_SCORE"].hist(ax=ax, bins=10)
        ax.set_xlabel("Urgency Score")
        ax.set_ylabel("Train Count")
        st.pyplot(fig)

        # Metrics
        st.subheader("📊 Summary Stats")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Max Urgency", round(df['URGENCY_SCORE'].max(),2))
        col2.metric("Min Urgency", round(df['URGENCY_SCORE'].min(),2))
        col3.metric("Avg Duration (mins)", int(df['DURATION_MINS'].mean()))
        col4.metric("Total Trains", len(df))
