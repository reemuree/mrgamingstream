import requests
from bs4 import BeautifulSoup
import re

# Fetch HTML content
url = 'https://mrgamingstreams.com/247-tv'
response = requests.get(url)
html_content = response.content

# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract names and create .m3u8 links
names_links = {}
channel_divs = soup.find_all('div', class_='wp-block-button')

for channel_div in channel_divs:
    channel_name = channel_div.a.text.strip()
    href = channel_div.a['href']

    # Fetch each channel's page
    channel_page_response = requests.get(href)
    if channel_page_response.status_code == 200:
        channel_page = channel_page_response.text
        # Search for .m3u8 URL in the response text
        m3u8_url = re.search(r'(https://[^\s]+\.m3u8)', channel_page)

        if m3u8_url:
            # Extracted .m3u8 URL
            extracted_m3u8 = m3u8_url.group()

            # Parse :authority: and :path: from the URL
            authority = extracted_m3u8.split('/')[2]
            path = '/'.join(extracted_m3u8.split('/')[3:])

            # Store the channel name, :authority:, and :path:
            if "247 Channels" not in names_links:
                names_links["247 Channels"] = []
            names_links["247 Channels"].append({
                "name": channel_name,
                "authority": authority,
                "path": path
            })
        else:
            print(f"No .m3u8 URL found for {channel_name}")
    else:
        print(f"Failed to fetch {channel_name} page")

# Write the content to a new .m3u8 file
with open('updated_file.m3u8', 'w') as file:
    file.write("#EXTM3U\n")
    for category, channels in names_links.items():
        file.write(f"#EXTGRP:{category}\n")  # Write category as a group header
        for channel in channels:
            file.write(f"#EXTINF:-1 , {channel['name']}\n")  # Write channel name
            file.write(f"https://{channel['authority']}/{channel['path']}\n")  # Write channel link
