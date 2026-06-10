import sqlite3
import os

DB_PATH = "/home/claude/carmike_analysis/carmike_cinemas.db"

# Remove existing db if present
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ─────────────────────────────────────────────
# TABLE 1: annual_financials
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE annual_financials (
    year            INTEGER PRIMARY KEY,
    revenue_mil     REAL,       -- Total revenue in millions USD
    net_income_mil  REAL,       -- Net income (loss) in millions USD; NULL if unknown
    total_debt_mil  REAL,       -- Total debt in millions USD; NULL if unknown
    data_quality    TEXT,       -- 'confirmed' = direct SEC filing; 'derived' = calculated from partial data; 'estimated' = historical source
    source_note     TEXT        -- Brief citation
)
""")

financials = [
    # year, revenue, net_income, total_debt, quality, source
    (1987, 84.0,    3.0,    None,   'confirmed', 'FundingUniverse / Forbes 1988'),
    (1992, 172.0,   None,   None,   'confirmed', 'FundingUniverse company history'),
    (1993, 242.0,   None,   None,   'confirmed', 'FundingUniverse company history'),
    (1999, 487.0,   None,   650.0,  'confirmed', 'Encyclopedia.com company profile; debt at BK filing'),
    (2002, 504.0,   None,   None,   'derived',   'SEC 10-K: box office $342.8M = 68% of total'),
    (2004, 494.5,   None,   None,   'confirmed', 'Encyclopedia.com company profile'),
    (2007, 482.1,   -126.9, None,   'confirmed', 'SEC 10-K FY2007 (incl. goodwill impairment)'),
    (2008, 472.7,   -41.4,  392.3,  'confirmed', 'SEC 8-K Q4 2008 earnings release'),
    (2009, 514.7,   -15.4,  369.1,  'confirmed', 'SEC 8-K Q4 2009 earnings release'),
    (2010, 491.3,   None,   353.4,  'confirmed', 'SEC 8-K Q4 2010 earnings release'),
    (2011, 477.8,   -7.7,   315.4,  'confirmed', 'SEC 8-K Q4 2011 / Q4 2012 comparative'),
    (2012, 539.3,   96.3,   366.2,  'confirmed', 'SEC 8-K Q4 2012 (*net income includes $86.5M tax reversal)'),
    (2013, 533.9,   None,   311.4,  'confirmed', 'SEC 8-K Q4 2013 earnings release'),
    (2014, 689.9,   None,   352.0,  'confirmed', 'SEC 8-K Q4 2014 earnings release'),
    (2015, 804.4,   None,   337.0,  'confirmed', 'SEC 8-K Q4 2015 earnings release (record year)'),
]

cursor.executemany("""
INSERT INTO annual_financials
    (year, revenue_mil, net_income_mil, total_debt_mil, data_quality, source_note)
VALUES (?, ?, ?, ?, ?, ?)
""", financials)

# ─────────────────────────────────────────────
# TABLE 2: theater_scale
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE theater_scale (
    year            INTEGER PRIMARY KEY,
    theater_count   INTEGER,    -- Number of theaters operated
    screen_count    INTEGER,    -- Number of screens operated
    data_quality    TEXT,
    source_note     TEXT
)
""")

scale = [
    (1982, 105,  265,  'confirmed', 'Martin Theatres acquisition base'),
    (1983, 130,  350,  'estimated', 'Post-Video Independent Theatres acquisition (+85 screens)'),
    (1988, 216,  670,  'confirmed', 'FundingUniverse / Forbes 1988'),
    (1990, 175,  1000, 'confirmed', 'FundingUniverse: "nearly 1,000 total screens in about 175 markets"'),
    (1992, None, 1400, 'confirmed', 'FundingUniverse: "operating 1,400 movie screens"'),
    (1993, 388,  1560, 'confirmed', 'FundingUniverse: "388 theaters, 1,560 screens"'),
    (1995, None, 2223, 'confirmed', 'FundingUniverse: "2,223 screens" — briefly #1 in US'),
    (2000, 448,  2800, 'confirmed', 'Wikipedia / FundingUniverse: peak before BK filing'),
    (2002, 308,  2250, 'confirmed', 'Post-bankruptcy restructuring; closed ~140 theaters'),
    (2004, 310,  2450, 'confirmed', 'Encyclopedia.com company profile'),
    (2007, 264,  2400, 'confirmed', 'SEC 10-K FY2007'),
    (2008, 250,  2308, 'confirmed', 'SEC Q2 2008 earnings call transcript'),
    (2009, 245,  2278, 'confirmed', 'SEC 8-K Q4 2009 earnings release (average)'),
    (2016, 276,  2954, 'confirmed', 'Wikipedia / AMC acquisition filing, March 2016'),
]

cursor.executemany("""
INSERT INTO theater_scale
    (year, theater_count, screen_count, data_quality, source_note)
VALUES (?, ?, ?, ?, ?)
""", scale)

