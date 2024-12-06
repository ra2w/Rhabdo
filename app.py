import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Set page title
st.title('Exercise Induced Rhabdomyolysis')

# Define the two workout start times
workout1_start = pd.to_datetime('2024-11-26 10:00:00')  # Tuesday 10 AM
workout2_start = pd.to_datetime('2024-11-27 14:30:00')  # Wednesday 2:30 PM

try:
    # Read the CSV file
    df = pd.read_csv('ck-values.csv')
    
    # Convert Date/Time to datetime
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    
    # Sort dataframe by Date/Time
    df = df.sort_values('Date/Time')
    
    with st.expander("Raw Data"):
        # Display the raw data table
        st.subheader('Raw Data')
        st.dataframe(df)
    
    # Add footnote
    st.markdown("""
    ---
    **Note on Creatine kinase (CK) Response:**  
    - Creatine kinase (CK) has a serum half-life of approximately 36 hours.  
    - CK levels rise within 12 hours of muscle injury, peak in 24-72 hours, and decrease at a rate of 30-40% per day.
                
    Source: https://www.uptodate.com/contents/rhabdomyolysis-clinical-manifestations-and-diagnosis
    """)
    # Create plots for both workouts
    st.write(f'### CK levels post Workout 1 (Pull-up/Arm workout on {workout1_start.strftime("%m/%d/%y")})')
    df['Hours_Elapsed_Workout1'] = ((df['Date/Time'] - workout1_start).dt.total_seconds() / 3600).round(1)
    
    # Add t=0 point for first workout
    zero_point1 = pd.DataFrame({
        'Date/Time': [workout1_start],
        'Value (U/L)': [0.0],  # Use first measured value
        'Hours_Elapsed_Workout1': [0.0]
    })
    # Create separate dataframes for interpolated and real data
    df_interp1 = pd.concat([zero_point1, df.iloc[0:1]], ignore_index=True).sort_values('Hours_Elapsed_Workout1')
    df_real1 = df.copy()
    
    # Create figure with two traces
    fig1 = px.line(df_interp1, x='Hours_Elapsed_Workout1', y='Value (U/L)', 
                   title='CK Values After Pull-up/Arm Workout',
                   template='plotly',
                   labels={'Hours_Elapsed_Workout1': 'Time elapsed since first workout', 'Value (U/L)': 'CK Value'})
    
    # Update the first trace to be dotted
    fig1.data[0].line.dash = 'dot'
    
    # Add the real data trace (excluding the zero point)
    df_real1_sorted = df_real1[df_real1['Hours_Elapsed_Workout1'] > 0].sort_values('Hours_Elapsed_Workout1')
    fig1.add_scatter(x=df_real1_sorted['Hours_Elapsed_Workout1'], 
                    y=df_real1_sorted['Value (U/L)'],
                    mode='lines+markers',
                    name='Measured Values',
                    marker=dict(size=8, symbol='circle-dot'))
    
    # Find peak value and its time
    peak_idx1 = df_real1_sorted['Value (U/L)'].idxmax()
    peak_time1 = df_real1_sorted.loc[peak_idx1, 'Hours_Elapsed_Workout1']
    peak_value1 = df_real1_sorted.loc[peak_idx1, 'Value (U/L)']
    
    # Add vertical lines for workouts
    fig1.add_vline(x=0, line_dash="dot", line_color="#1f77b4")
    fig1.add_vline(x=(workout2_start - workout1_start).total_seconds()/3600, 
                   line_dash="dot", line_color="#1f77b4")
    
    # Add workout labels
    fig1.add_annotation(x=0, y=max(df['Value (U/L)'])*0.2,
                       text="Workout 1", showarrow=True,
                       arrowhead=1, ax=-30, ay=-40)
    fig1.add_annotation(x=(workout2_start - workout1_start).total_seconds()/3600,
                       y=max(df['Value (U/L)'])*0.3,
                       text="Workout 2", showarrow=True,
                       arrowhead=1, ax=-30, ay=-40)
    
    # Add first CK test annotation
    first_test_value = df.iloc[0]['Value (U/L)']
    first_test_time = df.iloc[0]['Hours_Elapsed_Workout1']
    fig1.add_annotation(
        x=first_test_time,
        y=first_test_value,
        text="First CK Test",
        showarrow=True,
        arrowhead=1,
        ax=-10,
        ay=-60
    )
    
    # Add vertical line at peak
    fig1.add_vline(x=peak_time1, line_dash="dash", line_color="gray")
    fig1.add_annotation(
        x=peak_time1,
        y=peak_value1,
        text=f"Peak: {peak_value1:.0f} U/L @{peak_time1:.1f}h",
        showarrow=True,
        arrowhead=1,
        yshift=10,
        ax=-30,
        ay=-30
    )
    # Add safe discharge zone
    fig1.add_hrect(
        y0=0, y1=5000,
        fillcolor="lightgreen", opacity=0.2,
        layer="below", line_width=0
    )
    fig1.add_annotation(
        x=peak_time1*0.67,  # Center the label horizontally
        y=2500,
        text="Safe discharge zone",
        showarrow=False,
        font=dict(size=12),
        textangle=0
    )

    fig1.update_layout(
        xaxis_title=f"Time (hours) elapsed since first workout (t=0 at {workout1_start.strftime('%I:%M%p %m/%d/%y')})",
        yaxis_title="CK Value (U/L)",
        hovermode='x unified',
        xaxis=dict(
            dtick=12,  # Set tick interval to 12 hours
            tick0=0    # Start ticks at 0
        ),
        yaxis=dict(
            dtick=5000,  # Set tick interval to 5000 units
            tick0=0      # Start ticks at 0
        )
    )
    st.plotly_chart(fig1)

    st.write('### CK levels post Workout 2 (Quad + HIIT workout on {workout2_start.strftime("%m/%d/%y")})')
    df['Hours_Elapsed_Workout2'] = ((df['Date/Time'] - workout2_start).dt.total_seconds() / 3600).round(1)
    
    # Add t=0 point for second workout
    zero_point2 = pd.DataFrame({
        'Date/Time': [workout2_start],
        'Value (U/L)': [0.0],  # Use first measured value
        'Hours_Elapsed_Workout2': [0.0]
    })
    # Create separate dataframes for interpolated and real data
    df_interp2 = pd.concat([zero_point2, df.iloc[0:1]], ignore_index=True).sort_values('Hours_Elapsed_Workout2')
    df_real2 = df.copy()
    
    # Create figure with two traces
    fig2 = px.line(df_interp2, x='Hours_Elapsed_Workout2', y='Value (U/L)', 
                   title='CK Values After Quad + HIIT Workout',
                   template='plotly',
                   labels={'Hours_Elapsed_Workout2': 'Time elapsed since second workout', 'Value (U/L)': 'CK Value'})
    
    # Update the first trace to be dotted
    fig2.data[0].line.dash = 'dot'
    
    # Add the real data trace (excluding the zero point)
    df_real2_sorted = df_real2[df_real2['Hours_Elapsed_Workout2'] > 0].sort_values('Hours_Elapsed_Workout2')
    fig2.add_scatter(x=df_real2_sorted['Hours_Elapsed_Workout2'], 
                    y=df_real2_sorted['Value (U/L)'],
                    mode='lines+markers',
                    name='Measured Values',
                    marker=dict(size=8, symbol='circle-dot'))
    
    # Find peak value and its time
    peak_idx2 = df_real2_sorted['Value (U/L)'].idxmax()
    peak_time2 = df_real2_sorted.loc[peak_idx2, 'Hours_Elapsed_Workout2']
    peak_value2 = df_real2_sorted.loc[peak_idx2, 'Value (U/L)']
    
    # Add vertical lines for workouts
    fig2.add_vline(x=0, line_dash="dot", line_color="#1f77b4")
    
    # Add workout label
    fig2.add_annotation(x=0, y=max(df['Value (U/L)'])*0.2,
                       text="Workout 2", showarrow=True,
                       arrowhead=1, ax=-30, ay=-40)
    
    # Add first CK test annotation
    first_test_value = df.iloc[0]['Value (U/L)']
    first_test_time = df.iloc[0]['Hours_Elapsed_Workout2']
    fig2.add_annotation(
        x=first_test_time,
        y=first_test_value,
        text="First CK Test",
        showarrow=True,
        arrowhead=1,
        ax=-15,
        ay=-50
    )
    
    # Add vertical line at peak
    fig2.add_vline(x=peak_time2, line_dash="dash", line_color="gray")
    fig2.add_annotation(
        x=peak_time2,
        y=peak_value2,
        text=f"Peak: {peak_value2:.0f} U/L @{peak_time2:.1f}h",
        showarrow=True,
        arrowhead=1,
        yshift=10,
        ax=-70,
        ay=-30
    )
    

    # Add safe discharge zone
    fig2.add_hrect(
        y0=0, y1=5000,
        fillcolor="lightgreen", opacity=0.2,
        layer="below", line_width=0
    )
    fig2.add_annotation(
        x=peak_time2*0.67,  # Center the label horizontally
        y=2500,
        text="Safe discharge zone",
        showarrow=False,
        font=dict(size=12),
        textangle=0
    )

    fig2.update_layout(
        xaxis_title=f"Time (hours) elapsed since second workout (t=0 at {workout2_start.strftime('%I:%M%p %m/%d/%y')})",
        yaxis_title="CK Value (U/L)",
        hovermode='x unified',
        xaxis=dict(
            dtick=12,  # Set tick interval to 12 hours
            tick0=0    # Start ticks at 0
        ),
        yaxis=dict(
            dtick=5000,  # Set tick interval to 5000 units
            tick0=0      # Start ticks at 0
        )
    )
    st.plotly_chart(fig2)
    
    
    

    st.write(df['Value (U/L)'].describe())
    

except FileNotFoundError:
    st.error("Error: Could not find 'ck-values.csv'. Please make sure the file exists in the same directory as the app.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
