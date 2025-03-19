import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import altair as alt
from PIL import Image
from datetime import datetime
import os
import base64

# ---------- Custom UI Styling ----------
def set_professional_theme():
    return """
    <style>
    /* Main app background with darker gradient for better contrast with white text - darker by default */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        background-attachment: fixed;
    }
    
    /* Main content styling with deeper glassmorphism and white text */
    .main .block-container {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 1rem auto;
        max-width: 1200px;
        color: white;
    }
    
    /* Plotly charts with proper dark backgrounds */
    .js-plotly-plot .plotly {
        background: rgba(15, 23, 42, 0.9) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        padding: 15px !important;
    }
    
    /* Plotly chart paper background - make dark */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    
    .js-plotly-plot .plotly .plot-container {
        background: transparent !important;
    }
    
    /* Plotly chart grid and background - make dark */
    .js-plotly-plot .plotly .xaxis .grid path,
    .js-plotly-plot .plotly .yaxis .grid path {
        stroke: rgba(255, 255, 255, 0.1) !important;
    }
    
    .js-plotly-plot .plotly .bg {
        fill: rgba(15, 23, 42, 0.5) !important;
    }
    
    /* Plotly text colors - ensure white */
    .js-plotly-plot .plotly text {
        fill: white !important;
    }
    
    /* Make layout for bar graph axes white */
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtitle, 
    .js-plotly-plot .plotly .ytitle {
        fill: white !important;
    }
    
    /* Make more compact Kanban board header */
    .kanban-container {
        padding: 15px 10px !important;
        margin-bottom: 30px !important;
    }
    
    /* Make Kanban header more compact */
    .kanban-header {
        font-size: 0.95rem !important;
        padding: 10px !important;
        margin-bottom: 1rem !important;
    }
    
    /* Make Kanban columns more compact */
    .kanban-column {
        min-height: 400px !important;
        padding: 1rem !important;
    }
    
    /* Fix Kanban board gap and sizing */
    .kanban-column {
        width: 260px !important;
        min-width: 260px !important;
        margin-right: 8px !important;
    }
    
    /* Make Kanban card more compact */
    .kanban-card {
        padding: 12px !important;
        margin-bottom: 10px !important;
    }
    
    /* Make admin radio buttons dark by default */
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background: rgba(30, 41, 59, 0.8) !important;
        color: white !important;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background: rgba(44, 62, 80, 0.9) !important;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label span {
        color: white !important;
    }
    
    /* Fix form panels to be dark with white text */
    div[style*="background-color: white"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: white !important;
    }
    
    /* Ensure Admin panel white backgrounds are dark */
    div[style*="max-width: 800px; margin: 0 auto; padding: 20px; background-color: white;"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: white !important;
    }
    
    /* Sidebar with glassmorphism background */
    section[data-testid="stSidebar"] {
        background: rgba(20, 25, 40, 0.9);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        color: white;
        padding: 1.5rem 1rem;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Make white text universal */
    p, span, label, .stMarkdown, div {
        color: white;
    }
    
    /* Set input text colors */
    input, textarea, [data-baseweb="select"] {
        color: #FFFFFF !important;
    }
    
    /* Dashboard metrics styling with dark glassmorphism */
    div.css-1r6slb0.e1tzin5v2 {
        background: rgba(30, 40, 65, 0.75);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.4s ease;
        color: white;
    }
    
    div.css-1r6slb0.e1tzin5v2:hover {
        transform: translateY(-7px);
        background: rgba(40, 50, 80, 0.85);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* Kanban container styling with horizontal scrolling */
    .kanban-container {
        display: flex;
        flex-wrap: nowrap;
        gap: 12px;
        overflow-x: auto;
        padding: 20px 0;
        margin-bottom: 30px;
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    
    .kanban-container::-webkit-scrollbar {
        display: none;
    }
    
    /* Status column styling for Kanban with dark glassmorphism */
    .kanban-column {
        background: rgba(30, 40, 65, 0.75);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        min-height: 400px;
        width: 280px;
        min-width: 280px;
        flex: 0 0 auto;
        transition: all 0.3s ease;
        overflow-y: auto;
    }
    
    .kanban-column:hover {
        background: rgba(40, 50, 80, 0.85);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        transform: translateY(-5px);
    }
    
    /* Kanban cards with glassmorphism */
    .kanban-card {
        background: rgba(40, 55, 90, 0.8);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border-radius: 10px;
        border-left: 5px solid #ccc;
        padding: 16px;
        margin: 0 0 15px 0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        color: white;
    }
    
    .kanban-card:hover {
        transform: translateY(-5px) scale(1.02);
        background: rgba(50, 65, 110, 0.9);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Login/Signup form styling with glassmorphism */
    .auth-form {
        max-width: 500px;
        margin: 0 auto;
        padding: 2.5rem;
        background: rgba(30, 40, 65, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        color: white;
    }
    
    /* Custom button styling with glassmorphism */
    .stButton > button {
        background: rgba(41, 128, 185, 0.8);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        background: rgba(52, 152, 219, 0.9);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
        transform: translateY(-3px);
    }
    
    /* Tables and dataframes with glassmorphism */
    .dataframe {
        background: rgba(30, 40, 65, 0.75) !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        color: white !important;
    }
    
    .dataframe thead th {
        background-color: rgba(25, 35, 55, 0.9) !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 15px !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .dataframe tbody tr td {
        color: white !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(45, 55, 90, 0.7) !important;
    }
    
    /* Customize plotly charts with glassmorphism */
    .js-plotly-plot .plotly {
        background: rgba(30, 40, 65, 0.75) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        padding: 5px !important;
    }
    
    /* Empty state card with glassmorphism */
    .kanban-empty-state {
        background: rgba(40, 50, 80, 0.6);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 20px 15px;
        margin-top: 20px;
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 120px;
    }
    
    /* Sidebar navigation buttons with glassmorphism */
    div.css-1aumxhk {
        background: rgba(60, 75, 115, 0.3);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    div.css-1aumxhk:hover {
        background: rgba(80, 100, 150, 0.4);
        transform: translateX(5px);
    }
    
    /* Streamlit inputs with glassmorphism */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        background: rgba(40, 55, 90, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        color: white !important;
    }
    
    /* Streamlit radio buttons with glassmorphism */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        padding: 15px;
        flex-grow: 1;
        text-align: center;
        border-radius: 8px;
        background: rgba(40, 55, 90, 0.7);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
        color: white;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        background: rgba(50, 70, 120, 0.8);
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
    }
    
    h1 {
        font-weight: 700;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.8rem;
        margin-bottom: 2rem;
        font-size: 2.2rem;
    }
    
    h2 {
        font-weight: 600;
        color: white;
        margin-top: 1.5rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    h3 {
        font-weight: 600;
        color: white;
        margin-top: 1.2rem;
    }
    
    /* Fix for selectbox text */
    .stSelectbox label {
        color: white !important;
    }
    
    /* Fix for select dropdown background */
    [data-baseweb="select"] [data-baseweb="popover"] {
        background-color: rgba(30, 40, 65, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Fix for select dropdown options */
    [data-baseweb="select"] [data-baseweb="popover"] li {
        color: white !important;
    }
    
    [data-baseweb="select"] [data-baseweb="popover"] li:hover {
        background-color: rgba(52, 152, 219, 0.3) !important;
    }
    
    /* Fix for metric label and value colors */
    .stMetric label, .stMetric .metric-value {
        color: white !important;
    }
    
    /* Fix for slider color */
    .stSlider [data-baseweb="slider"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: white !important;
    }
    
    /* Fix text color in forms with dark backgrounds */
    .auth-form h3, .auth-form label, .auth-form p {
        color: white !important;
    }
    
    /* Fix white text in Plotly charts to be dark for readability */
    .js-plotly-plot .plotly text {
        fill: white !important;
    }
    
    /* Make tutorial text white */
    div[style*="background-color: white"] {
        background-color: rgba(30, 40, 65, 0.85) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    div[style*="background-color: white"] h3,
    div[style*="background-color: white"] p,
    div[style*="background-color: white"] li,
    div[style*="background-color: white"] strong {
        color: white !important;
    }
    
    /* Fix admin interface panels to use dark theme */
    div[style*="background-color: white;"] {
        background: rgba(30, 40, 65, 0.85) !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    div[style*="background-color: white;"] h3,
    div[style*="background-color: white;"] label,
    div[style*="background-color: white;"] p {
        color: white !important;
    }
    
    /* Make radio buttons text white */
    div.row-widget.stRadio > div[role="radiogroup"] > label span {
        color: white !important;
    }
    
    /* Fix chart title and axis colors */
    .js-plotly-plot .plotly .gtitle {
        fill: white !important;
    }
    
    .js-plotly-plot .plotly .xtitle, 
    .js-plotly-plot .plotly .ytitle {
        fill: white !important;
    }
    
    /* Fix data table color issues */
    div.stDataFrame {
        color: white !important;
    }
    
    /* Fix all headers to be truly white */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Ensure info/warning/error boxes have readable text */
    .stAlert p {
        color: rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Fix potential issues with colored text in specific components */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: white !important;
    }
    
    /* Ensure contrast for metric values */
    .stMetric .metric-value {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Fix text color in charts for better readability */
    .js-plotly-plot .plotly text {
        fill: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Enhanced chart styling */
    .js-plotly-plot .plotly {
        background: rgba(20, 30, 50, 0.85) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        padding: 15px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    .js-plotly-plot .plotly:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Chart axes and title styling */
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtitle, 
    .js-plotly-plot .plotly .ytitle {
        fill: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Make chart backgrounds dark with grid lines */
    .js-plotly-plot .plotly .bg {
        fill: rgba(15, 25, 45, 0.5) !important;
    }
    
    /* Altair charts styling */
    .vega-embed {
        background: rgba(20, 30, 50, 0.85) !important;
        border-radius: 16px !important;
        padding: 15px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    .vega-embed:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Chart tooltip styling */
    .js-plotly-plot .plotly .hoverlayer .hover text {
        fill: #333 !important;
    }
    
    /* Making charts more vibrant */
    svg.marks .mark-rect path {
        stroke: rgba(255, 255, 255, 0.3) !important;
        stroke-width: 1px !important;
    }
    
    /* Redesigned Kanban container with glass morphism */
    .kanban-container {
        display: flex;
        flex-wrap: nowrap;
        gap: 16px;
        overflow-x: auto;
        padding: 25px 10px;
        margin-bottom: 40px;
        -ms-overflow-style: none;
        scrollbar-width: none;
        position: relative;
        background: rgba(15, 25, 40, 0.4);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Greatly enhanced Kanban board styling */
    .kanban-column {
        background: rgba(30, 40, 60, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        min-height: 450px;
        width: 300px;
        min-width: 300px;
        flex: 0 0 auto;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        overflow-y: auto;
        position: relative;
    }
    
    .kanban-column:hover {
        background: rgba(40, 55, 85, 0.8);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
        transform: translateY(-8px);
    }
    
    /* Fancy scrollbar for kanban columns */
    .kanban-column::-webkit-scrollbar {
        width: 6px;
    }
    
    .kanban-column::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .kanban-column::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    /* Beautiful gradient headers for kanban columns */
    .kanban-header {
        font-weight: 600;
        font-size: 1.1rem;
        padding: 15px;
        margin-bottom: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        position: sticky;
        top: 0;
        z-index: 10;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        display: flex;
        justify-content: center;
        align-items: center;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .kanban-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 12px;
        padding: 2px;
        background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.1));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }
    
    /* Beautiful gradient headers */
    .kanban-header-not-started { 
        background: linear-gradient(135deg, #546E7A, #37474F); 
    }
    .kanban-header-in-progress { 
        background: linear-gradient(135deg, #1E88E5, #0D47A1); 
    }
    .kanban-header-trial-done { 
        background: linear-gradient(135deg, #00ACC1, #006064); 
    }
    .kanban-header-in-testing { 
        background: linear-gradient(135deg, #F57C00, #E65100); 
    }
    .kanban-header-deployed { 
        background: linear-gradient(135deg, #7B1FA2, #4A148C); 
    }
    .kanban-header-running { 
        background: linear-gradient(135deg, #00897B, #004D40); 
    }
    .kanban-header-completed { 
        background: linear-gradient(135deg, #43A047, #1B5E20); 
    }
    
    /* Completely redesigned kanban cards */
    .kanban-card {
        background: rgba(50, 65, 100, 0.6);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border-radius: 12px;
        border-left: none;
        padding: 18px;
        margin: 0 0 18px 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .kanban-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(to bottom, rgba(255,255,255,0.8), rgba(255,255,255,0.2));
    }
    
    .kanban-card:hover {
        transform: translateY(-5px) scale(1.02);
        background: rgba(60, 80, 130, 0.7);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.25);
    }
    
    /* Beautiful colored card borders */
    .kanban-card-not-started::before { background: linear-gradient(to bottom, #90A4AE, #546E7A); }
    .kanban-card-in-progress::before { background: linear-gradient(to bottom, #42A5F5, #1976D2); }
    .kanban-card-trial-done::before { background: linear-gradient(to bottom, #26C6DA, #0097A7); }
    .kanban-card-in-testing::before { background: linear-gradient(to bottom, #FFA726, #F57C00); }
    .kanban-card-deployed::before { background: linear-gradient(to bottom, #AB47BC, #7B1FA2); }
    .kanban-card-running::before { background: linear-gradient(to bottom, #26A69A, #00796B); }
    .kanban-card-completed::before { background: linear-gradient(to bottom, #66BB6A, #388E3C); }
    
    /* Enhanced card title */
    .kanban-card-title {
        font-weight: 600;
        font-size: 17px;
        color: white;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
        display: flex;
        align-items: center;
    }
    
    .kanban-card-title::before {
        content: '📌';
        margin-right: 8px;
        font-size: 16px;
    }
    
    /* Beautiful progress bar with animation */
    .progress-bar-container {
        height: 10px;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        margin-top: 15px;
        overflow: hidden;
        position: relative;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 6px;
        position: relative;
        transition: width 1.2s ease-in-out;
        background-size: 30px 30px;
        background-image: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.15) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255, 255, 255, 0.15) 50%,
            rgba(255, 255, 255, 0.15) 75%,
            transparent 75%,
            transparent
        );
        animation: progress-animation 2s linear infinite;
    }
    
    @keyframes progress-animation {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 60px 0;
        }
    }
    
    /* Vibrant progress bar colors */
    .progress-not-started {
        background-color: #78909C;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-in-progress {
        background-color: #2196F3;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-trial-done {
        background-color: #00BCD4;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-in-testing {
        background-color: #FF9800;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-deployed {
        background-color: #9C27B0;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-running {
        background-color: #009688;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    .progress-completed {
        background-color: #4CAF50;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
    }
    </style>
    """

