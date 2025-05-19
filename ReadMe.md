# GMedCC Health Burden & Intervention Forecasting

This project is a data-driven forecasting tool that models the economic burden of Non-Communicable Diseases (NCDs) in Indonesia and simulates the impact of health interventions (e.g., clinics, capacity). The system is modularized into:

- A **Flask backend API** that handles business logic
- A **Streamlit frontend** for demonstration and prototyping
- A `parameters.json` file for configuration and centralized control

---

## 📁 Project Structure (other files not listed are not essential)

```
.
├── flask_app.py                # Backend API (Flask)
├── home.py                    # Streamlit Frontend
├── model.py                   # Plotly visualization utilities
├── parameters.json            # Model configuration
├── data/
│   ├── indonesia_ncd_prevalence_cleaned.csv
│   ├── indonesia_ncd_economic_burden_cleaned.csv
│   ├── indonesia_ncd_economic_burden_undiagnosed_cleaned.csv
│   └── provinces_population.csv
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://your-repo-url.git
cd your-repo-folder
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Minimal required packages:

```text
flask
streamlit
pandas
numpy
plotly
```

---

## 🚀 Running the App

### Step 1: Start the Flask backend

This serves as the main engine for all calculations.

```bash
python flask_app.py
```

- Endpoint: `http://localhost:5000/predict`
- Accepts POST requests with JSON payload (see API contract below)

---

### Step 2: Launch the Streamlit frontend (optional)

For testing the app visually.

```bash
streamlit run home.py
```

---

## 📦 Configuration

Modify `parameters.json` to adjust constants (without touching logic):

```json
{
  "capacity_yearly": 110400,
  "old_ratio": 0.114785391254267,
  "old_population_all": 32424300,
  "growth_rate": 0.016,
  "undiagnosed_ratio": {
    "Diabetes": 0.75,
    "Hypertension": 0.6667,
    "Heart Problem": 0.93,
    "Stroke": 0.887
  }
}
```

---

## 📡 API Contract (`POST /predict`)

**Request Body**:

```json
{
  "disease": "Hypertension",
  "province": "Jakarta",
  "year": 2026,
  "clinics": 10,
  "providers": 4,
  "capacity_pct": 20
}
```

**Response**:

```json
{
  "population": 20403210,
  "susceptible_population": 1204394,
  "susceptible_diagnosed": 401456,
  "susceptible_undiagnosed": 802938,
  "economic_burden": 109200000,
  "economic_burden_per_capita": 136,
  "intervention_capacity": 11040,
  "pct_undiag_before": 66.67,
  "pct_undiag_after": 65.28,
  "economic_burden_after": 105100000,
  "economic_burden_delta": 4100000
}
```

---

## 👩‍💻 For Backend Developers

- Business logic is in `flask_app.py`
- Input/output are fully JSON-based
- All constants come from `parameters.json` (do not hardcode)
- You can modularize logic into `core_logic.py` for testability later

---

## 🎨 For Frontend Developers

- This app is currently prototyped in Streamlit (see `home.py`)
- Eventually, replace with a Vue/React/HTML frontend hitting Flask endpoints
- You can start by replicating the POST request and rendering metrics/pie charts

---

## 📌 Data Sources

- `indonesia_ncd_prevalence_cleaned.csv` — NCD prevalence by year
- `indonesia_ncd_economic_burden_cleaned.csv` — total economic burden
- `indonesia_ncd_economic_burden_undiagnosed_cleaned.csv` — burden of undiagnosed only
- `provinces_population.csv` — provincial population and clinic estimates

---

## 🧪 Future Roadmap (Optional)

- [ ] Add Swagger/OpenAPI docs
- [ ] Split Flask logic into `core_logic.py`
- [ ] Add unit tests (`pytest`)
- [ ] Dockerize the app for deployment
- [ ] Replace Streamlit with production frontend

---

## 📬 Contact

For any issues or improvements, please contact the lead developer or data science lead.
