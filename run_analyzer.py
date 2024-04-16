from saccade_analyzer import SaccadeAnalyzer
import numpy as np

# spa = PathAnalyzer(tsv_file='test.tsv')
# print("Scan paths:")
# spa.print_paths()

# print("Query for specific path AOI_2 followed by AOI_3:")
# print("Exact paths from AOI_2 to AOI_3: ",spa.approximate_sequence(['AOI_2','AOI_3']),"\n")
# print("1 gap paths from AOI_2 to AOI_3: ",spa.approximate_sequence(['AOI_2','AOI_3'],1),"\n")
# print("2 gap paths from AOI_2 to AOI_3: ",spa.approximate_sequence(['AOI_2','AOI_3'],2),"\n")
# print("Most common subsequences of max length 3 with a max gap of 2: ")
# mostCommon,sessionPaths = spa.common_subsequences(max_ngram=3,max_gap=2)
# for i in mostCommon:
#     print("Count: {0}; Path {1}".format(i[1],i[0]))
# print("\n\n")
# for sessid, commonPaths in sessionPaths.items():
#     print("Session {0} Common subpaths: {1}".format(sessid,commonPaths))

# print("\n\n")
# revisits = spa.aoi_revisits()
# print("=========Session revisits=========")
# for sessid, all_revisits in revisits.items():
#     for aoi, revisits in all_revisits.items():
#         meanTime = np.nan_to_num(np.mean([ visit[2] for visit in revisits[1]]))
#         meanLength = np.nan_to_num(np.mean([len(visit[3]) for visit in revisits[1]]))
#         print("Session: {0}, AOI: {1} revisit count: {2}; mean revisit latency: {3}; mean revisit path length: {4} ".format(sessid,aoi,revisits[0],meanTime,meanLength))

sa = SaccadeAnalyzer(xlsx_file="test.xlsx")
print(sa.AOIs)
sa.print_paths()
sa.print_saccade_paths()
data = sa.saccade_path_stats()
d = data[0]
print(d[0],d[1],d[2],d[3])
for k,v in d[4].items():
    print("{0} : {1} times:{2:.2f} ({3:.2f})".format(k,len(v),np.mean(v),np.std(v)))

data = sa.saccade_distance_to("AOI[Cover photos 2]Hit")
print(data[0])
data = sa.saccade_distance_to("AOI[Cover photos 2]Hit",ignore_self=True)
print(data[0])
data = sa.saccade_distance_to("AOI[Cover photos 2]Hit",ignore_self=True,ignore_nonAoI=True)
print(data[0])