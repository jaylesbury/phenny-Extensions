#!/usr/bin/env python2
# coding=utf-8
import re, web, sqlite3, bitly

def what(phenny, input):
   """.what - interface for what.cd"""
   db_conn = sqlite3.connect('modules/what.db')
   db_cur = db_conn.cursor()

   db_cur.execute('SELECT id FROM users WHERE name = "%s"' %  input.nick)
   user = db_cur.fetchone()

   if user is None:
      phenny.say('%s: sorry, you\'re not an authorised user' % input.nick)
      return
   else:
      userID = user[0]

   f = open ("modules/whatData.json")
   s = ""
   for line in f:
      s = s + line

   import simplejson
   decoder = simplejson.JSONDecoder()
   bLogin = decoder.decode(s)['bitly']['login']
   bApiKey = decoder.decode(s)['bitly']['apikey']

   import bitly
   api = bitly.Api(login=bLogin, apikey=bApiKey)

   try:
      args = input.group(2).rsplit(' ')
   except:
      if '.what' in input:
         phenny.say('%s: please specify find, add, genres, search, list or users' % input.nick)
         return
      else:
         args = (' ', ' ')

   if args[0] == 'search':
      if len(args) > 2:
         try:
            (url, searchRatio) = findTorrentPage(phenny, input)
            (artist, album, genre) = getTorrentDetails(url)
            phenny.say('%s: first result is "%s" (match: %.1f%%) | %s' % (input.nick, artist + u' - ' + album, searchRatio * 100, api.shorten(url))) 
         except SyntaxError:
            phenny.say('%s: found no results' % (input.nick))
            return
         except:
            phenny.say('%s: could not contact what.cd or malformed input' % input.nick)
            return
      else:
         phenny.say('%s: usage is .what search artist - album' % input.nick)
         return
   elif args[0] == 'add':
      if len(args) > 2:
         try:
            (url, searchRatio) = findTorrentPage(phenny, input)
            (artist, album, genre) = getTorrentDetails(url)
            if searchRatio < 0.9:
               phenny.say('%s: first result is "%s" [%s] (match %.1f%% too low, not adding)' % (input.nick, artist + u' - ' + album, api.shorten(url), searchRatio * 100))
               return
            else:
               phenny.say('%s: found "%s" (match: %.1f%%)' % (input.nick, artist + u' - ' + album, searchRatio * 100))
         except:
            return
      else:
         try:
            url = args[1]
            if 'what.cd' not in url:
               phenny.say('%s: url must point to what.cd' % input.nick)
               return
            if 'torrents.php' not in url:
               phenny.say('%s: url must point to a torrent' % input.nick)
               return
         except:
            phenny.say('%s: usage is .what add <url> or .what add artist - album' % input.nick)
            return

      try:
         shortUrl = api.shorten(url)
      except:
         phenny.say('%s: url appears malformed' % input.nick)
         return

      try:
         (artist, album, genre) = getTorrentDetails(url)
      except:
         phenny.say('%s: there was a problem parsing the given page' % input.nick)
         return

      try:
         db_cur.execute('SELECT id FROM genres WHERE name="%s"' % genre)
         genreID = db_cur.fetchone() 

         if genreID is None:
            db_cur.execute('INSERT INTO genres VALUES(null, "%s")' % genre)
            genreID = db_cur.lastrowid
         else:
            genreID = genreID[0]

         db_cur.execute('INSERT INTO recommendations VALUES(null, "%s", "%s", "%s", "%d", "%d")' % (artist, album, shortUrl, genreID, userID))
         db_conn.commit()

         phenny.say('%s: [%s - %s | %s | %s] added!' % (input.nick, artist, album, genre, shortUrl))

      except:
         phenny.say('%s: there was a problem communicating with the database' % input.nick)
         return

   elif args[0] == 'users':
      db_cur.execute('SELECT * FROM users');
      users = db_cur.fetchall()

      for user in users:
         db_cur.execute('SELECT id FROM recommendations WHERE user_id = %d' % user[0])
         entries = db_cur.fetchall()
         if entries is not None:
            numEntries = len(entries)
         else:
            numEntries = 0

         if numEntries == 1:
            strEnd = 'entry'
         else:
            strEnd = 'entries'

         phenny.say('%s: %d %s' % (user[1], numEntries, strEnd))

   elif args[0] == 'find':
      try:
         genre = args[1]
      except:
         phenny.say('%s: usage is .what find <genre> or .what find recent' % input.nick)
         return

      if args[1] == 'recent':
         try:
            db_cur.execute('SELECT r.id,artist,album,g.name,url,u.name FROM recommendations AS r LEFT JOIN users AS u ON r.user_id = u.id LEFT JOIN genres AS g ON r.genre_id = g.id ORDER BY r.id DESC LIMIT 3')
         except:
            phenny.say('%s: no recent recommendations!' % input.nick)
      else:
         try:
            db_cur.execute('SELECT r.id,artist,album,g.name,url,u.name FROM recommendations AS r LEFT JOIN users AS u ON r.user_id = u.id LEFT JOIN genres AS g ON r.genre_id = g.id WHERE g.name = "%s" ORDER BY r.id DESC LIMIT 3' % args[1])
         except:
            phenny.say('%s: no recommendations in database!' % input.nick)  
      
      recs = db_cur.fetchall()

      if len(recs) == 0:
         phenny.say('%s: no entries for genre "%s"' % (input.nick, genre))
         return

      for rec in recs:
         phenny.say('%d: %s - %s | %s | %s | %s' % (rec[0], rec[1], rec[2], rec[3], rec[4], rec[5]))

   elif args[0] == 'genres':
      db_cur.execute('SELECT name FROM genres ORDER BY name ASC');
      genres = db_cur.fetchall()

      if genres is None:
         phenny.say('%s: no genres in database!' % input.nick)
         return

      line = ''
      for genre in genres:
         line += genre[0] + ', '

      phenny.say('%s: %s' % (input.nick, line[:-2]))
      return
   else:
      args = input.split(' ')

      for arg in args:
         if 'what.cd/torrents.php?id=' in arg:
            try:
               (artist, album, genre) = getTorrentDetails(arg)
               phenny.say('%s: [%s - %s | %s | %s]' % (input.nick, artist, album, genre, api.shorten(arg)))
               return
            except:
               phenny.say('%s: there was a problem retrieving the torrent information' % input.nick)
               return
       
      phenny.say('%s: did not understand command' % input.nick)

