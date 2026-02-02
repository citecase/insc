import pandas as pd
from bs4 import BeautifulSoup
import glob
import os

def extract_case_details():
    # Find any HTML file in the root directory
    html_files = glob.glob("*.html")
    if not html_files:
        print("No HTML file found.")
        return
    
    html_path = html_files[0]
    print(f"Processing: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    # Find the specific table containing "Diary Number" or "Case Number" [cite: 3, 14, 54]
    target_table = None
    for table in soup.find_all('table'):
        header_text = table.get_text().lower()
        if "diary number" in header_text or "case number" in header_text:
            target_table = table
            break

    if not target_table:
        print("Could not find the specific case details table.")
        return

    data = []
    rows = target_table.find_all('tr')
    
    for row in rows:
        cols = row.find_all(['td', 'th'])
        # Skip small layout tables or navigation rows [cite: 1, 12, 122]
        if len(cols) < 5:
            continue
            
        row_data = []
        for col in cols:
            # Extract links specifically for PDFs attached to Neutral Citations [cite: 3, 34, 104]
            link = col.find('a')
            cell_text = col.get_text(separator=" ", strip=True)
            
            if link and link.get('href'):
                url = link['href']
                # Ensure the URL points to the sci.gov.in portal [cite: 4, 16, 21]
                if not url.startswith('http'):
                    url = "https://www.sci.gov.in" + url
                
                # Format as Markdown link [Text](Direct_PDF_URL)
                row_data.append(f"[{cell_text}]({url})")
            else:
                row_data.append(cell_text)
        
        if row_data:
            data.append(row_data)

    if not data:
        print("No case data extracted.")
        return

    # Use first valid row as header 
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Save to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# Supreme Court Judgments - PDF API Links\n\n")
        f.write("Click on the **Judgment** column citations to open the official PDF.\n\n")
        f.write(df.to_markdown(index=False))
    print("Successfully generated README.md with direct PDF links.")

if __name__ == "__main__":
    extract_case_details()
