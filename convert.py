import pandas as pd
from bs4 import BeautifulSoup
import glob
import os

def extract_html_table():
    # Automatically find any HTML file in the directory
    html_files = glob.glob("*.html")
    if not html_files:
        print("No HTML file found.")
        return
    
    html_path = html_files[0]
    print(f"Processing: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find the table in the Supreme Court document [cite: 3]
    table = soup.find('table')
    if not table:
        print("No table found in HTML.")
        return

    data = []
    # Extract headers [cite: 3]
    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    if not headers:
        # Fallback if the table uses <td> for headers
        rows = table.find_all('tr')
        headers = [td.get_text(strip=True) for td in rows[0].find_all('td')]
        rows = rows[1:]
    else:
        rows = table.find_all('tr')[1:]

    for row in rows:
        cols = row.find_all('td')
        # Handle rows with links in the 'Judgment' column [cite: 3, 119]
        row_data = []
        for i, col in enumerate(cols):
            link = col.find('a')
            if link and link.get('href'):
                # Convert to Markdown link format [cite: 3, 4]
                cell_text = f"[{col.get_text(strip=True)}]({link['href']})"
            else:
                cell_text = col.get_text(strip=True).replace('\n', ' ')
            row_data.append(cell_text)
        
        if row_data:
            data.append(row_data)

    # Create DataFrame and save as README.md
    df = pd.DataFrame(data, columns=headers if len(headers) == len(data[0]) else None)
    md_output = "# Supreme Court Judgments Summary\n\n" + df.to_markdown(index=False)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md_output)
    print("Successfully converted HTML table to README.md")

if __name__ == "__main__":
    extract_html_table()
