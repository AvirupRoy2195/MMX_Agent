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

# Sidebar
st.sidebar.title("MMX Command Center 🚀")
page = st.sidebar.radio("Mode", ["BI Dashboard", "MMX Lab", "Advanced MMM", "Simulator", "Agent Chat"])

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

elif page == "Advanced MMM":
    st.title("Advanced Marketing Mix Modeling")
    st.markdown("### Short-term vs Long-term Effects with Brand Equity")
    
    # Model Comparison
    st.subheader("Model Performance Comparison")
    model_comp = advanced.get('model_comparison', {})
    
    if model_comp:
        comp_df = pd.DataFrame({
            'Model': ['Immediate Only', 'With Adstock', 'Full (Adstock + Brand)'],
            'R² Score': [model_comp['immediate']['r2'], model_comp['adstock']['r2'], model_comp['full']['r2']],
            'RMSE': [model_comp['immediate']['rmse'], model_comp['adstock']['rmse'], model_comp['full']['rmse']]
        })
        
        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(comp_df, use_container_width=True)
        with c2:
            fig_comp = orch.viz.plot_model_comparison(model_comp)
            st.plotly_chart(fig_comp, use_container_width=True)
    
    # ROI Decomposition
    st.subheader("ROI Decomposition: Short-term vs Long-term")
    roi_decomp = advanced.get('roi_decomposition')
    if roi_decomp:
        fig_decomp = orch.viz.plot_roi_decomposition(roi_decomp)
        st.plotly_chart(fig_decomp, use_container_width=True)
        
        with st.expander("View Detailed ROI Breakdown"):
            decomp_df = pd.DataFrame(roi_decomp).T
            st.dataframe(decomp_df, use_container_width=True)
    
    # Brand Equity Analysis
    st.subheader("Brand Equity Analysis (NPS)")
    
    col1, col2, col3 = st.columns(3)
    nps_stats = advanced.get('nps_stats', {})
    if nps_stats:
        col1.metric("Avg NPS", f"{nps_stats.get('mean', 0):.1f}")
        col2.metric("NPS Range", f"{nps_stats.get('min', 0):.1f} - {nps_stats.get('max', 0):.1f}")
        
    nps_corr = advanced.get('nps_correlation')
    if nps_corr:
        col3.metric("NPS-Sales Correlation", f"{nps_corr:.2f}")
    
    # NPS Trend
    nps_trend = orch.brand.get_nps_trend()
    if nps_trend is not None:
        fig_nps = orch.viz.plot_nps_trend(nps_trend)
        st.plotly_chart(fig_nps, use_container_width=True)
    
    # Brand Impact
    brand_impact = advanced.get('brand_impact')
    if brand_impact:
        st.info(f"📊 **Brand Impact**: Each 1-point increase in NPS is associated with ${brand_impact:,.0f} in additional sales.")



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
