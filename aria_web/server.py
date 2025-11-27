#!/usr/bin/env python
"""
Simple web server for Aria Visual Command System
Serves the HTML/JS frontend and provides API endpoint for command generation
"""
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import re
from urllib.parse import urlparse, parse_qs

# Add project paths
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "AI" / "microsoft_phi-silica-3.6_v1"))

# Try to load the model (optional - will work without it using fallback)
MODEL = None
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch
    
    print("🔍 Loading Aria model...")
    adapter_path = REPO_ROOT / "data_out" / "aria_models" / "aria_expanded_v2" / "lora_adapter"
    
    if adapter_path.exists():
        base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16, device_map="auto")
        MODEL = PeftModel.from_pretrained(model, str(adapter_path))
        print("✅ Model loaded successfully!")
    else:
        print("⚠️ Model not found, using rule-based fallback")
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    print("Using rule-based fallback parser")

def generate_tags_ai(command: str) -> list[str]:
    """Generate tags using AI model"""
    if MODEL is None:
        return []
    
    try:
        from transformers import AutoTokenizer
        base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        
        input_text = f"<|user|>\n{command}</s>\n<|assistant|>\n"
        inputs = tokenizer(input_text, return_tensors="pt").to(MODEL.device)
        
        with torch.no_grad():
            outputs = MODEL.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.1,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.5,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        tags = re.findall(r'\[aria:[^\]]+\]', response)
        return tags[:2]  # Return first 2 tags max
    except Exception as e:
        print(f"AI generation error: {e}")
        return []

def generate_tags_fallback(command: str) -> list[str]:
    """Simple rule-based fallback tag generation"""
    cmd = command.lower()
    tags = []
    
    # Expressions
    if 'smile' in cmd or 'happy' in cmd:
        tags.append('[aria:expression:smile]')
    elif 'sad' in cmd:
        tags.append('[aria:expression:sad]')
    elif 'surprised' in cmd:
        tags.append('[aria:expression:surprised]')
    elif 'confused' in cmd:
        tags.append('[aria:expression:confused]')
    elif 'wink' in cmd:
        tags.append('[aria:expression:wink]')
    
    # Animations
    if 'jump' in cmd:
        tags.append('[aria:animate:jump]')
    elif 'dance' in cmd:
        tags.append('[aria:animate:dance]')
    elif 'spin' in cmd:
        tags.append('[aria:animate:spin]')
    elif 'bow' in cmd:
        tags.append('[aria:animate:bow]')
    elif 'flip' in cmd:
        tags.append('[aria:animate:flip]')
    
    # Gestures
    if 'wave' in cmd:
        tags.append('[aria:gesture:wave]')
    elif 'thumbs up' in cmd:
        tags.append('[aria:gesture:thumbs_up]')
    elif 'clap' in cmd:
        tags.append('[aria:gesture:clap]')
    elif 'shrug' in cmd:
        tags.append('[aria:gesture:shrug]')
    
    # Movement
    if 'left' in cmd:
        if 'walk' in cmd:
            tags.append('[aria:walk:left]')
        elif 'run' in cmd:
            tags.append('[aria:run:left]')
        else:
            tags.append('[aria:move:left]')
    elif 'right' in cmd:
        if 'walk' in cmd:
            tags.append('[aria:walk:right]')
        elif 'run' in cmd:
            tags.append('[aria:run:right]')
        else:
            tags.append('[aria:move:right]')
    
    # Effects
    if 'sparkle' in cmd:
        tags.append('[aria:effect:sparkle]')
    elif 'glow' in cmd:
        tags.append('[aria:effect:glow]')
    elif 'hearts' in cmd:
        tags.append('[aria:effect:hearts]')
    
    # Camera
    if 'center' in cmd:
        tags.append('[aria:camera:center]')
    elif 'zoom' in cmd:
        tags.append('[aria:camera:zoom_in]' if 'in' in cmd else '[aria:camera:zoom_out]')
    
    # Poses
    if 'sit' in cmd:
        tags.append('[aria:pose:sit]')
    elif 'stand' in cmd:
        tags.append('[aria:pose:stand]')
    elif 'crouch' in cmd:
        tags.append('[aria:pose:crouch]')
    elif 'lie' in cmd or 'lay' in cmd:
        tags.append('[aria:pose:lie]')
    
    return tags

class AriaRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """Serve static files"""
        print(f"📥 GET request: {self.path}")
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def do_POST(self):
        """Handle API requests"""
        if self.path == '/api/aria/command':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                data = json.loads(post_data.decode('utf-8'))
                command = data.get('command', '')
                
                print(f"📝 Command received: {command}")
                
                # Try AI first, fallback to rules
                tags = generate_tags_ai(command)
                if not tags:
                    tags = generate_tags_fallback(command)
                
                print(f"✨ Generated tags: {tags}")
                
                response = {
                    'command': command,
                    'tags': tags,
                    'model': 'ai' if (MODEL and tags) else 'fallback'
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except ConnectionAbortedError:
                # Client disconnected, ignore
                pass
            except Exception as e:
                print(f"❌ Error: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    error = {'error': str(e), 'tags': []}
                    self.wfile.write(json.dumps(error).encode('utf-8'))
                except:
                    pass
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        if 'favicon' not in args[0] if args else True:
            print(f"🌐 {args[0] if args else format}")

def main():
    import os
    
    # Change to aria_web directory
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    port = 8080
    server = HTTPServer(('0.0.0.0', port), AriaRequestHandler)
    
    print("\n" + "=" * 70)
    print("🎨 Aria Visual Command System - Web Server")
    print("=" * 70)
    print(f"🌐 Open in browser: http://localhost:{port}")
    print(f"🤖 Model: {'AI (aria_expanded_v2)' if MODEL else 'Rule-based fallback'}")
    print("📝 Type commands in the web interface to control Aria")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()
