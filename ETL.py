import streamlit as st
import pandas as pd
import os

# Function to find similar values in a column
def find_similar_values(df, column):
    unique_values = df[column].unique()
    similar_groups = {}

    # Simple grouping based on lowercased strings, can be enhanced
    for value in unique_values:
        key = value.lower().strip()
        if key in similar_groups:
            similar_groups[key].append(value)
        else:
            similar_groups[key] = [value]

    return {k: v for k, v in similar_groups.items() if len(v) > 1}

# Function to apply user's selections and rename values
def rename_values(df, column, selected_value, values_to_rename):
    df[column] = df[column].replace(values_to_rename, selected_value)
    return df

# Load stored mapping selections
def load_mappings():
    if os.path.exists('value_mappings.csv'):
        return pd.read_csv('value_mappings.csv')
    else:
        return pd.DataFrame(columns=['column', 'original_value', 'renamed_value'])

# Save updated mappings
def save_mappings(mappings_df):
    mappings_df.to_csv('value_mappings.csv', index=False)

# Main Streamlit app
def main():
    st.title("ETL Application with Anomaly Detection and Renaming")

    uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        if file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        st.write("Data Preview:")
        st.dataframe(df)

        # Load previous mappings
        mappings_df = load_mappings()

        # Iterate through columns and find similar values
        for column in df.columns:
            similar_values = find_similar_values(df, column)
            
            if similar_values:
                st.write(f"Anomalies found in column: {column}")
                
                for key, group in similar_values.items():
                    st.write(f"Similar values: {group}")
                    selected_value = st.selectbox(f"Select the correct value for {group}", group)

                    if selected_value:
                        # Rename the values in the DataFrame
                        df = rename_values(df, column, selected_value, group)

                        # Update mappings
                        for value in group:
                            if value != selected_value:
                                mappings_df = mappings_df.append({'column': column, 'original_value': value, 'renamed_value': selected_value}, ignore_index=True)

        # Save updated mappings
        save_mappings(mappings_df)

        # Display the modified DataFrame
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
