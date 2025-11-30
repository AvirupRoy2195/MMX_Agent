import streamlit as st
import pandas as pd
from src.agents.orchestrator import Orchestrator

# Page Config
st.set_page_config(page_title="MMX BI & Agent Tool", layout="wide")

# Initialize Orchestrator
@st.cache_resource
def get_orchestrator():
    orch = Orchestrator()
    return orch

orch = get_orchestrator()

# Run Analysis immediately
if 'analysis' not in st.session_state:
    with st.spinner("Orchestrator is coordinating agents..."):
        st.session_state.analysis = orch.run_analysis()
        st.session_state.plots = orch.get_plots(st.session_state.analysis)
        st.session_state.advanced_analysis = orch.run_advanced_analysis()

analysis = st.session_state.analysis
plots = st.session_state.plots
advanced = st.session_state.advanced_analysis

# Main Interface - Agent Only
st.title("🤖 MMX Agentic BI Assistant")
st.markdown("**Your AI-powered Marketing Mix Modeling & Business Intelligence Agent**")
st.markdown("Ask me anything about your sales, ROI, brand health, or model performance - I'll provide insights with visualizations!")

# Initialize Agentic BI Chat
from src.agents.agentic_bi_chat import AgenticBIChat

if 'bi_chat' not in st.session_state:
    st.session_state.bi_chat = AgenticBIChat(orch)
    st.session_state.bi_chat.set_analysis_results(analysis, advanced)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": """👋 **Welcome! I'm your MMX Agentic BI Assistant.**

I have analyzed your data and I'm ready to help! Here's what I can do:

📊 **Sales Analysis** - Category breakdowns, trends, totals
💰 **ROI Analysis** - Channel performance, short vs long-term effects  
🎯 **Contributions** - Sales impact by channel
📈 **Correlations** - Relationships between channels
💵 **Budget Optimization** - Spend mix, channel efficiency
🏆 **Brand Health** - NPS trends and impact
🔍 **Model Performance** - Accuracy metrics, comparisons

**Try asking:**
- "Show me ROI decomposition"
- "Which channel should I optimize?"
- "Show me sales by category"
- "What's the model accuracy?"

Type your question below! 👇""",
        "chart": None
    }]

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True, key=f"chart_{idx}")

# Chat input
if prompt := st.chat_input("Ask me anything about your marketing data..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "chart": None})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from Agentic BI Chat
    response = st.session_state.bi_chat.process_query(prompt)
    
    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response['text'],
        "chart": response.get('chart')
    })
    
    with st.chat_message("assistant"):
        st.markdown(response['text'])
        if response.get('chart'):
            # Use length of messages as unique key for new chart
            st.plotly_chart(response['chart'], use_container_width=True, key=f"chart_{len(st.session_state.messages)}")

