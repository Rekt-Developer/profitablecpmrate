import requests
import random
import time
import matplotlib.pyplot as plt
import os
from datetime import datetime

# URLs for the proxy lists
https_proxy_url = "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt"
socks4_proxy_url = "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt"
socks5_proxy_url = "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt"

# Target URL
url = "https://www.profitablecpmrate.com/tgzx4x7534?key=6ef5bb925723a00f5a280cee80cfc569"

# Metrics
impressions = 0
clicks = 0
success = 0
failures = 0
ctr = 0.0
cpm = 0.0
revenue = 0.0
metrics_history = []
daily_revenue_goal = 50.0

# Browser-like headers for requests
def generate_headers():
    return {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.63 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        ]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
    }

# Function to get proxies from a URL
def get_proxies(proxy_url):
    response = requests.get(proxy_url)
    if response.status_code == 200:
        return response.text.splitlines()
    return []

# Load proxies
https_proxies = get_proxies(https_proxy_url)
socks4_proxies = get_proxies(socks4_proxy_url)
socks5_proxies = get_proxies(socks5_proxy_url)

all_proxies = https_proxies + socks4_proxies + socks5_proxies

# Function to update the Markdown log file
def update_markdown_log():
    global impressions, clicks, ctr, cpm, revenue, success, failures

    log_content = f"""# Metrics Report

## Summary
- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Impressions:** {impressions}
- **Clicks:** {clicks}
- **Success:** {success}
- **Failures:** {failures}
- **CTR:** {ctr:.2f}%
- **CPM:** ${cpm:.2f}
- **Revenue:** ${revenue:.2f}
- **Daily Revenue Goal:** ${daily_revenue_goal} (Achieved: {'Yes' if revenue >= daily_revenue_goal else 'No'})

## Metrics Over Time
| Timestamp           | Impressions | Clicks | Success | Failures | Revenue |
|---------------------|-------------|--------|---------|----------|---------|
"""
    for record in metrics_history:
        log_content += f"| {record['timestamp']} | {record['impressions']} | {record['clicks']} | {record['success']} | {record['failures']} | ${record['revenue']:.2f} |
"

    with open("metrics_report.md", "w") as log_file:
        log_file.write(log_content)

# Function to plot a graph of metrics
def plot_metrics():
    global metrics_history

    timestamps = [record['timestamp'] for record in metrics_history]
    impressions_list = [record['impressions'] for record in metrics_history]
    clicks_list = [record['clicks'] for record in metrics_history]
    revenue_list = [record['revenue'] for record in metrics_history]

    plt.figure(figsize=(12, 7))

    plt.plot(timestamps, impressions_list, label="Impressions", marker="o")
    plt.plot(timestamps, clicks_list, label="Clicks", marker="x")
    plt.plot(timestamps, revenue_list, label="Revenue", marker="s")

    plt.title("Metrics Over Time")
    plt.xlabel("Timestamps")
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("metrics_graph.png")
    plt.close()

# Function to make a request using a proxy
def make_request_with_proxy(proxy):
    global impressions, clicks, ctr, cpm, revenue, success, failures
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(url, proxies=proxies, headers=generate_headers(), timeout=10)
        impressions += 1
        success += 1
        if response.status_code == 200:
            print(f"Impression logged with proxy: {proxy}")

            # Simulate a random click (20% chance of click)
            if random.random() < 0.2:
                clicks += 1
                print(f"Click registered with proxy: {proxy}")

        # Update metrics
        ctr = (clicks / impressions) * 100 if impressions > 0 else 0
        cpm = (revenue / impressions) * 1000 if impressions > 0 else 0

    except Exception as e:
        failures += 1
        print(f"Failed with proxy {proxy}: {e}")

# Main function to loop through proxies and perform requests
def main():
    global revenue, metrics_history

    # Simulate revenue (e.g., $0.01 per click)
    revenue_per_click = 0.01

    for proxy in random.sample(all_proxies, len(all_proxies)):
        make_request_with_proxy(proxy)
        revenue = clicks * revenue_per_click

        # Save current metrics to history
        metrics_history.append({
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "impressions": impressions,
            "clicks": clicks,
            "success": success,
            "failures": failures,
            "revenue": revenue
        })

        # Update logs and graph
        update_markdown_log()
        plot_metrics()

        # Print current metrics
        print(f"Metrics: Impressions={impressions}, Clicks={clicks}, CTR={ctr:.2f}%, CPM={cpm:.2f}, Revenue=${revenue:.2f}")

        # Sleep between requests to avoid detection
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    main()
