# Eye Tracking Analysis Tools

In this repository, we provide Python data analysis tools to explore eye-tracking data in ways that current out-of-the-box software offerings do not make available. The goal of this repository is to promote new types of exploration and analysis beyond the relatively straight-forward ones provides in software today (e.g., Tobii Studio). As our primary use of eye trackers has been through Tobii hardware and software, we focus on supporting data from the Tobii ecosystem but it should be straightforward to convert the output of other eye trackers to work with this repository. 

## Data Export

Eye trackers track many different movements of a participants eye over a session and then uses internal algorithms to group micro-fixations and saccades into high-level fixations. This is due to error inherent in the eye tracking process but also the inherent "jitter" present in natural eye movement. Accordingly, to accomodate this most eye trackers allow one to set sensitivity and sampling thresholds to determine how to group micro-fixations together. The side effect is that a single "fixation" is rarely a single fixation in truth and may encompass a non-trivial amount of tracked movement. 

As far as we are able to tell, Tobii uses the first micro-fixation in a grouped sequence of micro-fixations as the exemplar (though one could potentially choose an aggregate representation as well). Accordingly, this repository currently assumes that the exported data represents the single high-level fixation that in Tobii Studio can be exported by ensuring the "Export First Fixation Only" option (or equivalent in newer versions). 

In terms of other data points, we expect the _Participant ID_ and all _Gaze Event Data_. The code currently supports CSV and Excel formats, so choose whatever you are most comfortable manipulating. We also suggest that you modify the Area of Interest related headers in the exported data to be more human friendly. Tobii Studio exports these as `AOI[Name in Tobii]Hit` and can make data analysis and exploration more painful than you may like. Leave all other headers alone as we rely on this to accurate map data points.

We provide example data in `example-export.xlsx` which can be used to do rudimentary exploration of the tools in the repository. 

Note that if there is no fixation on an AOI that we create a pseudo-fixation called `NA` but this can be turned off by setting the `ignoreNA` parameter when loading data into one of the relevant classes.

The following is an example of the Tobii export settings:
!(Tobii Export Settings)[images/export_checklist.png "Tobii Export Settings"]

## Saccade Analysis

`path_analyzer/saccade_analyzer.py` is the primary class that facilitates saccade analysis. The underlying logic relies on creating "saccade paths" which are essentially the sequence of pairs of fixations in a scan path and the _screen pixel_ distance between each pair of fixation. We use the Euclidean distance between points to be more easily understood by humans than commonly reported saccade amplitude as the latter relates to eye movement and not distance between UI elements. We also note that we treat these as directed edges and so the pair `<A,B>` is different than the pair `<B,A>`

`saccade_path_stats` reports for each participant the total length of saccades, the average distance between saccades, the standard deviation, and a dictionary of saccade pairs to all distances from one to the other. This provides high-level statistics about saccade behaviours and can be used to do analysis about different saccade pairs across participants.

`saccade_distance_to` returns, for each participant, all distances where a saccade pair ends in a given AOI. There are options to ignore Non-AOI pseudo-fixations and to ignore self-fixations (i.e., where a saccade starts and ends in the same AOI). The goal of this method to to allow analysis of traversal behaviours to a particular AOI (e.g., many short, few long). 

`first_saccade_distance` returns, for each participant, the cumulative distance until an AOI is the destination in the sequences of saccade pairs. This is intended to be an "equivalent" measure to "time until first fixation" that is commonly reported. 

We refer interested parties to the supplied Jupyter Notebooks for examples of how these measures can be used to conduct different analyses. 

## Path Analyzer (Experimental)

`path_analyzer/path_analyzer.py` provides a class to conduct additional analyses on scan paths; primarily by allowing researchers to examine subsequences of fixations (e.g., n-grams or skip-grams in an NLP sense). This is currently still in development and being explored for utility.

## References

This repository is currently set to appear at TPDL 2024 as _Exploring the Utility of Saccade Length in Eye Tracking on Digital Library Experiences_ with authors Maja Kuhar, Adam Roegiest, and Tanja Merčun Kariž. 