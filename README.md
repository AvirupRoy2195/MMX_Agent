# MMX BI & Agent Tool 🤖

An intelligent **Multi-Agent Business Intelligence and Marketing Mix Modeling** tool built with Streamlit and Python. This system uses specialized AI agents to analyze sales data, understand media channel impact, and provide actionable insights.

## 🌟 Features

### Multi-Agent Architecture
-   **Orchestrator**: Central coordinator managing all sub-agents
-   **Explorer Agent**: BI analytics (KPIs, categories, correlations)
-   **MMX Agent**: Marketing Mix Modeling (ROI, contributions, predictions)
-   **Visualization Agent**: Generates all charts and graphs
-   **Critique Agent**: Evaluates model quality and flags issues

### Capabilities
1.  **BI Dashboard**:
    -   High-level KPIs (Total Sales, Spend, Data Points)
    -   Sales trends over time
    -   Revenue breakdown by product category
    -   Correlation heatmaps between channels

2.  **MMX Lab**:
    -   Marginal ROI analysis for each media channel
    -   Sales contribution decomposition
    -   Model quality feedback from Critique Agent

3.  **Scenario Simulator**:
    -   Predict future sales by adjusting media budgets
    -   Compare against historical averages

4.  **Agent Chat**:
    -   Natural language interface to query insights
    -   Direct access to specialized agents

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
    pip install streamlit pandas scikit-learn plotly kagglehub
    ```

3.  **Download Data:**
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

```
MMX_Agent/
├── app.py                          # Main Streamlit UI
├── src/
│   ├── data_loader.py             # Data ingestion & cleaning
│   ├── model.py                   # Linear Regression model
│   └── agents/
│       ├── orchestrator.py        # Central coordinator
│       ├── explorer_agent.py      # BI analytics
│       ├── mmx_agent.py           # Marketing Mix Modeling
│       ├── viz_agent.py           # Visualization generation
│       └── critique_agent.py      # Quality evaluation
├── data/                          # Dataset directory
└── download_data.py               # Kaggle data downloader
```

## 📊 Methodology

### Marketing Mix Model
-   **Algorithm**: Linear Regression
-   **Target**: Total Sales (aggregated from revenue columns)
-   **Features**: Media spend across 9 channels (TV, Digital, Radio, etc.)
-   **ROI Calculation**: Model coefficients represent marginal sales per dollar spent

### Quality Assurance
The **Critique Agent** automatically evaluates:
-   Model accuracy (R² score)
-   Coefficient validity (flags negative ROI)
-   Data quality (sample size, missing values)

## 🎯 Use Cases

-   **Marketing Teams**: Optimize budget allocation across channels
-   **Data Analysts**: Explore sales patterns and correlations
-   **Business Leaders**: Understand ROI and make data-driven decisions

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the MIT License.