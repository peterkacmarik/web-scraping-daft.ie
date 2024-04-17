**Daft.ie Scraper**

This Python script utilizes asynchronous programming to scrape property listings data from Daft.ie. It extracts details like title, price, floor area, number of bedrooms and bathrooms, and seller information.

**Requirements:**

* Python 3.6 or later
* aiohttp library (`pip install aiohttp`)
* asyncio library (included in Python 3.5+)
* pandas library (`pip install pandas`)
* json library (included in Python standard library)
* logging library (included in Python standard library)

**Installation:**

If you don't have the required libraries installed, you can use pip:

```bash
pip install aiohttp
```

**Usage:**

1. Clone or download this repository.
2. Open a terminal or command prompt and navigate to the directory containing the script (`daft_scraper.py`).
3. Run the script:

```bash
python daft_scraper.py
```

**Explanation:**

The script performs the following steps:

* **Configures logging:** Sets up detailed logging to provide insights into the scraping process.
* **Defines functions:**
    * `fetch(session, current_page)`: Fetches data from a specific page of Daft.ie's listings API asynchronously.
    * `main()`: Orchestrates the entire scraping process, including creating sessions, making asynchronous requests, handling errors, and storing scraped data.
* **Main function execution:**
    * Creates an `aiohttp` client session for making HTTP requests.
    * Initializes variables like `detail_task` (list to store page results), `current_page`, and a loop control flag (`proced`).
    * Records the start time of the operation using `time.time()`.
    * Enters a loop that continues as long as `proced` is True:
        * Fetches details for the current page using `fetch`.
        * Processes the fetched data:
            * If no details are found, stops the loop.
            * If details are found, adds them to the `detail_task` list.
            * Increments the `current_page` for the next iteration.
    * Converts the scraped data into a Pandas DataFrame (optional).
    * Logs information about the scraping duration in seconds and minutes.

**Customization:**

* You can adjust the starting page number (`current_page = 0`) in the `main` function.
* Modify the number of listings fetched per page in the `fetch` function's payload (`"pageSize": "20"`).
* Consider implementing error handling strategies like retries or exponential backoff for network errors.

**Note:**

This script is for educational purposes only. Be mindful of Daft.ie's terms of service when scraping their website.
