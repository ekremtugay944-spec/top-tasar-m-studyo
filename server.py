import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime

PORT = 8000
MEMORY_DIR = "designs_memory"
FULL_DIR = os.path.join(MEMORY_DIR, "full")
THUMB_DIR = os.path.join(MEMORY_DIR, "thumbnails")
INDEX_FILE = os.path.join(MEMORY_DIR, "designs.json")

os.makedirs(FULL_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump({"designs": [], "tag_index": {}}, f)

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/designs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/designs':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
                
            d_id = data.get("id")
            if not d_id:
                d_id = f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                data["id"] = d_id
                data["created"] = datetime.now().isoformat()
                # Default vals
                if "is_golden" not in data: data["is_golden"] = False
                if "tags" not in data: data["tags"] = []
                index["designs"].append(data)
            else:
                for i, d in enumerate(index["designs"]):
                    if d["id"] == d_id:
                        # Update without losing created date
                        data["created"] = d.get("created", datetime.now().isoformat())
                        index["designs"][i] = data
                        break
                        
            # Save full JSON (excluding huge preview if needed, but fine for now)
            with open(os.path.join(FULL_DIR, f"{d_id}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            # Rebuild tag index
            tag_index = {}
            for d in index["designs"]:
                for t in d.get("tags", []):
                    if t not in tag_index: tag_index[t] = []
                    tag_index[t].append(d["id"])
            index["tag_index"] = tag_index
            
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "id": d_id}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
    print(f"Server basladi. Port: {PORT}")
    httpd.serve_forever()
