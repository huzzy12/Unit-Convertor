import json
import requests
from typing import Dict, Any, List, Tuple, Optional
import plotly.graph_objects as go
import streamlit as st

# Define conversion categories and their units
CONVERSION_CATEGORIES = {
    "Length": {
        "units": ["meter", "kilometer", "centimeter", "millimeter", "mile", "yard", "foot", "inch"],
        "symbol": "📏",
        "color": "#FF5757"
    },
    "Mass": {
        "units": ["gram", "kilogram", "milligram", "pound", "ounce", "ton"],
        "symbol": "⚖️",
        "color": "#4CAF50"
    },
    "Volume": {
        "units": ["liter", "milliliter", "cubic_meter", "gallon", "quart", "pint", "cup", "fluid_ounce"],
        "symbol": "🧪",
        "color": "#2196F3"
    },
    "Temperature": {
        "units": ["kelvin", "celsius", "fahrenheit"],
        "symbol": "🌡️",
        "color": "#FF9800"
    },
    "Time": {
        "units": ["second", "minute", "hour", "day", "week", "month", "year"],
        "symbol": "⏱️",
        "color": "#9C27B0"
    },
    "Speed": {
        "units": ["meter_per_second", "kilometer_per_hour", "mile_per_hour", "knot"],
        "symbol": "🚀",
        "color": "#607D8B"
    },
    "Area": {
        "units": ["square_meter", "square_kilometer", "hectare", "acre", "square_foot", "square_inch"],
        "symbol": "📐",
        "color": "#795548"
    },
    "Data": {
        "units": ["bit", "byte", "kilobyte", "megabyte", "gigabyte", "terabyte"],
        "symbol": "💾",
        "color": "#00BCD4"
    },
    "Energy": {
        "units": ["joule", "kilojoule", "calorie", "kilocalorie", "watt_hour", "kilowatt_hour"],
        "symbol": "⚡",
        "color": "#FFEB3B"
    },
    "Pressure": {
        "units": ["pascal", "kilopascal", "bar", "atmosphere", "psi"],
        "symbol": "🔄",
        "color": "#3F51B5"
    }
}

# Define conversion factors for each unit to a base unit
CONVERSION_FACTORS = {
    # Length (base: meter)
    "meter": 1.0,
    "kilometer": 1000.0,
    "centimeter": 0.01,
    "millimeter": 0.001,
    "mile": 1609.344,
    "yard": 0.9144,
    "foot": 0.3048,
    "inch": 0.0254,
    
    # Mass (base: gram)
    "gram": 1.0,
    "kilogram": 1000.0,
    "milligram": 0.001,
    "pound": 453.59237,
    "ounce": 28.349523125,
    "ton": 1000000.0,
    
    # Volume (base: liter)
    "liter": 1.0,
    "milliliter": 0.001,
    "cubic_meter": 1000.0,
    "gallon": 3.78541178,
    "quart": 0.946352946,
    "pint": 0.473176473,
    "cup": 0.2365882365,
    "fluid_ounce": 0.0295735296875,
    
    # Time (base: second)
    "second": 1.0,
    "minute": 60.0,
    "hour": 3600.0,
    "day": 86400.0,
    "week": 604800.0,
    "month": 2592000.0,  # 30 days
    "year": 31536000.0,  # 365 days
    
    # Speed (base: meter_per_second)
    "meter_per_second": 1.0,
    "kilometer_per_hour": 0.277778,
    "mile_per_hour": 0.44704,
    "knot": 0.514444,
    
    # Area (base: square_meter)
    "square_meter": 1.0,
    "square_kilometer": 1000000.0,
    "hectare": 10000.0,
    "acre": 4046.8564224,
    "square_foot": 0.09290304,
    "square_inch": 0.00064516,
    
    # Data (base: byte)
    "bit": 0.125,
    "byte": 1.0,
    "kilobyte": 1024.0,
    "megabyte": 1048576.0,
    "gigabyte": 1073741824.0,
    "terabyte": 1099511627776.0,
    
    # Energy (base: joule)
    "joule": 1.0,
    "kilojoule": 1000.0,
    "calorie": 4.184,
    "kilocalorie": 4184.0,
    "watt_hour": 3600.0,
    "kilowatt_hour": 3600000.0,
    
    # Pressure (base: pascal)
    "pascal": 1.0,
    "kilopascal": 1000.0,
    "bar": 100000.0,
    "atmosphere": 101325.0,
    "psi": 6894.76
}

# Define base units for each category
CATEGORY_BASE_UNITS = {
    "Length": "meter",
    "Mass": "gram",
    "Volume": "liter",
    "Temperature": None,  # Special case
    "Time": "second",
    "Speed": "meter_per_second",
    "Area": "square_meter",
    "Data": "byte",
    "Energy": "joule",
    "Pressure": "pascal"
}

