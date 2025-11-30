import numpy as np
import pandas as pd

def geometric_adstock(x, decay=0.5):
    """
    Apply geometric adstock transformation to a time series.
    
    Args:
        x: Array or Series of media spend
        decay: Decay rate (0-1). Higher = longer carryover effect
        
    Returns:
        Adstocked series
    """
    adstocked = np.zeros_like(x, dtype=float)
    adstocked[0] = x[0]
    
    for t in range(1, len(x)):
        adstocked[t] = x[t] + decay * adstocked[t-1]
    
    return adstocked

def apply_adstock_to_dataframe(df, media_cols, decay_rates=None):
    """
    Apply adstock transformation to multiple media columns.
    
    Args:
        df: DataFrame with media spend columns
        media_cols: List of column names to transform
        decay_rates: Dict mapping column names to decay rates, or single float for all
        
    Returns:
        DataFrame with adstocked columns (original + new adstocked columns)
    """
    df_adstocked = df.copy()
    
    if decay_rates is None:
        decay_rates = 0.5  # Default decay
    
    for col in media_cols:
        if col not in df.columns:
            continue
            
        # Get decay rate for this column
        if isinstance(decay_rates, dict):
            decay = decay_rates.get(col, 0.5)
        else:
            decay = decay_rates
        
        # Apply adstock
        adstocked_col = f"{col}_adstock"
        df_adstocked[adstocked_col] = geometric_adstock(df[col].values, decay)
    
    return df_adstocked

def calculate_adstock_curve(decay, periods=12):
    """
    Calculate the adstock decay curve for visualization.
    
    Args:
        decay: Decay rate
        periods: Number of periods to show
        
    Returns:
        Array of cumulative effect over time
    """
    curve = np.zeros(periods)
    curve[0] = 1.0
    
    for t in range(1, periods):
        curve[t] = decay ** t
    
    return curve
