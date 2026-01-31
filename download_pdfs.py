import requests
import re
import os
import base64
from github import Github

# --- CONFIGURATION ---
MD_URL = "https://raw.githubusercontent.com/citecase/insc/refs/heads/main/2026.md"
REPO_NAME = os.getenv("GITHUB_REPOSITORY")  # Automatically gets "user/repo"
TOKEN = os.getenv("GITHUB_TOKEN")
TARGET_FOLDER = "pdfs/2026"

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def run():
    print(f"Fetching markdown content...")
    resp = requests.get(MD_URL)
    if resp.status_code != 200:
        return

    # Extracting: [Case Name](URL) | Neutral Citation
    # Matches: [Name](Link) followed by the Citation pattern
    matches = re.findall(r'\[(.*?)\]\((.*?\.pdf)\).*?(\d{4}\sINSC\s\d+)', resp.text)

    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)

    for case_name, pdf_url, citation in matches:
        filename = sanitize_filename(f"{case_name} - {citation}.pdf")
        path = f"{TARGET_FOLDER}/{filename}"

        try:
            # Download PDF
            pdf_data = requests.get(pdf_url, timeout=20).content
            
            try:
                # Check if exists to avoid unnecessary commits
                contents = repo.get_contents(path)
                print(f"Skipping (Already exists): {filename}")
            except:
                # Create file
                repo.create_file(path, f"Add {filename}", pdf_data)
                print(f"Uploaded: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    run()
