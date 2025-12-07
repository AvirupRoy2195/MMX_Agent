# MMX Agentic BI Assistant 🤖

An intelligent **AI-powered Marketing Mix Modeling and Business Intelligence Agent** built with a multi-agent architecture. Ask questions in natural language and get insights with dynamic visualizations.

## 🌟 Key Features

### Conversational BI Interface
- **Single Agent Interface**: No complex dashboards - just chat with the AI
- **Dynamic Visualizations**: Agent generates charts on-demand based on your questions
- **Natural Language Queries**: Ask questions like "Show me ROI decomposition" or "Which channel should I optimize?"
- **Intelligent Fallback**: Uses LLM-powered NL2SQL for any unrecognized query

### Agentic Capabilities (NEW!)
- **Planning Agent**: Breaks down complex, multi-step queries into executable plans
- **NL2SQL Agent**: Converts natural language to Pandas code for flexible data queries
- **LLM Integration**: Powered by Google Gemini for enhanced understanding

### 🏛️ LLM Council (Karpathy Pattern)

Inspired by [Karpathy's llm-council](https://github.com/karpathy/llm-council), this feature brings **multi-LLM deliberation** to your queries:

| Stage | Description |
|-------|-------------|
| **0. Reasoning** | GPT-5 analyzes query type, complexity, and approach |
| **1. First Opinions** | Claude Opus 4.5, GPT-5, Grok 4.1 respond independently |
| **2. Peer Review** | Each LLM reviews and ranks the others' responses |
| **3. Chairman Synthesis** | Claude Opus 4.5 synthesizes the final, refined answer |

**Premium Models Used:**
- `anthropic/claude-opus-4.5` - Chairman & Council Member
- `openai/gpt-5` - Reasoning & Council Member  
- `x-ai/grok-4.1-fast` - Council Member

**Key Features:**
- 🌐 **Multi-Model Diversity**: Uses OpenRouter to access GPT-5, Claude Opus, and Grok
- 🧠 **Reasoning Stage**: Analyzes query before generating responses
- 💾 **Conversation Memory**: Remembers last 10 exchanges for context
- 📊 **Data-Aware**: Council receives real-time analysis metrics
- 🔄 **Robust**: 3 retries with fallback to Gemini

### Component Architecture

| Component | API | Purpose |
|-----------|-----|----------|
| **LLM Council** | OpenRouter | Premium multi-model deliberation |
| **CritiqueAgent** | Gemini | Intelligent model critiques & recommendations |
| **NL2SQL Agent** | Gemini | Natural language to Pandas query translation |
| **Planning Agent** | Gemini | Complex query decomposition |
| **SchemaMapperAgent** | Gemini | Table mapping & relationship detection |
| **VizAgent** | - | Dynamic chart generation with NL2SQL |

### 🗺️ Schema Mapper Agent

The **SchemaMapperAgent** intelligently maps user queries to the correct database tables and relationships:

**How It Works:**
1. User asks: *"Show me products sold during Diwali sale"*
2. LLM analyzes query and identifies tables: `products`, `special_sales`
3. Suggests join: `product_analytic_vertical ↔ Product`
4. Returns properly mapped data

**Tables Mapped:**
| Table | Rows | Description |
|-------|------|-------------|
| `monthly_data` | 12 | Aggregated sales & spend |
| `media_investment` | 12 | Media spend by channel |
| `nps_scores` | 12 | Monthly NPS |
| `products` | 75 | Product catalog |
| `special_sales` | 44 | Sale events calendar |
| `transactions` | 1M+ | Individual orders |

**Relationships Detected:**
- `monthly_data` ↔ `media_investment` (via month)
- `monthly_data` ↔ `nps_scores` (via date)
- `transactions` ↔ `products` (via product category)

### 📋 Data Schema (YAML)

The agent uses `config/data_schema.yaml` for field definitions:

| Field | Description |
|-------|-------------|
| **ID** | Unique SKU identification |
| **Order_ID** | Unique order identification |
| **Order_Item_ID** | Item-level tracking |
| **GMV** | Gross Merchandise Value (Revenue) |
| **Units** | Number of units sold |
| **MRP** | Maximum Retail Price |
| **Procurement_SLA** | Time to procure (days) |

### Advanced Analytics Capabilities

#### 1. Marketing Mix Modeling (MMM)
- **Adstock Transformations**: Captures carryover effects of marketing spend
- **ROI Decomposition**: Separates immediate vs long-term returns
- **Multi-Model Comparison**: Compares 3 models (Immediate, Adstock, Full)

#### 2. Brand Equity Analysis
- **NPS Tracking**: Monitor Net Promoter Score trends
- **Brand Impact Quantification**: Measure sales lift per NPS point
- **Correlation Analysis**: Understand NPS-Sales relationships

#### 3. Business Intelligence
- **Sales Analysis**: Category breakdowns, trends, totals
- **Channel Performance**: ROI, contributions, efficiency metrics
- **Budget Optimization**: Spend mix analysis, allocation recommendations
- **Data Correlations**: Heatmaps showing channel relationships

## 🏗️ Architecture

### Multi-Agent System

```mermaid
graph TB
    User[User] -->|Natural Language Query| UI[Streamlit Chat UI]
    UI --> AgenticChat[Agentic BI Chat Agent]
    
    AgenticChat -->|Complex Queries| Planner[Planning Agent<br/>Query Decomposition]
    AgenticChat -->|Data Queries| NL2SQL[NL2SQL Agent<br/>Pandas Code Gen]
    AgenticChat -->|Council Mode| Council[LLM Council<br/>Multi-Model Deliberation]
    AgenticChat -->|Table Mapping| SchemaMapper[Schema Mapper Agent<br/>Table Relationships]
    AgenticChat -->|Coordinates| Orch[Orchestrator]
    
    SchemaMapper -->|YAML Schema| Schema[(config/data_schema.yaml)]
    SchemaMapper -->|Mapped Tables| NL2SQL
    
    Council -->|GPT + Claude + Gemini| AgenticChat
    
    Planner -->|Step Execution| AgenticChat
    NL2SQL -->|Results| AgenticChat
    
    Orch --> Explorer[Explorer Agent<br/>BI Analytics]
    Orch --> MMX[MMX Agent<br/>Basic Modeling]
    Orch --> AdvMMM[Advanced MMM<br/>Adstock & Brand]
    Orch --> Brand[Brand Agent<br/>NPS Analysis]
    Orch --> Viz[Visualization Agent<br/>Chart Generation]
    Orch --> Critique[Critique Agent<br/>Quality Checks]
    
    Explorer --> Data[(Data Layer<br/>CSV Files)]
    MMX --> Data
    AdvMMM --> Data
    Brand --> Data
    
    AdvMMM --> Adstock[Adstock Utils<br/>Carryover Effects]
    
    Viz -->|Returns Charts| AgenticChat
    AgenticChat -->|Response + Chart| UI
    
    style AgenticChat fill:#1e88e5,stroke:#0d47a1,stroke-width:3px,color:#fff
    style Planner fill:#ff5722,stroke:#bf360c,stroke-width:2px,color:#fff
    style NL2SQL fill:#4caf50,stroke:#1b5e20,stroke-width:2px,color:#fff
    style Council fill:#e91e63,stroke:#880e4f,stroke-width:2px,color:#fff
    style SchemaMapper fill:#00e676,stroke:#00c853,stroke-width:2px,color:#000
    style Orch fill:#ffc107,stroke:#ff6f00,stroke-width:2px,color:#000
    style AdvMMM fill:#00bcd4,stroke:#006064,stroke-width:2px,color:#fff
    style Viz fill:#9c27b0,stroke:#4a148c,stroke-width:2px,color:#fff
    style Schema fill:#607d8b,stroke:#37474f,stroke-width:1px,color:#fff
```

### 📊 Data Flow Diagram

The following diagram illustrates how data flows through the MMX Agent system, from raw data sources to final insights:

```mermaid
flowchart TB
    subgraph DataSources["📁 Data Sources (Kaggle Dataset)"]
        Sales["Sales.csv<br/>1M+ Transactions"]
        Media["MediaInvestment.csv<br/>Monthly Spend"]
        NPS["MonthlyNPSscore.csv<br/>NPS Scores"]
        Products["ProductList.csv<br/>Product Catalog"]
        Special["SpecialSale.csv<br/>Sale Events"]
        Monthly["Secondfile.csv<br/>Pre-aggregated"]
    end

    subgraph DataLayer["🔄 Data Layer"]
        DL["DataLoader<br/>Load & Cache"]
        Transform["Data Transformation<br/>Merge & Aggregate"]
        Tables["In-Memory Tables<br/>monthly_data, media_investment,<br/>nps_scores, products, special_sales"]
    end

    subgraph AgentLayer["🤖 Agent Processing Layer"]
        Schema["SchemaMapperAgent<br/>Table Mapping"]
        NL2SQL["NL2SQLAgent<br/>Query Generation"]
        Explorer["ExplorerAgent<br/>KPIs & Correlations"]
        MMX["MMXAgent<br/>Basic MMM"]
        AdvMMM["AdvancedMMM<br/>Adstock & Brand"]
        Brand["BrandAgent<br/>NPS Analysis"]
    end

    subgraph OutputLayer["📈 Output Layer"]
        Viz["VizAgent<br/>Chart Generation"]
        Insights["Insights & Metrics"]
        Response["Chat Response"]
    end

    Sales --> DL
    Media --> DL
    NPS --> DL
    Products --> DL
    Special --> DL
    Monthly --> DL

    DL --> Transform
    Transform --> Tables

    Tables --> Schema
    Tables --> Explorer
    Tables --> MMX
    Tables --> AdvMMM
    Tables --> Brand
    
    Schema --> NL2SQL
    NL2SQL --> Insights

    Explorer --> Insights
    MMX --> Insights
    AdvMMM --> Insights
    Brand --> Insights

    Insights --> Viz
    Viz --> Response
    Insights --> Response

    style DataSources fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style DataLayer fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style AgentLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style OutputLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

### 🔀 Query Processing Sequence

This sequence diagram shows how a user query is processed through the system:

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant Chat as AgenticBIChat
    participant Plan as PlanningAgent
    participant Schema as SchemaMapper
    participant NL2SQL as NL2SQLAgent
    participant Orch as Orchestrator
    participant Data as DataLoader
    participant Viz as VizAgent
    participant LLM as Gemini LLM

    U->>UI: Natural Language Query
    UI->>Chat: process_query()
    
    alt Complex Multi-Step Query
        Chat->>Plan: decompose_query()
        Plan->>LLM: Analyze & Plan
        LLM-->>Plan: Execution Steps
        Plan-->>Chat: Step-by-step Plan
    end

    Chat->>Schema: map_query_to_tables()
    Schema->>LLM: Identify Tables
    LLM-->>Schema: Table Mapping
    Schema-->>Chat: Relevant Tables & Joins

    alt Data Query
        Chat->>NL2SQL: generate_code()
        NL2SQL->>LLM: NL to Pandas
        LLM-->>NL2SQL: Python Code
        NL2SQL->>Data: Execute Query
        Data-->>NL2SQL: DataFrame Results
        NL2SQL-->>Chat: Query Results
    else Analytics Query
        Chat->>Orch: run_analysis()
        Orch->>Data: get_mmm_data()
        Data-->>Orch: Aggregated Data
        Orch-->>Chat: Analytics Results
    end

    Chat->>Viz: generate_chart()
    Viz-->>Chat: Plotly Figure
    
    Chat-->>UI: Response + Chart
    UI-->>U: Display Results
```

### Component Details

#### **Agentic BI Chat** (`src/agents/agentic_bi_chat.py`)
- Natural language understanding
- Query routing to appropriate agents
- Response formatting with visualizations

#### **Orchestrator** (`src/agents/orchestrator.py`)
- Central coordinator for all sub-agents
- Runs analysis pipelines
- Manages state and data flow

#### **Specialized Agents**
- **Explorer Agent**: KPIs, categories, correlations
- **MMX Agent**: Basic linear regression modeling
- **Advanced MMM**: Adstock transformations, multi-model comparison
- **Brand Agent**: NPS analysis and trends
- **Visualization Agent**: Dynamic chart generation
- **Critique Agent**: Model quality evaluation

#### **Data Layer** (`src/data_loader.py`)
- Loads and cleans Kaggle dataset
- Aggregates sales by category
- Merges media spend with NPS data

#### **Utilities**
- **Adstock Utils** (`src/utils/adstock.py`): Geometric adstock transformations
- **LLM Interface** (`src/utils/llm_interface.py`): Google Gemini integration
- **Memory** (`src/utils/memory.py`): Conversational context tracking

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AvirupRoy2195/MMX_Agent.git
   cd MMX_Agent
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas scikit-learn plotly kagglehub python-dotenv google-generativeai httpx
   ```

3. **Download data:**
   ```bash
   python download_data.py
   ```

### Running the Agent

```bash
streamlit run app.py
```

The agent will open at `http://localhost:8501`

### LLM Setup (Optional but Recommended)

To enable full Planning & NL2SQL capabilities:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Restart the app

### OpenRouter Setup (For LLM Council)

To enable the full **LLM Council** with diverse models (GPT, Claude, Gemini):

1. Get an API key from [OpenRouter](https://openrouter.ai/)
2. Add to your `.env` file:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your_key_here
   ```
3. Enable "🏛️ Council Mode" in the sidebar

## 💬 Sample Queries

### Sales Analysis
- "Show me sales by category"
- "What's the sales trend over time?"
- "Total sales"

### ROI & Performance
- "Show me ROI"
- "ROI decomposition" *(short vs long-term)*
- "Which channel has the best ROI?"

### Budget Optimization
- "Show me spend mix"
- "Channel efficiency"
- "Which channel should I optimize?"

### Brand Health
- "Show me NPS"
- "Brand analysis"
- "NPS trend"

### Model Performance
- "Compare models"
- "Model accuracy"
- "Show model performance"

### Correlations
- "Show correlations"
- "Relationship between channels"

### Flexible Data Queries (NL2SQL)
- "Show me the table rows in the data"
- "What are the column names?"
- "List all months where TV spend was above 50000"
- "Rank channels by total contribution"

### Multi-Step Queries (Planning Agent)
- "First show me sales trend, then tell me the best ROI channel"
- "Compare model performance and then summarize the feedback"

## 📊 Technical Details

### Models Implemented

1. **Immediate Effects Model**
   - Simple linear regression: `Sales = β₀ + Σ(βᵢ × Spendᵢ)`

2. **Adstock Model**
   - Includes carryover: `Sales = β₀ + Σ(βᵢ × Spendᵢ) + Σ(γᵢ × Adstock(Spendᵢ))`
   - Adstock: `Adstock[t] = Spend[t] + decay × Adstock[t-1]`

3. **Full Model**
   - Adstock + Brand Equity: `Sales = ... + β_NPS × NPS`

### Visualizations Available
- Line charts (trends)
- Bar charts (ROI, contributions)
- Stacked bar charts (ROI decomposition)
- Pie/Donut charts (spend mix, categories)
- Scatter plots (channel efficiency)
- Heatmaps (correlations)
- Model comparison charts

## 📁 Project Structure

```
MMX_Agent/
├── app.py                          # Main Streamlit app (Agent UI)
├── src/
│   ├── data_loader.py             # Data ingestion & cleaning
│   ├── model.py                   # Basic MMM model
│   ├── agents/
│   │   ├── orchestrator.py        # Central coordinator
│   │   ├── agentic_bi_chat.py     # Conversational agent
│   │   ├── explorer_agent.py      # BI analytics
│   │   ├── mmx_agent.py           # Basic modeling
│   │   ├── brand_agent.py         # NPS analysis
│   │   ├── viz_agent.py           # Chart generation
│   │   └── critique_agent.py      # Quality evaluation
│   ├── models/
│   │   └── advanced_mmm.py        # Adstock & multi-model
│   └── utils/
│       └── adstock.py             # Adstock transformations
├── data/                          # Dataset directory
└── download_data.py               # Kaggle data downloader
```

## 🎯 Use Cases

- **Marketing Teams**: Optimize budget allocation, understand channel ROI
- **Data Analysts**: Explore sales patterns, correlations, trends
- **Business Leaders**: Make data-driven decisions with AI insights
- **Researchers**: Study marketing mix modeling techniques

## ⚠️ Limitations

- **Small Sample Size**: Dataset has only 12 monthly observations
- **Overfitting Risk**: Models achieve near-perfect fit (R² ≈ 1.0)
- **Fixed Decay Rate**: Using 0.5 for all channels (ideally channel-specific)

### Production Recommendations
- Collect 2+ years of weekly data (100+ observations)
- Optimize decay rates per channel
- Add seasonality variables
- Implement train/test validation
- Apply regularization (Ridge/Lasso)

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the MIT License.

## 🔗 Links

- **GitHub**: [https://github.com/AvirupRoy2195/MMX_Agent](https://github.com/AvirupRoy2195/MMX_Agent)
- **Dataset**: [Kaggle - DT Mart Market Mix Modeling](https://www.kaggle.com/datasets/datatattle/dt-mart-market-mix-modeling)