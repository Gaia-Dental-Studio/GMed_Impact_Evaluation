import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    
    def create_pie_chart(self, labels, values, colors=None):
        if colors is None:
            # Default colors if not provided
            colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']  # Extend if needed

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.2,
            sort=False,  # <-- disables auto-sorting by Plotly
            direction='clockwise'  # <-- ensures clockwise order
        )])
        
        fig.update_traces(
            hoverinfo='label+percent',
            textinfo='value',
            textfont_size=20,
            marker=dict(colors=colors[:len(labels)],
                        line=dict(color='#000000', width=2))
        )
        
        fig.update_layout(
            legend=dict(
                orientation="v",
                x=1.05,
                y=1,
                xanchor="left",
                yanchor="top",
                font=dict(size=12),
                itemwidth=30  # Adjust this value to control wrapping width
            )
        )
        
        return fig
    
    


    def create_pictogram(self, value, scale, value_max, emoji_symbol='💵', columns=10, vertical_shift=0.5, zoom_ratio=1.2):
        """
        Create a pictogram chart using emojis in a grid layout with optional pan and zoom.
        
        Parameters:
        - value (int): actual value to visualize
        - scale (int): value per symbol
        - value_max (int): maximum value to fill full grid
        - emoji_symbol (str): emoji used
        - columns (int): number of columns in grid
        - vertical_shift (float): how much to shift the grid upward (positive = up)
        - zoom_ratio (float): <1 zooms out, >1 zooms in, 1 = original
        """
        filled_units = value // scale
        max_units = value_max // scale
        rows = (max_units + columns - 1) // columns

        x_vals = []
        y_vals = []
        texts = []
        hover_texts = []

        for i in range(max_units):
            row = i // columns
            col = i % columns
            x_vals.append(col)
            y_vals.append(-row)
            
            if i < filled_units:
                texts.append(emoji_symbol)
                hover_texts.append(f'{scale}')
            else:
                texts.append('')
                hover_texts.append('')

        # Compute axis ranges with zoom adjustment
        x_center = (columns - 1) / 2
        y_center = (-rows + 1) / 2
        x_half_range = (columns / 2) * zoom_ratio
        y_half_range = (rows / 2) * zoom_ratio

        fig = go.Figure(data=go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='text',
            text=texts,
            textfont=dict(size=28, family='Segoe UI Emoji'),
            hovertext=hover_texts,
            hoverinfo='text'
        ))

        fig.update_layout(
            # title=f'Representing {value} using {emoji_symbol} (1 symbol = {scale})',
            xaxis=dict(visible=False, range=[x_center - x_half_range, x_center + x_half_range]),
            yaxis=dict(visible=False, range=[y_center - y_half_range + vertical_shift, y_center + y_half_range]),
            height=rows * 70,
            width=columns * 70,
            margin=dict(t=40, l=10, r=10, b=10)
        )


        return fig
