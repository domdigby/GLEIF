import pandas as pd
import pprint

import re
import csv
import os
import traceback
import requests


def get_lei(bic):
    # URL of the GLEIF API endpoint for lei records and filter by BIC
    url = f"https://api.gleif.org/api/v1/lei-records?filter[bic]={bic}"

    # Make the API call to GLEIF
    response = requests.get(url)

    # Check if the API call was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(data)
        # Extract the LEI from the response
        if not data['data']:
            print(f"No LEI data for BIC:  {bic}")

        else:
            first_element = data['data'][0]
            if 'attributes' in first_element:
                lei = first_element['attributes'].get('lei')
                print('LEI for BIC {}: {}'.format(bic, lei))

                # Create a pretty printer
                pp = pprint.PrettyPrinter()
                # Print the JSON data in a pretty print format
                pp.pprint(data['data'][0]['attributes'])

                # Get relationships
                get_relationships(lei)

                # Get all BICs fo this LEI
                get_bic(lei)
    else:
        print('Error retrieving LEI: {}'.format(response.status_code))


def validate_lei(lei):
    # URL of the GLEIF API endpoint for LEI validation
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}"

    try:

        # Make the API call to GLEIF
        response = requests.get(url)

        # Check if the API call was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the data from the response
            if not data['data']:
                print(f"No LEI data for:  {lei}")

            else:
                first_element = data['data']
                if 'attributes' in first_element:
                    entity = first_element['attributes'].get('entity')
                    print('{}: Legal name for LEI: {} :  {}'.format(entity['status'], lei, entity['legalName']['name']))

                    # Create a pretty printer
                    pp = pprint.PrettyPrinter()
                    # Print the JSON data in a pretty print format
                    pp.pprint(data['data']['attributes']['entity'])
        else:
            print('Error retrieving LEI: {}'.format(response.status_code))

    except Exception as ex:
        print(f"Exception occurred:\n{ex}")


def get_bic(lei):
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}"

    response = requests.get(url)
    # Check if the API call was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        bic = data['data']['attributes']['bic']

        print('BIC for LEI: {}: {}'.format(lei, bic))
    else:
        print('Error retrieving BIC: {}'.format(response.status_code))


def get_relationships(lei):
    # URL of the GLEIF API endpoint for accessing parent relationships
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}/direct-parent-relationship"

    # Make the API call to GLEIF
    response = requests.get(url)

    # Check if the API call was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(data)
        # Extract the LEI from the response
        if not data['data']:
            print(f"No relationship data for LEI:  {lei}")

        else:
            first_element = data['data']
            if 'relationships' in first_element:
                relationships = first_element['relationships']
                print('Relationships for LEI {}:\n'.format(lei, relationships))

                # Create a pretty printer
                pp = pprint.PrettyPrinter()
                # Print the JSON data in a pretty print format
                pp.pprint(relationships)
    else:
        print('Error retrieving relationships: {}'.format(response.status_code))


def find_lei_by_field(field, value):
    url = f"https://api.gleif.org/api/v1/fields/{field}?={value}"

    # Make the API call to GLEIF
    response = requests.get(url)

    # Check if the API call was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Create a pretty printer
        pp = pprint.PrettyPrinter()
        # Print the JSON data in a pretty print format
        pp.pprint(data)

    else:
        print('Error retrieving data for {}: {}'.format(field, response.status_code))


