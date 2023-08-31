import re
from bs4 import BeautifulSoup as BS
import pandas as pd
import string
from selenium import webdriver
from tabulate import tabulate

def get_total_page_number(soup: BS):
    header = soup.find(
    'div', class_="DirectoryResultsHeader").get_text()
    pattern = r"(\d+)\s*\)$"
    match = re.search(pattern, header)
    if match:
        final_number = match.group(1)
    return final_number

def read_page(kol: pd.DataFrame, soup: BS):

    divs = soup.find_all('div', class_="DirectoryResultsItem1")

    uncleaned_entry = []
    for i in range(len(divs)):
        uncleaned_entry.append(re.split("\n", divs[i].text))
        print(uncleaned_entry)

    for i in range(len(uncleaned_entry)):
        for j in range(len(uncleaned_entry[i])):
            uncleaned_entry[i][j] = uncleaned_entry[i][j].replace(" ", "")

    for i in range(len(uncleaned_entry)):
        temp = []
        for j in range(len(uncleaned_entry[i])):
            if uncleaned_entry[i][j] != '':
                temp.append(uncleaned_entry[i][j])
        temp = pd.DataFrame(temp).T
        kol = pd.concat([kol, temp], axis=0)
    return kol

def validate_email(email):
    # pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    pattern = r"[^@]+@[^@]+\.[^@]+"
    match = re.match(pattern, email)
    if match:
        return True
    else:
        return False

def is_blank_or_punctuation(s):
    return all(char in string.whitespace or char in string.punctuation for char in s)

def init_column(tags):
    lines = tags[0].text.splitlines()

    filtered_list = [s for s in lines if not is_blank_or_punctuation(s)]

    stripped = list(map(str.strip, filtered_list))
    return stripped


def extract_page(kol: pd.DataFrame, source: str):
    soup = BS(source, 'lxml')
    # members = response.css('#ctl00_CphBody_PnlResults > div').extract()
    members = soup.select("#ctl00_CphBody_PnlResults > div")
    # print(members)

    # parse the html, that is, take the raw html text (response.text) and break it into Python objects. The second argument is the html parser
    # soup = BS(response.text, 'html.parser')

    membersExtracted = []

    for (i, member) in enumerate(members):
        id = "ctl00_CphBody_DrResults_ctl" + \
            str(i).zfill(2) + "_ctl00_ctl00_Label"
        tags = soup.select("#" + id + " > div:nth-child(1)")
        row = {}
        stripped = init_column(tags)

        # print(filtered_list)
        for (x, line) in enumerate(stripped.copy()):
            # print(x)
            # print(line)
            if (x == 0):
                row['Name'] = line.strip()
                del stripped[x]

            if (x == 1):
                row['Institution'] = line.strip()
                stripped.remove(line)

            if (line.find('Phone: ') != -1):
                row['Phone'] = line.strip()
                stripped.remove(line)

            if (validate_email(line)):
                row['Email'] = line.strip()
                stripped.remove(line)

        address = ' '.join(stripped)
        row['Address'] = address.strip()

        tags = soup.select("#" + id + " > div:nth-child(2)")
        stripped = init_column(tags)
        # print(stripped)

        for (x, line) in enumerate(stripped):
            if (line.find('Primary Role: ') != -1):
                prefix = 'Primary Role: '
                index = line.index(prefix) + len(prefix)
                row['Primary Role'] = line[index:].strip()

            if (line.find('Practice Area:') != -1):
                row['Practice Area'] = stripped[x + 1]

            if (line.find('Expertise Type:') != -1):
                row['Expertise Type'] = stripped[x + 1]

            if (line.find('Patient Type:') != -1):
                row['Patient Type'] = stripped[x + 1]

                # print(re.search(r'Primary Role: (.*?);', line))

        membersExtracted.append(row)
    return membersExtracted

def extract_in_pandas(driver: webdriver.Chrome, kol: pd.DataFrame):
    list_of_rows = extract_page(kol, driver.page_source)
    print(list_of_rows)

    # Creating a new DataFrame from the list of dictionaries
    new_df = pd.DataFrame(list_of_rows)

    # Concatenating the new DataFrame with the existing DataFrame
    kol = pd.concat([kol, new_df], ignore_index=True)

    print(tabulate(kol, headers='keys', tablefmt='psql'))

    return kol

