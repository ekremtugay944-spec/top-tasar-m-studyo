import xml.etree.ElementTree as ET
import re

def analyze_svg(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # namespace
        ns = re.match(r'\{.*\}', root.tag)
        ns = ns.group(0) if ns else ''
        
        width = root.attrib.get('width', 'N/A')
        height = root.attrib.get('height', 'N/A')
        viewBox = root.attrib.get('viewBox', 'N/A')
        
        paths = list(root.iter(f'{ns}path')) if ns else list(root.iter('path'))
        path_count = len(paths)
        
        groups = list(root.iter(f'{ns}g')) if ns else list(root.iter('g'))
        group_count = len(groups)
        
        print(f'File: {filepath}')
        print(f'Canvas: {width} x {height}, viewBox={viewBox}')
        print(f'Total paths: {path_count}')
        print(f'Total groups: {group_count}')
        
        for i in range(min(5, len(paths))):
            id_val = paths[i].attrib.get('id', 'N/A')
            fill_val = paths[i].attrib.get('fill', 'N/A')
            style_val = paths[i].attrib.get('style', 'N/A')
            print(f'  Path {i}: id={id_val}, fill={fill_val}, style={style_val}')
            
        print('-'*40)
    except Exception as e:
        print(f'Error analyzing {filepath}: {e}')

analyze_svg('soccer_template.svg')
analyze_svg('volleyball_template.svg')
analyze_svg('soccer_filled_reference.svg')
