import requests
import re
import time

def search_github_code(query, token, max_pages=5, per_page=10):
    url = "https://api.github.com/search/code"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    all_results = []

    for page in range(1, max_pages +1):
        params = {
            "q": query,
            "per_page": 10,
            "page": 1
        }

        print(f"[>] Searching page {page}")
        response = requests.get(url, headers=headers, params=params)


        if response.status_code !=200:
            print(f"[!] GitHub error: {response.status_code} - {response.text}")
            break

        data = response.json()
        items = data.get("items", [])
        all_results.extend(items)

        if len(items) < per_page:
            break

        time.sleep(1)
    
    return {"items": all_results, "total_count": len(all_results)}

     
def download_raw_file (owner, repo, path, branch="main"):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else: 
        print(f"[!]Failed to download: {url} (status{response.status_code})")
        return None

def sshkey_validate (text):
    pattern = re.compile(
        r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----"
    )
    return bool(pattern.search(text))

def get_default_branch(owner,repo,token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("default_branch","main")
    else:
        print(f"[!] Failed to get default branch for {owner}/{repo}")
        return "main"
