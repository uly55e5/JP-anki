# -*- coding: utf-8 -*-
import anki.stdmodels
from anki.hooks import addHook
from aqt import mw
import sqlite3
import os
nomecab=False
try:
    from japanese.reading import mecab
except:
    nomecab=True
def addJpVocabularyModel(col):
    models = col.models
    km = models.new(_("JP Vocabulary"))
    f = models.newField(_("Kanji Reading"))
    models.addField(km,f)
    f = models.newField(_("Reading"))
    models.addField(km,f)
    f = models.newField(_("Reading (Mecab)"))
    models.addField(km,f)
    f = models.newField(_("Reading (JMDict)"))
    models.addField(km,f)
    f = models.newField(_("Reading (Wadoku)"))
    models.addField(km,f)
    f = models.newField(_("Minna no nihongo Lesson"))
    models.addField(km,f)
    f = models.newField(_("Meaning DE"))
    models.addField(km,f)
    f = models.newField(_("Meaning DE (JMDict)"))
    models.addField(km,f)
    f = models.newField(_("Meaning DE (Wadoku)"))
    models.addField(km,f)
    f = models.newField(_("Meaning EN"))
    models.addField(km,f)
    f = models.newField(_("JLPT"))
    models.addField(km,f)
    f = models.newField(_("K Heisig Numbers"))
    models.addField(km,f)
    f = models.newField(_("K Halpern Numbers"))
    models.addField(km,f)
    f = models.newField(_("K Hadimitzky Numbers"))
    models.addField(km,f)
    f = models.newField(_("Politeness Level"))
    models.addField(km,f)
    f = models.newField(_("Extra"))
    models.addField(km,f)
    f = models.newField(_("Grammar"))
    models.addField(km,f)
    km['css'] += u"""\
.card {
font-family: arial;
font-size: 20px;
text-align: center;
color: black;
background-color: white;
}
.info {text-align: left; font-size: 20px;}
.left {text-align: left; }
.jp { font-size: 30px }
.big { font-size: 50px; }
.huge { font-size: 70px; }
.headline {font-size: 40px }
.win .jp { font-family: "MS Mincho"; }
.mac .jp { font-family: "Hiragino Mincho Pro"; }
.linux .jp .jpbig{ font-family: "Kochi Mincho"; }
.mobile .jp { font-family: "Hiragino Mincho ProN"; }"""
    t =models.newTemplate(_("Meaning"))
    t['qfmt'] = """\
({{Card}})
<br><br>
<div class=big>{{Kanji Reading}}</div><br>
{{#Reading (Mecab)}}{{hint:furigana:Reading (Mecab)}}{{/Reading (Mecab)}}
{{^Reading (Mecab)}}{{hint:Reading}}{{/Reading (Mecab)}}
<hr><div class=info>MNN: <b>{{Minna no nihongo Lesson}}</b> JLPT: <b>{{JLPT}}</b></div>"""
    t['afmt'] = """\
<div class=big>{{Kanji Reading}}</div>
<hr>{{Meaning DE}}<br><hr>
Zusatzinfo: {{Extra}}<br>
Hoeflickeit: {{Politeness Level}}
<hr>
<b>Kanji:</b> Heisig: <b>{{K Heisig Numbers}}</b> Hadamitzky: <b>{{K Hadimitzky Numbers}}</b> Halpern: <b>{{K Halpern Numbers}}</b>"""
    models.addTemplate(km,t)
    t=models.newTemplate(_("Reading"))
    t['qfmt'] = """\
({{Card}})
<br><br>
<div class=big>{{Kanji Reading}}</div>
<hr><div class=info>MNN: <b>{{Minna no nihongo Lesson}}</b> JLPT: <b>{{JLPT}}</b></div>"""
    t['afmt'] = """\
<div class=big>
{{#Reading (Mecab)}}{{furigana:Reading (Mecab)}}{{/Reading (Mecab)}}
{{^Reading (Mecab)}}{{Reading}}<br>{{Kanji Reading}}{{/Reading (Mecab)}}
</div><hr>{{Meaning DE}}<br><hr>
<b>Kanji:</b> Heisig: <b>{{K Heisig Numbers}}</b> Hadamitzky: <b>{{K Hadimitzky Numbers}}</b> Halpern: <b>{{K Halpern Numbers}}</b>"""
    models.addTemplate(km,t)
    t =models.newTemplate(_("Meaning reverse"))
    t['qfmt'] = """\
({{Card}})<br><br>
<div class=jp>{{Meaning DE}}</div>
<hr>
Zusatzinfo: {{Extra}}<br>
Hoeflickeit: {{Politeness Level}}
<hr><div class=info>MNN: <b>{{Minna no nihongo Lesson}}</b> JLPT: <b>{{JLPT}}</b></div>"""
    t['afmt'] = """\
<div class=big>{{furigana:Reading (Mecab)}}</div>
<hr>{{Meaning DE}}<br><hr>
<b>Kanji:</b> Heisig: <b>{{K Heisig Numbers}}</b> Hadamitzky: <b>{{K Hadimitzky Numbers}}</b> Halpern: <b>{{K Halpern Numbers}}</b>"""
    models.addTemplate(km,t)
    models.add(km)
    return km