# ─────────────────────────────────────────────
# TABLE 3: key_events
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE key_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    year            INTEGER NOT NULL,
    event_label     TEXT NOT NULL,
    event_type      TEXT NOT NULL,  -- 'founding' | 'acquisition' | 'bankruptcy' | 'leadership' | 'external' | 'format_shift'
    event_detail    TEXT
)
""")

events = [
    (1982, 'Carmike Founded',                   'founding',     'Patrick family buys Martin Theatres from Fuqua Industries for $25M in LBO'),
    (1986, 'IPO on NASDAQ',                     'founding',     'Goes public; acquires Essantee Theatres (+209 screens)'),
    (1989, 'Consolidated Theatres acquired',    'acquisition',  'Adds 116 screens; revenues approaching $100M'),
    (1991, 'Excellence Theatres JV',            'acquisition',  'Joint venture adds 353 screens — biggest single leap in company history'),
    (1993, 'Manos Enterprises acquired',        'acquisition',  'Adds 80 screens; revenue jumps to $242M'),
    (1994, 'Cinema World + General Cinema',     'acquisition',  'Acquires 178 screens from Cinema World and 48 from General Cinema'),
    (1995, '#1 US cinema chain by screens',     'external',     'Reaches 2,223+ screens — briefly largest chain in US by screen count'),
    (1997, 'Hollywood Connection JV w/ Walmart','acquisition',  'Entertainment center concept; combined multiplex, skating rink, arcade'),
    (1998, 'Goldman Sachs invests $55M',        'external',     'Goldman buys 16% stake; company begins heavy borrowing for expansion'),
    (1999, '$200M senior subordinated notes',   'external',     'Issues $200M in 9.375% bonds; total debt reaches ~$650M'),
    (2000, 'Chapter 11 Bankruptcy',             'bankruptcy',   'Files Aug 8, 2000; missed $9M interest payment; owed ~$650M'),
    (2002, 'Emerges from bankruptcy',           'bankruptcy',   'Restructured; reduced to 308 theaters from 448'),
    (2005, 'GKC Theatres acquired',             'acquisition',  'Buys George Kerasotes Corp for $66M; adds 30 theaters, 263 screens'),
    (2007, 'Carl Patrick Sr. dies',             'leadership',   'Founder passes July 4, 2007'),
    (2009, 'Michael Patrick removed as CEO',    'leadership',   'Board removes Patrick; David Passman named interim then permanent CEO (June 2009)'),
    (2009, 'Avatar released — 3D boom begins',  'external',     'Dec 2009; drives record Q4 attendance; Carmike had 500+ 3D screens'),
    (2010, 'Mark Cuban 9.4% stake (2008)',      'external',     'Cuban acquired stake Dec 2008 for investment purposes'),
    (2012, 'Rave Cinemas acquisition',          'acquisition',  'Buys 16 theaters, 251 screens for $19M + $100.4M assumed leases; first IMAX screens'),
    (2013, 'Muvico acquisition',                'acquisition',  'Acquires 9 complexes, 147 screens; expands Florida presence'),
    (2013, 'Passman wins EY Entrepreneur of Year','leadership', 'SE Region Leadership award; peak of Passman era'),
    (2015, 'Sundance Cinemas acquired',         'acquisition',  'October 2015; adds premium arthouse locations'),
    (2016, 'AMC acquisition announced',         'acquisition',  'AMC offers $30/share; ~$1.1B deal including debt assumption'),
    (2016, 'AMC acquisition closes',            'acquisition',  'December 21, 2016; Carmike ceases to exist as independent entity'),
    (2017, 'Brand retired — becomes AMC Classic','founding',    'Carmike name retired May 2017; smaller locations rebranded AMC Classic'),
]

cursor.executemany("""
INSERT INTO key_events (year, event_label, event_type, event_detail)
VALUES (?, ?, ?, ?)
""", events)

# ─────────────────────────────────────────────
# TABLE 4: bryce_employment
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE bryce_employment (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location        TEXT NOT NULL,
    city            TEXT NOT NULL,
    state           TEXT NOT NULL,
    start_year      INTEGER NOT NULL,
    start_month     INTEGER NOT NULL,
    end_year        INTEGER NOT NULL,
    end_month       INTEGER NOT NULL,
    role            TEXT,
    notes           TEXT
)
""")

employment = [
    ('Carmike Cinemas Snellville',  'Snellville', 'GA', 2008, 8,  2012, 1,
     '2nd Assistant Manager',
     'Home market of CEO David Passman; worked with Aaron Passman (son) during his stint; rose from crew to 2nd assistant'),
    ('Carmike Cinemas Athens',      'Athens',     'GA', 2012, 1,  2013, 12,
     '1st Assistant Manager',
     '1st assistant directly below GM; departed Dec 2013'),
]

cursor.executemany("""
INSERT INTO bryce_employment
    (location, city, state, start_year, start_month, end_year, end_month, role, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", employment)

conn.commit()
conn.close()
print("✅ Database built successfully:", DB_PATH)
