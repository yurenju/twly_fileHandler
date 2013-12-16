#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import codecs
import psycopg2
import json
import db_ly

def Legislator(legislator):
    complement = {"former_names":''}
    complement.update(legislator)
    c.execute('''UPDATE legislator_legislator
        SET name = %(name)s, former_names = %(former_names)s
        WHERE uid = %(uid)s''', complement
    )
    c.execute('''INSERT INTO legislator_legislator(uid, name, former_names)
        SELECT %(uid)s, %(name)s, %(former_names)s
        WHERE NOT EXISTS (SELECT 1 FROM legislator_legislator WHERE uid = %(uid)s)''', complement
    )

def LegislatorDetail(uid, term, ideal_term_end_year):
    complement = {"uid":uid, "gender":'', "party":'', "caucus":'', "contacts":None, "term_start":None, "term_end":{"date": '%04d-01-31' % int(ideal_term_end_year)}, "education":None, "experience":None, "remark":None, "image":'', "links":None}
    complement.update(term)
    c.execute('''UPDATE legislator_legislatordetail
        SET name = %(name)s, gender = %(gender)s, party = %(party)s, caucus = %(caucus)s, constituency = %(constituency)s, in_office = %(in_office)s, contacts = %(contacts)s, term_start = %(term_start)s, term_end = %(term_end)s, education = %(education)s, experience = %(experience)s, remark = %(remark)s, image = %(image)s, links = %(links)s
        WHERE legislator_id = %(uid)s and ad = %(ad)s''', complement
    )
    c.execute('''INSERT into legislator_legislatordetail(legislator_id, ad, name, gender, party, caucus, constituency, in_office, contacts, term_start, term_end, education, experience, remark, image, links)
        SELECT %(uid)s, %(ad)s, %(name)s, %(gender)s, %(party)s, %(caucus)s, %(constituency)s, %(in_office)s, %(contacts)s, %(term_start)s, %(term_end)s, %(education)s, %(experience)s, %(remark)s, %(image)s, %(links)s
        WHERE NOT EXISTS (SELECT 1 FROM legislator_legislatordetail WHERE legislator_id = %(uid)s and ad = %(ad)s )''', complement
    )
 
def Committees(committees):
    c.executemany('''INSERT INTO committees_committees(name)
        SELECT %(name)s
        WHERE NOT EXISTS (SELECT 1 FROM committees_committees WHERE name = %(name)s)''', committees
    )

def Legislator_Committees(legislator_id, committee):
    c.execute("SELECT id FROM committees_committees WHERE name = %(name)s", committee)
    committee_id = c.fetchone()[0]
    complement = {"legislator_id":legislator_id, "committee_id":committee_id}
    complement.update(committee)
    c.execute('''UPDATE committees_legislator_committees
        SET committee_id = %(committee_id)s, chair = %(chair)s
        WHERE legislator_id = %(legislator_id)s and ad = %(ad)s and session = %(session)s''', complement
    )
    c.execute('''INSERT INTO committees_legislator_committees(legislator_id, committee_id, ad, session, chair)
        SELECT %(legislator_id)s, %(committee_id)s, %(ad)s, %(session)s, %(chair)s
        WHERE NOT EXISTS (SELECT 1 FROM committees_legislator_committees WHERE legislator_id = %(legislator_id)s and committee_id = %(committee_id)s and ad = %(ad)s and session = %(session)s )''', complement
    )
   
conn = db_ly.con()
c = conn.cursor()

f = codecs.open('no_committees.txt','w', encoding='utf-8')
dict_list = json.load(open('merged.json'))
ideal_term_end_year = {"1":1993, "2":1996, "3":1999, "4":2002, "5":2005, "6":2008, "7":2012, "8":2016}
for legislator in dict_list:
    Legislator(legislator)
    for term in legislator["each_term"]:
        LegislatorDetail(legislator["uid"], term, ideal_term_end_year[str(term["ad"])])
        if term.get("committees"):
            Committees(term["committees"])
            for committee in term["committees"]:
                Legislator_Committees(legislator["uid"], committee)
        else:
            f.write('no committees!!, uid: %s, name: %s, ad: %s\n' % (legislator["uid"], term["name"], term["ad"]))
f.close()
conn.commit()
print 'Succeed'
