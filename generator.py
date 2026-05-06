import sys
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

# Namespace ayarları (SVG için)
ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")

def update_style(style_str, updates):
    if not style_str:
        style_str = ""
    # Mevcut style'ı parse et
    style_dict = {}
    for part in style_str.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            style_dict[k.strip()] = v.strip()
    
    # Güncelle
    for k, v in updates.items():
        style_dict[k] = v
        
    # Tekrar string yap
    return ';'.join([f"{k}:{v}" for k, v in style_dict.items()])

def generate_svg(data):
    ball_type = data.get("ball_type", "soccer")
    
    template_path = os.path.join("templates", f"{ball_type}_blank.svg")
    if not os.path.exists(template_path):
        print(f"Hata: Şablon {template_path} bulunamadı.")
        sys.exit(1)
        
    topology_dir = "32-panel-classic" if ball_type == "soccer" else "18-panel-classic"
    topology_path = os.path.join("templates", ball_type, topology_dir, "topology.json")
    topology = {}
    if os.path.exists(topology_path):
        with open(topology_path, 'r', encoding='utf-8') as f:
            topology = json.load(f)
            
    tree = ET.parse(template_path)
    root = tree.getroot()
    ns = re.match(r'\{.*\}', root.tag)
    ns = ns.group(0) if ns else ''
    
    # defs ekle/bul
    defs = root.find(f'{ns}defs')
    if defs is None:
        defs = ET.Element(f'{ns}defs')
        root.insert(0, defs)
    
    # Path'leri id bazında haritala
    paths = list(root.iter(f'{ns}path')) if ns else list(root.iter('path'))
    path_by_id = {p.attrib.get('id'): p for p in paths if 'id' in p.attrib}
    
    # Panel id sırasını topology'den al
    panel_id_list = list(topology.keys())
    if not panel_id_list:
        # Topology yoksa fallback olarak sadece panel-* id'lileri al
        panel_id_list = [p.attrib.get("id") for p in paths if p.attrib.get("id", "").startswith("panel-")]
        
    panels = data.get("panels", [])
    stroke_color = data.get("stroke_color")
    logos = data.get("logos", [])
    
    # Panelleri güncelle
    for panel in panels:
        idx = panel.get("index")
        if idx is None or idx >= len(panel_id_list):
            continue
            
        panel_id = panel_id_list[idx]
        p = path_by_id.get(panel_id)
        if p is None: continue
        
        fill_type = panel.get("fill_type", "solid")
        fill_val = panel.get("fill", "#ffffff")
        
        if fill_type == "gradient":
            grad = panel.get("gradient", {})
            grad_id = f"grad_{idx}"
            grad_type = grad.get("type", "linear")
            grad_elem = ET.SubElement(defs, f'{ns}linearGradient' if grad_type == "linear" else f'{ns}radialGradient', id=grad_id)
            
            if grad_type == "linear":
                dir_ = grad.get("direction", "horizontal")
                if dir_ == "vertical":
                    grad_elem.attrib.update({"x1": "0%", "y1": "0%", "x2": "0%", "y2": "100%"})
                elif dir_ == "diagonal":
                    grad_elem.attrib.update({"x1": "0%", "y1": "0%", "x2": "100%", "y2": "100%"})
                else:
                    grad_elem.attrib.update({"x1": "0%", "y1": "0%", "x2": "100%", "y2": "0%"})
                    
            ET.SubElement(grad_elem, f'{ns}stop', offset="0%", **{"stop-color": grad.get("from", "#ffffff")})
            ET.SubElement(grad_elem, f'{ns}stop', offset="100%", **{"stop-color": grad.get("to", "#000000")})
            fill_val = f"url(#{grad_id})"
            
        elif fill_type == "pattern":
            patt = panel.get("pattern", {})
            patt_id = f"patt_{idx}"
            patt_elem = ET.SubElement(defs, f'{ns}pattern', id=patt_id, width="20", height="20", patternUnits="userSpaceOnUse")
            ET.SubElement(patt_elem, f'{ns}rect', width="20", height="20", fill=patt.get("color1", "#ffffff"))
            p_type = patt.get("type", "stripes")
            c2 = patt.get("color2", "#000000")
            if p_type == "stripes":
                ET.SubElement(patt_elem, f'{ns}rect', width="10", height="20", fill=c2)
            elif p_type == "dots":
                ET.SubElement(patt_elem, f'{ns}circle', cx="10", cy="10", r="5", fill=c2)
            elif p_type == "waves":
                ET.SubElement(patt_elem, f'{ns}path', d="M0,10 Q5,0 10,10 T20,10", fill="none", stroke=c2, **{"stroke-width": "2"})
            elif p_type == "diamonds":
                ET.SubElement(patt_elem, f'{ns}polygon', points="10,0 20,10 10,20 0,10", fill=c2)
            fill_val = f"url(#{patt_id})"
            
        style = p.attrib.get("style", "")
        p.attrib["style"] = update_style(style, {"fill": fill_val})
            
    # Stroke rengini güncelle
    if stroke_color:
        for p_id in panel_id_list:
            p = path_by_id.get(p_id)
            if p:
                style = p.attrib.get("style", "")
                p.attrib["style"] = update_style(style, {"stroke": stroke_color})
                
    # Logoları ekle
    for logo in logos:
        p_idx = logo.get("panel_index")
        url = logo.get("url_or_data")
        if p_idx is not None and url and p_idx < len(panel_id_list):
            panel_id = panel_id_list[p_idx]
            topo = topology.get(panel_id)
            if topo:
                cx, cy = topo.get("center", (0, 0))
                scale = logo.get("scale", 0.5)
                opacity = logo.get("opacity", 1.0)
                # Area'ya göre ortalama kenar uzunluğu bul
                area = topo.get("area", 4000)
                side = (area ** 0.5) * scale * 1.5
                img = ET.SubElement(root, f'{ns}image', {
                    "x": str(cx - side/2),
                    "y": str(cy - side/2),
                    "width": str(side),
                    "height": str(side),
                    "opacity": str(opacity),
                    "preserveAspectRatio": "xMidYMid meet"
                })
                img.attrib[f"{{http://www.w3.org/1999/xlink}}href"] = url
    
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_svg = os.path.join("output", f"top_{timestamp}.svg")
    out_pdf = os.path.join("output", f"top_{timestamp}.pdf")
    
    # SVG Kaydet
    tree.write(out_svg, encoding="utf-8", xml_declaration=True)
    print(f"SVG kaydedildi: {out_svg}")
    
    # PDF Kaydet (opsiyonel)
    try:
        import cairosvg
        cairosvg.svg2pdf(url=out_svg, write_to=out_pdf)
        print(f"PDF kaydedildi: {out_pdf}")
    except ImportError:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
        
    generate_svg(data)
