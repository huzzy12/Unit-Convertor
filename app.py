import streamlit as st
import time
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import os
import random

# Import utility functions
from utils import (
    CONVERSION_CATEGORIES,
    convert_unit,
    create_comparison_chart,
    get_display_name,
    load_lottie_url,
    get_animation_url
)

# Set page configuration
st.set_page_config(
    page_title="Premium Unit Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if "current_category" not in st.session_state:
    st.session_state.current_category = "Length"
if "input_value" not in st.session_state:
    st.session_state.input_value = 1.0
if "from_unit" not in st.session_state:
    st.session_state.from_unit = "meter"
if "to_unit" not in st.session_state:
    st.session_state.to_unit = "kilometer"
if "result" not in st.session_state:
    st.session_state.result = 0.001  # 1 meter = 0.001 kilometers
if "conversion_history" not in st.session_state:
    st.session_state.conversion_history = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "animation_loaded" not in st.session_state:
    st.session_state.animation_loaded = {}

# Function to update result
def update_result() -> None:
    """
    Update the conversion result based on current input value and units
    """
    try:
        value = float(st.session_state.input_value)
        from_unit = st.session_state.from_unit
        to_unit = st.session_state.to_unit
        
        # Perform the conversion
        result = convert_unit(value, from_unit, to_unit)
        
        # Update session state
        st.session_state.result = result
        
        # Add to conversion history
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.conversion_history.append({
            "timestamp": timestamp,
            "category": st.session_state.current_category,
            "from_value": value,
            "from_unit": from_unit,
            "to_value": result,
            "to_unit": to_unit
        })
        
        # Keep only the last 10 conversions
        if len(st.session_state.conversion_history) > 10:
            st.session_state.conversion_history = st.session_state.conversion_history[-10:]
    except ValueError as ve:
        st.error(f"Invalid input: {str(ve)}")
    except KeyError as ke:
        st.error(f"Key error: {str(ke)}. Please check your conversion categories and units.")
    except Exception as e:
        st.error(f"Error updating result: {str(e)}")

# Function to handle category change
def on_category_change() -> None:
    """
    Handle category change by updating the available units
    """
    category = st.session_state.current_category
    units = CONVERSION_CATEGORIES[category]["units"]
    
    # Set default units for the category
    st.session_state.from_unit = units[0]
    st.session_state.to_unit = units[1] if len(units) > 1 else units[0]
    
    # Update the result
    update_result()

# Function to swap units
def swap_units() -> None:
    """
    Swap the 'from' and 'to' units
    """
    st.session_state.from_unit, st.session_state.to_unit = st.session_state.to_unit, st.session_state.from_unit
    update_result()

# Function to toggle theme
def toggle_theme() -> None:
    """
    Toggle between light and dark theme
    """
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Main application layout
def main() -> None:
    """
    Main application function that defines the UI layout and interactions
    """
    # Sidebar
    with st.sidebar:
        st.markdown("<h1 class='title'>Unit Converter</h1>", unsafe_allow_html=True)
        
        # Category selection using option menu
        selected_category = option_menu(
            "Conversion Category",
            options=[f"{data['symbol']} {cat}" for cat, data in CONVERSION_CATEGORIES.items()],
            icons=["arrow-right-circle"] * len(CONVERSION_CATEGORIES),
            menu_icon="list",
            default_index=list(CONVERSION_CATEGORIES.keys()).index(st.session_state.current_category),
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "orange", "font-size": "14px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#4CAF50"},
            }
        )
        
        # Extract category name from the selected option
        selected_category = selected_category.split(" ", 1)[1]
        
        # Update current category if changed
        if selected_category != st.session_state.current_category:
            st.session_state.current_category = selected_category
            on_category_change()
        
        # Theme toggle
        st.markdown("---")
        theme_col1, theme_col2 = st.columns([3, 1])
        with theme_col1:
            st.write("Toggle Theme:")
        with theme_col2:
            if st.button("🌓"):
                toggle_theme()
        
        # About section
        st.markdown("---")
        with st.expander("About"):
            st.write("""
            This unit converter allows you to convert between various units across different measurement categories.
            
            Features:
            - 10 different conversion categories
            - Visual representation of conversions
            - Conversion history tracking
            
            Made with ❤️ using Streamlit.
            """)

    # Main content
    st.markdown(f"<h1 class='title'>{CONVERSION_CATEGORIES[st.session_state.current_category]['symbol']} {st.session_state.current_category} Converter</h1>", unsafe_allow_html=True)
    
    # Input section
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.number_input(
                "Enter value",
                value=st.session_state.input_value,
                key="input_value",
                on_change=update_result,
                step=0.1
            )
            
            # From unit selection
            units = CONVERSION_CATEGORIES[st.session_state.current_category]["units"]
            display_units = [get_display_name(unit) for unit in units]
            
            from_unit_index = units.index(st.session_state.from_unit) if st.session_state.from_unit in units else 0
            selected_from_unit = st.selectbox(
                "From",
                display_units,
                index=from_unit_index,
                key="display_from_unit"
            )
            
            # Update from_unit in session state
            selected_from_unit_index = display_units.index(selected_from_unit)
            if units[selected_from_unit_index] != st.session_state.from_unit:
                st.session_state.from_unit = units[selected_from_unit_index]
                update_result()
        
        with col2:
            st.button("↔️ Swap", on_click=swap_units)
        
        with col3:
            # Result display
            st.metric(
                label="Result",
                value=f"{st.session_state.result:.6g}",
                delta=None
            )
            
            # To unit selection
            to_unit_index = units.index(st.session_state.to_unit) if st.session_state.to_unit in units else 1
            selected_to_unit = st.selectbox(
                "To",
                display_units,
                index=to_unit_index,
                key="display_to_unit"
            )
            
            # Update to_unit in session state
            selected_to_unit_index = display_units.index(selected_to_unit)
            if units[selected_to_unit_index] != st.session_state.to_unit:
                st.session_state.to_unit = units[selected_to_unit_index]
                update_result()
    
    # Visualization section
    st.subheader("Visual Comparison")
    
    # Create and display the comparison chart
    fig = create_comparison_chart(
        st.session_state.input_value,
        get_display_name(st.session_state.from_unit),
        get_display_name(st.session_state.to_unit),
        st.session_state.result,
        st.session_state.current_category
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Conversion formula explanation
    st.subheader("Conversion Details")
    
    from_unit_display = get_display_name(st.session_state.from_unit)
    to_unit_display = get_display_name(st.session_state.to_unit)
    
    st.markdown(f"""
    **Formula:**
    ```
    {st.session_state.input_value} {from_unit_display} = {st.session_state.result:.6g} {to_unit_display}
    ```
    
    **Conversion Factor:**
    ```
    1 {from_unit_display} = {convert_unit(1.0, st.session_state.from_unit, st.session_state.to_unit):.6g} {to_unit_display}
    ```
    """)
    
    # Conversion history
    if st.session_state.conversion_history:
        st.subheader("Recent Conversions")
        
        # Create a DataFrame from the conversion history
        history_df = pd.DataFrame(st.session_state.conversion_history)
        
        # Format the DataFrame for display
        display_df = history_df.copy()
        display_df["Conversion"] = display_df.apply(
            lambda row: f"{row['from_value']:.4g} {get_display_name(row['from_unit'])} → {row['to_value']:.4g} {get_display_name(row['to_unit'])}",
            axis=1
        )
        
        # Display the formatted history
        st.dataframe(
            display_df[["timestamp", "category", "Conversion"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "Time",
                "category": "Category",
                "Conversion": "Conversion"
            }
        )
        
        if st.button("Clear History"):
            st.session_state.conversion_history = []
            st.rerun()
    
    # Footer
    st.markdown("<div class='footer'>", unsafe_allow_html=True)
    st.markdown("© 2023 Unit Converter | Made with Streamlit", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()