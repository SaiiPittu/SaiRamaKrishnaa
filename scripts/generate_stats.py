import os
import requests

GITHUB_TOKEN = os.environ.get("METRICS_TOKEN") or os.environ.get("GITHUB_TOKEN")
USERNAME = "SaiiPittu"

graphql_query = """
query($login: String!) {
  user(login: $login) {
    name
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
    }
    repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR]) {
      totalCount
      nodes {
        stargazerCount
      }
    }
  }
}
"""

def fetch_stats():
    if not GITHUB_TOKEN:
        raise Exception("No GITHUB_TOKEN or METRICS_TOKEN found in environment.")
        
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": graphql_query, "variables": {"login": USERNAME}},
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"GraphQL query HTTP {response.status_code}: {response.text}")
        
    res = response.json()
    if "errors" in res:
        print(f"GraphQL Warnings/Errors: {res['errors']}")
        
    if "data" not in res or not res["data"].get("user"):
        raise Exception(f"User '{USERNAME}' not returned in GraphQL response: {res}")
        
    return res["data"]["user"]

def generate_svg(data):
    contribs = data["contributionsCollection"]
    total_commits = contribs["totalCommitContributions"]
    total_prs = contribs["totalPullRequestContributions"]
    total_issues = contribs["totalIssueContributions"]
    total_reviews = contribs["totalPullRequestReviewContributions"]
    
    repos = data.get("repositories", {}).get("nodes", [])
    total_stars = sum(r.get("stargazerCount", 0) for r in repos if r)

    svg = f"""<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #58a6ff; }}
    .stat {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
    .bold {{ font-weight: 700; fill: #f0f6fc; }}
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 6px; }}
  </style>

  <rect x="0.5" y="0.5" width="494" height="194" class="bg" />

  <text x="25" y="35" class="header">Sai Pittu — GitHub Activity &amp; Contributions</text>

  <g transform="translate(25, 60)">
    <text x="0" y="15" class="stat">⭐ Total Stars Earned: <tspan class="bold">{total_stars}</tspan></text>
    <text x="0" y="40" class="stat">💻 Total Commits: <tspan class="bold">{total_commits}</tspan></text>
    <text x="0" y="65" class="stat">🔀 Total PRs Created (Public &amp; Private): <tspan class="bold">{total_prs}</tspan></text>
    <text x="0" y="90" class="stat">❗ Total Issues Opened: <tspan class="bold">{total_issues}</tspan></text>
    <text x="0" y="115" class="stat">👀 Code Reviews Conducted: <tspan class="bold">{total_reviews}</tspan></text>
  </g>
</svg>"""
    return svg

if __name__ == "__main__":
    data = fetch_stats()
    svg_content = generate_svg(data)
    os.makedirs(".github/assets", exist_ok=True)
    with open(".github/assets/github-stats.svg", "w") as f:
        f.write(svg_content)
    print("Successfully generated .github/assets/github-stats.svg")
