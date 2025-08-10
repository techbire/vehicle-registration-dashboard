"""
Chart Generation Module

This module contains functions to create various charts and visualizations
for the vehicle registration dashboard using Plotly.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Optional, Dict


def create_trend_chart(data: pd.DataFrame, x_col: str, y_col: str, color_col: str, 
                      title: Optional[str] = None) -> go.Figure:
    """
    Create a time series trend chart.
    
    Args:
        data: DataFrame containing the data
        x_col: Column name for x-axis (time)
        y_col: Column name for y-axis (values)
        color_col: Column name for color grouping
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    if title is None:
        title = f"{y_col.title()} Trends Over Time"
    
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={
            x_col: x_col.replace('_', ' ').title(),
            y_col: y_col.replace('_', ' ').title(),
            color_col: color_col.replace('_', ' ').title()
        },
        line_shape='spline'
    )
    
    # Customize layout
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Customize hover template
    fig.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     f'{x_col.replace("_", " ").title()}: %{{x}}<br>' +
                     f'{y_col.replace("_", " ").title()}: %{{y:,.0f}}<br>' +
                     '<extra></extra>'
    )
    
    return fig


def create_growth_chart(data: pd.DataFrame, growth_col: str, title: str) -> go.Figure:
    """
    Create a growth rate visualization chart.
    
    Args:
        data: DataFrame containing growth data
        growth_col: Column name containing growth percentages
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Filter out infinite and NaN values
    clean_data = data[
        data[growth_col].notna() & 
        (data[growth_col] != float('inf')) & 
        (data[growth_col] != float('-inf'))
    ].copy()
    
    if clean_data.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No valid growth data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=title, height=400)
        return fig
    
    # Create bar chart for growth rates
    # Sort by growth rate for better visualization
    clean_data = clean_data.sort_values(growth_col, ascending=False)
    
    # Limit to top 15 for readability
    if len(clean_data) > 15:
        clean_data = clean_data.head(15)
    
    # Create manufacturer-category labels
    clean_data['label'] = clean_data['manufacturer'] + ' (' + clean_data['vehicle_category'] + ')'
    
    # Color based on positive/negative growth
    colors = ['#28a745' if x >= 0 else '#dc3545' for x in clean_data[growth_col]]
    
    fig = go.Figure(data=[
        go.Bar(
            x=clean_data['label'],
            y=clean_data[growth_col],
            marker_color=colors,
            text=[f'{x:.1f}%' for x in clean_data[growth_col]],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         f'{title}: %{{y:.1f}}%<br>' +
                         '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="Manufacturer (Category)",
        yaxis_title=f"{title} (%)",
        height=500,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis_tickangle=-45
    )
    
    # Add horizontal line at 0%
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    return fig


def create_market_share_chart(data: pd.DataFrame, category: str) -> go.Figure:
    """
    Create a market share pie chart for a specific vehicle category.
    
    Args:
        data: DataFrame containing market share data
        category: Vehicle category name
        
    Returns:
        Plotly Figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No market share data available for {category}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=f"Market Share - {category}", height=400)
        return fig
    
    # Sort by market share for better visualization
    data_sorted = data.sort_values('market_share_pct', ascending=False)
    
    # Group smaller manufacturers into "Others" if there are many
    if len(data_sorted) > 8:
        top_manufacturers = data_sorted.head(7)
        others_share = data_sorted.tail(len(data_sorted) - 7)['market_share_pct'].sum()
        others_registrations = data_sorted.tail(len(data_sorted) - 7)['registrations'].sum()
        
        # Add "Others" row
        others_row = pd.DataFrame({
            'manufacturer': ['Others'],
            'market_share_pct': [others_share],
            'registrations': [others_registrations]
        })
        
        plot_data = pd.concat([top_manufacturers, others_row], ignore_index=True)
    else:
        plot_data = data_sorted
    
    fig = go.Figure(data=[
        go.Pie(
            labels=plot_data['manufacturer'],
            values=plot_data['market_share_pct'],
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            insidetextorientation='radial',
            pull=[0.1 if i == 0 else 0 for i in range(len(plot_data))],  # Pull out the largest slice
            hovertemplate='<b>%{label}</b><br>' +
                         'Market Share: %{percent}<br>' +
                         'Registrations: %{customdata:,.0f}<br>' +
                         '<extra></extra>',
            customdata=plot_data['registrations']
        )
    ])
    
    fig.update_layout(
        title=f"Market Share - {category}",
        height=600,
        margin=dict(l=50, r=150, t=80, b=50),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        showlegend=True
    )
    
    return fig


