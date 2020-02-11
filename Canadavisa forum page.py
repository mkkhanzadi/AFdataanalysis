#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import bs4
from bs4 import BeautifulSoup as bs
import csv
import re
import numpy as np
import pandas as pd
import nltk
import random
# from https://github.com/pandas-dev/pandas/issues/22610
import csv


# In[3]:


#defining the url and using the ureq to read the website in html. This can be checked by print(canadavisa)


# In[4]:


canadavisa_url = 'https://www.canadavisa.com/canada-immigration-discussion-board/'
canadavisa = requests.get(canadavisa_url).text


# In[5]:


#all topics are in tag 'h3' - using bs to find all data in h3 - Topic tag has changed from nodeTitle to node-title


# In[6]:


soup = bs(canadavisa, 'html.parser')

topics = soup.find_all('h3', {'class':'node-title'})
topic_titles = list(map(lambda h: h.text.strip(), topics))
topic_titles_and_links = dict(map(lambda h: (h.text.strip(), h.find('a') ['href']), topics))
print(topic_titles_and_links)


# LM's example of randomised topic selection. Uses [sampling without replacement](https://web.ma.utexas.edu/users/parker/sampling/repl.htm) to ensure the same topic is not selected twice .

# In[7]:


topic_titles_and_links


# In[8]:


with open('titles_and_links.csv', mode='w') as csv_file:
    fieldnames = ['title', 'link']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for key, value in topic_titles_and_links.items():
        writer.writerow({'title': key, 'link': value})


# In[9]:


def sample_links(titles_and_links, titles, sample_size):
    num_links = len(titles_and_links)
    sample_titles_and_links = {}
    ids = []

    # This code creates an array of topic ids that are random and unique
    if sample_size < num_links:
        for i in range(0, sample_size):
            x = -1
            # 
            while not(x in ids):
                x = random.randint(0, num_links)
                ids.append(x)
            print(i, x)

    # Now create the topic sample
    if len(ids) > 0:
        for i in ids:
            key = titles[i]
            sample_titles_and_links[key] = titles_and_links[key]
        
    return sample_titles_and_links
    


# In[10]:


def data_frame(message_ids, links, date_contents, username_contents, message_contents, countries, likes, topic_contents, thread_contents):
    base_data_frame = pd.DataFrame({ "ID": message_ids, 
                                "Link": links, 
                                "Date": date_contents,
                                "Username": username_contents, 
                                "Message": message_contents, 
                                "Country": countries, 
                                "Like": likes, 
                                "Topic": topic_contents, 
                                "Thread": thread_contents})
    return base_data_frame


# In[11]:


def write_csv(file_name, base_data_frame):
    with open(file_name, "w", errors='surrogatepass') as _file:
        writer = csv.writer(_file)
        #writer.writerow(row)
        writer.writerow(base_data_frame.columns.values)
        for index, row in base_data_frame.iterrows():
            writer.writerow(row)


# In[16]:


SAMPLE_SIZE = 2


# In[17]:


topic_sample_titles_and_links = sample_links(topic_titles_and_links, topic_titles, SAMPLE_SIZE)
print(topic_sample_titles_and_links)


# In[18]:


print(topic_sample_titles_and_links)


# In[ ]:



message_ids = list()
links = list()
date_contents = list()
username_contents = list()
message_contents = list()
countries = list()
likes = list()
topic_contents = list()
thread_contents = list()
counter = 0
thread_counter = 0
thread_page_counter = 0

# Full data set
#for key, value in topic_titles_and_links.items():
# Random sample
for key, value in topic_sample_titles_and_links.items():
    counter = counter + 1
    if counter == 1:
        print('inside loop', key, value)
        continue

# For debugging only - COMMENT OUT LATER
   # if counter > 2:
    #    break
    topic_url = 'https://www.canadavisa.com' + value 
    topic_title = key

    print("Processing ", topic_title)
    try:
        topic_content = bs(requests.get(topic_url).text, 'html.parser')
        # Count number of page nav elements
        page_nav_count = len(topic_content.select('li.pageNav-page'))
        tc_last_page = int(topic_content.select('li.pageNav-page')[page_nav_count - 1].text)
        print("Count of topic pages: " + str(tc_last_page))
    except Exception as i:
        print(i)
    for x in range(1, tc_last_page + 1):
# For debugging only - COMMENT OUT LATER
      #  if x > 3:
       #     break
        topic_url = 'https://www.canadavisa.com' + value
        if x > 1:
            topic_url = topic_url + 'page-'+ str(x)
        print("TOPIC URL: " + topic_url)
        topic_content = bs(requests.get(topic_url).text, 'html.parser')
        threads = topic_content.find_all('div', {'class':'structItem-title'})
        threads_titles = list(map(lambda subtopic: subtopic.find('a').text.strip(), threads))
        thread_titles_and_links = dict(map(lambda subtopic: (subtopic.find('a').text.strip(), subtopic.find('a') ['href']), threads))
        #print(threads)
        # Randomise threads
        thread_sample_titles_and_links = sample_links(thread_titles_and_links, threads_titles, SAMPLE_SIZE)
        
        thread_counter = 1
        # For debugging only - COMMENT OUT LATER        
        #print (thread_titles_and_links)
        
        for st_key, st_value in thread_sample_titles_and_links.items():
            thread_counter = thread_counter + 1
            thread_url = 'https://www.canadavisa.com' + st_value
            thread_title = st_key
            thread_content = bs(requests.get(thread_url).text, 'html.parser')

            last_page = 1
            try:
                thread_page_nav_count = len(thread_content.select('li.pageNav-page'))
                #last_page = int(re.search('Page \d* of (\d*)', thread_content.select('li.pageNav-page')[0].text).group(1))
                last_page = int(thread_content.select('li.pageNav-page')[page_nav_count - 1].text)
                print("Count of thread pages: " + str(last_page))
            except Exception as e: 
                print(e)
                
            for y in range(1, last_page + 1):
