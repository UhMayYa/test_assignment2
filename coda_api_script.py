import requests
from dotenv import load_dotenv
import os
import time 
#List out constants such as base URI, page id and doc id
BASE_URI = "https://coda.io/apis/v1/docs"
DOC_ID = "b28tqhh75p"
PAGE_ID = "canvas-ejAOsSah6d"


def coda_content_export():
    HEADERS = {'Authorization': f'Bearer {os.getenv('API_KEY')}'}
    uri = f'{BASE_URI}/{DOC_ID}/pages/{PAGE_ID}/export'
    payload = {
        'outputFormat': 'html'
    }
    try:
        req = requests.post(uri,headers=HEADERS,json=payload)
        req.raise_for_status()
        #Get the url containing the request id.
        poll_link = req.json()["href"]
        #The last part of the href url is the request id. Extract it and then return that value.
        page_req_id = poll_link.split('/')[-1]
        return page_req_id
    except requests.exceptions.HTTPError as req_e:
        print(f'HTTP error: {req_e}')
        #Code returned an HTTP error. Return 'HTTP error' as flag value.
        return 'HTTP error'

def coda_get_export_status(req_id):
    HEADERS = {'Authorization': f'Bearer {os.getenv('API_KEY')}'}
    uri = f'{BASE_URI}/{DOC_ID}/pages/{PAGE_ID}/export/{req_id}'
    try:
        while True:
            res = requests.get(uri,headers=HEADERS)
            res.raise_for_status()
            #We only get the download link if the value of 'status' in the JSON response is 'complete'. Check whether status has that value.
            #If its not complete, the while loop will send a request every 5 seconds via time.sleep(5).
            if res.json()["status"] != "complete":
                print("Export not complete. Waiting for 5 seconds before sending another request...")
            else:
                #'status' : 'complete'. Now get the download link from 'downloadLink' key in the JSON response. return the download link.
                coda_download_link = res.json()["downloadLink"]
                return coda_download_link
            time.sleep(5)
    except requests.exceptions.HTTPError as res_e:
        print(f'HTTP error: {res_e}')
        #HTTP error with getting status. return 'No download link' as a flag value.
        return 'No download link'


def main():
    load_dotenv()
    print("Beginning Content Export")
    request_id = coda_content_export()
    print("---------------------")
    #We will use 'HTTP error' as a flag value.If we do not get a HTTP error, run the coda_get_export_status function else print the error message.
    if request_id != 'HTTP error':
        print("Waiting for download link")
        download_link = coda_get_export_status(request_id)
        print("---------------------")
        #'No download link' will be used as flag value. If we do not get a HTTP error, display the download link else print the error message.
        if download_link != 'No download link':
            print('Download link received. Here is the download link:\n')
            print(download_link)
        else:
            print("Download link could not be received. There seems to be an error getting the download link.")
    else:
        print("Could not complete content export. An error has occured.")

if __name__ == "__main__":
    main()