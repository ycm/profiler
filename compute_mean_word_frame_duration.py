#!/usr/bin/env python3
# compute_mean_word_frame_duration.py
import sys
import json
from collections import defaultdict

def get_session_to_mean_frame_duration(filename): 
    with open(filename) as f: 
        session_to_word_and_frames = defaultdict(list) 
        next(f) 
        for line in f: 
            session, response, sframe, nframes, word = line.strip().split(',') 
            if word[0] != '<': 
                session_to_word_and_frames[session].append((word, nframes)) 
    return { 
        session: sum([int(frames) for word, frames in word_and_frames])/len(word_and_frames) 
        for session, word_and_frames in session_to_word_and_frames.items() 
    }

if __name__ == "__main__":
    _, infile, outfile = sys.argv
    session_to_mean_frame_duration = get_session_to_mean_frame_duration(infile)
    with open(outfile, 'w') as f:
        json.dump(session_to_mean_frame_duration, f)