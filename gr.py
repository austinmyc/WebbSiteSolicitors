import gradio as gr
import pandas as pd
import pickle
from fuzzywuzzy import process

# Load your data
def load_lawyers(filename):
    return pd.read_csv(filename)

def load_history(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

lawyers_data = load_lawyers('data/lawyers.csv')
history_data = load_history('data/history.pkl')

# Search function
def search_solicitor(name):
    if not name or not isinstance(name, str):
        return "Invalid input"
    
    names_list = lawyers_data['name'].tolist()
    matches = process.extract(name, names_list, limit=None)
    threshold = 70
    matched_names = [(names_list.index(match[0])+1, match[0]) for match in matches if match[1] >= threshold]
    
    if matched_names:
        return pd.DataFrame(matched_names, columns=['idx', 'name'])
    else:
        return "No solicitors found."

# Display history function
def display_history(selected_index):
    if selected_index is None or not (0 < selected_index <= len(lawyers_data)):
        return "Invalid selection."
    
    solicitor = lawyers_data.iloc[selected_index - 1]
    name = solicitor['name']
    working_history_df = history_data[name][0]  # Get the DataFrame for the solicitor
    
    if working_history_df.columns.dtype == 'int64':
        first_row_values = working_history_df.iloc[0]
        working_history_df.columns = first_row_values
        working_history_df = working_history_df.drop(index=0)
    
    # Clean the DataFrame: drop unwanted columns and replace NaN values
    working_history_df = working_history_df.drop(columns=[col for col in working_history_df.columns if 'Unnamed' in str(col)], errors='ignore')
    working_history_df = working_history_df.fillna('')  # Replace NaN with empty strings
    nan_columns = [col for col in working_history_df.columns if pd.isna(col)]  # Identify columns with NaN as their name
    working_history_df = working_history_df.drop(columns=nan_columns, errors='ignore')
    
    return working_history_df

# Gradio interface
with gr.Blocks() as iface:
    gr.Markdown("# Solicitor Search and History Display")
    
    with gr.Row():
        name_input = gr.Textbox(label="Enter Solicitor's Name")
        search_button = gr.Button("Search Solicitor")
    
    search_results = gr.Dataframe(label="Search Results")
    
    with gr.Row():
        index_input = gr.Number(label="Select Solicitor by Number", precision=0)
        history_button = gr.Button("Display Working History")
    
    history_results = gr.Dataframe(label="Working History")

    # Define button actions
    search_button.click(search_solicitor, inputs=name_input, outputs=search_results)
    history_button.click(display_history, inputs=index_input, outputs=history_results)

if __name__ == "__main__":
    iface.launch()