def create_category_comparison_chart(data: pd.DataFrame, time_col: str = None) -> go.Figure:
    """
    Create a chart comparing vehicle categories over time.
    
    Args:
        data: DataFrame containing category trend data
        time_col: Column name for time axis (e.g., 'year_month', 'date')
        
    Returns:
        Plotly Figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No category data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Vehicle Category Comparison", height=400)
        return fig
    
    # Auto-detect time column if not specified
    if time_col is None or time_col not in data.columns:
        time_columns = ['year_month', 'date', 'year_quarter', 'year']
        for col in time_columns:
            if col in data.columns:
                time_col = col
                break
        else:
            # If no time column found, create a simple chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"No valid time column found. Available columns: {list(data.columns)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title="Vehicle Category Comparison", height=400)
            return fig
    
    # Create a simple trend chart for category comparison
    fig = go.Figure()
    
    # Plot registration volumes for each category
    for category in data['vehicle_category'].unique():
        category_data = data[data['vehicle_category'] == category].sort_values(time_col)
        
        fig.add_trace(
            go.Scatter(
                x=category_data[time_col],
                y=category_data['registrations'],
                mode='lines+markers',
                name=category,
                line=dict(width=3),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             f'{time_col.replace("_", " ").title()}: %{{x}}<br>' +
                             'Registrations: %{y:,.0f}<br>' +
                             '<extra></extra>'
            )
        )
    
    fig.update_layout(
        title="Vehicle Category Trends Comparison",
        xaxis_title=time_col.replace('_', ' ').title(),
        yaxis_title="Registrations",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
    fig.update_layout(
        title="Vehicle Category Comparison",
        height=700,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=80, b=0)
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Registrations", row=1, col=1)
    fig.update_yaxes(title_text="Growth Rate (%)", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=1)
    
    return fig


def create_manufacturer_ranking_chart(data: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Create a horizontal bar chart showing top manufacturers by registrations.
    
    Args:
        data: DataFrame containing manufacturer data
        top_n: Number of top manufacturers to show
        
    Returns:
        Plotly Figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No manufacturer data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Top Manufacturers", height=400)
        return fig
    
    # Get top manufacturers
    top_manufacturers = data.head(top_n)
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=top_manufacturers['manufacturer'],
            x=top_manufacturers['registrations'],
            orientation='h',
            marker_color='#1f77b4',
            text=[f'{x:,.0f}' for x in top_manufacturers['registrations']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                         'Registrations: %{x:,.0f}<br>' +
                         '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=f"Top {len(top_manufacturers)} Manufacturers by Registrations",
        xaxis_title="Total Registrations",
        yaxis_title="Manufacturer",
        height=max(400, len(top_manufacturers) * 40),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Reverse y-axis to show highest at top
    fig.update_yaxes(autorange="reversed")
    
    return fig


def create_heatmap_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                        value_col: str, title: str) -> go.Figure:
    """
    Create a heatmap chart for visualizing patterns in data.
    
    Args:
        data: DataFrame containing the data
        x_col: Column for x-axis
        y_col: Column for y-axis
        value_col: Column for color values
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Create pivot table for heatmap
    pivot_data = data.pivot_table(
        index=y_col,
        columns=x_col,
        values=value_col,
        aggfunc='sum',
        fill_value=0
    )
    
    if pivot_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=title, height=400)
        return fig
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Blues',
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>' +
                     f'{x_col}: %{{x}}<br>' +
                     f'{value_col}: %{{z:,.0f}}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig
