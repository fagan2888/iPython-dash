import requests, sqlite3, os, urllib, urllib2
from bs4 import BeautifulSoup as bs


# CONFIGURATION
docset_name = 'iPython.docset'
output = docset_name + '/Contents/Resources/Documents/'

# create docset directory
if not os.path.exists(output): os.makedirs(output)

# add icon
icon = 'http://winpython.googlecode.com/hg-history/ff40ef9edcde3e5e93f1262f60bb6f68975d9143/portable/icons/ipython.ico'
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, path):
  typ = 'Guide'
  if path.startswith('notebook') or path.startswith('interactive') or path.startswith('parallel'):
    typ = 'func'
  if path.startswith('install/'):
    typ = 'Instruction'
  if path.startswith('whatsnew/'):
    typ = 'Section'

  path = 'ipython.readthedocs.org/en/master/' + path
  
  cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
  fetched = cur.fetchone()
  if fetched is None:
      cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
      print('DB add >> name: %s, path: %s' % (name, path))
  else:
      print("record exists")


def add_urls():
 
  root_url = 'https://ipython.readthedocs.org/en/master/'
 
  # start souping index_page
  data = requests.get(root_url).text
  soup = bs(data)

  # collected needed pages and their urls
  for link in soup.findAll('a'):
    name = link.text.strip()
    path = link.get('href')
    if path is not None and name and not path.startswith('http') and not path.startswith('/') and not path.startswith('github-') and not path.startswith('#'):
        update_db(name, path)


def add_infoplist():
  name = docset_name.split('.')[0]
  info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
         "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
         "<plist version=\"1.0\"> " \
         "<dict> " \
         "    <key>CFBundleIdentifier</key> " \
         "    <string>{0}</string> " \
         "    <key>CFBundleName</key> " \
         "    <string>{1}</string>" \
         "    <key>DocSetPlatformFamily</key>" \
         "    <string>{2}</string>" \
         "    <key>isDashDocset</key>" \
         "    <true/>" \
         "    <key>isJavaScriptEnabled</key>" \
         "    <true/>" \
         "    <key>dashIndexFilePath</key>" \
         "    <string>{3}</string>" \
         "</dict>" \
         "</plist>".format(name, name, name, 'ipython.readthedocs.org/en/master/' + 'index.html')
  open(docset_name + '/Contents/info.plist', 'wb').write(info)

db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
cur = db.cursor()
try:
    cur.execute('DROP TABLE searchIndex;')
except:
    pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
# start
add_urls()
add_infoplist()

# # commit and close db
db.commit()
db.close()
