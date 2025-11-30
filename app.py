import streamlit as st
import pandas as pd
import plotly.express as px
from src.agent import MMXAgent

# Page Config
st.set_page_config(page_title="MMX Agent", layout="wide")

# Initialize Agent
@st.cache_resource
def get_agent():
    agent = MMXAgent()
    agent.load_and_train()
    return agent

agent = get_agent()

# Sidebar
st.sidebar.title("MMX Agent 🤖")
page = st.sidebar.radio("Navigate", ["Dashboard", "Simulator", "Chat"])

if page == "Dashboard":
    st.title("Marketing Mix Modeling Dashboard")
    
    if agent.data is not None:
        # Top Metrics
        summary = agent.get_summary()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sales", f"${summary['Total Sales']:,.0f}")
        c2.metric("Total Media Spend", f"${summary['Total Spend']:,.0f}")
        c3.metric("Model R²", f"{agent.training_results['r2']:.2f}")
        
        # Sales vs Spend Over Time
        st.subheader("Sales vs Media Spend Over Time")
        df_plot = agent.data.copy()
        # Create a 'Total Spend' column for plotting if not exists
        media_cols = agent.model.features
        df_plot['Total Media Spend'] = df_plot[media_cols].sum(axis=1)
        
        fig = px.line(df_plot, x='Date', y=['Total_Sales', 'Total Media Spend'], title="Sales vs Spend")
        st.plotly_chart(fig, use_container_width=True)
        
        # ROI Chart
        st.subheader("Marketing Channel ROI (Marginal Contribution)")
        rois = agent.get_roi_insights()
        roi_df = pd.DataFrame(list(rois.items()), columns=['Channel', 'Coefficient'])
        fig_roi = px.bar(roi_df, x='Channel', y='Coefficient', color='Coefficient', title="Impact of Spend on Sales")
        st.plotly_chart(fig_roi, use_container_width=True)
        
    else:
        st.error("Data could not be loaded. Please check the data directory.")

elif page == "Simulator":
    st.title("Scenario Simulator")
    st.markdown("Adjust media spend to predict future sales.")
    
    if agent.data is not None:
        inputs = {}
        cols = st.columns(3)
        features = agent.model.features
        
        # Get average spend as default
        avg_spend = agent.data[features].mean()
        
        for i, feature in enumerate(features):
            with cols[i % 3]:
                inputs[feature] = st.number_input(f"{feature} Spend", value=float(avg_spend[feature]))
        
        if st.button("Simulate Sales"):
            prediction = agent.simulate_scenario(inputs)
            st.success(f"Predicted Sales: ${prediction:,.2f}")
            
            # Compare with average
            avg_sales = agent.data['Total_Sales'].mean()
            diff = prediction - avg_sales
            st.metric("Vs Average Monthly Sales", f"${diff:,.2f}", delta_color="normal")

elif page == "Chat":
    st.title("Chat with MMX Agent")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me about ROI, Sales, or the Model."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        response = agent.chat(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
