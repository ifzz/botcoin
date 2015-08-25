#!/usr/bin/env python

import urllib.request

#'http://chartapi.finance.yahoo.com/instrument/1.0/'AMZN/chartdata;type=quote;range=60d/csv
YAHOO_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'

csv = urllib.request.urlopen(YAHOO_API.format('AMZN','1d')).read().decode('utf-8')
print(csv.splitlines())
