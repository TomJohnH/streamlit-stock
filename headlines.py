import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Set the URL of the New York Times website
url = "https://www.nytimes.com"

# Set the number of days for which you want to download the headlines
num_days = 5

# Loop through the days and download the headlines for each day
for i in range(num_days):
    # Calculate the date for the current day
    date = datetime.now() - timedelta(days=i)
    date_str = date.strftime("%Y/%m/%d")

    # Construct the URL for the current day
    day_url = f"{url}/{date_str}/"
    print(day_url)

    # Send a request to the URL and get the response
    response = requests.get(day_url)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the headlines on the page
    headlines = soup.find_all("h2")

    # Print the headlines for the current day
    print(f"Headlines for {date_str}:")
    for headline in headlines:
        print(headline.text)
