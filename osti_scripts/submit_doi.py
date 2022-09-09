import argparse
import pandas as pd
import ostiapi
import xml.etree.ElementTree as ET
import re
from dict2xml import dict2xml
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("account", help="Enter account name for submitting records")
parser.add_argument("password", help="Enter account password")
parser.add_argument("user_data", help="Enter file path for User Super Summary")
parser.add_argument("url", help="Enter URL for the static Narrative to receive the DOI")
parser.add_argument(
    "--reserve", help="Enter True to only reserve, not submit", action="store_true"
)
parser.add_argument(
    "--test_mode", help="Enter True to send record in testmode", action="store_true"
)
parser.add_argument(
    "--update_record", help="Enter OSTI record ID to update an existing record"
)

args = parser.parse_args()
if args.test_mode:
    print("Operating in testmode")
    ostiapi.testmode()
if args.update_record:
    osti_id = args.update_record
    print("Updating record {}".format(osti_id))

print("account", args.account)
print("password", args.password)
print("User data file", args.user_data)
print("SN URL", args.url)

usersummary = pd.read_excel(args.user_data)
usersummary = usersummary.fillna("blank")


def gen_record(url):
    """
    Read through a static Narrative to find all the information required for DOI submission, and prompt for anything missing.
    """
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    ## Constants
    site_code = "KBASE (U.S. Department of Energy Systems Biology Knowledgebase)"
    dataset_type = "GD"
    BER = "USDOE Office of Science (SC), Biological and Environmental Research (BER)"
    ## From static Narrative
    wsid = url[url.find("/n/") + 3 : url.rfind("/", 0, -1)]
    version = url[url.rfind("/", 0, -1) + 1 : -1]
    infix = "{}.{}".format(wsid, version)
    title = soup.find("title").text
    author_list = []
    research_orgs = []
    keywords = ""
    contract_nos = ""
    abstract = ""
    for d in soup.find_all("div"):
        if d.get("class") == ["kb-author-list"]:
            for a in d.find_all("a"):
                author_dict = {}
                # User super summary info pulled up separately in case I need to batch these in the future
                author_frame = usersummary.loc[usersummary["display_name"] == a.text]
                # If they only have first name and last name in their profile
                if len(a.text.split(" ")) == 2:
                    author_dict["last_name"] = a.text.split(" ")[1]
                    author_dict["first_name"] = a.text.split(" ")[0]
                # If they have middle name or compound last name or only a single name in their profile
                else:
                    print("Enter name for: {}".format(a.text))
                    author_dict["last_name"] = input("Family name: ")
                    author_dict["first_name"] = input("Given name: ")
                    author_dict["middle_name"] = input("Middle name: ")
                if author_frame["email"].to_list()[0] != "blank":
                    author_dict["private_email"] = author_frame["email"].to_list()[0]
                if author_frame["orcid"].to_list()[0] != "blank":
                    author_dict["orcid_id"] = author_frame["orcid"].to_list()[0]
                if author_frame["institution"].to_list()[0] != "blank":
                    author_dict["affiliation_name"] = author_frame[
                        "institution"
                    ].to_list()[0]
                    if author_frame["institution"].to_list()[0] not in research_orgs:
                        research_orgs.append(author_frame["institution"].to_list()[0])
                author_list.append(author_dict)
        if d.get("class") == ["branding"]:
            datestring = d.text.strip("\n")
            datestring = datestring[datestring.find(" ") + 1 :]
            pub_date = datetime.datetime.strptime(datestring, "%B %d, %Y").strftime(
                "%m/%d/%Y"
            )
        # User defined/custom classes
        if d.get("class") == ["user-abstract"]:
            abstract = d.text
    for m in soup.find_all("meta"):
        if m.get("name") == "user-keywords":
            keywords = m.get("content")
        if m.get("name") == "user-doi-funding":
            contract_nos = m.get("content")

    research_org = ""
    for ro in research_orgs:
        research_org += ro + ";"
    research_org = research_org[:-1]
    doi_list = []
    # Finding all the DOIs with regex. App DOIs are already in <li>s, so asking users to do likewise
    for l in soup.find_all("li"):
        if l.text.find("doi") != -1:
            doi = re.search("10.[0-9]*/\S*", l.text.lower())[0].strip(".")
            if doi not in doi_list:
                doi_list.append(doi)
    related_identifiers = [
        {
            "related_identifier": x,
            "relation_type": "Cites",
            "related_identifier_type": "DOI",
        }
        for x in doi_list
    ]

    # Manually entering abstract, keywords, contract numbers if they didn't include in HTML
    if abstract == "":
        abstract = input("No abstract found. Enter manual value: ")
    if contract_nos == "":
        contract_nos = input("No contract numbers found. Enter manual value: ")
    if keywords == "":
        keywords = input("No keywords found. Enter manual value: ")
    if contract_nos == "":
        contract_nos = "N/A"
    # Building record dict
    record = {
        "title": title,
        "dataset_type": dataset_type,
        "authors": author_list,
        "publication_date": pub_date,
        "site_url": url,
        "contract_nos": contract_nos,
        "sponsor_org": BER,
        "keyword": keywords,
        "description": abstract,
        "research_org": research_org,
        "doi_infix": infix,
        "related_identifiers": related_identifiers,
    }
    return record


record = gen_record(args.url)
if args.reserve:
    submit = ostiapi.reserve(record, args.account, args.password)
else:
    submit = ostiapi.post(record, args.account, args.password)
# Save the record with DOI from OSTI's as a backup
fname = record["record"]["doi"].replace(".", "_").replace("/", "-")
xml = dict2xml(submit)
with open("{}.xml".format(fname), "w") as f:
    f.write(xml)
