import requests
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def get_latest_repos(limit=5):
    """Fetch the latest active repositories from GitHub."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "Missing GITHUB_TOKEN"}
    
    headers = {"Authorization": f"token {token}"}
    url = "https://api.github.com/user/repos?sort=pushed&direction=desc"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        return [
            {
                "name": repo["name"],
                "url": repo["html_url"],
                "pushed_at": repo["pushed_at"],
                "language": repo["language"]
            }
            for repo in repos[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}

def check_vps_health(ip=None):
    """Check if the VPS IP responds on port 80 or 443."""
    target_ip = ip or os.getenv("VPS_IP")
    if not target_ip:
        return {"error": "Missing VPS_IP"}
    
    results = {}
    for port in [80, 443]:
        try:
            with socket.create_connection((target_ip, port), timeout=3):
                results[port] = "Online"
        except (socket.timeout, socket.error):
            results[port] = "Offline"
            
    return {
        "ip": target_ip,
        "status": "Healthy" if "Online" in results.values() else "Unreachable",
        "details": results
    }
