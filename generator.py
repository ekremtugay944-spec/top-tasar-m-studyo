import sys
import json
import os
import re
import base64
import xml.etree.ElementTree as ET
from datetime import datetime

ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")

def update_style(style_str, updates):
    if not style_str:
        style_str = ""
    style_dict = {}
    for part in style_str.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            style_dict[k.strip()] = v.strip()
    for k, v in updates.items():
        style_dict[k] = v
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
    
    defs = root.find(f'{ns}defs')
    if defs is None:
        defs = ET.Element(f'{ns}defs')
        root.insert(0, defs)
    
    paths = list(root.iter(f'{ns}path')) if ns else list(root.iter('path'))
    path_by_id = {p.attrib.get('id'): p for p in paths if 'id' in p.attrib}
    
    panel_id_list = list(topology.keys())
    if not panel_id_list:
        panel_id_list = [p.attrib.get("id") for p in paths if p.attrib.get("id", "").startswith("panel-")]
        
    panels = data.get("panels", [])
    stroke_color = data.get("stroke_color")
    
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    assets_dir_name = f"assets_{timestamp}"
    assets_dir_path = os.path.join(out_dir, assets_dir_name)
    os.makedirs(assets_dir_path, exist_ok=True)
    
    for panel in panels:
        idx = panel.get("index")
        if idx is None or idx >= len(panel_id_list):
            continue
            
        panel_id = panel_id_list[idx]
        p = path_by_id.get(panel_id)
        if p is None: continue
        
        # Sadece düz renk
        fill_val = panel.get("fill", "#ffffff")
        style = p.attrib.get("style", "")
        p.attrib["style"] = update_style(style, {"fill": fill_val})
        
        # Görsel (image) ekleme (ClipPath ile)
        img_data = panel.get("image")
        if img_data and img_data.get("url_or_data"):
            data_str = img_data.get("url_or_data")
            filepath = data_str
            
            # Base64 çöz ve kaydet
            if data_str.startswith("data:image"):
                try:
                    header, b64 = data_str.split(",", 1)
                    ext = "png" if "png" in header else ("svg" if "svg" in header else "jpg")
                    filepath = f"{assets_dir_name}/panel_{idx}.{ext}"
                    full_filepath = os.path.join(out_dir, filepath)
                    with open(full_filepath, "wb") as fh:
                        fh.write(base64.b64decode(b64))
                except Exception as e:
                    print(f"Görsel kaydedilemedi (Panel {idx}): {e}")
                    filepath = data_str # Fallback to original
            
            # ClipPath oluştur
            clip_id = f"clip_{panel_id}_{timestamp}"
            clip_elem = ET.SubElement(defs, f'{ns}clipPath', id=clip_id)
            use_elem = ET.SubElement(clip_elem, f'{ns}use')
            use_elem.attrib[f"{{http://www.w3.org/1999/xlink}}href"] = f"#{panel_id}"
            
            # Resmi yerleştir
            topo = topology.get(panel_id, {})
            cx, cy = topo.get("center", (0, 0))
            area = topo.get("area", 4000)
            
            scale = img_data.get("scale", 1.0)
            opacity = img_data.get("opacity", 1.0)
            ox = img_data.get("offset_x", 0)
            oy = img_data.get("offset_y", 0)
            blend_mode = img_data.get("blend_mode", "normal")
            
            # Görseli panel sınırlarını kaplayacak boyutta ayarla (Karekök alan * çarpan)
            side = (area ** 0.5) * scale * 2.0 
            
            img_elem = ET.SubElement(root, f'{ns}image', {
                "x": str(cx - side/2 + ox),
                "y": str(cy - side/2 + oy),
                "width": str(side),
                "height": str(side),
                "opacity": str(opacity),
                "preserveAspectRatio": "xMidYMid slice",
                "clip-path": f"url(#{clip_id})"
            })
            if blend_mode != "normal":
                img_elem.attrib["style"] = f"mix-blend-mode: {blend_mode};"
                
            img_elem.attrib[f"{{http://www.w3.org/1999/xlink}}href"] = filepath

    if stroke_color:
        for p_id in panel_id_list:
            p = path_by_id.get(p_id)
            if p:
                style = p.attrib.get("style", "")
                p.attrib["style"] = update_style(style, {"stroke": stroke_color})
                
    out_svg = os.path.join(out_dir, f"top_{timestamp}.svg")
    out_pdf = os.path.join(out_dir, f"top_{timestamp}.pdf")
    out_png = os.path.join(out_dir, f"top_{timestamp}_preview.png")
    
    tree.write(out_svg, encoding="utf-8", xml_declaration=True)
    print(f"SVG kaydedildi: {out_svg}")
    
    try:
        import cairosvg
        cairosvg.svg2pdf(url=out_svg, write_to=out_pdf)
        print(f"PDF kaydedildi: {out_pdf}")
        cairosvg.svg2png(url=out_svg, write_to=out_png)
        print(f"PNG Önizleme kaydedildi: {out_png}")
    except ImportError:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
        
    generate_svg(data)
