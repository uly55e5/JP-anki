import anki.stdmodels
from anki.hooks import addHook
from aqt import mw
import sqlite3
import os

def addJpKanjiModel(col):
    models = col.models
    km = models.new(_("JP Kanji"))
    f = models.newField(_("Kanji"))
    models.addField(km,f)
    f = models.newField(_("Meaning DE"))
    models.addField(km,f)
    f = models.newField(_("Meaning EN"))
    models.addField(km,f)
    f = models.newField(_("On Yomi"))
    models.addField(km,f)
    f = models.newField(_("Kun Yomi"))
    models.addField(km,f)
    f = models.newField(_("Minna no nihongo Lesson"))
    models.addField(km,f)
    f = models.newField(_("Heisig Lesson"))
    models.addField(km,f)
    f = models.newField(_("Heisig Number"))
    models.addField(km,f)
    f = models.newField(_("Heisig Keyword"))
    models.addField(km,f)
    f = models.newField(_("Heisig Primitiv Keyword(s)"))
    models.addField(km,f)
    f = models.newField(_("Heisig Story"))
    models.addField(km,f)
    f = models.newField(_("JLPT"))
    models.addField(km,f)
    f = models.newField(_("Grade"))
    models.addField(km,f)
    f = models.newField(_("Halpern Number"))
    models.addField(km,f)
    f = models.newField(_("Hadimitzky Number"))
    models.addField(km,f)
    f = models.newField(_("Radical Number"))
    models.addField(km,f)
    f = models.newField(_("Radicals"))
    models.addField(km,f)
    f = models.newField(_("Strokes"))
    models.addField(km,f)
    f = models.newField(_("Frequency"))
    models.addField(km,f)
    f = models.newField(_("Radical Name"))
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
<div class="jp big">{{Kanji}}</div>
<br><br>
Bedeutung
<br><br>
{{^Radical Name}}(Radikal){{/Radical Name}}
<br><hr>
<div class=info>
MNN: <b>{{Minna no nihongo Lesson}}</b> JLPT: <b>{{JLPT}}</b> Grade: <b>{{Grade}}</b> Hadimitzky: <b>{{Hadimitzky Number}}</b>
</div>"""
    t['afmt'] = """\
<div class="jp big">{{Kanji}}</div>
<hr><div class=big>{{Meaning DE}}</div><hr>
<div class=headline>Heisig</div>
<div class=left>
Stichwort: <b>{{Heisig Keyword}}</b><br>
Primitiv-Stichwort(e): <b>{{Heisig Primitiv Keyword(s)}}</b><br>
Story: <b>{{Heisig Story}}</b><br>
Lektion: <b>{{Heisig Lesson}}</b> Nummer: <b>{{Heisig Number}}</b> 
<hr>
Radicals: {{Radicals}}
</div>"""
    models.addTemplate(km,t)
    t=models.newTemplate(_("Reading"))
    t['qfmt'] = """\
<div class=big>{{Kanji}}</div>
<br><br>
Lesung
<br><br><hr>
<div class=info>MNN: <b>{{Minna no nihongo Lesson}}</b> JLPT: <b>{{JLPT}}</b> Grade: <b>{{Grade}}</b> Hadimitzky: <b>{{Hadimitzky Number}}</b></div>"""
    t['afmt'] = """\
<div class=big>{{Kanji}}</div>
<hr id=answer>
On<div class=big>{{On Yomi}}</div><hr>
Kun<div class=big>{{Kun Yomi}}</div><hr>
<div class=info>
Heisig: <b>{{Heisig Number}}</b> Hadimitzky: <b>{{Hadimitzky Number}}</b> Halpern: <b>{{Halpern Number}}</b>
</div>"""
    models.addTemplate(km,t)
    t =models.newTemplate(_("Meaning reverse"))
    t['qfmt'] = """\
(Kanji)
<div class=big>{{Meaning DE}}</div>
<br><br>
<div class=left>Heisig Stichwort: <b> {{Heisig Keyword}}</div>
<br><hr>
<div class=info>JLPT: <b>{{JLPT}}</b> Grade: <b>{{Grade}}</b> </div>"""
    t['afmt'] = """\
<div class=huge>{{Kanji}}</div>
<hr>
<div class=big>{{Meaning DE}}</div>
<br><br>
<div class=left>Heisig Stichwort: <b> {{Heisig Keyword}}</div>
<br><hr>
<div class=info>
Heisig: <b>{{Heisig Number}}</b> Hadimitzky: <b>{{Hadimitzky Number}}</b> Halpern: <b>{{Halpern Number}}</b>
</div>"""
    models.addTemplate(km,t)
    models.add(km)
    return km

def addJpVocabularyModel(col):
    pass

def addJpGrammarModel(col):
    pass


fields2dbMap = { "Kanji": "kanji",
    "Meaning DE" : ['meaning_de','heisig_mean_de'],
    "Meaning EN" : 'meaning_en',
    "On Yomi" : 'on_yomi',
    "Kun Yomi" : 'kun_yomi',
    "Heisig Lesson" : 'heisig_lesson_ger',
    "Heisig Number" : ['heisig_ger','heisig6','heisig'],
    "Heisig Keyword" : 'heisig_mean_de',
    "Heisig Primitiv Keyword(s)" : 'heisig_mean_prim_de',
    "Heisig Story" : 'heisig_story',
    "JLPT" : 'jlpt',
    "Grade" : 'grade',
    "Halpern Number" : 'halpern2',
    "Hadimitzky Number" : 'hadimitzky',
    "Radical Number" : 'radical_no',
    "Radicals" : 'radicals',
    "Strokes" : 'strokes',
    "Frequency" : 'freq',
    "Radical Name" : 'radname',
    "Minna no nihongo Lesson" : 'mnn_lesson'
}


def onFocusLost(flag, n, fidx):
    if (n.model()["name"].startswith("JP Kanji")):
        if mw.col.models.fieldNames(n.model()).index("Kanji") == fidx:
            kanji = mw.col.media.strip(n["Kanji"])
            if kanji != "":
                conkdb = sqlite3.connect("../../addons/myjp/data/jpdb")
                conkdb.row_factory = sqlite3.Row
                c = conkdb.cursor()
                kanji=(kanji,)
                c.execute("SELECT * FROM kanji WHERE kanji=?",kanji)
                row = c.fetchone()
                for f in fields2dbMap:
                    if n[f] == "":
                        if type(fields2dbMap[f]) == type([]):
                            for k in fields2dbMap[f]:
                                if row and row[k] == "":
                                    continue
                                elif row:
                                    n[f] = row[k]
                                    break
                        elif row and fields2dbMap[f] in row.keys():
                            n[f] = row[fields2dbMap[f]]
                return True 
    return flag
    

anki.stdmodels.models.append((_("JP Kanji"),addJpKanjiModel))
addHook('editFocusLost', onFocusLost)
