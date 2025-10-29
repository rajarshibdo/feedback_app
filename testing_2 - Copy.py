import requests
import json
from datetime import datetime

# 🔗 Your Power Automate Flow URL
POWER_AUTOMATE_URL = "https://default37d6c2dc481348e3a84228cab8171c.98.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/112a4ff1062f4ed48bc7903b03e654a8/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=cxN7IomRTtqXOhtaZqL2PYdd0jRGqMaVXGA4q1BcGEE"


def send_to_online_excel(data: dict):
    """Send a JSON payload to Power Automate"""
    headers = {"Content-Type": "application/json"}
    response = requests.post(POWER_AUTOMATE_URL, headers=headers, data=json.dumps(data))
    if response.status_code in (200, 202):
        st.success("✅ Feedback sent to Online Excel successfully!")
    else:
        st.error(f"⚠️ Failed to send data: {response.status_code}\n{response.text}")


# -------------------------
# When form is submitted
# -------------------------
if 'submitted' in locals() and submitted:
    if not review.strip():
        st.warning("Please enter a review before submitting.")
    else:
        # 1️⃣ Predict sentiment
        with st.spinner("Analyzing sentiment..."):
            sentiment = predict_sentiment(review)

        # 2️⃣ Prepare row as a plain dict (✅ JSON-serializable)
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
            "Bank Branch": bank_branch,
            "MobileNo": mobile_no,
            "Email": email,
            "Segment": segment,
            "AccountNo": account_no,
            "Created_at": str(created_at),
            "Closed_at": str(closed_at),
            "KYC_Status": kyc_status,
            "CIBIL": cibil,
            "Income": income,
            "Product_Name": product_name,
            "Category": category,
            "Revenue_Type": revenue_type,
            "Product_Type": product_type,
            "Transaction_Date": str(transaction_date),
            "Transaction_Type": transaction_type,
            "Amount": amount,
            "Channel": channel,
            "IS_DIGITAL": is_digital,
            "Transaction_Scope": transaction_scope,
            "Transaction_Mode": transaction_mode,
            "Review": review,
            "Sentiment": sentiment,
        }

        # 3️⃣ Send JSON payload to Power Automate
        send_to_online_excel(new_row)

        # 4️⃣ Show user confirmation
        st.success(f"✅ Thank you for your feedback! Sentiment detected: **{sentiment}**")
