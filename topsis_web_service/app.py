import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import smtplib
from email.message import EmailMessage

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="TOPSIS Web Application",
    layout="centered"
)

# -------------------------------------------------
# CONSTANTS & SETUP
# -------------------------------------------------
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# -------------------------------------------------
# TOPSIS FUNCTION
# -------------------------------------------------
def run_topsis(df, weights, impacts):
    # Minimum columns check
    if df.shape[1] < 3:
        raise ValueError("Input file must contain at least 3 columns")

    # First column is alternative name
    matrix = df.iloc[:, 1:]

    # Numeric check
    if not matrix.apply(pd.to_numeric, errors="coerce").notnull().all().all():
        raise ValueError("Criteria columns must contain numeric values only")

    # Parse weights & impacts
    weights = list(map(float, weights.split(",")))
    impacts = impacts.split(",")

    if len(weights) != len(impacts) or len(weights) != matrix.shape[1]:
        raise ValueError("Number of weights, impacts, and criteria must be equal")

    if any(i not in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be '+' or '-'")

    # Normalization
    norm_matrix = matrix / np.sqrt((matrix ** 2).sum())

    # Weighted normalized matrix
    weighted_matrix = norm_matrix * weights

    # Ideal best & worst
    ideal_best = []
    ideal_worst = []

    for i, impact in enumerate(impacts):
        if impact == '+':
            ideal_best.append(weighted_matrix.iloc[:, i].max())
            ideal_worst.append(weighted_matrix.iloc[:, i].min())
        else:
            ideal_best.append(weighted_matrix.iloc[:, i].min())
            ideal_worst.append(weighted_matrix.iloc[:, i].max())

    # Distance calculation
    dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

    # TOPSIS score & rank
    score = dist_worst / (dist_best + dist_worst)
    rank = score.rank(ascending=False, method="dense")

    # Result
    result = df.copy()
    result["Topsis Score"] = score
    result["Rank"] = rank.astype(int)

    return result

# -------------------------------------------------
# EMAIL FUNCTION (SECURE)
# -------------------------------------------------
def send_email(receiver_email, attachment_path):
    EMAIL_ADDRESS = os.getenv("TOPSIS_EMAIL")
    EMAIL_PASSWORD = os.getenv("TOPSIS_EMAIL_PASSWORD")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("Email credentials not configured on server")

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg.set_content("Please find the attached TOPSIS result file.")

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="topsis_result.csv"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.title("📊 TOPSIS Decision Making Tool")
st.write(
    "Upload a dataset, provide weights and impacts, and receive the TOPSIS result via email."
)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)

weights = st.text_input(
    "Weights (comma separated)",
    placeholder="1,1,1,2"
)

impacts = st.text_input(
    "Impacts (comma separated)",
    placeholder="+,+,-,+"
)

email = st.text_input(
    "Email ID",
    placeholder="example@gmail.com"
)

# -------------------------------------------------
# BUTTON ACTION
# -------------------------------------------------
if st.button("Run TOPSIS"):
    try:
        if uploaded_file is None:
            st.error("Please upload an input file")
            st.stop()

        if not re.match(EMAIL_REGEX, email):
            st.error("Invalid email format")
            st.stop()

        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Run TOPSIS
        result_df = run_topsis(df, weights, impacts)

        # Save result
        output_path = os.path.join(TEMP_DIR, "topsis_result.csv")
        result_df.to_csv(output_path, index=False)

        # Send email
        send_email(email, output_path)

        st.success("TOPSIS completed successfully! Result sent to your email.")
        st.dataframe(result_df)

    except Exception as e:
        st.error(f"Error: {str(e)}")
