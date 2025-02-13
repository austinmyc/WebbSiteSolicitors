from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the lawyers data
lawyers_data = pd.read_csv('data/lawyers.csv')

@app.route('/')
def index():
    return render_template('index.html', lawyers=lawyers_data.to_dict(orient='records'))

@app.route('/search', methods=['POST'])
def search():
    name_to_search = request.form['name']
    results = lawyers_data[lawyers_data['name'].str.contains(name_to_search, case=False)]
    return render_template('index.html', lawyers=results.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True) 