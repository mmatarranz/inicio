import yfinance as yfinance
import plotly.graph_objects as go
import pandas as pd

def get_market_data(symbol="^GSPC", period="1mo"):
    """Fetch historical market data using yfinance."""
    try:
        ticker = yfinance.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None
        return df
    except Exception:
        return None

def get_realtime_price(symbol="BTC-USD"):
    """Fetch real-time price for a given symbol."""
    try:
        ticker = yfinance.Ticker(symbol)
        data = ticker.fast_info
        return {
            "price": data.last_price,
            "change": data.year_high - data.year_low # Placeholder for actual change calculation if needed
        }
    except Exception:
        return None

def create_stock_chart(df, title="S&P 500 Performance"):
    """Create a Plotly line chart for market performance."""
    if df is None or df.empty:
        return None
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Close'], 
        mode='lines',
        name='Price',
        line=dict(color='#58a6ff', width=2),
        fill='tozeroy',
        fillcolor='rgba(88, 166, 255, 0.1)'
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300
    )
    return fig
