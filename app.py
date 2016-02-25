#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Usage: 
python app.py <user_id>
OR
python app.py <user_id> <bool>
The bool decides if you want the meta data saved as well as the video. Default is False

"""
import json
import os
import requests
import sys
import concurrent.futures
import csv

def crawl(user_id,  details, items=[]):
  url  = 'https://vine.co/api/timelines/users/' + user_id + '?size=99999'
  media = json.loads(requests.get(url).text)
  
  try:
    count = 0
    for item in media['data']['records']:
      items.append(item['videoUrl'])

      #this section writes text files with post meta data
      if details:

        #same dir scheme as vid download function
        if not os.path.exists('./'+user_id):
              os.makedirs('./'+user_id)
        #this is the file/video name      
        base_name = items[-1].split('/')[-1].split('?')[0]

        with open('./'+user_id+'/'+base_name+'.txt', 'w') as file:
              print 'Writing meta info for ' + base_name + '...'
              
              #it's a dict so writing as csv
              filewrite = csv.writer(file)
              for key, val in item.items():
                filewrite.writerow([key, val])
       # end of section

  except Exception as e:
    print 'Error getting vines' + e
  return items
  
def download(url, save_dir='./'):
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
  
  base_name = url.split('/')[-1].split('?')[0]
  file_path = os.path.join(save_dir, base_name)
  
  with open(file_path, 'wb') as file:
    print 'Downloading ' + base_name
    bytes = requests.get(url).content
    file.write(bytes)
    
if __name__ == '__main__':
  user_id = sys.argv[1]
  
  #checking to see if bool argument was added
  #defaults to false if missing
  try:
    details = sys.argv[2]
  except:
    details = False
  
  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_url = dict( (executor.submit(download, url, './' + user_id), url) for url in crawl(user_id, details) )

    for future in concurrent.futures.as_completed(future_to_url):
      url = future_to_url[future]
      
      if future.exception() is not None:
        print '%r generated an exception: %s' % (url, future.exception())

