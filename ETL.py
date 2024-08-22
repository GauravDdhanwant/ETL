import streamlit as st
import pandas as pd
import os

# Load stored mappings
def load_mappings():
    if os.path.exists('value_mappings.csv'):
        return pd.read_csv('value_mappings.csv')
    else:
        return pd.DataFrame(columns=['column', 'original_value', 'renamed_value'])

# Save updated mappings
def save_mappings(mappings_df):
    mappings_df.to_csv('value_mappings.csv', index=False)

# Function to apply previous mappings
def apply_mappings(df, mappings_df):
    for _, row in mappings_df.iterrows():
        df[row['column']] = df[row['column']].replace(row['original_value'], row['renamed_value'])
    return df

# Function to find and handle anomalies
def find_and_handle_anomalies(df, column, mappings_df):
    st.write(f"Processing column: {column}")
    
    # Find unique values in the column
    unique_values = df[column].unique()
    
    # Filter out values already mapped
    mapped_values = mappings_df[mappings_df['column'] == column]['original_value'].unique()
    remaining_values = [val for val in unique_values if val not in mapped_values]
    
    similar_groups = {}
    
    # Simple similarity detection based on string lowercasing and stripping (can be enhanced)
    for value in remaining_values:
        key = value.lower().strip()
        if key in similar_groups:
            similar_groups[key].append(value)
        else:
            similar_groups[key] = [value]
    
    # Handle anomalies
    for key, group in similar_groups.items():
        if len(group) > 1:
            st.write(f"Found similar values: {group}")
            selected_value = st.selectbox(f"Select the correct value for {group}", group, key=f"{column}_{key}")
            
            if selected_value:
                df[column] = df[column].replace(group, selected_value)
                for val in group:
                    if val != selected_value:
                        mappings_df = mappings_df.append({
                            'column': column,
                            'original_value': val,
                            'renamed_value': selected_value
                        }, ignore_index=True)
    
    return df, mappings_df

def main():
    st.title("ETL Application with Anomaly Detection and Renaming")
    
    uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file:
        # Read the uploaded file
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        st.write("Data Preview:")
        st.dataframe(df)
        
        # Load previous mappings
        mappings_df = load_mappings()
        
        # Apply previous mappings
        df = apply_mappings(df, mappings_df)
        
        # Allow user to select columns to check for anomalies
        columns_to_check = st.multiselect("Select columns to check for anomalies", df.columns)
        
        # Process each selected column
        for column in columns_to_check:
            df, mappings_df = find_and_handle_anomalies(df, column, mappings_df)
        
        # Save updated mappings
        save_mappings(mappings_df)
        
        st.write("Modified Data:")
        st.dataframe(df)
        
        # Option to download the modified file
        st.download_button(
            label="Download Modified File",
            data=df.to_csv(index=False),
            file_name="modified_file.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
