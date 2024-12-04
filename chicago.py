import csv
import requests
from typing import List, Any
from bs4 import BeautifulSoup
import re

def parse_race_results(html_content: str, year: int) -> List[List[str]]:
    """
    Parse HTML content of race results page from Marathon Guide.

    Args:
        html_content (str): HTML content of the race results page
        year (int): Year of the race

    Returns:
        List[List[str]]: Parsed results from the page
    """
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the results table
    results_table = soup.find('table', class_='colordataTable')

    # Prepare results list
    results = []

    # Skip the header row and iterate through data rows
    if results_table:
        data_rows = results_table.find_all('tr', recursive=False)[1:]

        for row in data_rows:
            # Skip rows that don't have the expected number of columns
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract name and sex/age
            name_col = cols[0].get_text(strip=True)

            # Use regex to extract name and sex
            name_match = re.match(r'^(.?)\s\(([MF])\)', name_col)
            if name_match:
                full_name = name_match.group(1).strip()
                sex = name_match.group(2)
            else:
                full_name = name_col
                sex = 'N/A'

            # Extract times and places
            finish_time = cols[1].get_text(strip=True)
            overall_place = cols[2].get_text(strip=True)

            # Parse sex/div place
            sex_div_place = cols[3].get_text(strip=True)
            sex_place, div_place = sex_div_place.split('/') if '/' in sex_div_place else (sex_div_place, 'N/A')

            # Extract other details
            division = cols[4].get_text(strip=True)
            country = cols[5].get_text(strip=True)
            bq_status = cols[6].get_text(strip=True)

            # Append to results
            results.append([
                year,
                full_name,
                sex,
                finish_time,
                overall_place,
                sex_place.strip(),
                div_place.strip(),
                division,
                country,
                bq_status
            ])

    return results

def fetch_race_results(race_id: str, begin: int, end: int, max: int) -> str:
    """
    Send a GET request to fetch race results for a specific range.

    Args:
        race_id (str): Race identifier from Marathon Guide
        begin (int): Starting result number
        end (int): Ending result number

    Returns:
        str: HTML content of the race results page
    """
    url = "https://www.marathonguide.com/results/browse.cfm"
    #https://www.marathonguide.com/results/browse.cfm?RL=1&MIDD=16100425&Gen=B&Begin=1&End=100&Max=36553
    params = {
        'RL': '1',
        'MIDD': race_id,
        'Gen': 'B',
        'Begin': begin,
        'End': end,
        'Max': max
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Referer': f'https://www.marathonguide.com/results/browse.cfm?RL=1&MIDD={race_id}&Gen=B&Begin=1&End=100&Max={max}'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching results: {e}")
        return ""

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
        'Sex',
        'Finish Time',
        'Overall Place',
        'Sex Place',
        'Division Place',
        'Division',
        'Country',
        'BQ Status'
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
        # Example race ID - you'll need to replace this with the actual race ID
        data = \
            [(67241013, 52129, 2024), (67231008, 48574, 2023), (67221009, 39420, 2022), (472231105, 51295, 2021),
             (472241103, 55527, 2024)]
        # [(16080413, 34212, 2008), (16070422, 35667, 2007), (16060423, 32924, 2006), (16050417, 35261, 2005),
        #       (16040418, 31659, 2004), (16030413, 32167, 2003), (16020414, 32536, 2002), (16010422, 30066, 2001),
        #       (16240421, 53790, 2024)]

        for (race_id, max, year)  in data:

            # Collect results
            all_results = []

            # Fetch results in batches of 100
            for begin in range(1, max, 100):
                end = begin + 99
                html_content = fetch_race_results(race_id, begin, end, max)

                if not html_content:
                    break

                # Parse results for the current year (2024 as an example)
                page_results = parse_race_results(html_content, year)

                if not page_results:
                    break

                all_results.extend(page_results)
                print(f"Fetched results {begin} to {end}")

            print(f"Total results scraped: {len(all_results)}")

            # Save results to CSV
            save_to_csv(all_results, f"marathon_results_{year}.csv")

    except Exception as e:
        print(f"An error occurred: {e}")

main()