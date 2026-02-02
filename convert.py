import pdfplumber
import pandas as pd
import os

def extract_with_links(pdf_path):
    all_rows = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            
            # Extract links and their positions
            links = page.annots if page.annots else []
            
            # Identify header
            start_row = 0 if not all_rows else 1
            
            for row in table[start_row:]:
                clean_row = []
                for i, cell in enumerate(row):
                    text = str(cell).replace('\n', ' ').strip() if cell else ""
                    
                    # Logic to wrap 'Judgment' column text in a Markdown link
                    # Typically the last column in the SC document [cite: 3, 119]
                    if i == len(row) - 1 and "2024 INSC" in text:
                        # Find matching link for this cell on the page
                        for link in links:
                            if 'uri' in link:
                                text = f"[{text}]({link['uri']})"
                                break 
                    clean_row.append(text)
                all_rows.append(clean_row)

    if not all_rows:
        return "No data found."

    df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
    return df.to_markdown(index=False)

# Entry point
if __name__ == "__main__":
    pdf_file = "Judgment_Date.pdf" # Ensure your PDF name matches this
    if os.path.exists(pdf_file):
        md_content = extract_with_links(pdf_file)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# Supreme Court Judgments Summary\n\n")
            f.write(md_content)
