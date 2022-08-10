import ostiapi
import pandas as pd
from datetime import datetime
import argparse
today = datetime.now()
parser = argparse.ArgumentParser()
parser.add_argument("account", help="Enter account name for submitting records")
parser.add_argument("password",help="Enter account password")
args = parser.parse_args()
account = args.account
pw = args.password
records = ostiapi.get({'site_input_code':'KBASE','rows':500},account,pw)['record']
simplified_records = {}
for i in records:
    title = i['title']
    doi = i['doi']
    status = i['@status']
    try:
        url = i['site_url']
    except:
        url = 'None'
    simplified_records[doi]=[title,url,status]
df = pd.DataFrame.from_dict(simplified_records,orient='index',columns=['Title','URL','Status'])
df.index.name='DOI'
df.to_csv('KBase_dois_{}_{}_{}.csv'.format(today.year,today.month,today.day))