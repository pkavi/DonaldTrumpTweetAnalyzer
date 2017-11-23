#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
from selenium import webdriver
from time import sleep
import random
import HTMLParser
import sys
import pandas as pd
import re
import traceback
import psycopg2





class tagError(Exception):
    def __init__(self,tag,dataType,startDate,endDate,tweetId):
        self.tag=tag
        self.dataType=dataType
        self.startDate=startDate
        self.endDate=endDate
        self.tweetId=tweetId
        
    def __str__(self):
        return "Tag Error- tweetId: " + str(self.tweetId)+" tag: "+ str(self.tag)+" datatype: "+ str(self.dataType)+" startDate: "+str(self.startDate)+" endDate: "+str(self.endDate)



def printingList(li):
    retStr='{'
    for i in range(len(li)):
        if i!=len(li)-1:
            retStr=retStr+'\''+li[i]+'\','
        else:
            retStr=retStr+'\''+li[i]+'\''
    retStr+="}"
    return retStr
    

#http://thiagomarzagao.com/2013/11/12/webscraping-with-selenium-part-1/
def dateSearchShortRange(cur,conn,startDate,endDate,accountName):   
    path_to_chromedriver = 'C:\\Users\\pkavikon\\Desktop\\DataScienceProject\\chromedriver.exe' # change path as needed
    
    url_twitter='https://twitter.com/search?l=&q=from%3A'+accountName+'%20since%3A'+str(startDate.strftime('%Y-%m-%d'))+'%20until%3A'+str(endDate.strftime('%Y-%m-%d'))+'&src=typd&lang=en'
    print(url_twitter)
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (X11;     Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0   Safari/537.36')
    
    browser = webdriver.Chrome(executable_path = path_to_chromedriver,chrome_options=options)
    browser.get(url_twitter)
    #Code below from https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
    # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
        sleep(0.999*random.uniform(1, 2))

    # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            #print("started")
            sleep(4.5)
            #print("ended")
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height
    
    #https://stackoverflow.com/questions/36615472/how-to-find-element-in-selenium-python-using-id-and-class-in-div
    arrow = browser.find_elements_by_xpath('//li[@data-item-type="tweet"]')
    tweetsToGet=[]
    accountNameTweets=[]
    verifiedList=[]
    for x in arrow:
        
        tweetId=x.get_attribute("data-item-id")
        #print(x.get_attribute("innerHTML").encode('utf-8'))
        verified=x.find_elements_by_xpath('.//span[@class="Icon Icon--verified"]')
        
        if len(verified)!=1:
            verified=False
        else:
            
            verified=True
        verifiedList.append(verified)
        accountNameTweet=x.find_elements_by_xpath('.//a[@class="account-group js-account-group js-action-profile js-user-profile-link js-nav"]')
        if len(accountNameTweet)!=1:
            raise tagError('a', 'accountNameTweet', startDate,endDate, None)
        accountNameTweet=accountNameTweet[0].get_attribute("href")
        accountNameTweets.append(accountNameTweet)
        tweetsToGet.append(tweetId)

    browser.close()
    for i in range(len(tweetsToGet)):
        try:
            tweetId=tweetsToGet[i]
            print(tweetId)
            sleep(0.5*random.uniform(0.5,2))
            
            #Open the page for each tweet
            r = urllib.urlopen('https://twitter.com/'+accountName+'/status/'+tweetId).read()
            tweetPage = BeautifulSoup(r,"html.parser")
            
            #lambda tag: tag.name == 'div' and 
             #                          tag.get('class') == ['product']
            #Get the div for tweet from each page
            divs=tweetPage.findAll(lambda tag: tag.name=='div' and tag.get('class')==['permalink-inner', 'permalink-tweet-container'])
            if len(divs)!=1:
                divs=tweetPage.findAll(lambda tag: tag.name=='div' and tag.get('class')==['permalink-inner','permalink-tweet-container', 'ThreadedConversation', 'ThreadedConversation--permalinkTweetWithAncestors'])
                if len(divs)!=1:
                    raise tagError('div', 'divs', startDate,endDate, tweetId)
                #print(tweetPage.encode('utf-8'))
            divs=divs[0]
            
            
            
                
            
            
            
            
            #Get the contentTag for tweet
            #Must still get emojis hashtags and others
            contentTag=divs.findAll(lambda tag: tag.name=='div' and tag.get("class")==['js-tweet-text-container'])
            if len(contentTag)!=1:
                raise tagError('div', 'contentTag', startDate,endDate, tweetId)
            contentTag=contentTag[0].findAll(lambda tag: tag.name=='p')
            if len(contentTag)!=1:
                raise tagError('p', 'contentTag', startDate,endDate, tweetId)
                
            
            hashtags=contentTag[0].findAll(lambda tag: tag.name=='a' and tag.get('class')==['twitter-hashtag', 'pretty-link', 'js-nav'])
            ats=contentTag[0].findAll(lambda tag: tag.name=='a' and tag.get('class')==['twitter-atreply', 'pretty-link', 'js-nav'])
            emojis=contentTag[0].findAll(lambda tag: tag.name=='img' and tag.get('class')==['Emoji','Emoji--forText'])
            
            rawText=contentTag[0].text
            
            emojiCodes=[]
            
            hashtagCollection=[]
            for h in hashtags:
                hashtagCollection.append(h.text[1:])
                
            atCollection=[]
            for a in ats:
                atCollection.append(a['href'][1:])
                
            emojiCollection=[]
            for e in emojis:
                emojiCollection.append(e['title'])
                emojiCodes.append(e['alt'])
                e.decompose()
            
            
            
            
            
            linkCollection=[]
            for div in contentTag[0].find_all(lambda tag: tag.name=="a" and tag.get("class")==['twitter-timeline-link']): 
                linkCollection.append(div['data-expanded-url'])
                div.decompose()
            
            for div in contentTag[0].find_all(lambda tag: tag.name=="a" and tag.get("class")!=['twitter-atreply', 'pretty-link', 'js-nav'] and tag.get("class")!=['twitter-hashtag', 'pretty-link', 'js-nav']): 
                div.decompose()
            
            
            #Filtered implies no puncutation and 
            textFiltered=re.sub(r'[^a-zA-z0-9 \�%]+', '', contentTag[0].text) #Includes filtered with hashtags and 
            
            
            
            
            for h in hashtags:
                h.decompose()
            for a in ats:
                a.decompose()
            
            textFilteredNoHashtagsAts=re.sub(r'[^a-zA-z0-9 \�%]+', '', contentTag[0].text)
            
            
            #Get the date time for each tweet
            postTimeDate=divs.findAll(lambda tag: tag.name=='span' and tag.get('class')==['metadata'])
            if len(postTimeDate)!=1:
                raise tagError('span', 'postTimeDate', startDate,endDate, tweetId)
            postTimeDate=postTimeDate[0]
            postTimeDate=postTimeDate.find(lambda tag: tag.name=='span').text.strip()
            postTimeDate= pd.to_datetime(postTimeDate, format='%I:%M %p - %d %b %Y' )
            
            
            
            
            #Get the retweets for the tweet
            retweets=divs.findAll(lambda tag: tag.name=='li' and tag.get('class')==['js-stat-count' ,'js-stat-retweets' ,'stat-count'])
            if len(retweets)!=1:
                try:
                    raise tagError('li', 'retweets', startDate,endDate, tweetId)
                except tagError as e:
                    print("Possible retweets of zero")
                    print(e)
                    print("^^^^")
                retweets=0
            else:
                retweets=retweets[0]
                retweets=retweets.findAll(lambda tag: tag.name=="a")
                if len(retweets)!=1:
                    try:
                        raise tagError('a', 'retweets', startDate,endDate, tweetId)
                    except tagError as e:
                        print("Possible retweets of zero")
                        print(e)
                        print("^^^^")
                    retweets=0
                else:
                    retweets=retweets[0]
                    retweets=int(retweets["data-tweet-stat-count"])
            
            
            
            #Get the favorites for the tweet
            favorites=divs.findAll(lambda tag: tag.name=='li' and tag.get('class')==['js-stat-count', 'js-stat-favorites', 'stat-count'])
            if len(favorites)!=1:
                try:
                    raise tagError('li', 'favorites', startDate,endDate, tweetId)
                except tagError as e:
                        print("Possible favorites of zero")
                        print(e)
                        print("^^^^")
                favorites=0
            else:
                favorites=favorites[0]
                favorites=favorites.findAll(lambda tag: tag.name=="a")
                if len(favorites)!=1:
                    try:
                        raise tagError('a', 'favorites', startDate,endDate, tweetId)
                    except tagError as e:
                        print("Possible favorites of zero")
                        print(e)
                        print("^^^^")
                    favorites=0
                else:
                    favorites=favorites[0]
                    favorites=int(favorites["data-tweet-stat-count"])
            
            postDate=postTimeDate.strftime("%Y-%m-%d")
            postTime=postTimeDate.strftime("%H:%M:%S ")+ ' CST'
            cur.execute("select tweetId from tweetsTable where tweetId=%s;",(tweetId.encode('utf-8'),))
            if cur.fetchone() is not None:
                #cur.execute("UPDATE SET tweetsTable (tweetId,accountName,verified,postTime,postDate,favorites,retweets,rawText,hashtagCollection,emojiCollection,emojiCodes,atCollection,linkCollection,textFiltered,textFilteredNoHashtagsAts) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",(tweetId.encode('utf-8'),accountName.encode('utf-8'),verified,postTime.encode('utf-8'),postDate.encode('utf-8'),favorites,retweets,rawText.encode('utf-8'),printingList(hashtagCollection).encode('utf-8'),printingList(emojiCollection).encode('utf-8'),printingList(emojiCodes).encode('utf-8'),printingList(atCollection).encode('utf-8'),printingList(linkCollection).encode('utf-8'),textFiltered.encode('utf-8'),textFilteredNoHashtagsAts.encode('utf-8')))
                print("delete and reinsert: "+ str(tweetId))
                cur.execute("DELETE FROM tweetsTable WHERE tweetId=%s;",(tweetId.encode('utf-8'),))
            cur.execute("INSERT INTO tweetsTable (tweetId,accountName,verified,postTime,postDate,favorites,retweets,rawText,hashtagCollection,emojiCollection,emojiCodes,atCollection,linkCollection,textFiltered,textFilteredNoHashtagsAts) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(tweetId.encode('utf-8'),accountName.encode('utf-8'),verified,postTime.encode('utf-8'),postDate.encode('utf-8'),favorites,retweets,rawText.encode('utf-8'),printingList(hashtagCollection).encode('utf-8'),printingList(emojiCollection).encode('utf-8'),printingList(emojiCodes).encode('utf-8'),printingList(atCollection).encode('utf-8'),printingList(linkCollection).encode('utf-8'),textFiltered.encode('utf-8'),textFilteredNoHashtagsAts.encode('utf-8')))
            conn.commit()
    #         print(accountNameTweets[i])
    #         print(verifiedList[i])
    #         print(tweetId)
    #         print(postTimeDate)
    #         print(favorites)
    #         print(retweets)
    #         print(rawText)
    #         print(hashtagCollection)
    #         print(emojiCollection)
    #         print(emojiCodes)
    #         print(atCollection)
    #         print(linkCollection)
    #         print(textFiltered)
    #         print(textFilteredNoHashtagsAts)
    #         print("\n\n\n\n\n")
        except tagError as err:
            print(err)
        except:
            traceback.print_exc()
        
        
#start=pd.to_datetime('2015-02-27'),end=pd.to_datetime('2015-04-01')        
def searchLongRange(cur,conn,start=pd.to_datetime('2015-04-23'),end=pd.to_datetime('2015-10-31'),accountName="realDonaldTrump"):        
    d = pd.date_range(start=start, end=end, freq='M')
    if len(d)<=1:
        d=pd.date_range(start=start,end=end,freq='D')
    print("STARTING: " + str(d[0]))
    print("ENDING: "+ str(d[-1]))
    print("STARTED".center(50,"-"))
    for i in range(len(d)):
        if i==len(d)-1:
            break
        try:
            print("\n\nstarted date range: "+ str(d[i]-pd.DateOffset(days=1)) + "-"+ str(d[i]+1+pd.DateOffset(days=1)) )
            dateSearchShortRange(cur,conn,d[i]-pd.DateOffset(days=1), d[i]+1+pd.DateOffset(days=1),accountName)
              
        except tagError as err:
            print(err)
        except:
            traceback.print_exc()
        print("ended date range: "+str(d[i]-pd.DateOffset(days=1)) + "-"+ str(d[i]+1+pd.DateOffset(days=1)))
        print("\n\n") 
    print("ENDED".center(50,"-"))

#print(re.sub(r'[^a-zA-z0-9 ]+', '', " my name is donad,asd trup's "))

conn = psycopg2.connect("dbname=TweetsDatabase user=pkavikon")
cur = conn.cursor()
#searchLongRange(cur,conn)
searchLongRange(cur,conn,start=pd.to_datetime('2017-05-29'),end=pd.to_datetime('2017-06-24'))
conn.commit()
cur.close()
conn.close()
#fix amperasanad
#hashtag
#emoji
#links
#at some account

# urla='https://twitter.com/search?l=&q=from%3ArealDonaldTrump%20since%3A2017-11-02%20until%3A2017-11-06&src=typd&lang=en'
# r = urllib.urlopen(urla).read()
# #r = open("C:\\Users\\pkavikon\\Downloads\\from_realDonaldTrump since_2017-11-02 until_2017-11-06 - Twitter Search.html")
# doc = BeautifulSoup(r,"lxml")
# #print(doc)
# col=doc.findAll("li",{"data-item-type":"tweet"})
# print(len(col))

#print(HTMLParser.HTMLParser().unescape(postTimeDate).encode(sys.getfilesystemencoding()))



#js-stream-item stream-item stream-item

#js-stream-item stream-item stream-item
#permalink-inner permalink-tweet-container     To scrape each individual tweet and get likes and dislikes




