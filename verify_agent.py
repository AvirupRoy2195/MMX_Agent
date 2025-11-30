from src.agent import MMXAgent

print("Initializing Agent...")
agent = MMXAgent()

print("Loading and Training...")
success = agent.load_and_train()

if success:
    print("Training Successful!")
    print("Summary:", agent.get_summary())
    print("ROI Insights:", agent.get_roi_insights())
    print("Chat Test:", agent.chat("Show me ROI"))
else:
    print("Training Failed!")
