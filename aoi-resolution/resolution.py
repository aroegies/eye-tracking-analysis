import pandas as pd
import numpy as np
from nltk.util import ngrams,skipgrams
from collections import Counter, defaultdict

import pandas as pd
import numpy as np
from nltk.util import ngrams,skipgrams
from collections import Counter, defaultdict


class FixationEvent(object):
    def __init__(self,aoi, x,y,ts,rowid):
        self.aoi = aoi
        self.x = x
        self.y = y
        self.rowid = rowid
        self.ts = ts
        self.point = np.array([x,y])
class ClickEvent(object):
    def __init__(self,type, x,y,ts, rowid):
        self.type = type
        self.x = x
        self.y = y
        self.rowid = rowid
        self.ts = ts
        self.point = np.array([x,y])
class BoundingBox(object):
    def __init__(self, x,y,width,height):
        self.left,self.top,self.right,self.bottom = x,y,x+width,y+height

    def overlaps(self,event):
        if (event.x >= self.left and self.right > event.x) and (event.y >= self.top and self.bottom > event.y):
            return True
        return False

class AOIResolver(object):
    def __init__(self,xlsx_file=None):
        if xlsx_file == None:
            raise Exception("required file not present")

        self._xls_file = pd.ExcelFile(xlsx_file)
        self._tobii_aoi = pd.read_excel(self._xls_file,'Tobii AOI Data')
        self._tobii_mouse = pd.read_excel(self._xls_file,'Tobii Mouse Data')
        self._raw_AOI_boxes = pd.read_excel(self._xls_file,'AOI Boxes')
        self._aoi_links = pd.read_excel(self._xls_file,'AOI Links')

        self._mouse_sessions = self._processTobiiMouse()
        self._aoi_sessions = self._processTobiiAOI()
        self._aoi_boxes = self._processAOIBoundingBoxes()
        self._aoi_dependencies = self._processAOIDependencies()

        
    def _processTobiiMouse(self):
        fixation = 0
        sessions = []
        fixation = 0
        session_data = []
        session_map = dict()
        count = 0
        for idx, row  in self._tobii_aoi.iterrows():
            newFixation = row['MouseEventIndex']
            if newFixation < fixation:
                session_map[count] = id
                sessions.append(session_data)
                count+=1
                session_data = []
            if row['MouseEvent'] == 'Left' or row['MouseEvent'] == 'Right':
                session_data.append(ClickEvent(row['MouseEvent'],row['MouseEventX (ADCSpx)'],row['MouseEventY (ADCSpx)'],row['Timestamp'],idx))
            fixation = newFixation
            id = row['ParticipantName']
        session_map[count]=id
        sessions.append(session_data)
        self.participants = session_map
        return sessions

    def _determineAOIs(self,fixations):
        aois = []
        for i,elt in enumerate(fixations):
            if elt == 1:
                aois.append(self.AOIs[i])
        if len(aois) == 0:
            return ['NA']
        return aois
    
    def _processTobiiAOI(self):
        self.AOIs = list(self._tobii_aoi.columns[10:])
        session_paths = []
        fixation = 0
        session_path = []
        session_map = dict()
        count = 0
        for idx, row in self._tobii_aoi.iterrows():
            newFixation = row['FixationIndex']
            if newFixation < fixation:
                session_map[count] = id
                session_paths.append(session_path)
                aois = self._determineAOIs(row[10:])
                count+=1
                session_path = [FixationEvent(aois,row['FixationPointX (MCSpx)'],row['FixationPointY (MCSpx)'],row['Timestamp'],idx)]
            else:
                aois = self._determineAOIs(row[10:])
                session_path.append(FixationEvent(aois,row['FixationPointX (MCSpx)'],row['FixationPointY (MCSpx)'],row['Timestamp'],idx))
            fixation = newFixation
            id = row['ParticipantName']
        session_map[count]=id
        session_paths.append(session_path)
        self.participants = session_map
        return session_paths
    
    def _processAOIBoundingBoxes(self):
        bboxes = dict()
        # Columns are AOI, Top, Left, Width, Height
        for idx, row in self._raw_AOI_boxes.iterrows():
            bboxes[row['AOI']] = BoundingBox(row['Top'],row['Left'],row['Width'],row['Height'])
        return bboxes
    
    def _processAOIDependencies(self):
        links = dict()
        # Columns: Parent (i.e., item to click to trigger child), Child
        for idx, row in self._aoi_links.iterrows():
            links[idx['Parent']] = idx['Child']
        return links
    
    def resolve_aois(self):

        return 
