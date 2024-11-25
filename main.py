import asyncio
import aiohttp
import random
import matplotlib.pyplot as plt
from datetime import datetime

# Advanced URLs for proxy APIs
proxy_sources = {
    "geonode": {
        "url": "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
        "protocol_key": "protocols",
        "ip_key": "ip",
        "port_key": "port"
    },
    "proxyscrape": {
        "url": "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json",
        "protocol_key": None,  # Custom parsing required
        "ip_key": None,
        "port_key": None
    },
    "brightdata": {
        "url": "https://brightdata.com/api-proxies",
        "protocol_key": None,  # Requires API key and structured response
        "ip_key": "ip",
        "port_key": "port"
    },
    "spys_one": {
        "url": "http://spys.one/en/free-proxy-list/",
        "protocol_key": None,
        "ip_key": None,
        "port_key": None
    }
}

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

# Generate random headers for requests
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

# Fetch proxies from API
async def fetch_proxies(source):
    async with aiohttp.ClientSession() as session:
        async with session.get(source["url"]) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    proxies = []
                    for entry in data.get("data", []):
                        protocol = entry.get(source["protocol_key"], ["http"])[0]
                        ip = entry.get(source["ip_key"])
                        port = entry.get(source["port_key"])
                        if ip and port:
                            proxies.append((protocol, f"{ip}:{port}"))
                    return proxies
                except Exception as e:
                    print(f"Error parsing proxies from {source['url']}: {e}")
                    return []
            return []

# Validate proxies asynchronously
async def validate_proxy(proxy, protocol):
    try:
        proxy_url = f"{protocol}://{proxy}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy_url, headers=generate_headers(), timeout=10) as response:
                return response.status == 200
    except Exception:
        return False

# Update the Markdown log file
def update_markdown_log():
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
        log_content += f"""| {record['timestamp']} | {record['impressions']} | {record['clicks']} | {record['success']} | {record['failures']} | ${record['revenue']:.2f} |\n"""

    with open("metrics_report.md", "w") as log_file:
        log_file.write(log_content)

# Plot metrics over time
def plot_metrics():
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

# Perform requests with proxies
async def make_request_with_proxy(proxy, protocol):
    global impressions, clicks, ctr, cpm, revenue, success, failures
    try:
        proxy_url = f"{protocol}://{proxy}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy_url, headers=generate_headers(), timeout=10) as response:
                impressions += 1
                success += 1
                if response.status == 200:
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

# Main logic
async def main():
    global revenue, metrics_history

    revenue_per_click = 0.01  # Simulate revenue per click

    # Load and validate proxies
    all_proxies = []
    for name, source in proxy_sources.items():
        proxies = await fetch_proxies(source)
        all_proxies.extend(proxies)

    print(f"Total proxies fetched: {len(all_proxies)}")

    # Validate proxies
    tasks = [validate_proxy(proxy, protocol) for protocol, proxy in all_proxies]
    valid_proxies = [proxy for proxy, valid in zip(all_proxies, await asyncio.gather(*tasks)) if valid]
    print(f"Total valid proxies: {len(valid_proxies)}")

    for protocol, proxy in valid_proxies:
        await make_request_with_proxy(proxy, protocol)
        revenue = clicks * revenue_per_click

        # Save metrics
        metrics_history.append({
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "impressions": impressions,
            "clicks": clicks,
            "success": success,
            "failures": failures,
            "revenue": revenue
        })

        # Update logs and graphs
        update_markdown_log()
        plot_metrics()

        print(f"Metrics: Impressions={impressions}, Clicks={clicks}, CTR={ctr:.2f}%, CPM={cpm:.2f}, Revenue=${revenue:.2f}")

        # Sleep between requests
        await asyncio.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    asyncio.run(main())
