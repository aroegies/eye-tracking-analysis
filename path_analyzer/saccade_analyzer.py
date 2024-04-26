import pandas as pd
import numpy as np
from nltk.util import ngrams,skipgrams
from collections import Counter, defaultdict


class FixationEvent(object):
    def __init__(self,aoi, x,y):
        self.aoi = aoi
        self.x = x
        self.y = y
        self.point = np.array([x,y])

class SaccadeEvent(object):
    def __init__(self,src,dst):
        self.event = src.aoi+"-"+dst.aoi
        self.dist = np.linalg.norm(src.point-dst.point)
        self.src_aoi = src.aoi
        self.dst_aoi = dst.aoi

class SaccadeAnalyzer(object):
    def __init__(self,xlsx_file=None,tsv_file=None):
        if xlsx_file == None and tsv_file == None:
            raise Exception("required file not present")
        
        if xlsx_file != None:
            self._data = pd.read_excel(xlsx_file)
        elif tsv_file != None:
            self._data = pd.read_csv(tsv_file,sep='\t')
        self._session_paths =self._process_tracking(self._data)
        self._saccade_paths = self._create_saccade_paths()

    def _determineAOI(self,fixations):
        for i,elt in enumerate(fixations):
            if elt == 1:
                return self.AOIs[i]
        return "NA"
    def _process_tracking(self,df):
        self.AOIs = list(df.columns[10:])
        session_paths = []
        fixation = 0
        session_path = []
        session_map = dict()
        count = 0
        for idx, row in df.iterrows():
            newFixation = row['FixationIndex']
            if newFixation < fixation:
                session_map[count] = id
                session_paths.append(session_path)
                aoi = self._determineAOI(row[10:])
                session_path = [FixationEvent(aoi,row['FixationPointX (MCSpx)'],row['FixationPointX (MCSpx)'])]
                count+=1
            else:
                aoi = self._determineAOI(row[10:])
                session_path.append(FixationEvent(aoi,row['FixationPointX (MCSpx)'],row['FixationPointX (MCSpx)']))
            fixation = newFixation
            id = row['ParticipantName']
        session_map[count]=id
        session_paths.append(session_path)
        self.participants = session_map
        return session_paths
    
    def _create_saccade_paths(self):
        saccade_paths = []
        for session in self._session_paths:
            if len(session) <= 2:
                saccade_paths.append([])
                continue
            saccade_path = []
            old_fixation = session[0]
            for idx in range(1,len(session)):
                new_fixation = session[idx]
                saccade_path.append(SaccadeEvent(old_fixation,new_fixation))
                old_fixation = new_fixation
            saccade_paths.append(saccade_path)

        return saccade_paths
        
    def print_paths(self):
        for idx, session in enumerate(self._session_paths):
            print(f"Session {idx}")
            for idx,fixation in enumerate(session):
                print("{0} => {1}".format(''.join([" " for i in range(idx)]),fixation.aoi))
            # print("Session {0}: {1}".format(idx,' => '.join("{0}".format(fixation.aoi) for fixation in session)))
            break
    def print_saccade_paths(self):
        for idx, session in enumerate(self._saccade_paths):
            print(f"Session {idx}")
            for idx,saccade in enumerate(session):
                print("{0} => {1} ({2})".format(''.join([" " for i in range(idx)]),saccade.event,saccade.dist))
            # print("Session {0}: {1}".format(idx,' => '.join("{0} ({1})".format(saccade.event,saccade.dist) for saccade in session)))
            break

    def saccade_path_stats(self):
        saccade_data = []
        for idx, session in enumerate(self._saccade_paths):
            distances = []
            paired = defaultdict(list)
            for saccade in session:
                distances.append(saccade.dist)
                paired[tuple([saccade.src_aoi,saccade.dst_aoi])].append(saccade.dist)
            saccade_data.append(tuple([idx,np.sum(distances),np.mean(distances),np.std(distances),paired]))
        return saccade_data
    
    def saccade_distance_to(self,aoi,ignore_self=False,ignore_nonAoI = False):
        saccade_data = []
        for idx, session in enumerate(self._saccade_paths):
            dists = []
            for saccade in session:
                if saccade.dst_aoi == aoi:
                    if ignore_nonAoI and saccade.src_aoi == "NA":
                        continue
                    if ignore_self and saccade.src_aoi == aoi:
                        continue
                    dists.append(saccade.dist)
            saccade_data.append(dists)
        return saccade_data

    def first_saccade_distance(self):
        all_firsts = []
        for idx, session in enumerate(self._saccade_paths):
            firsts = defaultdict(float)
            total = 0.0
            for saccade in session:
                total += saccade.dist
                if saccade.dst_aoi not in firsts:
                    firsts[saccade.dst_aoi] = total    
                
            all_firsts.append(firsts)
        return all_firsts

