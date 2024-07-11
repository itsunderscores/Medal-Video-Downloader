import sys
import requests
import subprocess
import re

def extract_content_id(url):
    try:
        # Using regex to extract the content ID from the URL
        match = re.search(r'(?:contentId=|/clips/)([a-zA-Z0-9_]{14,20})', url)
        if match:
            return match.group(1)
        else:
            # Handle other URL formats if needed
            match = re.search(r'/clips/([a-zA-Z0-9_]+)', url)
            if match:
                return match.group(1)
            else:
                return None
    except Exception as e:
        print(f"Error extracting content ID: {e}")
        return None

def extract_data_from_url(url, start_str, end_str):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the content of the page as a string
            page_content = response.text
            
            # Find the start and end positions of the data
            start_index = page_content.find(start_str) + len(start_str)
            end_index = page_content.find(end_str, start_index)
            
            # Extract the data
            if start_index != -1 and end_index != -1:
                extracted_data = page_content[start_index:end_index]
                return extracted_data.strip('"')
            else:
                return "Data not found"
        else:
            return f"Failed to retrieve the page. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def save_content_from_url(url, file_name):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the content to a file
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Content saved to {file_name}")
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def convert_m3u8_to_mp4(input_file, output_file):
    try:
        command = ['ffmpeg', '-protocol_whitelist', 'file,http,https,tcp,tls', '-i', input_file, '-c', 'copy', output_file]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")

# Check if a URL argument is provided
if len(sys.argv) < 2:
    print("Please provide a URL as an argument.")
    sys.exit(1)

# URL from command line argument
url = sys.argv[1]

# URL and strings to search between
start_str = 'contentUrlHls":"'
end_str = '"'

# Extract the content ID from the URL
content_id = extract_content_id(url)
if content_id:
    print(f"Content ID extracted: {content_id}")
    
    # Extract the data
    extracted_data = extract_data_from_url(f"https://medal.tv/?contentId={content_id}", start_str, end_str)
    
    if extracted_data.startswith("http"):  # Check if the extracted data looks like a URL
        # Save the content from the extracted URL
        m3u8_file = f"{content_id}.m3u8"
        save_content_from_url(extracted_data, m3u8_file)
        
        # Convert the M3U8 file to MP4
        mp4_file = f"{content_id}.mp4"
        convert_m3u8_to_mp4(m3u8_file, mp4_file)
    else:
        print(extracted_data)
else:
    print("Failed to extract content ID from URL.")
