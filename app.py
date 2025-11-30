import streamlit as st
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

analysis = st.session_state.analysis
plots = st.session_state.plots

# Sidebar
st.sidebar.title("MMX Command Center 🚀")
page = st.sidebar.radio("Mode", ["BI Dashboard", "MMX Lab", "Simulator", "Agent Chat"])

if page == "BI Dashboard":
    st.title("Business Intelligence Dashboard")
    
    # Top KPIs
    kpis = analysis.get('kpis', {})
    if kpis:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sales", f"${kpis.get('Total Sales', 0):,.0f}")
        c2.metric("Total Media Spend", f"${kpis.get('Total Spend', 0):,.0f}")
        c3.metric("Data Points", kpis.get('Data Points', 0))

    # Row 1: Trend & Categories
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.plotly_chart(plots.get('trend'), use_container_width=True)
    with r1c2:
        st.plotly_chart(plots.get('categories'), use_container_width=True)

    # Row 2: Correlations
    st.subheader("Data Correlations")
    st.plotly_chart(plots.get('correlation'), use_container_width=True)

elif page == "MMX Lab":
    st.title("Marketing Mix Modeling Lab")
    
    # Critique Section
    with st.expander("Critique Agent Feedback 🧐", expanded=True):
        for msg in analysis.get('feedback', []):
            st.write(msg)
            
    # ROI & Contribution
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.plotly_chart(plots.get('roi'), use_container_width=True)
    with r2c2:
        st.plotly_chart(plots.get('contributions'), use_container_width=True)
        
    st.info("The Contribution chart shows the estimated total sales driven by each channel over the entire period.")

elif page == "Simulator":
    st.title("Scenario Simulator")
    st.markdown("Adjust media spend to predict future sales.")
    
    if orch.data is not None:
        inputs = {}
        cols = st.columns(3)
        # Get features from the trained model in MMX agent
        features = orch.mmx.model.features
        
        # Get average spend as default
        avg_spend = orch.data[features].mean()
        
        for i, feature in enumerate(features):
            with cols[i % 3]:
                inputs[feature] = st.number_input(f"{feature} Spend", value=float(avg_spend[feature]))
        
        if st.button("Simulate Sales"):
            prediction = orch.simulate(inputs)
            st.success(f"Predicted Sales: ${prediction:,.2f}")

elif page == "Agent Chat":
    st.title("Chat with the Orchestrator")
    st.markdown("Ask about specific insights. (Note: Chat logic is currently simplified)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "I am the Orchestrator. I can ask the sub-agents for info. Try 'Show me ROI' or 'Analyze Categories'."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Simple routing logic for the demo
        response = "I'm not sure."
        prompt_lower = prompt.lower()
        
        if "roi" in prompt_lower:
            response = "The MMX Agent reports the following Marginal ROI:\n" + str(analysis.get('roi'))
        elif "category" in prompt_lower:
            response = "The Explorer Agent found these categories:\n" + str(analysis.get('categories')['Category'].tolist())
        elif "critique" in prompt_lower or "feedback" in prompt_lower:
            response = "The Critique Agent says:\n" + "\n".join(analysis.get('feedback', []))
        else:
            response = "I can route your request to: MMX Agent (ROI), Explorer Agent (Categories), or Critique Agent (Feedback)."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
