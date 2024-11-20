import json
from re import sub
import subprocess
from time import sleep
import os
from sys import argv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import requests

# Create a function to filter and find .m3u8 links
def find_m3u8(logs):
    for log_entry in logs:
        # Load the log as JSON
        try:
            log = json.loads(log_entry["message"])

            # Check for 'Network.requestWillBeSent' or 'Network.responseReceived'
            if "Network.requestWillBeSent" in log["message"]["method"]:
                # Extract the URL from request logs
                url = log["message"]["params"]["request"]["url"]
                if ".m3u8" in url or ".m3u" in url:
                    return url

            elif "Network.responseReceived" in log["message"]["method"]:
                # Extract the URL from response logs
                url = log["message"]["params"]["response"]["url"]
                if ".m3u8" in url:
                    return url
        except (KeyError, json.JSONDecodeError):
            # If there's a problem with key access or JSON parsing, just continue
            pass

    print("No .m3u8 URL found")
    return None




# Setup Selenium to work with the mitmproxy proxy
def setup_selenium():
    options = Options()
    # Enable Performance Logging
    options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
    # Set up the Chrome WebDriver
    service = Service(executable_path=rf"C:\Users\{os.getlogin()}\Downloads\chromedriver-win64\chromedriver.exe")  # Replace with the path to your chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    return driver


# Main logic to scrape the website
def scrape_website(url):
    sleep(3)
    # Set up Selenium
    driver = setup_selenium()
    try:
        # Open the website
        driver.get(url)
        # Wait for the page to load (you can adjust this)
        sleep(3)
        # Capture network traffic logs
        logs = driver.get_log("performance")
        # Find the m3u8 link in the logs




        soup = BeautifulSoup(driver.page_source, "html.parser")
        video_tags = soup.find_all("video")
        filnamn = r"D:\SteamLibrary\steamapps\junk\newned\_"+ soup.find("title").get_text().strip().replace(
            " ", "").replace("|", "")[:20] + ".mp4"
        filnamn = sub(r'[<>:"|?*] ', '', filnamn).replace("?", "")
        if not video_tags:
            video_tags = soup.find_all("src")
            if not video_tags:
                video_tags = soup.find_all("source")

        if len(video_tags) > 0:
            for index, video_tag in enumerate(video_tags, start=1):

                # Extract the 'src' attribute from each video tag
                video_source = video_tag.get("src")
                if video_source and video_source[0] == "b":
                    print("Laddar ned bloblink")
                    m3u8_link = find_m3u8(logs)
                    convertToMp4(m3u8_link, filnamn)
                    os.startfile(os.path.dirname(filnamn))
                    break


                if video_source:
                    print(f"Video {index} source:", video_source)


                    download_file(video_source,filnamn)
                    os.startfile(os.path.dirname(filnamn))

                else:
                    video_source= video_tag.find("source").get("src")
                    if video_source and video_source[0] == "b":
                        print("blob link")
                        m3u8_link = find_m3u8(logs)
                        convertToMp4(m3u8_link, filnamn)
                        os.startfile(os.path.dirname(filnamn))
                        break


                    if video_source:
                        print(f"Video {index} source:", video_source)

                        download_file(video_source, filnamn)
                        os.startfile(os.path.dirname(filnamn))


            return

    finally:
        driver.quit()

def download_file(url,filnamn):

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filnamn, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"File successfully downloaded: {filnamn}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


def convertToMp4(link, filnamn):
    if link is None:
        return

    command = f'ffmpeg -i "{link}" -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {filnamn}'
    print(command)
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Open the process and stream the output live to the console
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Stream the output of the command in real-time
    for line in process.stdout:
        print(line, end="")  # Print each line of ffmpeg output to the console

    process.wait()  # Wait for the process to finish

    # Check if the process was successful
    if process.returncode == 0:
        print("Conversion successful.")
    else:
        print(f"Error occurred during conversion (code {process.returncode})")


# Example usage
if __name__ == "__main__":
    if len(argv) < 2:
        url_to_scrape = input("link: ")  # Replace with the target URL
    else:
        url_to_scrape = argv[1]
  # // m3eu = scrape_website(url_to_scrape)
    #if m3eu != None:
    scrape_website(url_to_scrape)
