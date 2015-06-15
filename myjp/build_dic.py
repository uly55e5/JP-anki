#!/usr/bin/python2

import re
import codecs
import sqlite3
from xml.sax import make_parser, handler
import gzip
import os

jp_dic =dict()
count = 0
attr_names=[]
fpath=os.path.dirname(os.path.realpath(__file__))

class Entry:
    def __init__(self,entry):
        self.entry = entry
        self.attrs = { "JM_keb" : "",
            "JM_reb" : "",
            "JM_kinf" : "",
            "JM_rinf" : "",
            "JM_en_sense" : "",
            "JM_de_sense" : "",
            "JM_gram" : "",
            "watransl" : "",
            "wareading" : ""
        }

    def add_attr(self,name,value):
        global attr_names
        if name not in attr_names:
            attr_names.append(name)
        if self.attrs[name] == "":
            self.attrs[name] = value
        else:
            self.attrs[name] += ", "+value

    def get_attr_str(self,name):
        return self.attrs[name]

def readwadokujt():
    global count
    global jp_dic
    global fpath
    count = 0
    with codecs.getreader("utf8")(gzip.open(fpath+"/data/wadokujt_ed.utf8.gz","r")) as f:
        for line in f:
            if not line.startswith("?"):
                count +=1
                m = re.search(r"(.*) \[(.*)\] (.*$)",line)
                keyword = m.group(1)
                if keyword in jp_dic:
                    entry = jp_dic[keyword]
                else:
                    entry =  Entry(keyword)
                entry.add_attr("wareading",m.group(2))
                entry.add_attr("watransl",re.sub("/"," ",re.sub("(?<![\]\}\)])\/(?![\[\{\(]|$)",", ",re.sub("^/","",m.group(3)))).strip())
                jp_dic[keyword] =entry

class JMdict_Handler(handler.ContentHandler):

    def __init__(self):
        self.content = ""
        self.elementStartHandler = { "entry": self.entryS,
            "gloss" : self.glossS
        }
        
        self.elementEndHandler = { "keb": self.kebE,
            "ke_inf" : self.ke_infE,
            "reb" : self.rebE,
            "re_inf" : self.re_infE,
            "pos" : self.posE,
            "gloss" : self.glossE,
            "entry" : self.entryE
        }

    def entryS(self,attrs):
        self.keyword=""

    def glossS(self,attrs): 
        if "xml:lang" in attrs:
            self.lang = attrs["xml:lang"]
        else:
            self.lang = "eng"

    def kebE(self):
        global jp_dic
        if self.keyword=="":
            self.keyword=self.content
            if self.keyword in jp_dic:
                self.entry=jp_dic[self.keyword]
            else:
                self.entry=Entry(self.keyword)
        self.entry.add_attr("JM_keb",self.content)

    def ke_infE(self):
        self.entry.add_attr("JM_kinf",self.content)

    def rebE(self):
        global jp_dic
        if self.keyword=="":
            self.keyword=self.content
            if self.keyword in jp_dic:
                self.entry=jp_dic[self.keyword]
            else:
                self.entry=Entry(self.keyword)
        self.entry.add_attr("JM_reb",self.content)

    def re_infE(self):
        self.entry.add_attr("JM_rinf",self.content)

    def posE(self):
        self.entry.add_attr("JM_gram",self.content)

    def glossE(self):
        if self.lang=="eng":
            self.entry.add_attr("JM_en_sense",self.content)
        elif self.lang == "ger":
            self.entry.add_attr("JM_de_sense",self.content)

    def entryE(self):
        global jp_dic
        global count
        count += 1
        jp_dic[self.keyword] = self.entry

    def startElement(self, name, attrs):
        self.content = ""
        if name in self.elementStartHandler:
            self.elementStartHandler[name](attrs)

    def endElement(self, name):
    
        if name in self.elementEndHandler:
            self.elementEndHandler[name]()

    def characters(self,content):
        self.content += content.strip()

def readjmdic():
        global count
        global fpath
        count = 0
        parser = make_parser()
        parser.setContentHandler(JMdict_Handler())
        parser.parse(gzip.open(fpath+"/data/JMdict.gz"))

def generatedb():
    global count
    global jp_dic
    global fpath
    count = 0
    concdb = sqlite3.connect(fpath+"/data/jpdb")
    c = concdb.cursor()
    tkeys = ", ".join(attr_names)
    c.execute("CREATE TABLE IF NOT EXISTS jpdic ("+"keyword PRIMARY_KEY, "+tkeys+")")
    for j in jp_dic:
        count += 1
        keys = ",".join(jp_dic[j].attrs.keys())
        values = ", ".join("\""+re.sub("\"","",jp_dic[j].get_attr_str(v))+"\"" for v in jp_dic[j].attrs.keys())
        if j=="\"":
            j="''"
        c.execute("INSERT INTO jpdic (keyword, "+ keys +") values (\""+j+"\""+", "+values+")") 
    concdb.commit()



readwadokujt()
print count, "keywords read from wadoku"
print len(jp_dic), "added to dic"

readjmdic()
print count, "keywords read from jmdict"
print len(jp_dic), "in dic"

generatedb()
print count, "written to database"

