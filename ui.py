import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from tkinter import ttk  # Import ttk for Treeview
import pandas as pd
import pickle
from fuzzywuzzy import process  # Import fuzzywuzzy for fuzzy matching

def load_lawyers(filename):
    lawyers = pd.read_csv(filename)
    return lawyers

def load_history(filename):
    with open(filename, "rb") as f:
        history = pickle.load(f)
    return history

def search_solicitor(name, lawyers):
    if not name or not isinstance(name, str):
        return pd.DataFrame()  # Return an empty DataFrame if the input is invalid

    # Use fuzzy matching to find the best matches
    names_list = lawyers['name'].tolist()
    matches = process.extract(name, names_list, limit=None)  # Get all matches

    # Filter results based on a threshold (e.g., 70% match)
    threshold = 70
    matched_names = [(names_list.index(match[0])+1, match[0]) for match in matches if match[1] >= threshold]
    return pd.DataFrame(matched_names, columns=['idx', 'name'])

def create_ui(lawyers_data, history_data):
    def search():
        name_to_search = simpledialog.askstring("Input", "Enter the solicitor's name:")
        results = search_solicitor(name_to_search, lawyers_data)
        #print(results)
        
        if not results.empty:
            result_text.delete(1.0, tk.END)  # Clear previous results
            for _, solicitor in results.iterrows():
                result_text.insert(tk.END, f"{int(solicitor['idx'])}: {solicitor['name']}\n")
        else:
            messagebox.showinfo("Info", "No solicitors found.")

    def display_history():
        selected_index = simpledialog.askinteger("Input", "Select a solicitor by number:")
        if selected_index is not None and 0 < selected_index <= len(lawyers_data):
            solicitor = lawyers_data.iloc[selected_index - 1]
            name = solicitor['name']
            working_history_df = history_data[name][0]  # Get the DataFrame for the solicitor
            
            if working_history_df.columns.dtype=='int64':
                first_row_values = working_history_df.iloc[0]
                working_history_df.columns =first_row_values
                working_history_df = working_history_df.drop(index = 0)
            # Clean the DataFrame: drop unwanted columns and replace NaN values
            working_history_df = working_history_df.drop(columns=[col for col in working_history_df.columns if 'Unnamed' in str(col)], errors='ignore')
            working_history_df = working_history_df.fillna('')  # Replace NaN with empty strings
            nan_columns = [col for col in working_history_df.columns if pd.isna(col)] # Identify columns with NaN as their name
            working_history_df = working_history_df.drop(columns=nan_columns, errors='ignore') 
            
            # Create a new window to display the working history
            history_window = tk.Toplevel(root)
            history_window.title(f"Working History for {name}")
            
            # Create a Treeview widget for better display
            tree = ttk.Treeview(history_window, columns=list(working_history_df.columns), show='headings')
            tree.pack(pady=10)

            # Define headings
            for col in working_history_df.columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center')  # Center align the columns

            # Insert data into the Treeview
            for index, row in working_history_df.iterrows():
                tree.insert("", "end", values=list(row))

            # Add a scrollbar
            scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

        else:
            messagebox.showwarning("Warning", "Invalid selection.")

    root = tk.Tk()
    root.title("Solicitor Search")

    search_button = tk.Button(root, text="Search Solicitor", command=search)
    search_button.pack(pady=10)

    display_button = tk.Button(root, text="Display Working History", command=display_history)
    display_button.pack(pady=10)

    result_text = scrolledtext.ScrolledText(root, width=50, height=30)
    result_text.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    lawyers_data = load_lawyers('data/lawyers.csv')
    history_data = load_history('data/history.pkl')  # Load the working history
    create_ui(lawyers_data, history_data) 