# For debugging only - COMMENT OUT LATER
              #  if y > 3:
               #     break

                thread_url = 'https://www.canadavisa.com' + st_value
                if y > 1:
                    thread_url = thread_url + 'page-' + str(x)
                    
                print("THREAD URL: "  + thread_url)
                thread_content = bs(requests.get(thread_url).text, 'html.parser')
                #CHANGED - WORKS
                messages = thread_content.select('div.bbWrapper')
                #NOT WORKING - IDS CONCEALED 
                m_ids = thread_content.select('li.message')
                message_urls = list(map(lambda permLink: permLink['href'], thread_content.select('div.message-attribution-main > a.u-concealed')))
                message_reactions = thread_content.select('div.message-userExtras > dl:nth-of-type(3) > dd')
                message_reactionsbar = thread_content.select('div.reactionsBar')
                message_reactions = list(map(lambda rb: len(rb.select('bdi')), message_reactionsbar))
                times = thread_content.select('time')
                if (times is not None):
                    message_dates = list(map(lambda date: date.decode_contents().strip(), times))
                message_usernames = thread_content.select('a.username')
                message_list = list(map(lambda message: (message.decode_contents().strip()), messages))
                usernames_list = list(map(lambda a: a.text.strip(), message_usernames))
                for idx, m in enumerate(message_list):
                    message_id = ""
                    message_ids.append(message_id)

                    link = ""
                    try:
                        link = 'https://www.canadavisa.com/' + message_urls[idx]
                    except IndexError:
                        link = ""
                    links.append(link)
                    message_date = ""
                    try:
                        #message_date = message_dates[idx]['title']
                        message_date = message_dates[idx]
                    except IndexError:
                        message_date = ""
                    date_contents.append(message_date)
                    message_username = ""
                    try:
                        message_username = usernames_list[idx]
                    except IndexError:
                        message_username = ""
                    username_contents.append(message_username)
                    
                    message_contents.append(m.replace('\n', ""))

                    countries.append("NA")
                    like = 0
                    try:
                        like = message_reactions[idx]
                    except IndexError:
                        like = 0
                    likes.append(like)
                    topic_contents.append(topic_title)
                    thread_contents.append(thread_title)
    # Here write the contents to a file, and re-set the data structures
    base_data_frame = data_frame(message_ids, links, date_contents, username_contents, message_contents, countries, likes, topic_contents, thread_contents)
    write_csv("can-forum-" + str(counter) + ".csv", base_data_frame)
    message_ids = list()
    links = list()
    date_contents = list()
    username_contents = list()
    message_contents = list()
    countries = list()
    likes = list()
    topic_contents = list()
    thread_contents = list()


# In[ ]:


# Create empty frame
#base_data_frame = pd.DataFrame({ "ID": message_ids, "Link": links, "Date": date_contents, "Username": username_contents, "Message": message_contents, "Country": [], "Like": [], "Topic": topic_contents, "Thread": thread_contents})
base_data_frame = pd.DataFrame({ "ID": message_ids, 
                                "Link": links, 
                                "Date": date_contents,
                                "Username": username_contents, 
                                "Message": message_contents, 
                                "Country": countries, 
                                "Like": likes, 
                                "Topic": topic_contents, 
                                "Thread": thread_contents})
print('Finished')


# In[ ]:


len(base_data_frame)


# In[ ]:


# from https://github.com/pandas-dev/pandas/issues/22610
import csv
with open("can-forum.csv", "w", errors='surrogatepass') as _file:
    writer = csv.writer(_file)
    #writer.writerow(row)
    writer.writerow(base_data_frame.columns.values)
    for index, row in base_data_frame.iterrows():
        writer.writerow(row)


# In[ ]:


base_data_frame.iloc[0:100]


# In[ ]:


#print(topic_content)
tc_last_page = int(re.search('Page \d* of (\d*)', topic_content.select('h3', {'class':'pageNav-page'})))
print(tc_last_page)


# In[ ]:


https://www.canadavisa.com/canada-immigration-discussion-board/forums/quebec-immigration.55/


# In[ ]:


int(re.search('Page \d* of (\d*)', 'Page 1 of 1280').group(1))


# In[ ]:


thread_sample_titles_and_links = sample_links(thread_titles_and_links, threads_titles, SAMPLE_SIZE)
#print(thread_sample_titles_and_links)
for st_key, st_value in thread_sample_titles_and_links.items():
            thread_counter = thread_counter + 1
thread_url = 'https://www.canadavisa.com' + st_value
print(thread_url)
thread_content = bs(requests.get(thread_url).text, 'html.parser')
last_page = 1
try:
    last_page = int(re.search('Page \d* of (\d*)', thread_content.select('li.pageNav-page')[0].text).group(1))
except Exception as e: 
    print(e)
    for x in range(1, last_page + 1):
# For debugging only - COMMENT OUT LATER
                #if x > 3:
               #     break
            
                    #thread_url = 'https://www.canadavisa.com' + st_value
                if x > 1:
                    thread_url = thread_url + 'page-' + str(x)
                print(thread_url)


# In[ ]:


thread_content = bs(requests.get(thread_url).text, 'html.parser')
#print(thread_content)
message_usernames = thread_content.select('a.username')
usernames_list = list(map(lambda a: a.text.strip(), message_usernames))
tc_last_page = int(re.search('Page \d* of (\d*)', topic_content.select('div.pageNav-page')[0].text).group(1))


# In[ ]:


print(tc_last_page)


# In[ ]:





# In[ ]:




