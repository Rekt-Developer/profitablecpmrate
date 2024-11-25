import asyncio
import aiohttp
import random
import matplotlib.pyplot as plt
from datetime import datetime

# Configuration
url = "https://www.profitablecpmrate.com/tgzx4x7534?key=6ef5bb925723a00f5a280cee80cfc569"
revenue_per_click = 0.01  # Revenue per click in dollars
daily_revenue_goal = 50.0

# Proxy sources
proxy_sources = [
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt"
]

# Metrics
metrics = {
    "impressions": 0,
    "clicks": 0,
    "success": 0,
    "failures": 0,
    "ctr": 0.0,
    "cpm": 0.0,
    "revenue": 0.0,
}
metrics_history = []

# Generate random headers
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
        "Referer": "https://www.google.com",
    }

# Fetch proxies from sources
async def fetch_proxies():
    proxies = []
    async with aiohttp.ClientSession() as session:
        for source in proxy_sources:
            try:
                async with session.get(source, timeout=10) as response:
                    if response.status == 200:
                        proxies += (await response.text()).splitlines()
                        print(f"Fetched {len(proxies)} proxies from {source}")
            except Exception as e:
                print(f"Error fetching proxies from {source}: {e}")
    return list(set(proxies))  # Remove duplicates

# Validate a single proxy
async def validate_proxy(proxy):
    try:
        proxy_url = f"http://{proxy}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy_url, headers=generate_headers(), timeout=10) as response:
                return response.status == 200
    except Exception:
        return False

# Perform a single request using a proxy
async def make_request_with_proxy(proxy):
    global metrics
    try:
        proxy_url = f"http://{proxy}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy_url, headers=generate_headers(), timeout=10) as response:
                metrics["impressions"] += 1
                metrics["success"] += 1
                if response.status == 200:
                    print(f"Impression logged with proxy: {proxy}")

                    # Simulate a random click (20% chance)
                    if random.random() < 0.2:
                        metrics["clicks"] += 1
                        metrics["revenue"] += revenue_per_click
                        print(f"Click registered with proxy: {proxy}")

        # Update metrics
        metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
        metrics["cpm"] = (metrics["revenue"] / metrics["impressions"]) * 1000 if metrics["impressions"] > 0 else 0

    except Exception as e:
        metrics["failures"] += 1
        print(f"Request failed with proxy {proxy}: {e}")

# Update the markdown log
def update_markdown_log():
    log_content = f"""# Metrics Report

## Summary
- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Impressions:** {metrics["impressions"]}
- **Clicks:** {metrics["clicks"]}
- **Success:** {metrics["success"]}
- **Failures:** {metrics["failures"]}
- **CTR:** {metrics["ctr"]:.2f}%
- **CPM:** ${metrics["cpm"]:.2f}
- **Revenue:** ${metrics["revenue"]:.2f}
- **Daily Revenue Goal:** ${daily_revenue_goal} (Achieved: {'Yes' if metrics["revenue"] >= daily_revenue_goal else 'No'})

## Metrics Over Time
| Timestamp           | Impressions | Clicks | Success | Failures | Revenue |
|---------------------|-------------|--------|---------|----------|---------|
"""
    for record in metrics_history:
        log_content += f"| {record['timestamp']} | {record['impressions']} | {record['clicks']} | {record['success']} | {record['failures']} | ${record['revenue']:.2f} |\n"

    with open("metrics_report.md", "w") as file:
        file.write(log_content)

# Plot metrics graph
def plot_metrics():
    timestamps = [record["timestamp"] for record in metrics_history]
    impressions = [record["impressions"] for record in metrics_history]
    clicks = [record["clicks"] for record in metrics_history]
    revenue = [record["revenue"] for record in metrics_history]

    plt.figure(figsize=(12, 7))
    plt.plot(timestamps, impressions, label="Impressions", marker="o")
    plt.plot(timestamps, clicks, label="Clicks", marker="x")
    plt.plot(timestamps, revenue, label="Revenue", marker="s")
    plt.title("Metrics Over Time")
    plt.xlabel("Timestamps")
    plt.xticks(rotation=45)
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("metrics_graph.png")
    plt.close()

# Main function
async def main():
    global metrics_history

    proxies = await fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")

    # Validate proxies
    tasks = [validate_proxy(proxy) for proxy in proxies]
    valid_proxies = [proxy for proxy, valid in zip(proxies, await asyncio.gather(*tasks)) if valid]
    print(f"Total valid proxies: {len(valid_proxies)}")

    # Use valid proxies to make requests
    for proxy in valid_proxies:
        await make_request_with_proxy(proxy)

        # Save metrics snapshot
        metrics_history.append({
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **metrics,
        })

        # Update logs and graphs
        update_markdown_log()
        plot_metrics()

        print(f"Metrics Updated: {metrics}")

        await asyncio.sleep(random.uniform(1, 3))  # Pause between requests

if __name__ == "__main__":
    asyncio.run(main())