def get_all_leis(page_size=0, start_page=0, end_page=0):
    lei_name = []
    payload = {}
    headers = {'Accept': 'application/vnd.api+json'}

    try:

        if page_size == 0 or start_page == 0:
            url = "https://api.gleif.org/api/v1/lei-records"

            # Make the API call to GLEIF
            response = requests.get(url, headers=headers, data=payload)

            # Check if the API call was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Extract the LEIs into the LEI list
                for record in data['data']:
                    lei = record['attributes']['lei']
                    name = record['attributes']['entity']['legalName']['name']
                    lei_name.append([lei, name])

            else:
                print(f'Error retrieving data from page {start_page}: {response.status_code}\n{response.text}')

        else:

            while True:
                # Use the url to paginate through the pages based on the page size
                url = f"https://api.gleif.org/api/v1/lei-records?page[size]={page_size}&page[number]={start_page}"

                # Make the API call to GLEIF
                response = requests.get(url, headers=headers, data=payload)

                # Check if the API call was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()

                    # Extract the LEIs into the LEI list
                    for record in data['data']:
                        lei = record['attributes']['lei']
                        name = record['attributes']['entity']['legalName']['name']
                        lei_name.append([lei, name])

                    last_page = data['meta']['pagination']['lastPage']
                    # Check for more pages using min of end_page or last page
                    if end_page != 0:
                        end_page = min(end_page, last_page)
                    else:
                        end_page = last_page

                    if start_page == end_page:
                        break

                    # Increment the page number for the next url request
                    start_page += 1

                else:
                    # An error occurred, handle it appropriately
                    print(f'Error retrieving data from page {start_page}: {response.status_code}\n{response.text}')
                    break

        # Write the list to csv
        with open('lei-data.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Headers
            writer.writerow(['LEI', 'Legal Name'])

            # Write each row
            for row in lei_name:
                writer.writerow(row)

            print(f'LEI and name data written to file called: {csv_file.name}')

    except Exception as ex:
        print(f"An exception occurred:\n{ex}\n\n{traceback.format_exc()}")


def enrich_bic_lei_csv_map(csv_map_file, batch_size=100):
    """
    Takes the csv lei/bic mapping file and creates a richer csv file in the same file location
    which includes 6 additional fields about the LEI organisation - legal name, legal adr fields and status
    :param csv_map_file: standard csv file with 2 columns - lei and bic
    :param batch_size: integer to set the number of leis to get in each batch - to reduce the number of api calls
    (default is 100). Be wary of setting batch_size too high as it will exceed permitted url length and cause exception
    :return:
    """
    try:
        if os.path.exists(csv_map_file):
            # Get the path and filename to generate the path and new filename
            path = os.path.dirname(csv_map_file)
            enriched_filename = f"{os.path.splitext(os.path.basename(csv_map_file))[0]}_enriched.csv"
            enriched_filename = f"{path}\{enriched_filename}"

            # Load the existing CSV file of the mapped LEIs and BICs
            df = pd.read_csv(csv_map_file)

            if not df.empty:
                # Create the new columns for legal name and status
                df['LEGAL_NAME'] = pd.Series([None] * len(df))
                df['LEGAL_NAME'] = pd.Series([None] * len(df))
                df['LEGAL_ADR_CITY'] = pd.Series([None] * len(df))
                df['LEGAL_ADR_COUNTRY'] = pd.Series([None] * len(df))
                df['LEGAL_ADR_POSTALCODE'] = pd.Series([None] * len(df))
                df['STATUS'] = pd.Series([None] * len(df))

                # Get the LEI values into a list
                leis = df['LEI']
                lei_csv_parameter = []

                # Parse the lei list into csv strings based on batch_size
                for i in range(0, len(leis), batch_size):
                    # Get a batch of leis
                    leis_batch = leis[i:i+batch_size]
                    # Convert the batch of LEI values to a comma-separated string
                    lei_csv = ','.join(leis_batch)
                    # Add the comma-separated string to the list
                    lei_csv_parameter.append(lei_csv)

                for i in range(len(lei_csv_parameter)):
                    print(f"API call # {i+1}")  # Print statement only to show in the console that there is progress
                    # Pass each csv lei string to the API, returns a 2D list of enriched leis
                    enriched_leis = get_enriched_lei_data(lei_csv_parameter[i], batch_size)

                    lei_data = {}   # A dictionary to store the enriched fields with lei as key
                    for item in enriched_leis:
                        lei = item[0]       # Get the lei
                        fields_to_enrich = item[1:]  # Get the enriched data fields
                        lei_data[lei] = fields_to_enrich

                    # Join the enriched leis data dictionary to the dataframe of LEIs and BICs
                    for lei, fields_to_enrich in lei_data.items():
                        df.loc[df['LEI'] == lei, ['LEGAL_NAME', 'LEGAL_ADR_CITY', 'LEGAL_ADR_COUNTRY',
                                                  'LEGAL_ADR_POSTALCODE', 'STATUS']] = fields_to_enrich

                # Save the enriched dataframe to new csv
                df.to_csv(enriched_filename, encoding='utf-16', index=False)
                print(f"Enriched LEI data saved to CSV file: {enriched_filename}")
    except Exception as ex:
        print(f"An exception occurred:\n{ex}\n\n{traceback.format_exc()}")


def get_enriched_lei_data(lei_csv_param, batch_size):
    """
    Gets
    :param lei_csv_param:
    :param batch_size:
    :return:
    """
    lei_enriched_data = []

    try:

        # URL of the GLEIF API endpoint
        url = f"https://api.gleif.org/api/v1/lei-records?page[size]={batch_size}&filter[lei]={lei_csv_param}"

        # Make the API call to GLEIF
        response = requests.get(url)

        # Check if the API call was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the data from the response
            if not data['data'][0]:
                return 'No LEI data found'

            else:
                for item in data['data']:
                    # Get the LEI
                    if 'attributes' in item:
                        lei = item['attributes'].get('lei')
                        legal_name = item['attributes']['entity']['legalName']['name']
                        legal_adr_city = item['attributes']['entity']['legalAddress']['city']
                        legal_adr_ctry = item['attributes']['entity']['legalAddress']['country']
                        legal_adr_postalcode = item['attributes']['entity']['legalAddress']['postalCode']
                        status = item['attributes']['entity']['status']
                        lei_enriched_data.append([lei, legal_name, legal_adr_city, legal_adr_ctry,
                                                  legal_adr_postalcode, status])

            return lei_enriched_data

        else:
            return 'Error retrieving data: {}'.format(response.status_code)

    except Exception as ex:
        return f'Exception occurred:  {ex}\n\n{traceback.format_exc()}'


def is_lei_valid(lei) -> bool:
    """
    Checks if the lei is valid, both format and the checksum. Case-sensitive (ensure upper case).
    1. Take the first 18 chars of the 20 chars string into lei_to_check
    2. Take the last 2 chars of the 20 chars into the original_checksum
    3. For the lei_to_check, convert all letters to number equivalent (ordinal of char minus 55)
    4. Append two zeros to end of lei_to_check
    5. Concatenate all numbers in lei_to_check into one number (not sum)
    6. Euclidean divide the number (divide by 97, aka MOD97) and save the remainder
    7. Subtract the remainder from 98 - the result is the calculated checksum
    8. Compare calculated checksum to the original checksum
    9. If the same, return is_valid = True, else is_valid is False
    :param lei: string of the lei to validate
    :return: bool
    """
    is_valid = False    # Set default return value
    mod = 97    # Set divider for the MOD97/Euclidean divider
    valid_pattern = r"^[0-9A-Z]{18}[0-9]{2}$"  # Specify the regex for a valid LEI format

    try:
        # Check correct format as pregex pattern above, i.e. 20 chars/digits, only 0-9A-Z and last 2 chars are numbers
        matched = re.search(valid_pattern, lei)
        if bool(matched):
            # Validate the checksum
            # Parse the lei to the first 18 chars and the last 2 chars (checksum)
            lei_to_check = lei[:18]
            original_checksum = int(lei[18:])

            # 1. letter conversion to numbers
            lei_chars = []
            for char in lei_to_check:
                # If the char is a number, add to the array
                if char.isdigit():
                    lei_chars.append(int(char))
                # Convert the letter to its ordinal number minus 55
                else:
                    lei_chars.append(ord(char) - 55)

            # Append two zeros
            lei_chars.append(0)
            lei_chars.append(0)

            lei_chars = [str(x) for x in lei_chars]
            big_number = "".join(lei_chars)
            quotient, remainder = divmod(int(big_number), mod)
            calc_checksum = 98 - remainder
            if calc_checksum == original_checksum:
                is_valid = True

        return is_valid

    except Exception as ex:
        print(f"Exception occurred: {ex}")
        return is_valid


if __name__ == '__main__':
    enrich_bic_lei_csv_map(r'C:\Users\domdi\Documents\My Work Files\SWIFT\LEI\lei-bic-20231124T000000.csv',
                           batch_size=100)

    enrich_isin_lei_csv_map(r'C:\Users\domdi\Documents\My Work Files\SWIFT\LEI\lei-isin-20231205T080955.csv',
                           batch_size=100)

    #print(f"LEI validation result: {is_lei_valid('YMUU1WGHJKORF9E36I98')}")

    #get_lei('LOYDGB22TSY')

    #get_fields_for_filtering()

    #find_lei_by_field('LEIREC_LEGAL_NAME', 'ΛΟΥΚΑΣ ΜΑΝΑΙΟΣ ΙΔΙΩΤΙΚΟ ΙΑΤΡΕΙΟ ΜΟΝΟΠΡΟΣΩΠΗ ΙΑΤΡΙΚΗ ')

    #validate_lei('YMUU1WGHJKORF9E36I98')

    #get_bic('549300EI2QZDOKF0UR93')

    #get_all_leis(page_size=10, start_page=1)
