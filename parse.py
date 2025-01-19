import requests
from bs4 import BeautifulSoup

def get_route_info(route_url):
    """Fetch and parse information from a route page."""
    try:
        response = requests.get(route_url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title from h1 element
        h1_element = soup.find('h1')
        if h1_element:
            # Remove any child elements to get clean text
            title = h1_element.contents[0].strip()
        else:
            title = "Title not found"
        difficulty = soup.find('span', class_='rateYDS').text.strip() if soup.find('span', class_='rateYDS') else "Difficulty not found"
        location_div = soup.find('div', class_='mb-half small text-warm')
        if location_div:
            locations = [a.text.strip() for a in location_div.find_all('a')]
        else:
            locations = ["Locations not found"]
        
        # Return the extracted information
        return {
            "title": title,
            "difficulty": difficulty,
            "location": locations,
        }
    except Exception as e:
        print(f"Error fetching {route_url}: {e}")
        return None

# File containing the URLs
input_file = "gathered_urls.txt"

# File to save the route information
output_file = "route_info.txt"  

try:
    # Open the file and read all URLs
    with open(input_file, "r") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]

    # Open the output file for writing
    with open(output_file, "w") as outfile:
        # Iterate through each URL and fetch information
        for url in urls:
            print(f"Fetching info for {url}...")
            route_info = get_route_info(url)
            
            if route_info:
                # Write route information to the output file
                for key, value in route_info.items():
                    if isinstance(value, list):  # Handle locations list
                        outfile.write(f"{key.capitalize()}: {' > '.join(value)}\n")
                    else:
                        outfile.write(f"{key.capitalize()}: {value}\n")
                outfile.write("-" * 40 + "\n")  # Separator for readability
        print(f"Route information written to {output_file}")
except Exception as e:
    print(f"Error reading URLs from file: {e}")
