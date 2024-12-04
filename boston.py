import csv
import requests
import concurrent.futures
from typing import List, Any
from bs4 import BeautifulSoup

def parse_race_results(html_content: str, year: int) -> List[List[str]]:
    """
    Parse HTML content of race results page.

    Args:
        html_content (str): HTML content of the race results page
        year (int): Year of the race

    Returns:
        List[List[str]]: Parsed results from the page
    """
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all list items with the specified class
    race_entries = soup.find_all('li', class_=['list-active list-group-item row', 'list-group-item row'])

    # Prepare results list
    results = []

    # Extract information from each entry
    for entry in race_entries:
        # Extract full name and location
        name_elem = entry.find('h4', class_='list-field type-fullname')
        full_name = name_elem.get_text(strip=True) if name_elem else 'N/A'

        # Extract overall place
        overall_place_elem = entry.find('div', class_='list-field type-place place-secondary hidden-xs numeric')
        overall_place = overall_place_elem.get_text(strip=True) if overall_place_elem else 'N/A'

        # Extract gender place
        gender_place_elem = entry.find('div', class_='list-field type-place place-primary numeric')
        gender_place = gender_place_elem.get_text(strip=True) if gender_place_elem else 'N/A'

        # Extract BIB number with more robust method
        bib_elem = entry.find('div', class_='list-field type-field', style='width: 45px')
        bib_number = 'N/A'
        if bib_elem:
            bib_label = bib_elem.find('div', class_='visible-xs-block visible-sm-block list-label')
            if bib_label:
                # Try different methods to extract BIB number
                bib_text = bib_label.find_next_sibling()
                if bib_text:
                    bib_number = bib_text.get_text(strip=True)
                elif bib_label.next_sibling:
                    bib_number = bib_label.next_sibling.strip()

        # Extract finish times
        finish_times = entry.find_all('div', class_='split list-field type-time')

        # Remove 'HALF', 'Finish Net', 'Finish Gun' prefixes and clean up times
        half_time = finish_times[0].get_text(strip=True).replace('HALF', '').strip() if finish_times else 'N/A'
        finish_net_time = finish_times[1].get_text(strip=True).replace('Finish Net', '').strip() if len(finish_times) > 1 else 'N/A'
        finish_gun_time = finish_times[2].get_text(strip=True).replace('Finish Gun', '').strip() if len(finish_times) > 2 else 'N/A'

        # Append to results with year
        results.append([
            year,
            full_name,
            overall_place,
            gender_place,
            bib_number,
            half_time,
            finish_net_time,
            finish_gun_time
        ])

    return results

def fetch_race_results(year: int, page_number: int) -> str:
    """
    Send a POST request to fetch race results for a specific page and year.

    Args:
        year (int): The year of the race
        page_number (int): The page number to fetch results for

    Returns:
        str: HTML content of the race results page
    """
    url = f"https://results.baa.org/{year}/"

    payload = {
        "page": page_number,
        "event": "R",
        "event_main_group": "runner",
        "num_results": 1000,
        "pid": "search",
        "search[age_class]": "%",
        "search[nation]": "%",
        "search_sort": "name"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {page_number} for year {year}: {e}")
        return ""

def determine_max_pages(year: int) -> int:
    """
    Determine the maximum number of pages for a given year by making an initial request.

    Args:
        year (int): The year to check

    Returns:
        int: Maximum number of pages (or a large default if cannot be determined)
    """
    try:
        # First page to determine if results exist and max pages
        first_page_html = fetch_race_results(year, 1)

        if not first_page_html:
            return 0

        soup = BeautifulSoup(first_page_html, 'html.parser')

        # Look for pagination elements
        pagination = soup.find('ul', class_='pagination')

        if not pagination:
            # If no pagination, check if there are results at all
            race_entries = soup.find_all('li', class_=['list-active list-group-item row', 'list-group-item row'])
            return 1 if race_entries else 0

        # Find the last page number in pagination
        page_links = pagination.find_all('a')
        if page_links:
            # Get the second to last link (last is usually 'next')
            last_page_link = page_links[-2] if len(page_links) > 1 else page_links[-1]
            max_pages = int(last_page_link.get_text(strip=True))
            return max_pages

        return 100  # Fallback large number if can't determine

    except Exception as e:
        print(f"Error determining max pages for {year}: {e}")
        return 100  # Safe fallback

def scrape_race_results(start_year: int = 2010, end_year: int = 2024) -> List[Any]:
    """
    Scrape race results across multiple years and pages using concurrent requests.

    Args:
        start_year (int, optional): First year to start scraping. Defaults to 2010.
        end_year (int, optional): Last year to scrape. Defaults to 2024.

    Returns:
        List[Any]: Parsed results from all pages
    """
    all_results = []

    # Create a list to track scraping jobs
    scraping_jobs = []

    # Discover pages for each year
    for year in range(start_year, end_year + 1):
        max_pages = determine_max_pages(year)
        print(f"Year {year}: {max_pages} pages detected")

        if max_pages == 0:
            print(f"No results found for year {year}")
            continue

        # Add scraping jobs for this year
        scraping_jobs.extend([(year, page) for page in range(1, max_pages + 1)])

    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Create futures for each scraping job
        futures = [executor.submit(fetch_and_parse_page, year, page) for year, page in scraping_jobs]

        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            page_results = future.result()
            if page_results:
                all_results.extend(page_results)

        return all_results

def fetch_and_parse_page(year: int, page: int) -> List[Any]:
    """
    Fetch and parse results for a specific year and page.

    Args:
        year (int): Year of the race
        page (int): Page number to fetch

    Returns:
        List[Any]: Parsed results for this page
    """
    html_content = fetch_race_results(year, page)
    if html_content:
        return parse_race_results(html_content, year)
    return []

def save_to_csv(results, output_file):
    """
    Save results to a CSV file.

    Args:
        results (List[List[str]]): Race results to save
        output_file (str): Path to output CSV file
    """
    # Define headers
    headers = [
        'Year',
        'Full Name',
        'Overall Place',
        'Gender Place',
        'BIB Number',
        'Half Marathon Time',
        'Finish Net Time',
        'Finish Gun Time'
    ]

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(results)

    print(f"Results saved to {output_file}")

def main():
    """
    Main function to execute the race results scraping.
    """
    try:
        # Scrape results from 2010 to 2024
        results = scrape_race_results(start_year=2010, end_year=2024)
        print(f"Total results scraped: {len(results)}")

        # Save results to CSV
        save_to_csv(results, "all_years_results_boston_2024.csv")

    except Exception as e:
        print(f"An error occurred: {e}")


main()