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
import ConfigParser, feedparser,os.path, re,simplexml , urllib


def parseFeed(url,tag):
        print "Parsing feed "+ url+ " for tag " + tag
        items = []
        feed = feedparser.parse(url)
        for feeditem in feed.entries:
            if tag == "title":
                foundItem = feeditem.title
            if tag == "link":
                foundItem = feeditem.guid
                # looking for an identifier with at least 2 numbers in the GUID url.
                matches = re.findall("[0-9]{2,}", foundItem)
                if len(matches)>0:
                    foundItem = matches[0]
                    
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
    items = parseFeed(searchQueryUrl,"link")
    if items is not None and len(items)>0:
        return items[0]
    
          

def enqueue_sabznbd(downloadItem,sabnzbd_host,sabnzbd_port,sabnzbd_user,sabnzbd_pass,sabnzbd_apikey):
    #print "Enqueue sabnzbd for: "+ downloadItem
    sabnzbdkeys = {"mode":"addid",
                   "name":downloadItem,
                   "apikey":sabnzbd_apikey}
    if sabnzbd_user is not None and sabnzbd_pass is not None:
        authentication = {"ma_username":sabnzbd_user,"ma_password":sabnzbd_pass}
    enqueueUrl = "http://" + sabnzbd_host + ":" + sabnzbd_port + "/sabnzbd/api?" + urllib.urlencode(sabnzbdkeys)
    if authentication is not None:
        enqueueUrl = enqueueUrl + "&" + urllib.urlencode(authentication)
    response = urllib.urlopen(enqueueUrl)
    result = response.read()
    if result == "ok\n":
        print "Queued newzbin postId: " + downloadItem
        return True
    else:
        print "Problem while trying to enqueue newzbin postId: " + downloadItem
        print "Result: "+ result
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
    for (item,feed) in enqueuedItems:
        xmlItem = elements[0].newchild("item")
        xmlItem.attr("feed", feed)
        titleItem = xmlItem.newchild("title")
        titleItem.value = item 
    doc.save(xmlFilePath)
    
    
def already_downloaded(item,feed,xmlFilePath):
    print "Check if "+item+" is already downloaded"
    if os.path.exists(xmlFilePath):
        filename = xmlFilePath
    else: 
        filename = None
        return False
    doc = simplexml.xmldoc(filename)
    elements = doc.elements("items/item(feed="+feed+")/title")
    for element in elements:
        if element.value == item:
            print "Already in "+ xmlFilePath + " so skipping this item"
            return True
    print "Not found, so search & enqueue"
    return False

def get_config_sabnzbd(config):
    host = config.get('sabnzbd', 'host')
    port = config.get('sabnzbd', 'port')
    username = config.get('sabnzbd', 'username')
    password = config.get('sabnzbd', 'password')
    apikey = config.get('sabnzbd', 'apikey')
    return host,port,username,password,apikey

def get_config_global(config):
    config.read('pyrssmonitor.cfg')
    if not config.has_section('pyrssmonitor'):
        raise Exception("configuration file section %1 missing", "pyrssmonitor")
    
    if not config.has_section('sabnzbd'):
        raise Exception("configuration file section %1 missing", "sabnzbd")
    
    xmlFilePath = config.get('pyrssmonitor', 'xmlfile')
 
    return xmlFilePath
def main():
    config = ConfigParser.RawConfigParser()
    xmlFilePath = get_config_global(config)
    rssfeeds = config.items('rssfeeds')
    (sab_host , sab_port , sab_user , sab_pass , sab_apikey) = get_config_sabnzbd(config)
    
    enqueuedItems = []
    for (rssfeedname,rssfeedurl) in rssfeeds:
        items = parseFeed(rssfeedurl,"title")
        for item in items:
            if not already_downloaded(item,rssfeedname,xmlFilePath):
                result = search_newzbin(item)
                if result is not None:
                    if enqueue_sabznbd(result,sab_host,sab_port,sab_user,sab_pass,sab_apikey) is True:
                        enqueuedItem = (item,rssfeedname)
                        enqueuedItems.append(enqueuedItem)
    save_downloaded(xmlFilePath,enqueuedItems)
if __name__ == '__main__':
    main()


    

