Use this program to search for items in a RSS feed on newzbin until the item is found.

For instance, you can use this program to monitor a 'My Movies' list on IMDb. Register on imdb.com, create a category, make it public, and insert the RSS feed URL into this program.
This program will continue to search newzbin for the full title in the RSS feed (rss/channel/item/title) until it is found.

See pyrssmonitor.sample.cfg for the configuration file. In the configuration file, you can specify additional search parameters for newzbin to match the category, format etc you want.

Currently tested with IMDb and Amazon Wish List (use http://www.edazzle.net/amazon/ to generate a RSS feed)

Required libraries:
  * simplexml: http://pypi.python.org/pypi/simplexml/0.6.1
  * feedparser: http://www.feedparser.org/

Written for Py 2.5