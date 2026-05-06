import sys
import subprocess
import os

try:
    from svgpathtools import svg2paths2
except ImportError:
    print("Installing svgpathtools...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "svgpathtools"])
    from svgpathtools import svg2paths2

import xml.etree.ElementTree as ET
import re

def analyze_svg(filepath):
    print(f"Parsing {filepath} with svgpathtools...")
    paths, attributes, svg_attributes = svg2paths2(filepath)
    
    print(f"Total paths loaded: {len(paths)}")
    
    path_areas = []
    
    # Check first 50 paths bounding boxes to see if they are clustered
    print("\n--- İlk 50 Path Bbox Analizi ---")
    clustered_count = 0
    
    for i, p in enumerate(paths):
        # some paths might be empty
        if len(p) == 0:
            continue
            
        xmin, xmax, ymin, ymax = p.bbox()
        width = xmax - xmin
        height = ymax - ymin
        area = width * height
        
        # Sadece analiz için ilk 50
        if i < 50:
            print(f"Path {i}: bbox=({xmin:.2f}, {ymin:.2f}, {xmax:.2f}, {ymax:.2f}) width={width:.2f} height={height:.2f} area={area:.2f}")
            if area < 10:  # 10 pikselden küçük alanlar mesh/hata parçası olabilir
                clustered_count += 1
                
        # Index'i (i) sakla ki asıl XML'deki yerini bilelim
        path_areas.append((i, area, xmin, ymin, width, height))

    print(f"\nİlk 50 path içinde alanı çok küçük olan (<10): {clustered_count}")

    # Alanı en büyük olan 32 path'i bul
    path_areas.sort(key=lambda x: x[1], reverse=True)
    
    print("\n--- En büyük 35 path (İlk 32 panel adayı) ---")
    for j in range(min(35, len(path_areas))):
        i, area, x, y, w, h = path_areas[j]
        print(f"Rank {j+1} -> Original Index: {i}, Area: {area:.2f}, Size: {w:.2f} x {h:.2f}")
        
    return path_areas[:32]

if __name__ == "__main__":
    analyze_svg('templates/soccer_blank.svg')
