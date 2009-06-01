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
        # for each entry in the feed,
        for feeditem in feed.entries:
            # if we are looking for a title (in the rss feeds in the config)
            if tag == "title":
                foundItem = feeditem.title
            # specific for the newzbin feed, because we need a postId to queue sabnzbd
            if tag == "link":
                foundItem = feeditem.guid
                # looking for an identifier with at least 2 numbers in the GUID url.
                matches = re.findall("[0-9]{2,}", foundItem)
                if len(matches)>0:
                    foundItem = matches[0]
                    
            # add the found item to the list        
            items.append(foundItem)
            
        # return the list of items in the feed.   
        return items
    
def search_newzbin(item,extraKeys):
    print "Search newzbin for: "+item
    baseUrl = "http://v3.newzbin.com/search/query/?"
    # these keys will generate the search query. See the HTML form on newzbin on information.
    searchKeys = {"q":"\""+item+"\"",
                  "searchaction":"Search",
                  "fpn":"p",
             #     "category":"-1",
                  "u_nfo_posts_only":"0",
                  "u_url_posts_only":"0",
                  "u_comment_posts_only":"0",
                  "u_v3_retention":"20736000",
             #     "ps_rb_region":"1073741824",
             #     "ps_rb_source":"64",
             #     "ps_rb_video_format":"2",
             #     "ps_rb_language":"4096",
                  "sort":"ps_edit_date",
                  "order":"desc",
                  "u_post_results_amt":"10",
                  "feed":"rss",
                  }
        
    queryParams = {}
    queryParams.update(searchKeys) 
    queryParams.update(extraKeys) 
    
    searchQueryUrl = baseUrl + urllib.urlencode(queryParams)
    
    # newzbin can output the search query as RSS so we need feedparser here too!
    items = parseFeed(searchQueryUrl,"link")
    if items is not None and len(items)>0:
        return items[0]
    
          

def queue_sabznbd(downloadItem,sabnzbd_host,sabnzbd_port,sabnzbd_user,sabnzbd_pass,sabnzbd_apikey):
    #print "Enqueue sabnzbd for: "+ downloadItem
    queryParams = {}
    sabnzbdkeys = {"mode":"addid",
                   "name":downloadItem,
                   "apikey":sabnzbd_apikey}
    queryParams.update(sabnzbdkeys)
    
    # check if we need authentication
    if not sabnzbd_user and len(sabnzbd_user) > 0  and not sabnzbd_pass and len(sabnzbd_pass) > 0:
        authentication = {"ma_username":sabnzbd_user,"ma_password":sabnzbd_pass}
        queryParams.update(authentication)
            
    queueUrl = "http://" + sabnzbd_host + ":" + sabnzbd_port + "/sabnzbd/api?" + urllib.urlencode(queryParams)
    # open the URL so the item gets queued        
    response = urllib.urlopen(queueUrl)
    result = response.read()
    
    # check if queue was succesful.
    if result == "ok\n":
        print "Queued newzbin postId: " + downloadItem
        return True
    else:
        print "Problem while trying to queue newzbin postId: " + downloadItem
        print "Result: "+ result
        return False


def save_downloaded(xmlFilePath,queuedItems):
    # before we read the file, check if it exists. 
    if os.path.exists(xmlFilePath):
        filename = xmlFilePath
    else: 
        filename = None
    doc = simplexml.xmldoc(filename)
    # create new file and new root if file does not exists.
    if doc is None or doc.root is None:
        doc.new_root("items")       
    # items is the root element
    elements = doc.elements("items")
    
    # for each item in enqueuedelements we need to store that it is downloaded
    for (item,feed) in queuedItems:
        # each element 'item' in the XML has an attribute 'feed'
        # and each element 'item' has a child named 'title'.
        xmlItem = elements[0].newchild("item")
        xmlItem.attr("feed", feed)
        xmlItem.value = item
    doc.save(xmlFilePath)
    
    
def already_downloaded(item,feed,xmlFilePath):
    print "Check if " + item + " is already downloaded"
    # check if the file exists, if the file does not exists, the title isn't downloaded yet.
    if os.path.exists(xmlFilePath):
        filename = xmlFilePath
    else: 
        filename = None
        return False
    doc = simplexml.xmldoc(filename)
    # search for item elements in items from a specific feed. Return all title elements.
    elements = doc.elements("items/item(feed=" + feed + ")")
    for element in elements:
        # check if the element matches the item we are inspecting.
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
    # read config file
    config.read('pyrssmonitor.cfg')
    # check if sections exist.
    if not config.has_section('pyrssmonitor'):
        raise Exception("configuration file section %1 missing", "pyrssmonitor")
    
    if not config.has_section('sabnzbd'):
        raise Exception("configuration file section %1 missing", "sabnzbd")
    
    if not config.has_section('rssfeeds'):
        raise Exception("configuration file section %1 missing", "ressfeeds")
    
    # this config item tells us where to find the xml file.
    xmlFilePath = config.get('pyrssmonitor', 'xmlfile')
    # this config file has items which represent all our rss feeds we want to check
    # these items are written as: 
    # feedname = feedurl
    rssfeeds = config.items('rssfeeds')
    return xmlFilePath,rssfeeds

def get_feed_newzbin_params(rssfeedname,config):
    if config.has_section(rssfeedname):
        return config.items(rssfeedname)
    
def main():
    config = ConfigParser.RawConfigParser()
    
    # get config variables
    (xmlFilePath,rssfeeds) = get_config_global(config)
    (sab_host , sab_port , sab_user , sab_pass , sab_apikey) = get_config_sabnzbd(config)
    
    queuedItems = []
    # for each rssfeed
    for (rssfeedname,rssfeedurl) in rssfeeds:
        extraKeys = get_feed_newzbin_params(rssfeedname,config)
        # parse the feed
        items = parseFeed(rssfeedurl,"title")
        # for each item in the rss feed
        for item in items:
            # check if we downloaded this title
            if not already_downloaded(item,rssfeedname,xmlFilePath):
                # if we haven't downloaded it, search it on newzbin.
                result = search_newzbin(item,extraKeys)
                if result is not None:
                    # if we have a result, queue it in sabnzbd
                    if queue_sabznbd(result,sab_host,sab_port,sab_user,sab_pass,sab_apikey) is True:
                        queuedItem = (item,rssfeedname)
                        # append it to the list with queued items, so we can store it in the xml file
                        queuedItems.append(queuedItem)
    
    # store all downloaded items in the xml file                    
    save_downloaded(xmlFilePath,queuedItems)
    
# main shit
if __name__ == '__main__':
    main()


    