# ---------- 1) Thread-safe SQLite connection ----------
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('industry_4_0_app.db', check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()

# ---------- 2) Session State Management ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- 3) Create necessary tables ----------
def create_tables():
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, 
            password TEXT, 
            role TEXT,
            department TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            department_name TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            year TEXT, 
            jjm_strategic_pillars TEXT,
            target_main_category TEXT,
            target_sub_category TEXT,
            target_16_dimensions TEXT,
            jjm_action_plan TEXT,
            start_date TEXT, 
            end_date TEXT, 
            roadmap_captain TEXT,
            project_leaders TEXT,
            project_owners TEXT,
            task_status TEXT,
            task_completion_rate REAL, 
            jjm_comments TEXT,
            target_remark TEXT,
            manager TEXT
        )
    ''')
    
    # If "manager" column was missing in older DB, add it
    c.execute("PRAGMA table_info(projects)")
    columns_info = c.fetchall()
    existing_cols = [col[1] for col in columns_info]
    if "manager" not in existing_cols:
        c.execute("ALTER TABLE projects ADD COLUMN manager TEXT;")
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dimensions (
            dimension_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            dimension_name TEXT,
            dimension_score INTEGER,
            timestamp TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS training_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            description TEXT, 
            schedule TEXT, 
            material_path TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER, 
            session_id INTEGER,
            status TEXT,
            FOREIGN KEY(session_id) REFERENCES training_sessions(session_id)
        )
    ''')
    conn.commit()

