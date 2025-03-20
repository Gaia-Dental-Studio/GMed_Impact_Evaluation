import pandas as pd
import numpy as np
import plotly.express as px


class Model:
    def __init__(self):
        self.data = None
        
    def line_chart(self, data, column):
        fig = px.line(data.reset_index(), x='index', y=column, title=f'{column} Prevalency (%) in Indonesia, Age 40+', labels={'index': 'Year', column: 'Prevalence (%)'})
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=2010, dtick=1),
            xaxis_title='Year',
            yaxis_title='Prevalence (%)',
            template='plotly_white',
            
        )
        
        return fig
    
    
    def line_chart_economy(self, data, column):
        fig = px.line(data.reset_index(), x='index', y=column, title=f'{column} Economy Burden (in $ Billion)', labels={'index': 'Year', column: 'Prevalence (%)'})
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=2010, dtick=1),
            xaxis_title='Year',
            yaxis_title='Prevalence (%)',
            template='plotly_white',
            
        )
        
        return fig