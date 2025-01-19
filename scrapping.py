import requests
from bs4 import BeautifulSoup

def get_urls_from_sitemap(sitemap_url, filter_prefix=None):
    """Fetches URLs from a sitemap and optionally filters them by prefix."""
    urls = []
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        loc_tags = soup.find_all('loc')
        for loc in loc_tags:
            url = loc.text
            if filter_prefix is None or url.startswith(filter_prefix):
                urls.append(url)
    except Exception as e:
        print(f"Error fetching or parsing {sitemap_url}: {e}")
    return urls

# Initial sitemap
base_sitemap_url = "https://www.mountainproject.com/sitemap.xml"
filter_prefix = "https://www.mountainproject.com/sitemap-routes"

# Fetch the first-level URLs that match the prefix
first_level_urls = get_urls_from_sitemap(base_sitemap_url, filter_prefix)

# Fetch all URLs from the filtered sitemaps
all_urls = []
for url in first_level_urls:
    print(f"Fetching URLs from {url}...")
    urls = get_urls_from_sitemap(url)
    all_urls.extend(urls)

# Save all gathered URLs to a file
output_file = "gathered_urls.txt"
try:
    with open(output_file, "w") as file:
        for url in all_urls:
            file.write(url + "\n")
    print(f"All URLs have been written to {output_file}")
except Exception as e:
    print(f"Error writing to file: {e}")
