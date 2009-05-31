'''
Created on 31 mei 2009

@author: Bram Walet
'''
import feedparser, urllib

def parseFeed(url):
        items = []
        feed = feedparser.parse(url)
        for feeditem in feed["items"]:
            items.append(feeditem["title"])
           
        return items
    
def search_newzbin(item):
    
    # http://v3.newzbin.com/search/query/?q=300+(2006)
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
    print searchQueryUrl
    feed = feedparser.parse(searchQueryUrl)
    for feeditem in feed["items"]:
        if feeditem["report_id"] is not None:
            return feeditem["report_id"]

def enqueue_sabznbd(downloadItem):
    sabnzbd_host = "http://192.168.16.20:9200/sabnzbd/"
    sabnzbd_user = ""
    sabnzbd_pass = "" 
    sabnzbd_apikey = "d024408218ef9728d99ffe0a1d1f33d6" 
    sabnzbdkeys = {"mode":"addid",
                   "name":downloadItem,
#                   "ma_username":sabnzbd_user,
#                   "ma_password":sabnzbd_pass,
                   "cat":"\"movies\"",
                   "apikey":sabnzbd_apikey}
    enqueueUrl = sabnzbd_host + "api?" + urllib.urlencode(sabnzbdkeys)
    print enqueueUrl
    response = urllib.urlopen(enqueueUrl)
    if response.read() == "ok\n":
        print "Enqueued newzbin postId: " + downloadItem
    else:
        print response.read()

def main():
    downloadList = []
    rssfeed = "http://rss.imdb.com/mymovies/list?l=29166270"
    items = parseFeed(rssfeed)
    for item in items:
        results = search_newzbin(item)
        if results is not None:
            downloadList.append(results)
    if len(downloadList) > 0:
        for downloadItem in downloadList:
            enqueue_sabznbd(downloadItem)
        
if __name__ == '__main__':
    main()
    

