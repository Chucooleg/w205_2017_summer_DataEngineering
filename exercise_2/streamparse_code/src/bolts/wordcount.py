from __future__ import absolute_import, print_function, unicode_literals

from collections import Counter
from streamparse.bolt import Bolt

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class WordCounter(Bolt):

    def initialize(self, conf, ctx):
        self.counts = Counter()
        self.conn = psycopg2.connect(database="tcount", user="postgres", password="pass", host="localhost", port="5432")

    def process(self, tup):

        word = tup.values[0]
        word = str(word) # convert unicode word to regular string
        

        # Write codes to increment the word count in Postgres
        # Use psycopg to interact with Postgres
        # Database name: Tcount 
        # Table name: Tweetwordcount 
        # you need to create both the database and the table in advance.
        cur = self.conn.cursor()

        cur.execute("UPDATE tweetwordcount SET count=count+1 WHERE word=%s", (word,))
        if cur.rowcount ==0 :
            try:
                cur.execute("INSERT INTO tweetwordcount (word,count) VALUES (%s, 1)", (word, ))
            except:
                print ("Error: New word insertion into postgres database failed")
                exit(1)


        self.conn.commit()

        # Increment the local count
        self.counts[word] += 1
        self.emit([word, self.counts[word]])

        # Check if db count is larger than local count
        cur = self.conn.cursor()

        cur.execute("SELECT count FROM tweetwordcount WHERE word=%s", (word,))
        record = cur.fetchall()[0]       
        if self.counts[word] > record[0]:
            print ("Error: Postgres databaese count udpdate problem")
            exit(1)


        # Log the count - just to see the topology running
        self.log('%s: %d' % (word, self.counts[word]))


