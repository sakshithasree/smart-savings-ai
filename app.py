from flask import Flask, render_template, request, jsonify
import numpy as np
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

# -----------------------------
# LOAD MODELS & ASSETS
# -----------------------------
try:
    model_final = joblib.load("xgb_model.pkl")
    lstm_model = load_model("lstm_model.h5", compile=False)
    scaler = joblib.load("scaler.pkl")
    print("Models loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load model files. {e}")
    model_final = None
    lstm_model = None
    scaler = None

SEQUENCE_LENGTH = 21


# -----------------------------
# PAGE ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template('home.html')   # if using index.html, change this back


@app.route('/dashboard')
def dashboard():
    trend_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    actual_balance = [4200, 4700, 5100, 5800, 6500, 7200]
    predicted_balance = [4250, 4750, 5150, 5850, 6550, 7300]

    insights_list = [
        "Unusual spending detected in Entertainment category",
        "You're on track to exceed your savings goal",
        "Recommended: Increase emergency fund by 5%"
    ]

    return render_template(
        'dashboard.html',
        trend_labels=trend_labels,
        actual_balance=actual_balance,
        predicted_balance=predicted_balance,
        insights_list=insights_list
    )


@app.route('/planner')
def planner():
    return render_template('planner.html')


@app.route('/scenario')
def scenario():
    return render_template('scenario.html')


@app.route('/insights')
def insights():
    category_labels = ['Housing', 'Food', 'Transport', 'Entertainment', 'Utilities', 'Other']
    category_values = [42, 16, 11, 10, 7, 14]

    weekly_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    weekly_spending = [670, 710, 580, 850]

    income_expense_labels = ['Jan', 'Feb', 'Mar', 'Apr']
    income_values = [6500, 6500, 7300, 6500]
    expense_values = [2700, 2780, 2940, 2710]
    savings_values = [3800, 3720, 4360, 3790]

    return render_template(
        'insights.html',
        category_labels=category_labels,
        category_values=category_values,
        weekly_labels=weekly_labels,
        weekly_spending=weekly_spending,
        income_expense_labels=income_expense_labels,
        income_values=income_values,
        expense_values=expense_values,
        savings_values=savings_values,
        risk_text="Risk Level: Low"
    )


@app.route('/reports')
def reports():
    weekly_report_labels = ['W1', 'W2', 'W3', 'W4']
    weekly_report_values = [680, 720, 590, 860]

    monthly_report_labels = ['Jan', 'Feb', 'Mar', 'Apr']
    monthly_income = [6500, 6500, 7300, 6500]
    monthly_expenses = [2700, 2780, 2940, 2710]
    monthly_savings = [3800, 3720, 4360, 3790]

    return render_template(
        'reports.html',
        weekly_report_labels=weekly_report_labels,
        weekly_report_values=weekly_report_values,
        monthly_report_labels=monthly_report_labels,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_savings=monthly_savings
    )


@app.route('/assistant')
def assistant():
    return render_template('assistant.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


# -----------------------------
# AI ASSISTANT ROUTE
# -----------------------------
@app.route('/assistant-chat', methods=['POST'])
def assistant_chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()

    if 'spending' in user_message:
        reply = "Your recent spending is mostly stable, but entertainment expenses are slightly elevated. A weekly discretionary cap may help."
    elif 'saving' in user_message or 'savings' in user_message:
        reply = "You are currently saving well. Increasing your savings by 5% monthly can help you reach your target sooner."
    elif 'budget' in user_message:
        reply = "A practical approach is 50% needs, 30% wants, and 20% savings. You may also reduce unnecessary spending categories."
    else:
        reply = "I can help with spending analysis, savings recommendations, budgeting, and financial planning."

    return jsonify({"reply": reply})


# -----------------------------
# EXACT SAME COLAB LOGIC
# -----------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if model_final is None or lstm_model is None or scaler is None:
            return jsonify({"error": "Model files are not loaded properly."}), 500

        data = request.get_json()

        # -----------------------------
        # PREPARE FEATURES
        # -----------------------------
        features = np.array([[
            float(data['income']),
            float(data['expense']),
            float(data['balance']),
            int(data['txn_count']),
            float(data['avg_txn']),
            float(data['rolling_7_exp']),
            float(data['rolling_7_inc']),
            float(data['lag_exp_1']),
            float(data['lag_exp_3']),
            float(data['lag_bal_1']),
            float(data['lag_bal_7']),
            int(data['dow']),
            int(data['is_weekend']),
            int(data['days_since_inc'])
        ]], dtype=np.float32)

        # -----------------------------
        # LSTM PREDICTION
        # -----------------------------
        lstm_input = np.tile(features, (SEQUENCE_LENGTH, 1))
        lstm_input = scaler.transform(lstm_input)
        lstm_input = lstm_input.reshape(1, SEQUENCE_LENGTH, -1)

        lstm_pred = lstm_model.predict(lstm_input, verbose=0)[0][0]

        # -----------------------------
        # FINAL PREDICTION (XGBOOST)
        # -----------------------------
        final_input = np.append(features, lstm_pred).reshape(1, -1)
        predicted_balance = model_final.predict(final_input)[0]

        # -----------------------------
        # SMART SAVINGS LOGIC
        # EXACT SAME AS COLAB
        # -----------------------------
        current_balance = float(data['balance'])
        rolling_7_expense = float(data['rolling_7_exp'])

        emergency_buffer = rolling_7_expense * 1.7
        surplus = predicted_balance - emergency_buffer

        if surplus <= 0:
            savings = 0
            message = "❌ Not safe to save (low balance)"
        elif surplus > 5000:
            savings = min(5000, surplus * 0.3)
            message = "✅ Strong saving opportunity"
        elif surplus > 2000:
            savings = surplus * 0.2
            message = "👍 Moderate saving possible"
        else:
            savings = 0
            message = "⚠️ Better to wait"

        # -----------------------------
        # OUTPUT
        # -----------------------------
        return jsonify({
            "current_balance": round(current_balance, 2),
            "predicted_balance": round(float(predicted_balance), 2),
            "emergency_buffer": round(float(emergency_buffer), 2),
            "surplus": round(float(surplus), 2),
            "savings": round(float(savings), 2),
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)