create_tables()

# ---------- 4) User Authentication Functions ----------
def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, password))
    return c.fetchone()

def add_user(username, password, role, department):
    c.execute('INSERT INTO users (username, password, role, department) VALUES (?, ?, ?, ?)',
              (username, password, role, department))
    conn.commit()

def get_all_users():
    c.execute('SELECT * FROM users')
    return c.fetchall()

def get_all_departments():
    c.execute('SELECT * FROM departments')
    return c.fetchall()

def add_department(department_name):
    c.execute('INSERT INTO departments (department_name) VALUES (?)', (department_name,))
    conn.commit()

# ---------- 5) Project Management ----------
def add_project(project_name, year, jjm_strategic_pillars, target_main_category,
                target_sub_category, target_16_dimensions, jjm_action_plan,
                start_date, end_date, roadmap_captain, project_leaders,
                project_owners, task_status, task_completion_rate, jjm_comments,
                target_remark, manager):
    c.execute('''
        INSERT INTO projects (
            project_name, year, jjm_strategic_pillars, target_main_category,
            target_sub_category, target_16_dimensions, jjm_action_plan,
            start_date, end_date, roadmap_captain, project_leaders, project_owners,
            task_status, task_completion_rate, jjm_comments, target_remark, manager
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
        project_name, year, jjm_strategic_pillars, target_main_category,
        target_sub_category, target_16_dimensions, jjm_action_plan, str(start_date),
        str(end_date), roadmap_captain, project_leaders, project_owners,
        task_status, task_completion_rate, jjm_comments, target_remark, manager
    ))
    conn.commit()

def update_project(project_id, project_name, year, jjm_strategic_pillars, target_main_category,
                   target_sub_category, target_16_dimensions, jjm_action_plan,
                   start_date, end_date, roadmap_captain, project_leaders,
                   project_owners, task_status, task_completion_rate, jjm_comments,
                   target_remark, manager):
    c.execute('''
        UPDATE projects
        SET project_name=?,
            year=?,
            jjm_strategic_pillars=?,
            target_main_category=?,
            target_sub_category=?,
            target_16_dimensions=?,
            jjm_action_plan=?,
            start_date=?,
            end_date=?,
            roadmap_captain=?,
            project_leaders=?,
            project_owners=?,
            task_status=?,
            task_completion_rate=?,
            jjm_comments=?,
            target_remark=?,
            manager=?
        WHERE project_id=?
    ''',
    (
        project_name, year, jjm_strategic_pillars, target_main_category,
        target_sub_category, target_16_dimensions, jjm_action_plan, str(start_date),
        str(end_date), roadmap_captain, project_leaders, project_owners,
        task_status, task_completion_rate, jjm_comments, target_remark, manager, project_id
    ))
    conn.commit()

def get_all_projects():
    c.execute('SELECT * FROM projects')
    return c.fetchall()

def get_project_by_name(project_name):
    c.execute('SELECT * FROM projects WHERE project_name = ?', (project_name,))
    return c.fetchone()

def update_project_status(project_id, new_status):
    c.execute('UPDATE projects SET task_status = ? WHERE project_id = ?', (new_status, project_id))
    conn.commit()

def get_project_status():
    c.execute("SELECT task_status, COUNT(*) FROM projects GROUP BY task_status")
    return c.fetchall()

# ---------- 6) Progress / Training ----------
def get_user_progress(user_id):
    c.execute('SELECT session_id, status FROM user_progress WHERE user_id = ?', (user_id,))
    return c.fetchall()

# ---------- 7) Excel Processing: Soft error handling ----------
def process_excel_file(uploaded_file):
    """
    Reads Excel, skipping rows that are missing 'Project Name' entirely.
    'Start Date'/'End Date' are attempted best-effort. 
    Missing columns won't cause a crash; we fill with None or skip if absolutely necessary.
    """
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.warning(f"Failed to read Excel: {e}")
        return

    # Map Excel columns to DB fields. If any column is missing, we won't error out.
    mapping = {
        "Project Name": "project_name",
        "Year": "year",
        "JJM Strategic Pillars": "jjm_strategic_pillars",
        "Target Main Category": "target_main_category",
        "Target Sub Category": "target_sub_category",
        "Target 16 Dimensions": "target_16_dimensions",
        "JJM Action Plan": "jjm_action_plan",
        "Start Date": "start_date",
        "End Date": "end_date",
        "Roadmap Captain": "roadmap_captain",
        "Project Leaders": "project_leaders",
        "Project Owners": "project_owners",
        "Task Status": "task_status",
        "Task Completion Rate": "task_completion_rate",
        "JJM Comments": "jjm_comments",
        "Target Remark": "target_remark",
        "Manager": "manager",
    }

    for idx, row in df.iterrows():
        # Construct a dict from the row
        row_data = {}
        for excel_col, db_field in mapping.items():
            if excel_col in df.columns:
                # If the row doesn't have a valid value, store None
                row_data[db_field] = row.get(excel_col, None)
            else:
                # This column missing in Excel, store None
                row_data[db_field] = None

        p_name = row_data.get("project_name", "")
        if not p_name or pd.isna(p_name):
            st.warning(f"Skipping row {idx+1}: no Project Name.")
            continue

        # Attempt to parse start_date / end_date as string
        start_date_val = row_data.get("start_date")
        end_date_val = row_data.get("end_date")

        # Convert if it's a Timestamp
        if pd.notnull(start_date_val) and hasattr(start_date_val, "strftime"):
            start_date_val = start_date_val.strftime("%Y-%m-%d")
        else:
            # If it's NaN or missing, store blank
            start_date_val = "" if not start_date_val else str(start_date_val)

        if pd.notnull(end_date_val) and hasattr(end_date_val, "strftime"):
            end_date_val = end_date_val.strftime("%Y-%m-%d")
        else:
            end_date_val = "" if not end_date_val else str(end_date_val)

        # Convert numeric
        tcr_val = 0.0
        try:
            tcr_val = float(row_data.get("task_completion_rate") or 0.0)
        except:
            tcr_val = 0.0

        # Check if project exists
        existing = get_project_by_name(p_name)
        if existing:
            # Update
            pid = existing[0]
            update_project(
                project_id=pid,
                project_name=p_name,
                year=row_data.get("year", ""),
                jjm_strategic_pillars=row_data.get("jjm_strategic_pillars", ""),
                target_main_category=row_data.get("target_main_category", ""),
                target_sub_category=row_data.get("target_sub_category", ""),
                target_16_dimensions=row_data.get("target_16_dimensions", ""),
                jjm_action_plan=row_data.get("jjm_action_plan", ""),
                start_date=start_date_val,
                end_date=end_date_val,
                roadmap_captain=row_data.get("roadmap_captain", ""),
                project_leaders=row_data.get("project_leaders", ""),
                project_owners=row_data.get("project_owners", ""),
                task_status=row_data.get("task_status", "Not Started"),
                task_completion_rate=tcr_val,
                jjm_comments=row_data.get("jjm_comments", ""),
                target_remark=row_data.get("target_remark", ""),
                manager=row_data.get("manager", "")
            )
            st.success(f"Updated project '{p_name}' from Excel row {idx+1}.")
        else:
            # Insert
            add_project(
                project_name=p_name,
                year=row_data.get("year", ""),
                jjm_strategic_pillars=row_data.get("jjm_strategic_pillars", ""),
                target_main_category=row_data.get("target_main_category", ""),
                target_sub_category=row_data.get("target_sub_category", ""),
                target_16_dimensions=row_data.get("target_16_dimensions", ""),
                jjm_action_plan=row_data.get("jjm_action_plan", ""),
                start_date=start_date_val,
                end_date=end_date_val,
                roadmap_captain=row_data.get("roadmap_captain", ""),
                project_leaders=row_data.get("project_leaders", ""),
                project_owners=row_data.get("project_owners", ""),
                task_status=row_data.get("task_status", "Not Started"),
                task_completion_rate=tcr_val,
                jjm_comments=row_data.get("jjm_comments", ""),
                target_remark=row_data.get("target_remark", ""),
                manager=row_data.get("manager", "")
            )
            st.success(f"Inserted new project '{p_name}' from Excel row {idx+1}.")

# ---------- 8) Visualization / Reporting ----------
def visualize_projects():
    st.subheader("Project Dashboard Overview")

    # Fetch DB
    projects = get_all_projects()
    df = pd.DataFrame(projects, columns=[
        "ID", "Project Name", "Year", "JJM Strategic Pillars", "Target Main Category",
        "Target Sub Category", "Target 16 Dimensions", "JJM Action Plan", "Start Date",
        "End Date", "Roadmap Captain", "Project Leaders", "Project Owners",
        "Task Status", "Task Completion Rate", "JJM Comments", "Target Remark",
        "Manager"
    ])

    # Convert date columns to datetime for analysis
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["End Date"]   = pd.to_datetime(df["End Date"], errors="coerce")

    # ========== Dashboard Header with Animated Title ==========
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 30px; 
                background: linear-gradient(90deg, rgba(15,23,42,0.7), rgba(30,41,59,0.7)); 
                padding: 15px; border-radius: 15px; backdrop-filter: blur(5px);">
        <h2 style="text-align: center; padding: 10px; color: white; 
                  text-shadow: 0 2px 5px rgba(0,0,0,0.2); font-size: 1.8rem; font-weight: 600;">
            🚀 Industry 4.0 Project Dashboard
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== Number Cards with multiple statuses ==========
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <h2 style="text-align: center; padding: 10px; color: white; border-bottom: 3px solid #3498DB;">
            Project Summary
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    colA, colB, colC, colD = st.columns(4)
    total_projects = len(df)
    colA.metric("📊 Total Projects", total_projects)

    # Let's also show Completed
    completed_projects = len(df[df["Task Status"] == "Completed"])
    colB.metric("✅ Completed", completed_projects)

    # In Progress
    in_progress_projects = len(df[df["Task Status"] == "In Progress"])
    colC.metric("🔄 In Progress", in_progress_projects)

    # Delayed: EndDate < now, not completed
    now = datetime.now()
    delayed_projects = df[
        (df["End Date"].notnull()) &
        (df["End Date"] < now) &
        (df["Task Status"] != "Completed")
    ]
    colD.metric("⚠️ Delayed", len(delayed_projects))

    # Another row for other statuses
    st.write("## Additional Status Counts:")
    colX, colY, colZ = st.columns(3)
    trial_done = len(df[df["Task Status"] == "Trial Done"])
    colX.metric("🧪 Trial Done", trial_done)

    in_testing = len(df[df["Task Status"] == "In Testing"])
    colY.metric("🔍 In Testing", in_testing)

    deployed = len(df[df["Task Status"] == "Production Deployed"])
    colZ.metric("🚀 Deployed", deployed)

    # ========== Project Status Visualization (Plotly bar with fixed background) ==========
    status_counts = df["Task Status"].value_counts()
    status_df = pd.DataFrame({"Task Status": status_counts.index, "Count": status_counts.values})
    fig_status_bar = px.bar(
        status_df, x="Task Status", y="Count",
        title="Project Status Overview",
        color="Task Status", 
        color_discrete_map={
            "Completed": "#4CAF50", 
            "In Progress": "#2196F3",
            "Not Started": "#78909C", 
            "Trial Done": "#00BCD4",
            "In Testing": "#FF9800",
            "Production Deployed": "#9C27B0",
            "Running": "#009688"
        }
    )
    
    # Set dark mode for the plot
    fig_status_bar.update_layout(
        plot_bgcolor='rgba(15,23,42,0)',
        paper_bgcolor='rgba(15,23,42,0)',
        title_font=dict(size=20, color='#ffffff', family="Segoe UI, sans-serif"),
        font=dict(family="Segoe UI, sans-serif", color='#ffffff'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        hoverlabel=dict(font_size=14, font_family="Segoe UI, sans-serif"),
        margin=dict(t=80, b=40, l=40, r=40),
    )
    
    # Add text labels on top of bars
    fig_status_bar.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )
    
    st.plotly_chart(fig_status_bar, use_container_width=True)

    # ========== Completion Rate Visualization (REPLACED ALTAIR WITH PLOTLY) ==========
    df["Task Completion Rate"] = pd.to_numeric(df["Task Completion Rate"], errors="coerce").fillna(0)
    
    # Group by JJM Strategic Pillars and Target Main Category
    completion_df = df.groupby(['JJM Strategic Pillars', 'Target Main Category'])['Task Completion Rate'].mean().reset_index()
    
    # Create a line chart with Plotly instead of Altair
    fig_completion = px.line(
        completion_df, 
        x='JJM Strategic Pillars', 
        y='Task Completion Rate',
        color='Target Main Category',
        title="Task Completion Rate Across Projects",
        markers=True,
        line_shape='spline',  # Makes the lines curved
    )
    
    # Update the chart styling to match other charts
    fig_completion.update_layout(
        plot_bgcolor='rgba(15,23,42,0)',
        paper_bgcolor='rgba(15,23,42,0)',
        title_font=dict(size=20, color='#ffffff', family="Segoe UI, sans-serif"),
        font=dict(family="Segoe UI, sans-serif", color='#ffffff'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="JJM Strategic Pillars"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Avg. Completion Rate (%)"
        ),
        legend_title_text="Target Main Category",
        hovermode="x unified"
    )
    
    # Add hover data and make lines thicker
    fig_completion.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"
    )
    
    st.plotly_chart(fig_completion, use_container_width=True)

    # ========== Milestone Visualization (REPLACED ALTAIR WITH PLOTLY) ==========
    mile_df = df.groupby("Target Main Category")["Task Completion Rate"].mean().reset_index()
    
    # Create milestone chart with Plotly instead of Altair
    fig_milestone = px.bar(
        mile_df,
        x='Target Main Category',
        y='Task Completion Rate',
        color='Target Main Category',
        title="Milestone Progress by Category",
        text_auto='.1f'  # Show the values on the bars
    )
    
    # Update the chart styling to match other charts
    fig_milestone.update_layout(
        plot_bgcolor='rgba(15,23,42,0)',
        paper_bgcolor='rgba(15,23,42,0)',
        title_font=dict(size=20, color='#ffffff', family="Segoe UI, sans-serif"),
        font=dict(family="Segoe UI, sans-serif", color='#ffffff'),
        xaxis=dict(
            showgrid=False,
            title="Target Main Category",
            categoryorder='total descending'  # Sort by highest value
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Avg. Completion Rate (%)",
            range=[0, 100]  # Fixed range for better comparison
        ),
        showlegend=False,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    
    # Add hover data and bar styling
    fig_milestone.update_traces(
        marker_line_width=1,
        marker_line_color="rgba(255,255,255,0.3)",
        opacity=0.85,
        textposition='outside',
        textfont=dict(color='white'),
        hovertemplate="<b>%{x}</b><br>Completion: %{y:.1f}%<extra></extra>"
    )
    
    st.plotly_chart(fig_milestone, use_container_width=True)

    # ========== Scatter of Completion Rate vs. Strategic Pillars (Plotly) ==========
    scatter_fig = px.scatter(
        df, x="JJM Strategic Pillars", y="Task Completion Rate",
        color="Target Main Category", hover_data=["Project Name"],
        title="Completion Rate vs. JJM Strategic Pillars"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    # ========== Kanban Board Visualization ==========
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-top: 30px; margin-bottom: 15px;">
        <h2 style="text-align: center; padding: 8px; color: white; border-bottom: 2px solid #3498DB;">
            📋 Project Kanban Board
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    kanban_df = df[["Project Name", "Task Status", "Manager", "Task Completion Rate"]].copy()
    status_order = [
        "Not Started", "In Progress", "Trial Done",
        "In Testing", "Production Deployed", "Running", "Completed"
    ]
    
    # Map status to icons and colors
    status_icons = {
        "Not Started": "⭕",
        "In Progress": "🔄",
        "Trial Done": "🧪",
        "In Testing": "🔍",
        "Production Deployed": "🚀",
        "Running": "🏃",
        "Completed": "✅"
    }
    
    status_colors = {
        "Not Started": "#95a5a6",
        "In Progress": "#3498db",
        "Trial Done": "#2ecc71",
        "In Testing": "#f39c12",
        "Production Deployed": "#9b59b6",
        "Running": "#1abc9c",
        "Completed": "#27ae60"
    }
    
    # Add custom CSS for Kanban container
    st.markdown('<div class="kanban-container">', unsafe_allow_html=True)
    
    # We'll create columns for each status
    kanban_cols = st.columns(len(status_order))
    
    for i, status in enumerate(status_order):
        with kanban_cols[i]:
            # Create column header with icon and count
            count = len(kanban_df[kanban_df["Task Status"] == status])
            
            # Use CSS classes for consistent styling
            header_class = f"kanban-header-{status.lower().replace(' ', '-')}"
            st.markdown(f"""
            <div class="kanban-column">
                <div class="kanban-header {header_class}">
                    {status_icons.get(status, "")} {status} ({count})
                </div>
            """, unsafe_allow_html=True)
            
            # Show each project as a "card"
            subset = kanban_df[kanban_df["Task Status"] == status]
            if not subset.empty:
                for _, row in subset.iterrows():
                    completion = int(row['Task Completion Rate']) if pd.notnull(row['Task Completion Rate']) else 0
                    manager = row['Manager'] if pd.notnull(row['Manager']) else "Unassigned"
                    
                    # Create a card with progress bar
                    card_class = f"kanban-card-{status.lower().replace(' ', '-')}"
                    progress_class = f"progress-{status.lower().replace(' ', '-')}"
                    
                    st.markdown(f"""
                    <div class="kanban-card {card_class}">
                        <div class="kanban-card-title">{row['Project Name']}</div>
                        <div class="kanban-card-property">
                            <span style="margin-right: 5px;">👤</span> {manager}
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill {progress_class}" style="width: {completion}%;"></div>
                            <span class="progress-percentage">{completion}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="kanban-empty-state">
                    <div class="kanban-empty-state-icon">📋</div>
                    <div>No projects</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Close kanban column div
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Close kanban container
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== Additional Visualizations ==========

    # Bar chart for JJM Strategic Pillars (# of projects, # completed)
    st.subheader("Projects by JJM Strategic Pillars")
    pillar_group = df.groupby('JJM Strategic Pillars').agg(
        Total_Projects=('Project Name', 'count'),
        Completed_Projects=('Task Status', lambda x: (x == 'Completed').sum())
    ).reset_index()

    # Ensure both columns are of the same numeric type (e.g., int)
    pillar_group['Total_Projects'] = pillar_group['Total_Projects'].astype(int)
    pillar_group['Completed_Projects'] = pillar_group['Completed_Projects'].astype(int)

    fig_pillars = px.bar(
        pillar_group,
        x='JJM Strategic Pillars',
        y=['Total_Projects', 'Completed_Projects'],
        labels={'value': 'Number of Projects', 'variable': 'Project Status'},
        title='Projects by JJM Strategic Pillars',
        barmode='group'
    )
    st.plotly_chart(fig_pillars, use_container_width=True)

    # Pie chart for Target Main Category
    st.subheader("Projects by Target Main Category")
    category_counts = df['Target Main Category'].value_counts(dropna=True)
    fig_category = px.pie(
        names=category_counts.index,
        values=category_counts.values,
        title='Distribution of Projects by Main Category'
    )
    st.plotly_chart(fig_category, use_container_width=True)

    # Bar chart for Target 16 Dimensions
    st.subheader("Projects by Target 16 Dimensions")
    dims_counts = df['Target Sub Category'].value_counts()
    dims_df = pd.DataFrame({'Target Sub Category': dims_counts.index, 'Count': dims_counts.values})
    fig_dimensions = px.bar(
        dims_df,
        x='Target Sub Category',
        y='Count',
        labels={'x': 'Target Sub Category', 'y': 'Count'},
        title='Number of Projects by Sub Category'
    )
    st.plotly_chart(fig_dimensions, use_container_width=True)

    # Grouped bar for Task Status by Manager
    st.subheader("Task Status by Manager")
    status_by_manager = df.groupby(['Manager', 'Task Status']).size().unstack(fill_value=0)
    if not status_by_manager.empty:
        fig_manager_status = px.bar(
            status_by_manager,
            x=status_by_manager.index,
            y=status_by_manager.columns,
            labels={'value': 'Count', 'index': 'Manager'},
            title='Task Status by Manager'
        )
        st.plotly_chart(fig_manager_status, use_container_width=True)

    # ========== Gantt Chart ==========
    st.subheader("Gantt Chart")
    # For Gantt, we need 'Task', 'Start', 'Finish'
    # We'll color by "Task Status"
    # We'll skip rows missing Start or End
    gantt_df = df.dropna(subset=["Start Date", "End Date"]).copy()
    # Make sure they're strings recognized by px.timeline
    gantt_df["Start"] = gantt_df["Start Date"].dt.strftime("%Y-%m-%d")
    gantt_df["Finish"] = gantt_df["End Date"].dt.strftime("%Y-%m-%d")
    if len(gantt_df):
        fig_gantt = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Project Name",
            color="Task Status",
            hover_data=["Task Completion Rate", "Manager"],
            title="Project Gantt Chart"
        )
        # Reverse y-axis so earliest project is at top
        fig_gantt.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No valid Start/End dates to display a Gantt chart.")

    # ========== Correlation Matrix for numeric columns ==========
    st.subheader("Correlation Matrix for Numeric Columns")
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) > 1:
        corr_matrix = numeric_df.corr()
        fig_corr = px.imshow(
            corr_matrix,
            labels=dict(x="Columns", y="Columns", color="Correlation"),
            title="Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.write("Not enough numeric columns for correlation matrix.")


# ---------- 9) Sidebar with Logo and Text ----------
def display_sidebar():
    with st.sidebar:
        logo_path = r'C:\Users\brajb\OneDrive\Desktop\coding development\industry 4.0\Jay jay  (2).png'
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            st.image(logo, width=250)
        
        st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h3 style="color: #ecf0f1; font-weight: 600; border-bottom: 2px solid #3498DB; padding-bottom: 10px;">
                Jay Jay Group Industry 4.0
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 14px; color: #ecf0f1;">Logged in as</p>
                <p style="margin: 0; font-weight: 600; color: #ecf0f1;">{st.session_state.role}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Logout", key="logout_button"):
                st.session_state.logged_in = False
                st.session_state.page = "login"


# ---------- 10) User Authentication Page ----------
def login_page():
    # Apply professional theme
    st.markdown(set_professional_theme(), unsafe_allow_html=True)
    
    display_sidebar()
    
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 30px;">
        <h1 style="text-align: center; padding: 20px; color: #2C3E50; font-size: 2.5em;">
            Industry 4.0 Project Management
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    menu = ["Login", "Sign Up", "Tutorial"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.markdown("""
        <div class="auth-form">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">Welcome Back</h3>
        """, unsafe_allow_html=True)
        
        username = st.text_input("User Name", key="login_username")
        password = st.text_input("Password", type='password', key="login_password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            login_button = st.button("Login", key="login_button", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if login_button:
            if username and password:
                result = login_user(username, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result[0]
                    st.session_state.role = result[3]
                    st.session_state.page = "dashboard"
                    st.success(f"Welcome {username}")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect Username/Password")
            else:
                st.warning("Please enter both username and password")

    elif choice == "Sign Up":
        st.markdown("""
        <div class="auth-form">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">Create New Account</h3>
        """, unsafe_allow_html=True)
        
        new_user = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type='password', key="signup_password")
        all_depts = get_all_departments()
        dept_names = [d[1] for d in all_depts] if all_depts else ["General"]
        department = st.selectbox("Select Department", dept_names, key="signup_department")
        role = st.selectbox("Select Role", ["Admin", "Manager", "User"], key="signup_role")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            signup_button = st.button("Sign Up", key="signup_button", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if signup_button:
            if new_user and new_password:
                add_user(new_user, new_password, role, department)
                st.success("Account Created Successfully! Please Login.")
            else:
                st.warning("Please enter all details to sign up.")

    elif choice == "Tutorial":
        st.markdown("""
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                    border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">Industry 4.0 Project Management - Tutorial</h3>
            <p style="font-size: 16px; color: #2C3E50;">
                <strong>Key Sections:</strong>
                <ol>
                    <li><strong>User Authentication System:</strong> Different roles (Admin, Manager, User).</li>
                    <li><strong>Project Management with 16-Dimension Tool:</strong> Add, update, and delete projects with a structured breakdown.</li>
                    <li><strong>Dropdown Selections:</strong> For Year, JJM Strategic Pillars, and categories to maintain consistency.</li>
                    <li><strong>Interactive Dashboards:</strong> Delayed projects, on-time projects, completion rates, milestone progress, Kanban board, Gantt chart, etc.</li>
                    <li><strong>Learning Portal:</strong> Admin can add training sessions; users can access and track progress.</li>
                </ol>
            </p>
        </div>
        """, unsafe_allow_html=True)


def show_16_dimension_tool():
    st.subheader("16-Dimension Industry 4.0 Assessment Tool")
    st.write("Coming soon...")

# ---------- 11) Admin Dashboard ----------
def admin_dashboard(user_id):
    # Apply professional theme
    st.markdown(set_professional_theme(), unsafe_allow_html=True)
    
    display_sidebar()
    
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <h1 style="text-align: center; padding: 10px; color: white; border-bottom: 3px solid #3498DB;">
            Admin Dashboard
        </h1>
    </div>
    """, unsafe_allow_html=True)

    # Add enhanced admin tab styling
    st.markdown("""
    <style>
    /* Enhanced admin tabs with modern design */
    .admin-tabs {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 12px;
        margin-bottom: 30px;
        padding: 5px;
    }
    
    .admin-tab {
        flex: 1;
        min-width: 130px;
        max-width: 160px;
        height: 100px;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        padding: 10px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        text-align: center;
    }
    
    .admin-tab:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .admin-tab.active {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }
    
    /* Tab icon and text */
    .tab-icon {
        font-size: 28px;
        margin-bottom: 8px;
        z-index: 1;
    }
    
    .tab-text {
        font-weight: 600;
        font-size: 12px;
        z-index: 1;
    }
    
    /* Tab gradient backgrounds */
    .tab-departments {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
    }
    
    .tab-users {
        background: linear-gradient(135deg, #2193b0, #6dd5ed);
        color: white;
    }
    
    .tab-projects {
        background: linear-gradient(135deg, #834d9b, #d04ed6);
        color: white;
    }
    
    .tab-training {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        color: white;
    }
    
    .tab-reports {
        background: linear-gradient(135deg, #2c3e50, #4ca1af);
        color: white;
    }
    
    .tab-dimensions {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .tab-status {
        background: linear-gradient(135deg, #f2994a, #f2c94c);
        color: white;
    }
    
    /* Tab shimmer effect */
    .admin-tab::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            to bottom right,
            rgba(255, 255, 255, 0) 0%,
            rgba(255, 255, 255, 0.2) 50%,
            rgba(255, 255, 255, 0) 100%
        );
        transform: rotate(45deg);
        transition: all 0.5s ease;
        opacity: 0;
    }
    
    .admin-tab:hover::after {
        animation: shimmer 1.5s infinite;
        opacity: 1;
    }
    
    @keyframes shimmer {
        0% { left: -50%; top: -50%; }
        100% { left: 150%; top: 150%; }
    }
    
    /* Hide the original radio buttons */
    div.row-widget.stRadio > div {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }
    </style>
    
    <div class="admin-tabs">
        <div class="admin-tab tab-departments" onclick="selectTab('Manage Departments')">
            <div class="tab-icon">🏢</div>
            <div class="tab-text">Departments</div>
        </div>
        <div class="admin-tab tab-users" onclick="selectTab('Manage Users')">
            <div class="tab-icon">👥</div>
            <div class="tab-text">Users</div>
        </div>
        <div class="admin-tab tab-projects" onclick="selectTab('Manage Projects')">
            <div class="tab-icon">📊</div>
            <div class="tab-text">Projects</div>
        </div>
        <div class="admin-tab tab-training" onclick="selectTab('Manage Training')">
            <div class="tab-icon">🎓</div>
            <div class="tab-text">Training</div>
        </div>
        <div class="admin-tab tab-reports" onclick="selectTab('View Reports')">
            <div class="tab-icon">📈</div>
            <div class="tab-text">Reports</div>
        </div>
        <div class="admin-tab tab-dimensions" onclick="selectTab('16-Dimension Tool')">
            <div class="tab-icon">🧩</div>
            <div class="tab-text">16-Dimension</div>
        </div>
        <div class="admin-tab tab-status" onclick="selectTab('Update Project Status')">
            <div class="tab-icon">🔄</div>
            <div class="tab-text">Status</div>
        </div>
    </div>

    <script>
    // Function to handle tab selection
    function selectTab(tabName) {
        // Find all radio buttons
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        
        // Click the matching radio button
        for (let i = 0; i < radioButtons.length; i++) {
            if (radioButtons[i].value === tabName) {
                radioButtons[i].click();
                break;
            }
        }
        
        // Update visual active state
        const tabElements = document.querySelectorAll('.admin-tab');
        tabElements.forEach(tab => tab.classList.remove('active'));
        
        // Find and highlight the clicked tab
        let selectedTab;
        if (tabName === 'Manage Departments') selectedTab = document.querySelector('.tab-departments');
        else if (tabName === 'Manage Users') selectedTab = document.querySelector('.tab-users');
        else if (tabName === 'Manage Projects') selectedTab = document.querySelector('.tab-projects');
        else if (tabName === 'Manage Training') selectedTab = document.querySelector('.tab-training');
        else if (tabName === 'View Reports') selectedTab = document.querySelector('.tab-reports');
        else if (tabName === '16-Dimension Tool') selectedTab = document.querySelector('.tab-dimensions');
        else if (tabName === 'Update Project Status') selectedTab = document.querySelector('.tab-status');
        
        if (selectedTab) selectedTab.classList.add('active');
    }
    
    // Set initial active tab based on current selection
    document.addEventListener('DOMContentLoaded', function() {
        // Find the selected radio button
        const selectedRadio = document.querySelector('input[type="radio"]:checked');
        if (selectedRadio) {
            selectTab(selectedRadio.value);
        }
    });
    </script>
    """, unsafe_allow_html=True)

    menu = [
        "Manage Departments",
        "Manage Users",
        "Manage Projects",
        "Manage Training",
        "View Reports",
        "16-Dimension Tool",
        "Update Project Status"
    ]
    
    choice = st.radio("", menu, horizontal=True)

    if choice == "Manage Departments":
        st.markdown("""
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                    border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">Department Management</h3>
        """, unsafe_allow_html=True)
        
        department_name = st.text_input("Department Name", key="department_name")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            add_dept_button = st.button("Add Department", key="add_dept_button", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if add_dept_button:
            add_department(department_name)
            st.success(f"Department {department_name} added successfully!")
        st.write(pd.DataFrame(get_all_departments(), columns=["ID", "Department Name"]))

    elif choice == "Manage Users":
        st.markdown("""
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                    border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">User Management</h3>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", key="admin_username")
        password = st.text_input("Password", type='password', key="admin_password")
        depts = get_all_departments()
        dept_names = [d[1] for d in depts] if depts else ["General"]
        department = st.selectbox("Select Department", dept_names, key="admin_department")
        role = st.selectbox("Role", ["Admin", "Manager", "User"], key="admin_role")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            add_user_button = st.button("Add User", key="add_user_button", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if add_user_button:
            if username and password:
                add_user(username, password, role, department)
                st.success(f"User {username} added successfully!")
            else:
                st.warning("Please provide all user details.")
        st.write(pd.DataFrame(get_all_users(), columns=["ID", "Username", "Password", "Role", "Department"]))

    elif choice == "Manage Projects":
        st.markdown("""
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                    border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #2C3E50; margin-bottom: 20px;">Project Management</h3>
        """, unsafe_allow_html=True)
        
        project_name = st.text_input("Project Name", key="project_name")
        year = st.selectbox("Year", ["2023-2024", "2025-2026", "2027-2028"], key="project_year")
        jjm_strategic_pillars = st.text_input("JJM Strategic Pillars", key="jjm_strategic_pillars")
        main_cat = ["E2E Supply Chain Visibility & Connectivity", "Real-Time Data & Analytics", "Organization Readiness"]
        target_main_category = st.selectbox("Target Main Category", main_cat, key="target_main_category")

        if target_main_category == "E2E Supply Chain Visibility & Connectivity":
            sub_cat_opts = ["Digitized Product Development", "Automation and Deskillment", "Seamless Connectivity"]
        elif target_main_category == "Real-Time Data & Analytics":
            sub_cat_opts = ["Predictive Analytics and Digitized Planning", "AI-Based Decision Making"]
        else:
            sub_cat_opts = ["Digital Performance Management", "Cross-Functional Digitization"]
        target_sub_category = st.selectbox("Target Sub Category", sub_cat_opts, key="target_sub_category")

        sixteen_dims = [
            "Management Mindset", "Strategy Roadmap", "Change Management Plan", "Technology Readiness",
            "Data-Driven Decision Making", "Organizational Structure", "Process Digitization", "Talent Readiness",
            "Supply Chain Integration", "Automation and Deskilling", "Predictive Analytics", "Customer Integration",
            "Digital Product Development", "Real-Time Analytics", "Security and Compliance", "Continuous Improvement"
        ]
        target_16_dimensions = st.selectbox("Target 16 Dimensions", sixteen_dims, key="target_16_dimensions")

        jjm_action_plan = st.text_area("JJM Action Plan and Tasks", key="jjm_action_plan")
        start_date = st.date_input("Start Date", key="start_date")
        end_date = st.date_input("End Date", key="end_date")
        roadmap_captain = st.text_input("Roadmap Captain", key="roadmap_captain")
        project_leaders = st.text_input("Project Leaders", key="project_leaders")
        project_owners = st.text_input("Project Owners", key="project_owners")

        task_status_list = [
            "Not Started", "In Progress", "Trial Done", "In Testing",
            "Production Deployed", "Running", "Completed"
        ]
        task_status = st.selectbox("Task Status", task_status_list, key="task_status")
        task_completion_rate = st.slider("Task Completion Rate", 0, 100, 0, key="task_completion_rate")
        jjm_comments = st.text_area("JJM Comments", key="jjm_comments")
        target_remark = st.text_area("Target Remark", key="target_remark")

        # Assign project manager (users with role == Manager)
        all_users = get_all_users()
        manager_opts = [u[1] for u in all_users if u[3] == "Manager"]
        manager = st.selectbox("Assign Project Manager", manager_opts, key="manager")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            add_project_button = st.button("Add Project", key="add_project_button", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if add_project_button:
            add_project(
                project_name, year, jjm_strategic_pillars, target_main_category,
                target_sub_category, target_16_dimensions, jjm_action_plan, start_date,
                end_date, roadmap_captain, project_leaders, project_owners, task_status,
                task_completion_rate, jjm_comments, target_remark, manager
            )
            st.success(f"Project '{project_name}' added successfully!")

        # ========== Section: Add/Update from Excel without crashing on missing columns ==========
        st.subheader("Add/Update Projects from Excel (Optional)")
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        if uploaded_file is not None:
            process_excel_file(uploaded_file)

        # ========== Section: Update Project by ID ==========
        st.subheader("Update Existing Project")
        all_projects = get_all_projects()
        if all_projects:
            project_id_list = [(p[0], p[1]) for p in all_projects]  # (ID, Name)
            sel_texts = [f"{pid} - {pname}" for pid, pname in project_id_list]
            selected_upd = st.selectbox("Select Project by ID", sel_texts)
            # Parse the selection
            if selected_upd:
                chosen_id = int(selected_upd.split(" - ")[0])
                if st.button("Update Project Details"):
                    update_project(
                        chosen_id,
                        project_name,
                        year,
                        jjm_strategic_pillars,
                        target_main_category,
                        target_sub_category,
                        target_16_dimensions,
                        jjm_action_plan,
                        start_date,
                        end_date,
                        roadmap_captain,
                        project_leaders,
                        project_owners,
                        task_status,
                        task_completion_rate,
                        jjm_comments,
                        target_remark,
                        manager
                    )
                    st.success(f"Project ID {chosen_id} updated successfully!")
        else:
            st.info("No projects in the database yet.")

        # Show Visualization
        visualize_projects()

    elif choice == "Update Project Status":
        st.subheader("Update Project Status")

        all_projects = get_all_projects()
        if all_projects:
            # We'll show the project name instead of ID
            name_dict = {p[1]: p[0] for p in all_projects}  # {Name:ID}
            selected_project_name = st.selectbox("Select Project", list(name_dict.keys()))
            st.info(f"Selected Project: **{selected_project_name}**")
            new_status_list = [
                "Not Started", "In Progress", "Trial Done", "In Testing",
                "Production Deployed", "Running", "Completed"
            ]
            new_status = st.selectbox("New Status", new_status_list)
            if st.button("Update Status"):
                pid = name_dict[selected_project_name]
                update_project_status(pid, new_status)
                st.success(f"Updated '{selected_project_name}' to status: {new_status}")
        else:
            st.info("No projects found to update.")

    elif choice == "Manage Training":
        st.subheader("Training Management")
        title = st.text_input("Training Title", key="training_title")
        description = st.text_area("Training Description", key="training_description")
        schedule = st.date_input("Schedule Date", key="training_schedule")
        material = st.file_uploader("Upload Training Material", type=["pdf", "docx", "pptx"], key="training_material")
        
        material_path = None
        if material is not None:
            material_path = f"training_materials/{material.name}"
            if not os.path.exists('training_materials'):
                os.makedirs('training_materials')
            with open(material_path, "wb") as f:
                f.write(material.getbuffer())
            st.success(f"Uploaded {material.name} successfully!")

        if st.button("Add Training"):
            if material_path:
                c.execute('''
                    INSERT INTO training_sessions (title, description, schedule, material_path)
                    VALUES (?, ?, ?, ?)
                ''', (title, description, str(schedule), material_path))
                conn.commit()
                st.success("Training Session Added!")
            else:
                st.error("Please upload the training material before adding the session.")

    elif choice == "View Reports":
        st.subheader("Reports and Analysis")
        projects = get_all_projects()
        df = pd.DataFrame(projects, columns=[
            "ID", "Project Name", "Year", "JJM Strategic Pillars",
            "Target Main Category", "Target Sub Category", "Target 16 Dimensions",
            "JJM Action Plan", "Start Date", "End Date", "Roadmap Captain",
            "Project Leaders", "Project Owners", "Task Status", "Task Completion Rate",
            "JJM Comments", "Target Remark", "Manager"
        ])
        st.dataframe(df)

        # Download button for CSV
        st.download_button(
            "Download as CSV",
            df.to_csv(index=False),
            file_name="project_report.csv",
            mime='text/csv'
        )

    elif choice == "16-Dimension Tool":
        show_16_dimension_tool()

# ---------- 12) Manager Dashboard ----------
def manager_dashboard(user_id):
    # Apply professional theme
    st.markdown(set_professional_theme(), unsafe_allow_html=True)
    
    display_sidebar()
    
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <h1 style="text-align: center; padding: 10px; color: #2C3E50; border-bottom: 3px solid #3498DB;">
            Manager Dashboard
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Project Management and Reporting")
    visualize_projects()

# ---------- 13) User Dashboard ----------
def user_dashboard(user_id):
    # Apply professional theme
    st.markdown(set_professional_theme(), unsafe_allow_html=True)
    
    display_sidebar()
    
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <h1 style="text-align: center; padding: 10px; color: #2C3E50; border-bottom: 3px solid #3498DB;">
            User Dashboard
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Your Assigned Tasks and Progress")
    progress = get_user_progress(user_id)
    if progress:
        for record in progress:
            st.write(f"Session {record[0]}: {record[1]}")
    else:
        st.write("No progress recorded yet.")

# ---------- 14) Main Function ----------
def main():
    # Apply professional theme everywhere
    st.markdown(set_professional_theme(), unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        if st.session_state.role == "Admin":
            admin_dashboard(st.session_state.user_id)
        elif st.session_state.role == "Manager":
            manager_dashboard(st.session_state.user_id)
        else:
            user_dashboard(st.session_state.user_id)
    else:
        login_page()

if __name__ == '__main__':
    main()
