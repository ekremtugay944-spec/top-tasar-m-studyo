import os
import math
import json
import xml.etree.ElementTree as ET
from svgpathtools import svg2paths2

def dist(p1, p2):
    return math.hypot(p1.real - p2.real, p1.imag - p2.imag)

def get_samples(path, num_samples=50):
    samples = []
    if path.length() == 0: return samples
    for i in range(num_samples):
        samples.append(path.point(i / (num_samples - 1)))
    return samples

def paths_are_neighbors(path1, path2, threshold=5.0):
    samples1 = get_samples(path1)
    samples2 = get_samples(path2)
    for p1 in samples1:
        for p2 in samples2:
            if dist(p1, p2) < threshold:
                return True
    return False

def analyze_soccer():
    print("Processing Soccer...")
    filepath = "templates/soccer_blank.svg"
    paths, attributes, svg_attributes = svg2paths2(filepath)
    
    path_data = []
    for i, p in enumerate(paths):
        if len(p) == 0: continue
        xmin, xmax, ymin, ymax = p.bbox()
        width = xmax - xmin
        height = ymax - ymin
        area = width * height
        cx = xmin + width / 2
        cy = ymin + height / 2
        path_data.append({"index": i, "area": area, "bbox": (xmin, xmax, ymin, ymax), "center": (cx, cy), "path": p, "width": width, "height": height})
    
    path_data.sort(key=lambda x: x["area"], reverse=True)
    
    # Filter panels
    panels = []
    # Rank 1 anomaly check
    rank1 = path_data[0]
    if rank1["area"] > 9000:
        print(f"Skipping Rank 1 anomaly (Area: {rank1['area']:.2f}, Center: {rank1['center']})")
    
    hexagons = []
    pentagons = []
    
    for pd in path_data:
        area = pd["area"]
        if 5000 < area < 6000:
            hexagons.append(pd)
        elif 3000 < area < 4500:
            pentagons.append(pd)
            
    print(f"Found {len(hexagons)} hexagons and {len(pentagons)} pentagons.")
    
    # Find outlier in hexagons
    if len(hexagons) == 21:
        # One is duplicate or outlier.
        # Check for duplicates (same center)
        unique_hex = []
        for h in hexagons:
            is_dup = False
            for uh in unique_hex:
                if dist(complex(*h["center"]), complex(*uh["center"])) < 2.0:
                    is_dup = True
                    break
            if not is_dup:
                unique_hex.append(h)
            else:
                print(f"Removed duplicate hexagon at {h['center']}")
        
        # If still 21, try finding the one furthest from the center of the ball
        if len(unique_hex) == 21:
            # Ball center approx average of all pentagon centers
            avg_x = sum(p["center"][0] for p in pentagons) / len(pentagons)
            avg_y = sum(p["center"][1] for p in pentagons) / len(pentagons)
            # Find hex furthest from avg
            unique_hex.sort(key=lambda h: dist(complex(*h["center"]), complex(avg_x, avg_y)))
            outlier = unique_hex.pop()
            print(f"Removed outlier hexagon at {outlier['center']} (furthest from center)")
            
        hexagons = unique_hex

    print(f"Final: {len(hexagons)} hexagons, {len(pentagons)} pentagons")
    
    # Assign IDs
    panel_info = {}
    for i, h in enumerate(hexagons):
        id_str = f"panel-hex-{i+1:02d}"
        h["id"] = id_str
        h["type"] = "hexagon"
        panels.append(h)
        
    for i, p in enumerate(pentagons):
        id_str = f"panel-pent-{i+1:02d}"
        p["id"] = id_str
        p["type"] = "pentagon"
        panels.append(p)
        
    # Calculate Topology
    print("Calculating topology...")
    topology = {}
    for i, p1 in enumerate(panels):
        neighbors = []
        for j, p2 in enumerate(panels):
            if i == j: continue
            # Bbox quick check
            b1 = p1["bbox"]
            b2 = p2["bbox"]
            if b1[0] > b2[1] + 5 or b1[1] < b2[0] - 5 or b1[2] > b2[3] + 5 or b1[3] < b2[2] - 5:
                continue
            if paths_are_neighbors(p1["path"], p2["path"]):
                neighbors.append(p2["id"])
        
        topology[p1["id"]] = {
            "type": p1["type"],
            "neighbors": neighbors,
            "center": p1["center"],
            "area": p1["area"]
        }
    
    # Modify XML
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = ET.register_namespace('', "http://www.w3.org/2000/svg")
    ns_prefix = re.match(r'\{.*\}', root.tag)
    ns_prefix = ns_prefix.group(0) if ns_prefix else ''
    
    xml_paths = list(root.iter(f'{ns_prefix}path')) if ns_prefix else list(root.iter('path'))
    for p in panels:
        idx = p["index"]
        xml_paths[idx].attrib["id"] = p["id"]
        # Add class for easier selection
        xml_paths[idx].attrib["class"] = p["type"]
        
    os.makedirs("templates/soccer/32-panel-classic", exist_ok=True)
    tree.write("templates/soccer_blank.svg", encoding="utf-8", xml_declaration=True)
    with open("templates/soccer/32-panel-classic/topology.json", "w") as f:
        json.dump(topology, f, indent=2)
    print("Soccer processing done.")