what.commands = ['what']
what.priority = 'medium'
what.name = 'what'
#what.rule =  r'.*what\.cd/torrents\.php\?id=.*'

def findTorrentPage(phenny, input):
   import urllib
   from BeautifulSoup import BeautifulSoup, SoupStrainer
   from Levenshtein import ratio

   if '-' not in input.group(2):
      raise Exception()
      return

   (artist, album) = input.group(2).split('-')
   functionEnd = artist.find(' ')
   artist = artist[functionEnd + 1:].strip()
   album = album.strip()
   searchString = artist + u' - ' + album

   data = {'artistname' : artist, 'groupname' : album}
   data = urllib.urlencode(data)
   url = 'https://ssl.what.cd/torrents.php?action=advanced&' + data

   html = getHTML(url)

   tableStrainer = SoupStrainer(id='torrent_table')
   tableResults = BeautifulSoup(html, tableStrainer)

   firstArtist = tableResults.find('a', href=re.compile('artist.php\?id\='))
   
   if firstArtist is None:
      raise SyntaxError()
      return

   foundArtist = firstArtist.string
   foundAlbum = firstArtist.next.next.next.string

   foundString = foundArtist + ' - ' + foundAlbum
   searchRatio = ratio(searchString.lower(), foundString.lower())

   return ('https://ssl.what.cd/' + tableResults.find('a', href=re.compile('torrents.php\?id\='))['href'], searchRatio)

def getHTML(url):
   f = open ("modules/whatData.json")
   s = ""
   for line in f:
      s = s + line

   import simplejson
   decoder = simplejson.JSONDecoder()
   wSession = decoder.decode(s)['what']['cookie']


   import urllib2
   opener = urllib2.build_opener()
   opener.addheaders.append(('Cookie', wSession))
   response = opener.open(url)
   return response.read()

def getTorrentDetails(url):
   from BeautifulSoup import BeautifulSoup, SoupStrainer

   html = getHTML(url)
   spanResults = BeautifulSoup(html)
   ltrSpan = spanResults.find('span', {'dir' : 'ltr'})

   if ltrSpan == None:
      raise Exception
      return

   if 'artist.php' not in ltrSpan.next.attrs[0][1] or ('Album' not in ltrSpan.nextSibling and 'Anthology' not in ltrSpan.nextSibling and 'Compilation' not in ltrSpan.nextSibling and 'Single' not in ltrSpan.nextSibling and 'Soundtrack' not in ltrSpan.nextSibling and 'EP' not in ltrSpan.nextSibling):
      raise Exception
      return

   tagStrainer = SoupStrainer('a', href=re.compile('torrents.php\?taglist\='))
   tagResults = BeautifulSoup(html, tagStrainer)

   artist = ''

   for element in ltrSpan.contents[:-1]:
      try:
         artist += element.string
      except:
         artist += element

   album = ltrSpan.contents[-1][3:]
   genre = tagResults.first().string

   return (unescape(artist), unescape(album), genre)

def unescape(text):
    import htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

if __name__ == '__main__': 
   print __doc__.strip()
