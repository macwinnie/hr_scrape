#!/usr/bin/env python3

import argparse, os, pync, re, requests, sqlite3
from bs4 import BeautifulSoup

# prepare database
con      = sqlite3.connect('database.db')
cursor   = con.cursor()
checkSQL = "SELECT name FROM sqlite_master WHERE type='table';"
cursor.execute( checkSQL )
if cursor.fetchall() == []:
    createSQL = [
        """
CREATE TABLE IF NOT EXISTS sources (
  aktion  TEXT,
  gkz     TEXT,
  regart  TEXT,
  regnr   TEXT,
  gkz_alt TEXT,
  titel   TEXT
);
""",
        """
CREATE TABLE IF NOT EXISTS entries (
  source_id    INTEGER,
  url          TEXT,
  changedate   TEXT,
  beschreibung TEXT
);
"""
    ]
    for sql in createSQL:
        cursor.execute( sql )
    con.commit()

# definiton of parameters and their meaning
params = [
    {
        "short": "a",
        "long":  "aktion"
    },
    {
        "short": "z",
        "long":  "gkz"
    },
    {
        "short": "r",
        "long":  "regart"
    },
    {
        "short": "n",
        "long":  "regnr"
    },
    {
        "short": "k",
        "long":  "gkz_alt"
    },
    {
        "short": "t",
        "long":  "titel"
    },
]

# fetch environmental variables
from dotenv   import load_dotenv
load_dotenv()
envs = {}
for p in params:
    envs[ p[ 'long' ] ] = os.getenv( p[ 'long' ] )

# fetch script call parameters
parser = argparse.ArgumentParser()
for p in params:
    parser.add_argument( '-' + p[ 'short' ], type=str, nargs='?', help=p[ 'long' ] )

args   = parser.parse_args()

# fetching the actual values
vals = {}
for p in params:
    # default to empty string
    vals[ p[ 'long' ] ] = ""
    h = getattr(args, p[ 'short' ])
    # arguments first
    if h != None:
        vals[ p[ 'long' ] ] = h
    # environmental variables second
    elif envs[ p[ 'long' ] ]:
        vals[ p[ 'long' ] ] = envs[ p[ 'long' ] ]

# fetch sources ID from DB – or create
sql       = "SELECT rowid FROM sources WHERE aktion = ? AND gkz = ? AND regart = ? AND regnr = ? AND gkz_alt = ? LIMIT 1;";
cursor.execute( sql, ( vals[ 'aktion' ], vals[ 'gkz' ], vals[ 'regart' ], vals[ 'regnr' ], vals[ 'gkz_alt' ] ) )
try:
    source_id = cursor.fetchone()[0]
except:
    sql       = "INSERT INTO sources (aktion, gkz, regart, regnr, gkz_alt, titel) VALUES (?, ?, ?, ?, ?, ?);";
    cursor.execute( sql, ( vals[ 'aktion' ], vals[ 'gkz' ], vals[ 'regart' ], vals[ 'regnr' ], vals[ 'gkz_alt' ], vals[ 'titel' ] ) )
    con.commit()
    source_id = cursor.lastrowid

# fetch sources title
sql   = "SELECT titel FROM sources WHERE rowid = ?"
cursor.execute( sql, [ source_id ] )
titel = cursor.fetchone()[0]
del vals[ 'titel' ]

# define our request session
requestSession = requests.Session()
refererUrl     = "https://www.handelsregister.de/"
publicationUrl = "https://www.handelsregisterbekanntmachungen.de/"
announcement   = "skripte/hrb.php?"
# handelsregisterbekanntmachungen.de needs the referer to be defined
requestSession.headers.update( { 'referer': refererUrl } )
# after that, we can access the results page
# (since we named the variables within the vals like the url params, we can simply join them)
requestPath    = "index.php?" + '&'.join( ['{}={}'.format(k,v) for k,v in vals.items()] )
result         = requestSession.get( publicationUrl + requestPath )
soup           = BeautifulSoup( result.content, 'html.parser' )

# retrieve all publications
relevants = []
for a in soup.find_all('a'):
    try:
        if re.match( r'javascript:NeuFenster', a.get( 'href' ) ):
            relevants.append( a )
    except TypeError as e:
        # invalid usage of an `a` Tag – but that's normal at handelsregister.de ...
        pass
        # # to retrieve the type of an error:
        # print( type(e).__name__ )

# alert for new ones and store them in SQLite
checkSQL  = "SELECT rowid FROM entries WHERE source_id = ? AND url = ?"
insertSQL = "INSERT INTO entries (source_id, url, changedate, beschreibung) VALUES (?, ?, ?, ?);"
headline  = "News im Handelsregister …"
for a in relevants:
    m   = re.search( r'\(\'(.*?)\'\)', a.get( 'href' ) );
    url = m.group(1)
    cursor.execute( checkSQL, ( source_id, url ) )
    try:
        row_id = cursor.fetchone()[0]
    except:
        content      = a.get_text( separator = "\n" ).split( "\n" )
        changedate   = content[0]
        beschreibung = "\n".join( content[1:] )
        cursor.execute( insertSQL, ( source_id, url, changedate, beschreibung ) )
        con.commit()
        pync.notify( beschreibung, open = publicationUrl + announcement + url, title = headline, subtitle = titel + ' (' + changedate + ')')

con.close()
