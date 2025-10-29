import streamlit as st
import pandas as pd
from datetime import datetime
import os
from transformers import pipeline
import requests
import json

# -----------------------------
# Load sentiment analysis pipeline
# -----------------------------
@st.cache_resource
def load_sentiment_model():
    """
    Load a pre-trained sentiment analysis model from Hugging Face.
    Using cardiffnlp/twitter-roberta-base-sentiment-latest for 3-class sentiment (Positive, Neutral, Negative).
    """
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

sentiment_pipeline = load_sentiment_model()


# -----------------------------
# Prediction function
# -----------------------------
def predict_sentiment(review_text: str) -> str:
    if not review_text or review_text.strip() == "":
        return "Neutral"

    max_length = 512
    truncated_text = review_text[:max_length]
    result = sentiment_pipeline(truncated_text)[0]

    label = result['label']
    if label.lower() == 'positive':
        return "Positive"
    elif label.lower() == 'negative':
        return "Negative"
    else:
        return "Neutral"


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("💬 Customer Feedback and Sentiment Capture")
st.markdown("Please fill out the following details and provide your feedback below:")

with st.form("feedback_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        CustomerID = st.text_input("Customer ID")
        name = st.text_input("Name")
        DOB = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        occupation = st.text_input("Occupation")
        address = st.text_area("Address")
        pincode = st.text_input("Pincode")
        city = st.text_input("City")
        state = st.text_input("State")
        region = st.selectbox("Region", ["North", "South", "East", "West"])

    with col2:
        bank_branch = st.text_input("Bank Branch")
        mobile_no = st.text_input("Mobile No")
        email = st.text_input("Email")
        segment = st.selectbox("Segment", ["Retail", "Corporate", "SME", "NA"])
        account_no = st.text_input("Account No")
        created_at = st.date_input("Created At")
        closed_at = st.date_input("Closed At")

    with col3:
        kyc_status = st.selectbox("KYC Status", ["Completed", "Pending", "Rejected"])
        cibil = st.number_input("CIBIL Score", min_value=300, max_value=900, step=1)
        income = st.number_input("Income", min_value=0.0, step=1000.0)
        product_name = st.text_input("Product Name")
        category = st.text_input("Category")
        revenue_type = st.selectbox("Revenue Type", ["Commision", "Fee", "Interest", "NA"])
        product_type = st.selectbox("Product Type", ["Asset", "Liability", "NA"])

    st.markdown("---")

    col4, col5 = st.columns(2)
    with col4:
        transaction_date = st.date_input("Transaction Date", value=datetime.today())
        transaction_type = st.selectbox("Transaction Type", ["Credit", "Debit"])
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
    with col5:
        channel = st.selectbox("Channel", ["Online", "Branch", "ATM", "Mobile"])
        is_digital = st.selectbox("IS_DIGITAL", ["Yes", "No"])
        transaction_scope = st.selectbox("Transaction Scope", ["Domestic", "International"])
        transaction_mode = st.selectbox(
            "Transaction Mode", ["Cash", "Cheque", "Online Transfer", "NEFT", "RTGS", "IMPS", "UPI"]
        )

    st.markdown("---")

    review = st.text_area("📝 Review / Feedback")

    submitted = st.form_submit_button("Submit Feedback")

# -----------------------------
# Power Automate Connection
# -----------------------------
POWER_AUTOMATE_URL = "https://default37d6c2dc481348e3a84228cab8171c.98.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/112a4ff1062f4ed48bc7903b03e654a8/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=cxN7IomRTtqXOhtaZqL2PYdd0jRGqMaVXGA4q1BcGEE"

def send_to_online_excel(data: dict):
    headers = {"Content-Type": "application/json"}
    response = requests.post(POWER_AUTOMATE_URL, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 202]:
        st.success("✅ Feedback sent to Online Excel successfully!")
    else:
        st.error(f"⚠️ Failed to send data: {response.status_code}\n{response.text}")

# -----------------------------
# When form is submitted
# -----------------------------
if submitted:
    if not review.strip():
        st.warning("Please enter a review before submitting.")
    else:
        with st.spinner("Analyzing sentiment..."):
            sentiment = predict_sentiment(review)

        # ✅ Create plain JSON-serializable dictionary
        new_row = {
            "CustomerID": CustomerID,
            "Name": name,
            "DOB": str(DOB),
            "Gender": gender,
            "Occupation": occupation,
            "Address": address,
            "Pincode": pincode,
            "City": city,
            "State": state,
            "Region": region,
            "BankBranch": bank_branch,
            "MobileNo": mobile_no,
            "Email": email,
            "Segment": segment,
            "AccountNo": account_no,
            "CreatedAt": str(created_at),
            "ClosedAt": str(closed_at),
            "KYCStatus": kyc_status,
            "CIBIL": cibil,
            "Income": income,
            "ProductName": product_name,
            "Category": category,
            "RevenueType": revenue_type,
            "ProductType": product_type,
            "TransactionDate": str(transaction_date),
            "TransactionType": transaction_type,
            "Amount": amount,
            "Channel": channel,
            "IS_DIGITAL": is_digital,
            "TransactionScope": transaction_scope,
            "TransactionMode": transaction_mode,
            "Review": review,
            "Sentiment": sentiment,
        }

        # Send data to Power Automate
        send_to_online_excel(new_row)

        st.success(f"✅ Thank you for your feedback! Sentiment detected: **{sentiment}**")
