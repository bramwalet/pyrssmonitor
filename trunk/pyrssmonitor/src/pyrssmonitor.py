'''
Created on 31 mei 2009

Copyright 2009 (c) Bram Walet

PyRssMonitor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyRssMonitor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyRssMonitor.  If not, see <http://www.gnu.org/licenses/>.

@author: Bram Walet
'''

import feedparser, urllib
import os.path
import simplexml 

def parseFeed(url,tag):
        print "Parsing feed "+ url+ " for tag " + tag
        items = []
        feed = feedparser.parse(url)
        for feeditem in feed["items"]:
            foundItem = feeditem[tag]
            items.append(foundItem)
           
        return items
    
def search_newzbin(item):
    print "Search newzbin for: "+item
    baseUrl = "http://v3.newzbin.com/search/query/?"
    searchKeys = {"q":item,
                  "searchaction":"Search",
                  "fpn":"p",
                  "category":"-1",
                  "u_nfo_posts_only":"0",
                  "u_url_posts_only":"0",
                  "u_comment_posts_only":"0",
                  "u_v3_retention":"20736000",
                  "ps_rb_region":"1073741824",
                  "ps_rb_source":"64",
                  "ps_rb_video_format":"2",
                  "ps_rb_language":"4096",
                  "sort":"ps_edit_date",
                  "order":"desc",
                  "u_post_results_amt":"10",
                  "feed":"rss",
                  }
    searchQueryUrl = baseUrl + urllib.urlencode(searchKeys)
    items = parseFeed(searchQueryUrl,"report_id")
    if items is not None and len(items)>0:
        return items[0]
    
          

def enqueue_sabznbd(downloadItem):
    print "Enqueue sabnzbd for: "+ downloadItem
    sabnzbd_host = "http://192.168.16.20:9200/sabnzbd/"
    # sabnzbd_user = ""
    # sabnzbd_pass = "" 
    sabnzbd_apikey = "d024408218ef9728d99ffe0a1d1f33d6" 
    sabnzbdkeys = {"mode":"addid",
                   "name":downloadItem,
   #                "ma_username":sabnzbd_user,
   #                "ma_password":sabnzbd_pass,
                   "apikey":sabnzbd_apikey}
    enqueueUrl = sabnzbd_host + "api?" + urllib.urlencode(sabnzbdkeys)
    response = urllib.urlopen(enqueueUrl)

    if response.read() == "ok\n":
        print "Enqueued newzbin postId: " + downloadItem
        return True
    else:
        print "Problem while trying to enqueue newzbin postId: " + downloadItem
        return False


def save_downloaded(xmlFilePath,enqueuedItems):
    if os.path.exists(xmlFilePath):
        filename = xmlFilePath
    else: 
        filename = None
    doc = simplexml.xmldoc(filename)
    if doc is None or doc.root is None:
        doc.new_root("items")       
    elements = doc.elements("items")
    for item in enqueuedItems:
        xmlItem = elements[0].newchild("item")
        titleItem = xmlItem.newchild("title")
        titleItem.value = item 
    doc.save(xmlFilePath)
    
    
def already_downloaded(item,xmlFilePath):
    print "Check if "+item+" is already downloaded"
    if os.path.exists(xmlFilePath):
        filename = xmlFilePath
    else: 
        filename = None
        return False
    doc = simplexml.xmldoc(filename)
    elements = doc.elements("items/item/title")
    for element in elements:
        if element.value == item:
            print "Already in "+ xmlFilePath + " so skipping this item"
            return True
    print "Not found, so search & enqueue"
    return False
    
def main():
    
    xmlFilePath = "downloadlist.xml"
    #read_downloaded(xmlFilePath)
    enqueuedItems = []
    rssfeed = "http://rss.imdb.com/mymovies/list?l=29166270"
    items = parseFeed(rssfeed,"title")
    for item in items:
        if not already_downloaded(item,xmlFilePath):
            result = search_newzbin(item)
            if result is not None:
                if enqueue_sabznbd(result) is True:
                    enqueuedItems.append(item)
    save_downloaded(xmlFilePath,enqueuedItems)
if __name__ == '__main__':
    main()
    

