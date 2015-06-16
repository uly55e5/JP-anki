import os.path
fpath=os.path.dirname(os.path.realpath(__file__))
if not os.path.isfile(fpath+"/myjp/data/jpdb"):
    import myjp.build_dic
    import myjp.build_kanji
import myjp.myjpv
import myjp.myjpk
import myjp.myjpg

