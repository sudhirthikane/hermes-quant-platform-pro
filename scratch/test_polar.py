import pandas as pd
import plotly.express as px

data = [
    {"Sector": "Bank", "TrendScore": 10, "SliceSize": 1},
    {"Sector": "IT", "TrendScore": -10, "SliceSize": 1},
    {"Sector": "Auto", "TrendScore": 5, "SliceSize": 1}
]
df = pd.DataFrame(data)

fig = px.bar_polar(
    df,
    r='SliceSize',
    theta='Sector',
    color='TrendScore',
    color_continuous_scale='RdYlGn',
)
fig.update_layout(
    polar=dict(
        radialaxis=dict(showticklabels=False, ticks='', showgrid=False),
        hole=0.4
    )
)
print("SUCCESS")
