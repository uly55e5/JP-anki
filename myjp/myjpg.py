# -*- coding: utf-8 -*-
import anki.stdmodels
from anki.hooks import addHook
from aqt import mw
import sqlite3

nomecab=False
try:
    from japanese.reading import mecab
except:
    nomecab=True


def addJpGrammarModel(col):
    models = col.models
    km = models.new(_("JP Grammar"))
    f = models.newField(_("Text"))
    models.addField(km,f)
    f = models.newField(_("Text Cloze"))
    models.addField(km,f)
    f = models.newField(_("Translation DE"))
    models.addField(km,f)
    f = models.newField(_("Explanation DE"))
    models.addField(km,f)
    f = models.newField(_("Minna no nihongo Lesson"))
    models.addField(km,f)
    f = models.newField(_("Reading"))
    models.addField(km,f)
    f = models.newField(_("Text Type"))
    models.addField(km,f)
    f = models.newField(_("Extra"))
    models.addField(km,f)
    f = models.newField(_("Gewehr Page"))
    models.addField(km,f)
    f = models.newField(_("JLPT"))
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
<div class=big>  {{Text}} </div><br>
{{#Extra}}{{Extra}}{{/Extra}}
<hr><div class=info>
MNN: <b>{{Minna no nihongo Lesson}} </b> JLPT: <b>{{JLPT}}</b> Gewehr: <b>{{Gewehr Page}}</b></div><br>({{Text Type}})<br>"""
    t['afmt'] = """\
<div class=jp>{{Text}}</div><hr>
{{Translation DE}}<hr>
<div class=info>{{Explanation DE}}</div>"""
    models.addTemplate(km,t)
    t=models.newTemplate(_("Cloze"))
    t['qfmt'] = """\
{{#Text Cloze}}
<div class=big>  {{Text Cloze}} </div><br>
{{Translation DE}}<br><br>
{{#Extra}}{{Extra}}{{/Extra}}
<hr><div class=info>
MNN: <b>{{Minna no nihongo Lesson}} </b> JLPT: <b>{{JLPT}}</b></div><br>({{Text Type}})<br>
{{/Text Cloze}}"""
    t['afmt'] = """\
<div class=jp>{{Text}}</div><hr>
{{Translation DE}}<hr>
<div class=info>{{Explanation DE}}"""
    models.addTemplate(km,t)
    t =models.newTemplate(_("Meaning reverse"))
    t['qfmt'] = """\
<div class=big>  {{Translation DE}} </div><br>
{{#Extra}}{{Extra}}{{/Extra}}
<hr><div class=info>
MNN: <b>{{Minna no nihongo Lesson}} </b> JLPT: <b>{{JLPT}}</b> Gewehr: <b>{{Gewehr Page}}</b></div><br>({{Text Type}})<br>"""
    t['afmt'] = """\
<div class=big>  {{Text}} </div><br>
{{Translation DE}}<hr>
<div class=info>{{Explanation DE}}</div>"""
    models.addTemplate(km,t)
    models.add(km)
    return km

def onFocusLost(flag, n, fidx):
    if (n.model()["name"].startswith("JP Grammar")):
        if mw.col.models.fieldNames(n.model()).index("Text") == fidx:
            text = mw.col.media.strip(n["Text"])
            if not nomecab:
                n["Reading"] = mecab.reading(text)
                return True

anki.stdmodels.models.append((_("JP Grammar"),addJpGrammarModel))
addHook('editFocusLost', onFocusLost)

