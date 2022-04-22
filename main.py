import Journaling.analisys_data as analisys
import Journaling.config_upload as conf
import Journaling.elaboration as elab

if conf.analisys():
    analisys.go()
else:
    elab.go()