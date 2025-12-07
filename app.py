import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from src.agents.orchestrator import Orchestrator

# Page Config
st.set_page_config(page_title="MMX BI & Agent Tool", layout="wide")

# Initialize Orchestrator
@st.cache_resource
def get_orchestrator():
    orch = Orchestrator()
    return orch

orch = get_orchestrator()

# --- DEBUGGING / CONFIG CHECK ---
import os
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.sidebar.warning("⚠️ GEMINI_API_KEY not found!")
    st.sidebar.info("The Planning & NL2SQL Agents will be disabled. Basic keyword matching only.")
else:
    st.sidebar.success("✅ LLM Active")
    
    # Debug Info
    with st.sidebar.expander("Debugger"):
        st.write(f"Key loaded: {api_key[:10]}...")
        if st.button("Clear Cache & Restart"):
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()
    
    # Council Mode Toggle
    st.sidebar.markdown("---")
    council_mode = st.sidebar.checkbox("🏛️ Council Mode", value=False, 
                                        help="Use multiple LLMs to answer complex queries")
    if council_mode:
        st.sidebar.info("Council Mode: 3 LLMs + Chairman")
# --------------------------------

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

# Data Preview Section
with st.expander("📊 Explore Database", expanded=False):
    st.markdown("### DT Mart Marketing Mix Database")
    
    # Get data loader for full access
    from src.data_loader import DataLoader
    dl = DataLoader()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Monthly Data", "Media Spend", "NPS", "Products", "Special Sales"])
    
    with tab1:
        st.markdown("**Monthly Aggregated Data (12 months)**")
        mmm_data = dl.get_mmm_data()
        if mmm_data is not None:
            st.dataframe(mmm_data[['month', 'Total_Sales', 'TV', 'Digital', 'Sponsorship', 'NPS']].head(12), use_container_width=True)
            st.markdown(f"**Total Sales:** ${mmm_data['Total_Sales'].sum():,.0f}")
    
    with tab2:
        st.markdown("**Media Investment by Channel (millions)**")
        media = dl.load_media_investment()
        if media is not None:
            st.dataframe(media, use_container_width=True)
    
    with tab3:
        st.markdown("**Monthly NPS Scores**")
        nps = dl.load_nps_data()
        if nps is not None:
            st.dataframe(nps, use_container_width=True)
            st.metric("Average NPS", f"{nps['NPS'].mean():.1f}")
    
    with tab4:
        st.markdown("**Product Catalog (75 products)**")
        products = dl.load_product_catalog()
        if products is not None:
            st.dataframe(products.head(20), use_container_width=True)
    
    with tab5:
        st.markdown("**Special Sale Events (44 dates)**")
        special = dl.load_special_sales_calendar()
        if special is not None:
            st.dataframe(special, use_container_width=True)

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
    
    # Add to memory
    if hasattr(st.session_state.bi_chat, 'memory') and st.session_state.bi_chat.memory:
        st.session_state.bi_chat.memory.add_message('user', prompt)
    
    # Get response from Agentic BI Chat
    # Check if Council Mode is enabled
    if api_key and council_mode and st.session_state.bi_chat.council:
        with st.spinner("🏛️ LLM Council deliberating..."):
            # Build context from analysis results
            context = ""
            if analysis:
                context += f"Total Sales: ${analysis.get('kpis', {}).get('total_sales', 0):,.0f}\n"
                context += f"Top Channel by ROI: {max(analysis.get('roi', {}).items(), key=lambda x: x[1])[0] if analysis.get('roi') else 'Unknown'}\n"
            if advanced:
                context += f"Model R²: {advanced.get('model_comparison', {}).get('full', {}).get('r2', 0):.2%}\n"
            
            council_result = st.session_state.bi_chat.council.ask(prompt, context=context)
            response = {
                'text': f"**🏛️ Council Decision**\n\n{council_result['final_response']}",
                'chart': None
            }
            # Show reasoning and deliberation details
            with st.expander("🧠 Council Reasoning & Deliberation", expanded=False):
                # Show reasoning
                if council_result.get('reasoning'):
                    st.markdown("### 🧠 Query Analysis")
                    reasoning = council_result['reasoning']
                    st.json(reasoning)
                
                st.markdown("### 💬 Expert Opinions")
                for opinion in council_result['opinions']:
                    if opinion['response']:
                        model_name = opinion['model'].split('/')[-1]
                        with st.expander(f"🤖 {model_name}"):
                            st.markdown(opinion['response'][:1000] + "..." if len(opinion['response']) > 1000 else opinion['response'])
                
                st.markdown("### 🔍 Peer Reviews")
                for review in council_result['reviews']:
                    if review['review']:
                        st.json(review['review'])
    else:
        response = st.session_state.bi_chat.process_query(prompt)
    
    # Add to memory
    if hasattr(st.session_state.bi_chat, 'memory') and st.session_state.bi_chat.memory:
        st.session_state.bi_chat.memory.add_message('assistant', response['text'], 
                                                     {'has_chart': response.get('chart') is not None})
    
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