# Function to load Lottie animations from URL
def load_lottie_url(url: str) -> Optional[Dict[str, Any]]:
    """
    Load a Lottie animation from a URL
    
    Args:
        url: URL of the Lottie animation JSON
        
    Returns:
        Dictionary containing the Lottie animation data or None if failed
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Function to convert units
def convert_unit(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a value from one unit to another using conversion factors
    
    Args:
        value: The numerical value to convert
        from_unit: The source unit
        to_unit: The target unit
        
    Returns:
        The converted value
    """
    try:
        # Special case for temperature
        if from_unit in ["celsius", "fahrenheit", "kelvin"] and to_unit in ["celsius", "fahrenheit", "kelvin"]:
            # Convert to Kelvin first (as base unit)
            if from_unit == "celsius":
                kelvin_value = value + 273.15
            elif from_unit == "fahrenheit":
                kelvin_value = (value - 32) * 5/9 + 273.15
            else:  # from_unit is already kelvin
                kelvin_value = value
                
            # Convert from Kelvin to target unit
            if to_unit == "celsius":
                return kelvin_value - 273.15
            elif to_unit == "fahrenheit":
                return (kelvin_value - 273.15) * 9/5 + 32
            else:  # to_unit is kelvin
                return kelvin_value
        
        # For all other units, use conversion factors
        # Convert from source unit to base unit
        base_value = value * CONVERSION_FACTORS[from_unit]
        
        # Convert from base unit to target unit
        result = base_value / CONVERSION_FACTORS[to_unit]
        
        return result
    except Exception as e:
        st.error(f"Conversion error: {str(e)}")
        return 0.0

# Function to create a comparison chart
def create_comparison_chart(value: float, from_unit: str, to_unit: str, result: float, category: str) -> go.Figure:
    """
    Create a visual comparison chart between the original and converted values
    
    Args:
        value: The original value
        from_unit: The source unit
        to_unit: The target unit
        result: The converted value
        category: The conversion category
        
    Returns:
        A Plotly figure object
    """
    color = CONVERSION_CATEGORIES[category]["color"]
    
    # Create a bar chart comparing the two values
    fig = go.Figure()
    
    # Add bars for original and converted values
    fig.add_trace(go.Bar(
        x=[from_unit, to_unit],
        y=[value, result],
        text=[f"{value:.4g} {from_unit}", f"{result:.4g} {to_unit}"],
        textposition='auto',
        marker_color=[color, "#888888"],
        opacity=0.8  # Changed from array to single value
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{category} Conversion: {from_unit} to {to_unit}",
        xaxis_title="Units",
        yaxis_title="Value",
        height=400,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    
    return fig

# Function to get a nice display name for a unit
def get_display_name(unit: str) -> str:
    """
    Convert a unit name to a more readable display format
    
    Args:
        unit: The unit name
        
    Returns:
        A formatted display name
    """
    # Replace underscores with spaces and capitalize each word
    return unit.replace('_', ' ').title()

# Function to get animation URL based on category
def get_animation_url(category: str) -> str:
    """
    Get a relevant Lottie animation URL for a conversion category
    
    Args:
        category: The conversion category
        
    Returns:
        URL to a relevant Lottie animation
    """
    # Animation URLs for different categories
    animations = {
        "Length": "https://assets5.lottiefiles.com/packages/lf20_ksahd5rx.json",  # Ruler animation
        "Mass": "https://assets5.lottiefiles.com/private_files/lf30_nojtukcf.json",  # Scale animation
        "Volume": "https://assets9.lottiefiles.com/packages/lf20_jqfghjd8.json",  # Liquid animation
        "Temperature": "https://assets3.lottiefiles.com/packages/lf20_qvk8qrqj.json",  # Thermometer
        "Time": "https://assets1.lottiefiles.com/packages/lf20_ysas4vcp.json",  # Clock animation
        "Speed": "https://assets9.lottiefiles.com/packages/lf20_qdbb21wb.json",  # Speed animation
        "Area": "https://assets5.lottiefiles.com/packages/lf20_kcsr6fcp.json",  # Area animation
        "Data": "https://assets1.lottiefiles.com/packages/lf20_xlkxtmul.json",  # Data animation
        "Energy": "https://assets9.lottiefiles.com/packages/lf20_rjqemd61.json",  # Energy animation
        "Pressure": "https://assets1.lottiefiles.com/packages/lf20_yppp1cui.json"  # Pressure animation
    }
    
    return animations.get(category, "https://assets9.lottiefiles.com/packages/lf20_khzniaya.json")  # Default animation