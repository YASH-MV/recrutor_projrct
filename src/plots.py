"""
Visualization module for RecruitIQ
Provides various plotting functions for candidate evaluation and analytics
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def plot_single_metric_ranking(df, metric_name):
    """Plot top candidates ranked by a single metric"""
    fig = go.Figure(data=[
        go.Bar(
            x=df['name'],
            y=df[metric_name],
            marker_color='#1f77b4',
            text=df[metric_name],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f"Top Candidates by {metric_name}",
        xaxis_title="Candidate",
        yaxis_title="Score",
        yaxis_range=[0, 10],
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_multi_metric_comparison(df):
    """Plot grouped bar chart comparing all metrics across candidates"""
    metrics = [col for col in df.columns if col != 'candidate_name' and col != 'name']
    
    if not metrics:
        return go.Figure()
    
    candidate_names = df['candidate_name'] if 'candidate_name' in df.columns else df['name']
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    for idx, metric in enumerate(metrics):
        fig.add_trace(go.Bar(
            name=metric,
            x=candidate_names,
            y=df[metric],
            marker_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        title="Multi-Metric Comparison",
        xaxis_title="Candidate",
        yaxis_title="Score",
        barmode='group',
        yaxis_range=[0, 10],
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_multi_metric_ranking(df, metrics, score_col='composite_score'):
    """Plot ranking with multiple metrics shown"""
    candidate_names = df['name']
    
    fig = go.Figure()
    
    # Main ranking bar
    fig.add_trace(go.Bar(
        name='Overall Score',
        x=candidate_names,
        y=df[score_col],
        marker_color='#1f77b4',
        text=df[score_col].round(2),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Candidate Rankings",
        xaxis_title="Candidate",
        yaxis_title="Score",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_radar_chart(candidate_row, metrics, name_col='name'):
    """Create a radar/spider chart for a candidate"""
    candidate_name = candidate_row[name_col] if name_col in candidate_row.index else "Candidate"
    
    values = [candidate_row.get(metric, 0) for metric in metrics]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name=candidate_name,
        line_color='#1f77b4'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title=f"Skill Profile: {candidate_name}",
        template='plotly_white'
    )
    
    return fig


def plot_score_distribution(df, metrics):
    """Plot distribution of scores across metrics"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    for idx, metric in enumerate(metrics):
        fig.add_trace(go.Box(
            y=df[metric],
            name=metric,
            boxmean='sd',
            marker_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        title="Score Distribution by Metric",
        yaxis_title="Score",
        xaxis_title="Metric",
        yaxis_range=[0, 10],
        template='plotly_white'
    )
    
    return fig


def plot_metric_distribution(df, metric):
    """Plot distribution for a single metric"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df[metric],
        nbinsx=20,
        marker_color='#1f77b4',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f"Distribution of {metric} Scores",
        xaxis_title="Score",
        yaxis_title="Frequency",
        xaxis_range=[0, 10],
        template='plotly_white'
    )
    
    return fig


def plot_performance_heatmap(df, metrics):
    """Create a heatmap showing performance across candidates and metrics"""
    candidate_names = df['candidate_name'] if 'candidate_name' in df.columns else df['name']
    
    # Prepare data for heatmap
    heatmap_data = []
    for metric in metrics:
        heatmap_data.append(df[metric].tolist())
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=candidate_names,
        y=metrics,
        colorscale='RdYlGn',
        zmin=0,
        zmax=10,
        text=heatmap_data,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title="Score")
    ))
    
    fig.update_layout(
        title="Performance Heatmap",
        xaxis_title="Candidate",
        yaxis_title="Metric",
        template='plotly_white'
    )
    
    return fig


def plot_candidate_scores(scores, candidate_name):
    """Plot scores for a single candidate"""
    metrics = [s['metric'] for s in scores]
    values = [s['value'] for s in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color='#1f77b4',
            text=values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f"Scores for {candidate_name}",
        xaxis_title="Metric",
        yaxis_title="Score",
        yaxis_range=[0, 10],
        template='plotly_white',
        height=300
    )
    
    return fig


def bar_top_metric(metric_name, rows):
    """Legacy function - plot top candidates for a metric"""
    names = [r['name'] for r in rows]
    vals = [r['value'] for r in rows]
    fig = go.Figure([go.Bar(x=names, y=vals, marker_color='#1f77b4')])
    fig.update_layout(
        title=f"Top: {metric_name}",
        xaxis_title="Candidate",
        yaxis_title="Score",
        yaxis_range=[0, 10],
        template='plotly_white'
    )
    return fig
