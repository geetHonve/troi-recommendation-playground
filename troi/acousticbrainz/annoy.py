import sys
import urllib
from urllib.parse import quote

import requests
import ujson

from troi import Element, Recording


class AnnoyLookupElement(Element):
    '''
        Given an recording MBID, lookup tracks that are similar given some 
        criteria (e.g. mfccs, gfccs, etc).
    '''

    SERVER_URL = "http://similarity.acousticbrainz.org/api/v1/similarity/"
#    mfccsw/4a1d9e0f-b268-4580-b30a-fe0cbd9e9705"

    def __init__(self, metric, mbid):
        '''
            The given recording mbid is the source track that will be looked up 
            in the annoy index using the passed metric.
        '''
        self.mbid = mbid
        self.metric = metric

    def outputs(self):
        return [Recording]

    def push(self, inputs):

        url = self.SERVER_URL + self.metric + "/" + self.mbid
        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        try:
            results = ujson.loads(r.text)
        except Exception as err:
            raise RuntimeError(str(err))


        entities = []
        for row in results:
            r = Recording(mbid=row['recording_mbid'], 
                          acousticbrainz={
                              'similarity': row['distance'], 
                              'offset' : row['offset']
                          }
                         )
            r.add_note("Related to %s" % self.mbid)
            entities.append(r)

        self.next_elements[0].push([entities])
