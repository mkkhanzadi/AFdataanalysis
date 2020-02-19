#!/usr/bin/env python
# coding: utf-8

# In[101]:


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


# In[102]:


#defining the url and using the ureq to read the website in html. This can be checked by print(canadavisa)


# In[103]:


canadavisa_url = 'https://www.canadavisa.com/canada-immigration-discussion-board/'
canadavisa = requests.get(canadavisa_url).text


# In[104]:


#all topics are in tag 'h3' - using bs to find all data in h3 - Topic tag has changed from nodeTitle to node-title


# In[105]:


soup = bs(canadavisa, 'html.parser')

topics = soup.find_all('h3', {'class':'node-title'})
topic_titles = list(map(lambda h: h.text.strip(), topics))
topic_titles_and_links = dict(map(lambda h: (h.text.strip(), h.find('a') ['href']), topics))
print(topic_titles_and_links)


# LM's example of randomised topic selection. Uses [sampling without replacement](https://web.ma.utexas.edu/users/parker/sampling/repl.htm) to ensure the same topic is not selected twice .

# In[106]:


topic_titles_and_links


# In[107]:


with open('titles_and_links.csv', mode='w') as csv_file:
    fieldnames = ['title', 'link']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for key, value in topic_titles_and_links.items():
        writer.writerow({'title': key, 'link': value})


# In[108]:


def sample_links(titles_and_links, titles, sample_size):
   num_links = len(titles_and_links)
   sample_titles_and_links = {}
   ids = []

   #This code creates an array of topic ids that are random and unique
   if sample_size < num_links:
       for i in range(0, sample_size):
           x = -1
            
           while not(x in ids):
               x = random.randint(0, num_links)
               ids.append(x)

   # Now create the topic sample
   if len(ids) > 0:
       for i in ids:
           if (i < len(titles)):
               key = titles[i]
               sample_titles_and_links[key] = titles_and_links[key]
        
   return sample_titles_and_links
    


# In[109]:


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


# In[110]:


def write_csv(file_name, base_data_frame):
    with open(file_name, "w", errors='surrogatepass') as _file:
        writer = csv.writer(_file)
        #writer.writerow(row)
        writer.writerow(base_data_frame.columns.values)
        for index, row in base_data_frame.iterrows():
            writer.writerow(row)


# In[111]:


SAMPLE_SIZE = 3
PAGE_SAMPLE_SIZE = 3


# In[112]:


topic_sample_titles_and_links = sample_links(topic_titles_and_links, topic_titles, SAMPLE_SIZE)
##print(topic_sample_titles_and_links)


# In[113]:


##print(topic_sample_titles_and_links)


# In[114]:



total_message_ids = list()
total_links = list()
total_date_contents = list()
total_username_contents = list()
total_message_contents = list()
total_countries = list()
total_likes = list()
total_topic_contents = list()
total_thread_contents = list()


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
        #tc_last_page = int(re.search('Page \d* of (\d*)', topic_content.select('li.pageNav-page')[0].text).group(1))
    except Exception as i:
        pass
        
    #for x in range(1, tc_last_page + 1):
    topic_sample = range(1, tc_last_page + 1)
    if (len(topic_sample) > PAGE_SAMPLE_SIZE):
        topic_sample = random.sample(topic_sample, PAGE_SAMPLE_SIZE)
    for x in topic_sample:
