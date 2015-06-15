#!/usr/bin/python2
import os
from xml.sax import make_parser, handler
from hashlib import md5
import codecs 
import sqlite3
import json
import re
import gzip
kanji_dic = dict()
count = 0
attr_names = dict()
fpath=os.path.dirname(os.path.realpath(__file__))
class Kanji:

    def __init__(self):
        self.kanji = None
        self.attrs = dict()
        self.attrs["radical_no"] = []
        self.attrs["on_yomi"] = []
        self.attrs["kun_yomi"] = []
        self.attrs["radname"] = []
        self.attrs["meaning_de"] = []
        self.attrs["meaning_en"] = []
        self.attrs["nanori"] = []
        self.attrs["radicals"] = []

    def add_attr(self,name,attr):
        global attr_names
        attr = re.sub("\"","'",attr)
        if name in self.attrs and type(self.attrs[name]) == type([]):
            self.attrs[name].append(attr)
        else:
            self.attrs[name] = attr
        if name not in attr_names:
            attr_names[name]=type(self.attrs[name])

    def get_attr_str(self,name):
        if type(self.attrs[name]) == type([]):
            return ", ".join(self.attrs[name])
        else:
            return self.attrs[name]

    def __unicode__(self):
        return self.kanji


class Kanjidic2_Handler(handler.ContentHandler):

    def __init__(self):
        self.content = ""
        self.elementStartHandler = { "character": self.characterS,
            "rad_value" : self.rad_valueS,
            "dic_ref" : self.dic_refS,
            "reading" : self.readingS,
            "meaning" : self.meaningS
        }
        
        self.elementEndHandler = { "character" : self.characterE,
            "literal" : self.literalE,
            "stroke_count" : self.strokesE,
            "rad_value" : self.rad_valueE,
            "jlpt" : self.jlptE,
            "grade" : self.gradeE,
            "freq" : self.freqE,
            "rad_name" : self.rad_nameE,
            "dic_ref" : self.dic_refE,
            "reading" : self.readingE,
            "meaning" : self.meaningE,
            "nanori" : self.nanoriE
        }

        self.number=0

    def add_attr(self,name):
        self.kanji.add_attr(name,self.content)

    def characterS(self,attrs):
        self.kanji=Kanji()
    
    def rad_valueS(self,attrs):
        self.radType = attrs["rad_type"]

    def dic_refS(self,attrs):
        self.dicType = attrs["dr_type"]

    def readingS(self,attrs):
        self.readType = attrs["r_type"]
    
    def meaningS(self, attrs):
        if "m_lang" in attrs:
            self.mLang = attrs["m_lang"]
        else: 
            self.mLang = "en"

    def characterE(self):
        global count
        count +=1
        global kanji_dic
        kanji_dic[self.kanji.kanji] = self.kanji
    
    def literalE(self):
        self.kanji.kanji=self.content

    def rad_valueE(self):
        if self.radType == "classical":
            self.add_attr("radical_no")
    
    def jlptE(self):
        self.add_attr("jlpt")

    def gradeE(self):
        self.add_attr("grade")

    def freqE(self):
        self.add_attr("freq")
    
    def rad_nameE(self):
        self.add_attr("radname")

    def dic_refE(self):
        if self.dicType == "heisig":
            self.add_attr("heisig")
        elif self.dicType == "heisig6":
            self.add_attr("heisig6")
        elif self.dicType == "halpern_kkld_2ed":
            self.add_attr("halpern2")
        elif self.dicType == "sh_kk":
            self.add_attr("hadimitzky")
    
    def readingE(self):
        if self.readType == "ja_on":
            self.add_attr("on_yomi")
        elif self.readType == "ja_kun":
            self.add_attr("kun_yomi")
        
    def meaningE(self):
        if self.mLang == "en":
            self.add_attr("meaning_en")
        elif self.mLang == "de":
            self.add_attr("meaning_de")
    
    def nanoriE(self):
        self.add_attr("nanori")

    def strokesE(self):
        self.add_attr("strokes")

    def startElement(self, name, attrs):
        self.content = ""
        if name in self.elementStartHandler:
            self.elementStartHandler[name](attrs)

    def endElement(self, name):
        if name in self.elementEndHandler:
            self.elementEndHandler[name]()

    def characters(self,content):
        self.content += content.strip()
    
def readkanji_dic():
    global fpath
    parser = make_parser()
    parser.setContentHandler(Kanjidic2_Handler())
    xmlfile = gzip.open(fpath+"/data/kanjidic2.xml.gz")
    parser.parse(xmlfile)


def readradicals():
    global count
    global fpath
    count = 0
    with codecs.getreader("utf-8")(gzip.open(fpath+"/data/kradfile-u.gz","r")) as f:
        for line in f:
            if not line.startswith("#"):
                count +=1
                l = line.split()
                k = l[0]
                if k not in kanji_dic:
                    kanji_dic[k] = Kanji()
                    kanji_dic[k].kanji = k
                for r in l[2:]:
                    kanji_dic[k].add_attr("radicals",r)


def readheisiganki():
    global kanji_dic
    global count
    global fpath
    count = 0
    conh = sqlite3.connect(fpath+"/data/heisig-ger.anki2")
    ch = conh.cursor()
    ch.execute("SELECT models FROM col")
    m=ch.fetchone()
    models = json.loads(m[0])
    fields = models.items()[0][1]["flds"]
    fnames = []
    for i in fields:
        fnames.append(i["name"])
    ch.execute("SELECT flds FROM notes")
    notes = ch.fetchall()
    for row in notes:
        count += 1
        fval = row[0].split("\x1f")
        fdic=dict(zip(fnames,fval))
        k=fdic["Kanji"]
        if k not in kanji_dic:
            kanji_dic[k] = Kanji()
            kanji_dic[k].kanji=k
        kanji_dic[k].add_attr("heisig_mean_de",fdic["Bedeutung"])
        kanji_dic[k].add_attr("heisig_mean_prim_de",fdic["Primiv Bedeutung"])
        kanji_dic[k].add_attr("heisig_lesson_ger",fdic["Lesson number"])
        kanji_dic[k].add_attr("heisig_ger",fdic["Heisig number"])

    
def generatedb():
    global count
    global kanji_dic
    global fpath
    count = 0
    conkdb = sqlite3.connect(fpath+"/data/jpdb")
    c = conkdb.cursor()
    tkeys = ", ".join(attr_names.keys())
    c.execute("CREATE TABLE IF NOT EXISTS kanji ("+"kanji PRIMARY_KEY, meaning_de, "+tkeys+")")
    for k in kanji_dic:
        count += 1
        keys = ",".join(kanji_dic[k].attrs.keys())
        values = ", ".join("\""+kanji_dic[k].get_attr_str(v)+"\"" for v in kanji_dic[k].attrs.keys())
        c.execute("INSERT INTO kanji (kanji, "+ keys +") values (\""+k+"\""+", "+values+")") 
    conkdb.commit()


readkanji_dic()
print count, "kanji read from kanji_dic"
readradicals()
print count, "kanji read from radicals"
readheisiganki()
print count, "read from heisig anki file"
generatedb()
print count, "inserted to database"