def analyze_volleyball():
    print("Processing Volleyball...")
    filepath = "templates/volleyball_blank.svg"
    paths, attributes, svg_attributes = svg2paths2(filepath)
    
    path_data = []
    for i, p in enumerate(paths):
        if len(p) == 0: continue
        xmin, xmax, ymin, ymax = p.bbox()
        width = xmax - xmin
        height = ymax - ymin
        area = width * height
        cx = xmin + width / 2
        cy = ymin + height / 2
        path_data.append({"index": i, "area": area, "bbox": (xmin, xmax, ymin, ymax), "center": (cx, cy), "path": p})
    
    # Filter panels (volleyball has 18 paths, let's just use all of them if area > 0)
    panels = [p for p in path_data if p["area"] > 10]
    print(f"Found {len(panels)} panels in volleyball.")
    
    topology = {}
    for i, p in enumerate(panels):
        p["id"] = f"panel-vb-{i+1:02d}"
        p["type"] = "volleyball_panel"
        
    print("Calculating topology...")
    for i, p1 in enumerate(panels):
        neighbors = []
        for j, p2 in enumerate(panels):
            if i == j: continue
            if paths_are_neighbors(p1["path"], p2["path"]):
                neighbors.append(p2["id"])
        
        topology[p1["id"]] = {
            "type": p1["type"],
            "neighbors": neighbors,
            "center": p1["center"],
            "area": p1["area"]
        }
        
    # Modify XML
    tree = ET.parse(filepath)
    root = tree.getroot()
    import re
    ns = ET.register_namespace('', "http://www.w3.org/2000/svg")
    ns_prefix = re.match(r'\{.*\}', root.tag)
    ns_prefix = ns_prefix.group(0) if ns_prefix else ''
    
    xml_paths = list(root.iter(f'{ns_prefix}path')) if ns_prefix else list(root.iter('path'))
    for p in panels:
        idx = p["index"]
        if idx < len(xml_paths):
            xml_paths[idx].attrib["id"] = p["id"]
            xml_paths[idx].attrib["class"] = p["type"]
            
    os.makedirs("templates/volleyball/18-panel-classic", exist_ok=True)
    tree.write("templates/volleyball_blank.svg", encoding="utf-8", xml_declaration=True)
    with open("templates/volleyball/18-panel-classic/topology.json", "w") as f:
        json.dump(topology, f, indent=2)
    print("Volleyball processing done.")

if __name__ == "__main__":
    import re
    analyze_soccer()
    analyze_volleyball()
