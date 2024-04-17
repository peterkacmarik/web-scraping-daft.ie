import aiohttp  # Import the aiohttp library for asynchronous HTTP requests
import time  # Import the time library for timing the operation
import pandas as pd  # Import pandas for data manipulation and analysis
import asyncio  # Import the asyncio library for asynchronous programming
import json  # Import the json library for JSON encoding and decoding
import logging  # Import the logging library for logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Define the fetch coroutine to retrieve data from a given page
async def fetch(session, current_page):
    """
    Asynchronously fetches data from a given API endpoint.

    Args:
        session (aiohttp.ClientSession): The session to use for making the HTTP request.
        current_page (int): The current page number to fetch data from.

    Returns:
        Union[List[Dict[str, Union[str, int]]], bool, None]: A list of dictionaries containing the details of the listings on the current page, or False if no listings are found, or None if an error occurs.

    Raises:
        Exception: If an error occurs during the request or processing of the data.
    """
    # The URL of the API endpoint
    url = "https://gateway.daft.ie/old/v1/listings"

    # Payload to be sent with the POST request
    payload = json.dumps({
    "section": "residential-for-sale",
    "filters": [
        {
        "name": "adState",
        "values": [
            "published"
        ]
        }
    ],
    "andFilters": [],
    "ranges": [],
    "paging": {
        "from": str(current_page),
        "pageSize": "20"
    },
    "geoFilter": {},
    "terms": ""
    })
    # Headers to be sent with the POST request
    headers = {
    'accept': 'application/json',
    'accept-language': 'sk-SK,sk;q=0.9,cs;q=0.8,en-US;q=0.7,en;q=0.6',
    'brand': 'daft',
    'cache-control': 'no-cache, no-store',
    'content-type': 'application/json',
    'expires': '0',
    'origin': 'https://www.daft.ie',
    'platform': 'web',
    'pragma': 'no-cache',
    'referer': 'https://www.daft.ie/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        # Perform the POST request to the API endpoint
        async with session.post(url, headers=headers, data=payload) as response:
            # Check if the response status is not 200 (OK)
            if response.status != 200:
                logging.error(f"Error fetching page {url}: {response.status}")
                return None
            else:
                # Parse the JSON response
                json_data = await response.json()
                start_point = json_data['listings']
                page_detail = []
            
                # If listings are found, process each listing
                if start_point:
                    for item in start_point:
                        # Extract relevant data from each listing
                        list_data = {
                            'ID': item['listing']['id'],
                            'title': item.get('listing').get('title'),
                            'price': item.get('listing').get('price'),
                            'floor_area': item.get('listing').get('floorArea'),
                            'num_bathrooms': item.get('listing').get('numBathrooms'),
                            'num_bedrooms': item.get('listing').get('numBedrooms'),
                            'detail_url': 'https://www.daft.ie' + item.get('listing').get('seoFriendlyPath'),
                            'sale_type': item.get('listing').get('saleType')[0],
                            'property_type': item.get('listing').get('propertyType'),
                            'property_size': item.get('listing').get('propertySize'),
                            'category': item.get('listing').get('category'),
                            # seller details
                            'seller_id': item.get('listing').get('seller').get('sellerId'),
                            'seller_name': item.get('listing').get('seller').get('name'),
                            'seller_phone': item.get('listing').get('seller').get('phone'),
                            'alternative_phone': item.get('listing').get('seller').get('alternativePhone'),
                            'branch_name': item.get('listing').get('seller').get('branch'),
                            'seller_type': item.get('listing').get('seller').get('sellerType'),
                        }
                        # Add the extracted data to the page_detail list
                        page_detail.append(list_data)
                    # Return the list of details for the current page
                    return page_detail
                else:
                    # Return False if no listings are found
                    return False
    
    except Exception as e:
        # Print the exception if any occurs during the request or processing
        logging.error(f"An error occurred while fetching or processing data: {e}")
        # Return None to indicate that an error occurred
        return None


# Define an asynchronous function called 'main'
async def main():
    """
    An asynchronous function that handles the scraping process of multiple pages.
    It initializes necessary variables, fetches page details, processes and stores the data,
    and logs information about the operation's duration.
    """
    # Create an asynchronous context manager that will handle the session
    async with aiohttp.ClientSession() as session:
        detail_task = []  # Initialize an empty list to store page fetch results
        current_page = 0  # Set the starting page number
        proced = True  # Initialize a flag to control the while loop
        
        start_time = time.time()  # Record the start time of the operation
        # Continue looping as long as 'proced' is True
        logging.info(f"Scraping process started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while proced:
            try:
                # Print the current page number being scraped
                logging.info(f'Currently scraping page: {current_page}')
                
                # Asynchronously fetch the details of the current page
                page_fetched = await fetch(session, current_page)
                
                # If 'page_fetched' is empty or None, stop the loop
                if not page_fetched:
                    logging.warning(f"No details found on page {current_page}, skipping.")
                    proced = False
                else:
                    # If details are found, extend the 'detail_task' list with the results
                    detail_task.extend(page_fetched)
                    # Increment the current page number by 20
                    current_page += 20
                    
            except aiohttp.ClientError as e:
                # Handle client-related network errors
                logging.error(f"Network-related error occurred: {e}")
                proced = False  # Stop the loop or consider a retry logic
            
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                proced = False  # Stop the loop or handle the exception as needed
            
        try:
            df = pd.DataFrame(detail_task)
            # df.to_csv('scrape daft/daft_output_data.csv', index=False, encoding='utf-8-sig')
            logging.info(f"Successfully created DataFrame with scraped data.")
            print(df)
        except Exception as e:
            logging.error(f"Error creating DataFrame: {e}")
        
        # Get the current time after the completion of the operation
        end_time = time.time()

        # Log information about the duration of the operation in seconds, rounded to 2 decimal places
        logging.info(f"This operation took: {end_time - start_time:.2f} seconds")

        # Calculate the total duration of the operation in seconds
        duration_seconds = end_time - start_time

        # Convert the total duration to minutes and seconds
        minutes, seconds = divmod(duration_seconds, 60)

        # Log information about the duration of the operation in minutes and seconds, rounded to the nearest integer
        logging.info(f"This operation took: {int(minutes)} minutes {int(seconds)} seconds")

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
