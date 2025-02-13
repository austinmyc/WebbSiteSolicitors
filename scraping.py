import requests
import pandas as pd
from bs4 import BeautifulSoup
import pickle

url = "https://webb-site.com/dbpub/hksols.asp?p=0"

resp = requests.get(url)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, "html.parser")

rows = soup.find_all("tr")[1:]
names, urls, admission_years, firms, ages = [], [], [], [], []

for row in rows:
    cells = row.find_all("td")
    names.append(cells[1].get_text())
    urls.append(cells[1].find("a")["href"])
    admission_years.append(cells[2].get_text())
    firms.append(cells[3].get_text())
    ages.append(cells[4].get_text())

lawyers = pd.DataFrame({
    "name": names,
    "url": urls,
    "admission_year": admission_years,
    "firm": firms,
    "age": ages
})

lawyers.to_csv("lawyers.csv", index=False)

base_url = "https://webb-site.com/dbpub/"
sub_url = base_url + lawyers.iloc[0]["url"]
history = {}
skipped = []
for i in range(len(lawyers)):
    print("Getting history for", lawyers.iloc[i]["name"], "...", (i+1), "of", len(lawyers))
    url = lawyers.iloc[i]["url"]
    sub_url = base_url + url
    name = lawyers.iloc[i]["name"]
    try: 
        dfs = pd.read_html(sub_url)
        history[name] = dfs
    except:
        history[name] = None
        skipped.append(name)
print("Skipped", len(skipped), ": ",skipped)

with open("history.pkl", "wb") as f:
    pickle.dump(history, f)

print("Scraping Done.")
