import re
from bs4 import BeautifulSoup as BS
import pandas as pd

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