import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from batch_analysis import find_batch_indices, get_batch_data

# Set page configuration
st.set_page_config(page_title="Batch Analysis Dashboard", layout="centered", page_icon="📊")
st.title("Biopharmaceutical Batch Analysis")

# File uploader in the sidebar
st.sidebar.title("Dashboard Controls")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Load data from the uploaded file
    df = pd.read_csv(uploaded_file)
    
    # Sidebar options for operation, product, parameter, and graphic type
    selected_operation = st.sidebar.selectbox("Betrieb", ["Betrieb 1"])
    selected_product = st.sidebar.selectbox("Produkt", ["Produkt 1"])
    selected_parameter = st.sidebar.selectbox("Parameter", ["Select Parameter", "Penicillin concentration (P:g/L)", "pH"])
    selected_graphic = st.sidebar.selectbox("Grafik", ["Select Grafik", "Line Chart", "Control Chart"])

    # Main area filter options (only visible if a file is uploaded)
    st.write("### Filter Options")
    #time_threshold = st.number_input("Batch Start Time Threshold (Time (h))", min_value=0.0, max_value=1.0, step=0.2, value=0.2)
    selected_batch = st.number_input("Select Batch Number", min_value=1, max_value=10, value=3)

    # Find batch indices based on the specified time threshold
    batch_indices = find_batch_indices(df, time=0.2)

    # Retrieve data for the selected batch
    try:
        batch_df = get_batch_data(df, selected_batch, batch_indices)
        
        # Display batch data
        st.write(f"### Data for Batch {selected_batch}")
        st.write(batch_df)
        
        # Visualization area
        st.write("### Visualization")
        
        # Line Chart
        if selected_graphic == "Line Chart" and selected_parameter in batch_df.columns:
            fig, ax = plt.subplots(figsize=(6, 4))  # Smaller size
            ax.plot(batch_df['Time (h)'], batch_df[selected_parameter], label=f'{selected_parameter}', color='royalblue')
            ax.set_xlabel('Time (h)')
            ax.set_ylabel(selected_parameter)
            ax.set_title(f'{selected_parameter} vs Time (h) for Batch {selected_batch}')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Display the matplotlib plot in Streamlit
            st.pyplot(fig)
        
        # Control Chart
        elif selected_graphic == "Control Chart" and selected_parameter in batch_df.columns:
            mean_val = batch_df[selected_parameter].mean()
            std_dev = batch_df[selected_parameter].std()
            
            # Calculate control limits (mean ± 3*std deviation)
            upper_control_limit = mean_val + 3 * std_dev
            lower_control_limit = mean_val - 3 * std_dev
            
            # Plotly Control Chart with control limits
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=batch_df['Time (h)'], y=batch_df[selected_parameter], mode='lines+markers', name=selected_parameter, line=dict(color='royalblue')))
            fig2.add_trace(go.Scatter(x=batch_df['Time (h)'], y=[upper_control_limit]*len(batch_df), mode='lines', name='Upper Control Limit', line=dict(color='red', dash='dash')))
            fig2.add_trace(go.Scatter(x=batch_df['Time (h)'], y=[lower_control_limit]*len(batch_df), mode='lines', name='Lower Control Limit', line=dict(color='red', dash='dash')))
            fig2.add_trace(go.Scatter(x=batch_df['Time (h)'], y=[mean_val]*len(batch_df), mode='lines', name='Mean', line=dict(color='green', dash='dash')))
            
            # Update layout
            fig2.update_layout(
                title=f"{selected_parameter} Control Chart for Batch {selected_batch}",
                xaxis_title="Time (h)",
                yaxis_title=selected_parameter,
                template="plotly_white",
                height=400,  # Compact height
            )
            
            # Display the Plotly control chart
            st.plotly_chart(fig2)
        
        else:
            st.write(f"The selected parameter '{selected_parameter}' is not available in this data.")
    
    except ValueError as e:
        st.write(e)

else:
    st.write("Please upload a CSV file to proceed.")
