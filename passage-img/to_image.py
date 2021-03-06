#!/usr/bin/env python

import os
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

OUTPUT_DIR = 'output_imgs'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for passage in [x for x in os.listdir() if x.startswith('passage')]:
     pdf_path = os.path.join(passage, passage + '.pdf')
     page = convert_from_path(pdf_path)[0]
     page.save(os.path.join(OUTPUT_DIR, 'raw_' + passage + '.png'), 'PNG')

for raw_image in [x for x in os.listdir(OUTPUT_DIR) if x.startswith('raw')]:
    raw_image_path = os.path.join(OUTPUT_DIR, raw_image)
    img = Image.open(raw_image_path)
    
    left = 200
    top = 200
    
    crop = img.crop((left, top, left + 960, top + 1440))
    
    w, h = crop.size
    lowest = 0
    for y in range(h):
        for x in range(w):
            if sum(crop.getpixel((x, y))) != 765: # 255 * 3 == white
                lowest = y
                continue
    
    crop = crop.crop((0, 0, w, lowest + 100))
    
    w, h = crop.size
    crop = crop.resize((800, int(800 * h / w)))
    
    crop.save(os.path.join(OUTPUT_DIR, '3026.' + raw_image.replace('raw_passage_', '')))
    
    print('done with', raw_image)
