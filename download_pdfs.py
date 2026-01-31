import requests
import re
import os
from github import Github

# --- CONFIGURATION ---
MD_URL = "https://raw.githubusercontent.com/citecase/insc/refs/heads/main/2026.md"
REPO_NAME = os.getenv("GITHUB_REPOSITORY") 
TOKEN = os.getenv("GITHUB_TOKEN")
TARGET_FOLDER = "pdfs/2026"

def sanitize_filename(name):
    # Removes characters like / \ : * ? " < > |
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def run():
    print(f"--- Starting Sync Process ---")
    resp = requests.get(MD_URL)
    if resp.status_code != 200:
        print(f"Error: Could not reach the MD file. Status: {resp.status_code}")
        return

    content = resp.text
    # This regex is more robust: 
    # 1. Finds the Case Name and URL: [Name](URL)
    # 2. Looks for the Neutral Citation: 2026 INSC [Number]
    pattern = r'\[(.*?)\]\((https?://.*?\.pdf)\).*?(\d{4}\s+INSC\s+\d+)'
    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)

    if not matches:
        print("No matches found! Check if the Markdown format matches the regex.")
        # Debug: print first 200 chars of the file to see what we are dealing with
        print("File Snippet:", content[:200])
        return

    print(f"Found {len(matches)} cases to process.")

    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)

    for case_name, pdf_url, citation in matches:
        # Format: Case Name - 2026 INSC 1.pdf
        clean_filename = sanitize_filename(f"{case_name.strip()} - {citation.strip()}.pdf")
        path = f"{TARGET_FOLDER}/{clean_filename}"

        try:
            # Check if file exists in the repo already
            try:
                repo.get_contents(path)
                print(f"[-] Already exists: {clean_filename}")
                continue 
            except:
                # File doesn't exist, proceed to download
                print(f"[+] Downloading: {clean_filename}...")
                pdf_data = requests.get(pdf_url, timeout=30).content
                
                repo.create_file(
                    path=path,
                    message=f"Automated upload: {citation}",
                    content=pdf_data
                )
                print(f"[✓] Successfully uploaded to GitHub.")
        except Exception as e:
            print(f"[!] Failed {clean_filename}: {e}")

if __name__ == "__main__":
    run()
