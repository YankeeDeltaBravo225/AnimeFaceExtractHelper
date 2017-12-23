# AnimeFaceExtractHelper
A helper utility to extract anime faces.

Purpose:  
Extract partial images for machine learning.

Requires:  
- Python 3 Interperter
- Open CV 
- lbpcascade_animeface  
https://github.com/nagadomi/lbpcascade_animeface

Usage:  
`python AnimeFaceExtractHelper.py <input directory> <output directory>`
  
How to use:  
This program scans images from the given directory, and then classifies
candidates to extract anime faces using lbpcascade_animeface.  
Those candidates are shown in blue box and white boxes.
The blue one is the current selection, when you hit Enter key,
the partial image shown in the blue box will be saved.  
You can also change the selection by left or right arrow key.
Then a white box will be blue, it is the currently selected area.  
You can also select the area to extract by mouse.

More details will be available at Qiita