fields2dbMap = { "Kanji Reading": "keyword",
    "Reading" : ["wareading","JM_reb"],
    "Reading (Mecab)" : 'gen_reading',
    "Reading (JMDict)" : 'JM_reb',
    "Reading (Wadoku)" : 'wareading',
    "Minna no nihongo Lesson" : 'mnn_lesson',
    "Meaning DE" : ['watransl','JM_de_sense'],
    "Meaning DE (JMDict)" : 'JM_de_sense',
    "Meaning DE (Wadoku)" : 'watransl',
    "Meaning EN" : 'JM_en_sense',
    "K Heisig Numbers" : ['heisig_ger','heisig6','heisig'],
    "K Halpern Numbers" : 'halpern2',
    "K Hadimitzky Numbers" : 'hadimitzky',
    "JLPT" : 'jlpt',
    "Politeness Level" : 'polite',
    "Extra" : 'extra',
    "Grammar" : 'JM_gram'
}

def onFocusLost(flag, n, fidx):
    if (n.model()["name"].startswith("JP Vocabulary")):
        if mw.col.models.fieldNames(n.model()).index("Kanji Reading") == fidx:
            keyword = mw.col.media.strip(n["Kanji Reading"])
            if keyword != "":
                conkdb = sqlite3.connect("../../addons/myjp/data/jpdb")
                conkdb.row_factory = sqlite3.Row
                c = conkdb.cursor()
                keywords=(keyword,)
                if not nomecab:
                    n["Reading (Mecab)"] = mecab.reading(keyword)
                c.execute("SELECT * FROM jpdic WHERE keyword=?",keywords)
                row = c.fetchone()
                for f in fields2dbMap:
                    if n[f] == "":
                        if f.startswith("K "):
                            for i in range(0,len(keyword)):
                                k =  keyword[i]
                                c.execute("SELECT * FROM kanji WHERE kanji=?",k)
                                krow = c.fetchone()
                                if krow and type(fields2dbMap[f]) == type([]):
                                    for k in fields2dbMap[f]:
                                        if k not in krow.keys() or krow[k] == "":
                                            continue
                                        else:
                                            if n[f] != "":
                                                n[f] +=", "
                                            n[f] += krow[k]
                                            break
                                if krow and fields2dbMap[f] in krow.keys():
                                    if n[f] != "":
                                        n[f] +=", "
                                    n[f] += krow[fields2dbMap[f]]
                        elif row and type(fields2dbMap[f]) == type([]):
                            for k in fields2dbMap[f]:
                                if k not in row.keys() or row[k] == "":
                                    continue
                                else:
                                    n[f] = row[k]
                                    break
                        elif row and fields2dbMap[f] in row.keys():
                            n[f] = row[fields2dbMap[f]]
                return True 
    return flag
    

anki.stdmodels.models.append((_("JP Vocabulary"),addJpVocabularyModel))
addHook('editFocusLost', onFocusLost)
