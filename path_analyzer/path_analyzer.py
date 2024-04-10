import pandas as pd
from nltk.util import ngrams,skipgrams
from collections import Counter, defaultdict


class PathSubsequence(object):
    def __init__(self,items):
        self._subsequence = items
    def __str__(self):
        return 'Seq: ' + ' => '.join(self._subsequence)
    def __repr__(self):
        return self.__str__()
    def __eq__(self,other):
        if type(other) != PathSubsequence:
            return False
        return self._subsequence.__eq__(other._subsequence)
    def __hash__(self):
        return self._subsequence.__hash__()

    

class PathAnalyzer(object):
    def __init__(self,xlsx_file=None,tsv_file=None):
        if xlsx_file == None and tsv_file == None:
            raise Exception("required file not present")
        
        if xlsx_file != None:
            self._data = pd.read_excel(xlsx_file)
        elif tsv_file != None:
            self._data = pd.read_csv(tsv_file,sep='\t')
        self._session_paths =self._process_tracking(self._data)

    def _determineAOI(self,fixations):
        for i,elt in enumerate(fixations):
            if elt == 1:
                return self.AOIs[i]
        return "NA"
    
    def _process_tracking(self,df):
        self.AOIs = list(df.columns[2:])
        session_paths = []
        fixation = 0
        session_path = []
        for idx, row in df.iterrows():
            newFixation = row['FixationID']
            if newFixation < fixation:
                session_paths.append(session_path)
                aoi = self._determineAOI(row[2:])
                session_path = [(row['TS'],aoi)]
            else:
                aoi = self._determineAOI(row[2:])
                session_path.append((row['TS'],aoi))
            fixation = newFixation
        session_paths.append(session_path)
        return session_paths
    
    
    def exact_subsequence(self,seqAOI):
        def scan_sequence(session,AOIs):
            subseq = Counter(ngrams([x[1] for x in session],len(AOIs)))
            return subseq[tuple(AOIs)]
        counts = []
        for session in self._session_paths:
            count = scan_sequence(session,seqAOI)
            counts.append(count)
        
        return sum([1 if c > 0 else 0 for c in counts]), [{"session":id,"occurrences":c}for (id,c) in enumerate(counts)]
    
    def approximate_sequence(self, seqAOI, max_gap = 0):
        def scan_sequence(session):
            subseq = Counter(skipgrams([x[1] for x in session],len(seqAOI),max_gap))
            return subseq[tuple(seqAOI)]
        counts = []
        for session in self._session_paths:
            count = scan_sequence(session)
            counts.append(count)
        return sum([1 if c > 0 else 0 for c in counts]),[{"session":id,"occurrences":c}for (id,c) in enumerate(counts)]
    
    def common_subsequences(self,max_ngram=2,max_gap=0,top_k = None,min_count = 1):
        counts = Counter()
        pathSequences = defaultdict(set)
        for idx, session in enumerate(self._session_paths):
            for n in range(2,max_ngram+1):
                grams = [PathSubsequence(x) for x in skipgrams([x[1] for x in session],n,max_gap)]
                
                pathSequences[idx].update(grams)
            counts.update(pathSequences[idx])
        
        top_subsequences =  [c for c  in counts.most_common(top_k) if c[1]>min_count]
        mostCommonSubsequences = set([c[0] for c in top_subsequences])
        pathCommonSubsequences = {}
        for idx, subsequences in pathSequences.items():
            pathCommonSubsequences[idx]=subsequences.intersection(mostCommonSubsequences)

        return top_subsequences,pathCommonSubsequences
        
    def aoi_revisits(self):
        def calculate_revisits(session,indices):
            if len(indices) <= 1:
                return []
            index_pairs = ngrams(indices,2)
            all_revisits = []
            for (start,end) in index_pairs:
                timeDiff = session[end][0] - session[start][0]
                intermediates = [fixation[1] for fixation in session[start+1:end]]
                all_revisits.append((start,end,timeDiff,intermediates))
            return all_revisits
        
        session_revisits = dict()
        for idx, session in enumerate(self._session_paths):
            enumerated_session = list(enumerate(session))
            if idx not in session_revisits:
                session_revisits[idx] = dict()
            for aoi in self.AOIs:
                indices = [index for (index,fixation) in enumerated_session if fixation[1] == aoi]
                revisits = calculate_revisits(session,indices)
                if len(revisits) == 0:
                    continue
                session_revisits[idx][aoi] = (len(revisits),revisits)
        return session_revisits
    
    def print_paths(self):
        for idx, session in enumerate(self._session_paths):
            print("Session {0}: {1}".format(idx,' => '.join("{0} ({1}ms)".format(fixation[1],fixation[0]) for fixation in session)))