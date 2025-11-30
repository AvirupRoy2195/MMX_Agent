# MMX Agent & Chatbot 🤖

An intelligent Marketing Mix Modeling (MMX) Agent built with Streamlit and Python. This tool helps marketers analyze sales data, understand the impact of media channels (TV, Digital, Radio, etc.), and simulate future scenarios to optimize budgets.

## 🌟 Features

-   **Interactive Dashboard**: Visualize sales trends against media spend and understand channel performance.
-   **ROI Analysis**: Automatically calculates the Marginal ROI (Return on Investment) for each marketing channel using a regression model.
-   **Scenario Simulator**: Predict future sales by adjusting media budgets in real-time.
-   **Chat Interface**: Ask natural language questions about your data, such as "Show me ROI" or "What is the model accuracy?".

## 🚀 Getting Started

### Prerequisites

-   Python 3.8 or higher
-   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AvirupRoy2195/MMX_Agent.git
    cd MMX_Agent
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install manually: `pip install streamlit pandas scikit-learn plotly kagglehub`)*

3.  **Download Data:**
    The app uses a Kaggle dataset. Run the download script:
    ```bash
    python download_data.py
    ```

### Running the App

Launch the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## 📂 Project Structure

-   `app.py`: Main Streamlit application entry point.
-   `src/`: Source code directory.
    -   `agent.py`: Core logic for the MMX Agent (orchestration).
    -   `data_loader.py`: Handles data ingestion and cleaning.
    -   `model.py`: Implements the Marketing Mix Model (Linear Regression).
-   `data/`: Directory where dataset files are stored (after running `download_data.py`).

## 📊 Methodology

The agent uses a **Linear Regression** model to estimate the contribution of each media channel to Total Sales.
-   **Target**: Total Sales (aggregated from revenue columns).
-   **Features**: Spend on TV, Digital, Sponsorship, Content Marketing, Online Marketing, Affiliates, SEM, Radio, and Other.
-   **ROI Calculation**: The coefficients of the regression model represent the marginal contribution of each channel.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is open-source.