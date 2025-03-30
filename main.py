import yaml
import os
import time
import csv
from github_api import search_github_code, download_raw_file, sshkey_validate, get_default_branch


def load_config():
    with open("config.yaml","r") as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = load_config()
    token = config['github']['token']
    query = config['github']['query']

    results = search_github_code(query, token, max_pages=3, per_page=30)

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    csv_file = open("results.csv","w",newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Repository", "File Path", "Raw URL", "Saved As"])

    if results:
        print(f"\n Found {results['total_count']} matching files.\n")

        for item in results["items"]:
            owner = item["repository"]["full_name"].split("/")[0]
            repo = item["repository"]["full_name"].split("/")[1]
            path = item["path"]
            safe_filename = f"{owner}_{repo}_{path}".replace("/","_")
            output_path = os.path.join(results_dir, safe_filename)

            print(f"[.] Downloading {owner}/{repo}/{path}")
            branch = get_default_branch(owner, repo, token)
            content = download_raw_file(owner, repo, path, branch)
            time.sleep(1)

            if content and sshkey_validate(content):
                print(f"SSH key found in repo {owner}/{repo}/{path}")

                try:
                    with open (output_path, "w") as f:
                        f.write(content)
    
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
                    csv_writer.writerow([f"{owner}/{repo}", path, raw_url, output_path])
                    print(f"Saved to {output_path}")
                except Exception as e:
                        print(f"[!] Failed to save file {output_path}")
                        
            else:
                print("No keys found")
    
    csv_file.close()