# For debugging only - COMMENT OUT LATER
        topic_url = 'https://www.canadavisa.com' + value
        if x > 1:
            topic_url = topic_url + 'page-'+ str(x)
        print("Topic URL: " + topic_url)
        topic_content = bs(requests.get(topic_url).text, 'html.parser')
        threads = topic_content.find_all('div', {'class':'structItem-title'})
        threads_titles = list(map(lambda subtopic: subtopic.find('a').text.strip(), threads))
        thread_titles_and_links = dict(map(lambda subtopic: (subtopic.find('a').text.strip(), subtopic.find('a') ['href']), threads))

        # Randomise threads
        thread_sample_titles_and_links = sample_links(thread_titles_and_links, threads_titles, SAMPLE_SIZE)
        thread_counter = 1

        
        for st_key, st_value in thread_sample_titles_and_links.items():
            thread_counter = thread_counter + 1
            thread_url = 'https://www.canadavisa.com' + st_value
            print("Thread URL: " + thread_url)
            thread_title = st_key
            thread_content = bs(requests.get(thread_url).text, 'html.parser')

            last_page = 1
            try:
                thread_page_nav_count = len(thread_content.select('li.pageNav-page'))
                #last_page = int(re.search('Page \d* of (\d*)', thread_content.select('li.pageNav-page')[0].text).group(1))
                last_page = int(thread_content.select('li.pageNav-page')[thread_page_nav_count - 1].text)
                print("Count of thread pages: " + str(last_page))
            except Exception as e: 
                pass
            
            #for y in range(1, last_page):
            thread_sample = range(1, last_page + 1)
            if (len(thread_sample) > PAGE_SAMPLE_SIZE):
                thread_sample = random.sample(thread_sample, PAGE_SAMPLE_SIZE)

            for y in thread_sample:
# For debugging only - COMMENT OUT LATER
                #if y > 3:
                #    break

                thread_url = 'https://www.canadavisa.com' + st_value
                if y > 1:
                    thread_url = thread_url + 'page-' + str(y)
                    
                thread_content = bs(requests.get(thread_url).text, 'html.parser')
                #CHANGED - WORKS
                messages = thread_content.select('div.bbWrapper')
                #NOT WORKING - IDS CONCEALED 
                message_urls = list(map(lambda permLink: permLink['href'], thread_content.select('div.message-attribution-main > a')))
                message_reactions = thread_content.select('div.message-userExtras > dl:nth-of-type(3) > dd')
                message_reactionsbar = thread_content.select('div.reactionsBar')
                message_likes = list(map(lambda rb: len(rb.select('bdi')), message_reactionsbar))
                times = thread_content.select('time')
                if (times is not None):
                    message_dates = list(map(lambda date: date.decode_contents().strip(), times))
                message_usernames = thread_content.select('a.username')
                message_list = list(map(lambda message: (message.decode_contents().strip()), messages))
                usernames_list = list(map(lambda a: a.text.strip(), message_usernames))
                for idx, m in enumerate(message_list):
                    #message_id = ""
                    #try:
                     #   message_id = re.search('post-(\d*)', m_ids[idx]['id']).group(1)
                    #except IndexError:
                     #   message_id = ""
                    #message_ids.append(message_id)
                    message_ids.append(0)
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
                        like = message_likes[idx]
                    except IndexError:
                        like = 0
                    likes.append(like)
                    topic_contents.append(topic_title)
                    thread_contents.append(thread_title)
    # Here write the contents to a file, and re-set the data structures
    base_data_frame = data_frame(message_ids, links, date_contents, username_contents, message_contents, countries, likes, topic_contents, thread_contents)
    write_csv("can-forum-" + str(counter) + ".csv", base_data_frame)
    total_message_ids.extend(message_ids)
    total_links.extend(links)
    total_date_contents.extend(date_contents)
    total_username_contents.extend(username_contents)
    total_message_contents.extend(message_contents)
    total_countries.extend(countries)
    total_likes.extend(likes)
    total_topic_contents.extend(topic_contents)
    total_thread_contents.extend(thread_contents)
    message_ids = list()
    links = list()
    date_contents = list()
    username_contents = list()
    message_contents = list()
    countries = list()
    likes = list()
    topic_contents = list()
    thread_contents = list()

total_base_data_frame = data_frame(total_message_ids, total_links, total_date_contents, total_username_contents, total_message_contents, total_countries, total_likes, total_topic_contents, total_thread_contents)    
write_csv("can-forum-ALL.csv", total_base_data_frame)


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


print(sample_titles_and_links)


# In[ ]:





# In[ ]:




