#!/usr/bin/env python
"""
Simple web server for Aria Visual Command System
Serves the HTML/JS frontend and provides API endpoint for command generation
"""
import sys
from pathlib import Path
from typing import List
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import re
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project paths
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "AI" / "microsoft_phi-silica-3.6_v1"))
sys.path.insert(0, str(REPO_ROOT))  # Add root for shared imports

# Try to import shared chat providers for LLM integration
try:
    from shared.chat_providers import detect_provider
    LLM_AVAILABLE = True
    logger.info("✓ LLM providers available for automatic action generation")
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("✗ LLM providers not available - will use rule-based fallback only")

# Skip AI model loading for faster startup - use rule-based fallback
MODEL = None
print("⚠️ Skipping AI model loading - using rule-based fallback for faster startup")

# Global stage state that AI can see
stage_state = {
    'aria': {
        'position': {'x': 15, 'y': 20},  # percentage coordinates
        'expression': 'neutral',
        'held_object': None,
        'facing': 'right'
    },
    'objects': {
        'apple': {'position': {'x': 55, 'y': 35}, 'state': 'on_table'},
        'book': {'position': {'x': 48, 'y': 35}, 'state': 'on_table'},
        'cup': {'position': {'x': 62, 'y': 35}, 'state': 'on_table'},
        'ball': {'position': {'x': 70, 'y': 35}, 'state': 'on_table'},
        'flower': {'position': {'x': 52, 'y': 35}, 'state': 'on_table'}
    },
    'environment': {
        'table': {'position': {'x': 60, 'y': 20}},
        'stage_bounds': {'width': 100, 'height': 100}
    }
}

# Structured action schema for LLM-powered automatic execution
ARIA_ACTIONS = {
    "move": {
        "params": ["target", "speed"],
        "description": "Move Aria to a target position or object",
        "example": {"action": "move", "target": {"x": 50, "y": 30}, "speed": "normal"}
    },
    "say": {
        "params": ["text", "emotion"],
        "description": "Make Aria speak with optional emotion",
        "example": {"action": "say", "text": "Hello!", "emotion": "happy"}
    },
    "pickup": {
        "params": ["object_id"],
        "description": "Pick up an object from the stage",
        "example": {"action": "pickup", "object_id": "apple"}
    },
    "drop": {
        "params": ["position"],
        "description": "Drop currently held object at position",
        "example": {"action": "drop", "position": {"x": 50, "y": 30}}
    },
    "throw": {
        "params": ["target", "force"],
        "description": "Throw held object toward target",
        "example": {"action": "throw", "target": {"x": 70, "y": 40}, "force": "medium"}
    },
    "gesture": {
        "params": ["gesture_type"],
        "description": "Perform a gesture animation",
        "example": {"action": "gesture", "gesture_type": "wave"}
    },
    "look": {
        "params": ["target"],
        "description": "Look at a target position or object",
        "example": {"action": "look", "target": "apple"}
    },
    "wait": {
        "params": ["duration"],
        "description": "Wait for specified duration in seconds",
        "example": {"action": "wait", "duration": 2.0}
    }
}


class AriaActionParser:
    """LLM-powered action parser for automatic command execution"""

    def __init__(self):
        self.provider = None
        self.provider_choice = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize LLM provider if available, robust to tuple return values."""
        if not LLM_AVAILABLE:
            logger.info("LLM not available - will use rule-based fallback")
            return

        try:
            detected = detect_provider()
            # detect_provider returns (provider_instance, ProviderChoice)
            if isinstance(detected, tuple) and len(detected) == 2:
                self.provider, self.provider_choice = detected
            else:
                # older style (just provider)
                self.provider = detected
            provider_name = getattr(self.provider_choice, 'name', getattr(self.provider, '__class__', type(self.provider)).__class__.__name__)
            logger.info(f"✓ Initialized LLM provider: {provider_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM provider: {e}")
            self.provider = None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with action schema and current state"""
        actions_json = json.dumps(ARIA_ACTIONS, indent=2)
        state_json = json.dumps(stage_state, indent=2)
        
        return f"""You are an action planner for Aria, a 3D character assistant.

Available Actions:
{actions_json}

Current Stage State:
{state_json}

Your task: Parse user commands into a sequence of structured actions.
- Return ONLY valid JSON array of actions
- Use exact action names from schema
- Provide all required params for each action
- Consider current state when planning
- Keep actions simple and atomic

Example output:
[
  {{"action": "move", "target": {{"x": 50, "y": 30}}, "speed": "normal"}},
  {{"action": "say", "text": "Hello!", "emotion": "happy"}}
]

Rules:
1. Always move Aria before picking up objects
2. Aria can only hold one object at a time
3. Objects on table are at y=35, x varies
4. Stage bounds: 0-100 for both x and y
5. If command is unclear, choose most reasonable interpretation"""
    
    def parse_with_llm(self, command: str) -> List[dict]:
        """Parse command using LLM provider"""
        if not self.provider:
            raise ValueError("LLM provider not available")
        
        system_prompt = self._build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]
        
        try:
            response = self.provider.complete(messages, stream=False)
            
            # Extract JSON from response
            content = response.get('content', '').strip()
            
            # Try to parse as JSON
            if content.startswith('['):
                actions = json.loads(content)
            else:
                # Extract JSON array from markdown or text
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    actions = json.loads(json_match.group(0))
                else:
                    raise ValueError("No JSON array found in response")
            
            # Validate actions
            validated = []
            for action in actions:
                if 'action' in action and action['action'] in ARIA_ACTIONS:
                    validated.append(action)
                else:
                    logger.warning(f"Skipping invalid action: {action}")
            
            return validated
            
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            raise
    
    def parse_with_fallback(self, command: str) -> List[dict]:
        """Rule-based fallback parser (uses existing generate_tags_fallback logic)"""
        actions = []
        command_lower = command.lower()
        
        # Parse move commands
        if any(word in command_lower for word in ['go', 'move', 'walk', 'run']):
            # Extract target from command
            if 'table' in command_lower:
                actions.append({"action": "move", "target": {"x": 60, "y": 35}, "speed": "normal"})
            elif 'center' in command_lower or 'middle' in command_lower:
                actions.append({"action": "move", "target": {"x": 50, "y": 50}, "speed": "normal"})
            elif 'left' in command_lower:
                actions.append({"action": "move", "target": {"x": 20, "y": 50}, "speed": "normal"})
            elif 'right' in command_lower:
                actions.append({"action": "move", "target": {"x": 80, "y": 50}, "speed": "normal"})
        
        # Parse say commands
        if any(word in command_lower for word in ['say', 'speak', 'tell', 'greet']):
            # Extract text after say/speak
            for trigger in ['say ', 'speak ', 'tell ', 'greet ']:
                if trigger in command_lower:
                    text = command[command_lower.index(trigger) + len(trigger):].strip(' "\'')
                    emotion = 'happy' if any(w in text.lower() for w in ['!', 'hello', 'hi']) else 'neutral'
                    actions.append({"action": "say", "text": text, "emotion": emotion})
                    break
        
        # Parse pickup commands
        for obj in ['apple', 'book', 'cup', 'ball', 'flower']:
            if obj in command_lower and any(word in command_lower for word in ['pick', 'get', 'grab', 'take']):
                # Move to object first
                obj_pos = stage_state['objects'][obj]['position']
                actions.append({"action": "move", "target": obj_pos, "speed": "normal"})
                actions.append({"action": "pickup", "object_id": obj})
                break
        
        # Parse gesture commands
        gestures = ['wave', 'bow', 'nod', 'shake', 'point']
        for gesture in gestures:
            if gesture in command_lower:
                actions.append({"action": "gesture", "gesture_type": gesture})
                break
        
        return actions
    
    def parse(self, command: str, use_llm: bool = True) -> List[dict]:
        """
        Parse command into structured actions
        
        Args:
            command: Natural language command
            use_llm: Try LLM first if available
        
        Returns:
            List of action dicts
        """
        if use_llm and self.provider:
            try:
                actions = self.parse_with_llm(command)
                logger.info(f"✓ LLM parsed: {command} -> {len(actions)} actions")
                return actions
            except Exception as e:
                logger.warning(f"LLM parsing failed, using fallback: {e}")
        
        actions = self.parse_with_fallback(command)
        logger.info(f"✓ Fallback parsed: {command} -> {len(actions)} actions")
        return actions


# --------------------------- World Generation ---------------------------
import random, datetime
import math
import os
from functools import lru_cache

def _sanitize_id(raw: str) -> str:
    import re as _re
    cleaned = _re.sub(r"[^a-zA-Z0-9_]+", "_", raw.strip().lower())
    return cleaned[:30] or f"obj_{random.randint(1000,9999)}"

THEME_OBJECT_LIBRARY = {
    'forest': [
        ("tree", "🌲"), ("mushroom", "🍄"), ("rock", "🪨"), ("flower", "🌼"), ("owl", "🦉"), ("fox", "🦊")
    ],
    'space': [
        ("planet", "🪐"), ("star", "⭐"), ("rocket", "🚀"), ("alien", "👽"), ("astronaut", "👩‍🚀"), ("satellite", "🛰️")
    ],
    'ocean': [
        ("fish", "🐟"), ("shell", "🐚"), ("coral", "🪸"), ("whale", "🐋"), ("ship", "🚢"), ("dolphin", "🐬")
    ],
    'lab': [
        ("beaker", "🧪"), ("microscope", "🔬"), ("dna", "🧬"), ("robot", "🤖"), ("atom", "⚛️"), ("chip", "💾")
    ],
    'medieval': [
        ("sword", "🗡️"), ("shield", "🛡️"), ("crown", "👑"), ("scroll", "📜"), ("goblet", "🍷"), ("castle", "🏰")
    ],
    'desert': [
        ("cactus", "🌵"), ("skull", "💀"), ("camel", "🐪"), ("scorpion", "🦂"), ("sun", "☀️"), ("sand", "🟨")
    ],
    'garden': [
        ("rose", "🌹"), ("tulip", "🌷"), ("butterfly", "🦋"), ("bee", "🐝"), ("bench", "🪑"), ("pond", "💧")
    ],
    'cyberpunk': [
        ("drone", "🛸"), ("neon", "💡"), ("chip", "💾"), ("server", "🖥️"), ("bot", "🤖"), ("battery", "🔋")
    ],
    'arcade': [
        ("joystick", "🕹️"), ("coin", "🪙"), ("ghost", "👻"), ("trophy", "🏆"), ("console", "🎮"), ("heart", "❤️")
    ],
}

def _generate_positions_rejection(n: int, min_dist: int, rng: random.Random) -> list:
    """Generate up to n non-overlapping (approx) positions using rejection sampling.
    Falls back gracefully if density too high.
    Returns list of (x,y)."""
    positions = []
    attempts = 0
    max_attempts = n * 120  # generous attempts budget
    while len(positions) < n and attempts < max_attempts:
        attempts += 1
        x = rng.randint(8, 92)
        y = rng.randint(12, 88)
        if all(math.hypot(x - px, y - py) >= min_dist for px, py in positions):
            positions.append((x, y))
            continue
    # If we failed to place enough due to high density, relax constraint slightly
    if len(positions) < n:
        relax_dist = max(4, int(min_dist * 0.6))
        while len(positions) < n:
            x = rng.randint(5, 95)
            y = rng.randint(10, 90)
            if all(math.hypot(x - px, y - py) >= relax_dist for px, py in positions):
                positions.append((x, y))
    return positions

def _generate_positions_poisson(n: int, min_dist: int, rng: random.Random, width: int = 100, height: int = 100, k: int = 30) -> list:
    """Poisson-disc sampling (Bridson) for uniform-ish spacing.
    Returns list of (x,y) up to n points. If fewer found, pads via relaxed rejection sampling.
    """
    if n <= 1:
        return [(rng.randint(5, width-5), rng.randint(10, height-10))]
    cell_size = min_dist / (2 ** 0.5)
    grid_w = int(width / cell_size) + 2
    grid_h = int(height / cell_size) + 2
    grid = [[None] * grid_h for _ in range(grid_w)]

    def grid_coords(pt):
        return int(pt[0] / cell_size), int(pt[1] / cell_size)

    def far_enough(pt):
        gx, gy = grid_coords(pt)
        for ix in range(max(0, gx-2), min(grid_w, gx+3)):
            for iy in range(max(0, gy-2), min(grid_h, gy+3)):
                other = grid[ix][iy]
                if other is not None and math.hypot(pt[0]-other[0], pt[1]-other[1]) < min_dist:
                    return False
        return True

    # Seed first point
    first = (rng.uniform(8, width-8), rng.uniform(12, height-12))
    pts = [first]
    active = [first]
    gx, gy = grid_coords(first)
    grid[gx][gy] = first

    while active and len(pts) < n:
        idx = rng.randint(0, len(active)-1)
        base = active[idx]
        placed = False
        for _ in range(k):
            radius = rng.uniform(min_dist, 2 * min_dist)
            angle = rng.uniform(0, 2 * math.pi)
            nx = base[0] + math.cos(angle) * radius
            ny = base[1] + math.sin(angle) * radius
            if 5 <= nx <= width-5 and 10 <= ny <= height-10 and far_enough((nx, ny)):
                pts.append((nx, ny))
                active.append((nx, ny))
                gx, gy = grid_coords((nx, ny))
                grid[gx][gy] = (nx, ny)
                placed = True
                break
        if not placed:
            active.pop(idx)

    if len(pts) < n:
        # Pad with relaxed rejection sampling
        remainder = n - len(pts)
        pts.extend(_generate_positions_rejection(remainder, max(4, int(min_dist*0.6)), rng))

    return [(int(p[0]), int(p[1])) for p in pts[:n]]

def generate_world_fallback(theme: str, count: int, seed: int | None = None, spacing: int = 10, algorithm: str = 'rejection') -> dict:
    """Generate a world procedurally without LLM using deterministic, spaced placement.

    Args:
        theme: world theme name
        count: desired number of objects (>=1)
        seed: optional deterministic seed; if None a random seed is chosen
        spacing: minimum desired distance between objects (in stage coordinate units)
    """
    count = max(1, int(count))
    rng = random.Random(seed) if seed is not None else random.Random()
    effective_seed = seed if seed is not None else rng.randint(100000, 999999)
    catalog_src = THEME_OBJECT_LIBRARY.get(theme.lower(), THEME_OBJECT_LIBRARY['forest'])
    objects_catalog = list(catalog_src)  # copy
    rng.shuffle(objects_catalog)
    # If we need more than catalog size, cycle with suffixes
    chosen = []
    for idx in range(count):
        base_name, emoji = objects_catalog[idx % len(objects_catalog)]
        name = base_name if idx < len(objects_catalog) else f"{base_name}_{idx}"
        chosen.append((name, emoji))

    if algorithm == 'poisson':
        positions = _generate_positions_poisson(len(chosen), spacing, rng)
        generation_method = 'fallback_poisson_disc'
    else:
        positions = _generate_positions_rejection(len(chosen), spacing, rng)
        generation_method = 'fallback_rejection'
    stage_objects = {}
    for (name, emoji), (x, y) in zip(chosen, positions):
        oid = _sanitize_id(name)
        stage_objects[oid] = {
            'id': oid,
            'emoji': emoji,
            'position': {'x': x, 'y': y},
            'state': 'on_stage'
        }
    environment = {
        'theme': theme,
        'generated_at': datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00','Z'),
        'seed': effective_seed,
        'spacing': spacing,
        'generation_method': generation_method,
        'stage_bounds': {'width': 100, 'height': 100}
    }
    return {
        'objects': stage_objects,
        'environment': environment,
        'llm': False
    }

def generate_world_with_llm(theme: str, count: int, provider, seed: int | None = None, spacing: int = 10, algorithm: str = 'rejection') -> dict:
    """Use LLM provider to generate a themed world. Returns fallback on failure.

    Args:
        theme: theme name
        count: desired number of objects
        provider: LLM provider implementing .complete(messages, stream=False)
        seed: optional seed passed to fallback if needed
        spacing: spacing for fallback if LLM output unusable
    """
    system_prompt = (
        "You are a STRICT JSON generator for a 2D stage (x,y in 0-100).\n"
        "Return ONLY a single JSON object with keys: objects, environment.\n"
        "objects: a mapping from id -> {id, emoji, position:{x,y}, state}.\n"
        "environment: include theme, stage_bounds:{width:100,height:100}, generated_at (ISO UTC).\n"
        "Rules: concise snake_case ids; 0<=x<=100; 0<=y<=100; avoid overlap (distance>=6).\n"
        "Do NOT output markdown, comments, or code fences."
    )
    user_prompt = (
        f"theme: {theme}\ncount: {count}\n"
        f"Goal: diverse distinct objects consistent with theme."
    )
    try:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        raw = provider.complete(messages, stream=False)
        # Provider may return dict with 'content' key or direct string
        if isinstance(raw, dict):
            raw_str = raw.get('content') or raw.get('text') or str(raw)
        else:
            raw_str = raw if isinstance(raw, str) else str(raw)
        # Strip code fences if any slipped through
        if '```' in raw_str:
            import re as _re
            m = _re.search(r"```(?:json)?\n(.*?)(```)$", raw_str, flags=_re.DOTALL)
            if m:
                raw_str = m.group(1).strip()
        import json as _json, re as _re
        # Attempt direct JSON parse
        json_candidate = raw_str.strip()
        # If provider wrapped inside text, try last JSON object
        if not json_candidate.startswith('{'):
            obj_match = _re.search(r"\{.*\}\s*$", json_candidate, flags=_re.DOTALL)
            if obj_match:
                json_candidate = obj_match.group(0)
        data = _json.loads(json_candidate)
        objects = data.get('objects') or {}
        env = data.get('environment') or {}
        sanitized_objects = {}
        for key, val in list(objects.items())[:count]:
            if not isinstance(val, dict):
                continue
            oid = _sanitize_id(val.get('id') or key)
            pos = val.get('position', {})
            x = int(max(0, min(100, pos.get('x', random.randint(10, 90)))))
            y = int(max(0, min(100, pos.get('y', random.randint(10, 90)))))
            state = val.get('state', 'on_stage')
            emoji = val.get('emoji', '✨')
            sanitized_objects[oid] = {
                'id': oid,
                'emoji': emoji,
                'position': {'x': x, 'y': y},
                'state': state
            }
        if not sanitized_objects:
            return generate_world_fallback(theme, count, seed=seed, spacing=spacing, algorithm=algorithm)
        # Distance post-check; if too many overlaps, fallback
        coords = [o['position'] for o in sanitized_objects.values()]
        if any(math.hypot(a['x']-b['x'], a['y']-b['y']) < 5 for i,a in enumerate(coords) for j,b in enumerate(coords) if i<j):
            return generate_world_fallback(theme, count, seed=seed, spacing=spacing, algorithm=algorithm)
        env.setdefault('theme', theme)
        env.setdefault('generated_at', datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00','Z'))
        env.setdefault('stage_bounds', {'width': 100, 'height': 100})
        env.setdefault('generation_method', 'llm')
        return {
            'objects': sanitized_objects,
            'environment': env,
            'llm': True,
            'raw_response_len': len(raw_str)
        }
    except Exception as e:
        logger.warning(f"World generation via LLM failed: {e}; falling back.")
        return generate_world_fallback(theme, count, seed=seed, spacing=spacing, algorithm=algorithm)

def persist_world(world: dict, theme: str, seed: int | None = None, base_dir: Path | None = None) -> str:
    """Persist world JSON to data_out/aria_worlds and return file path."""
    try:
        if base_dir is None:
            base_dir = REPO_ROOT / 'data_out' / 'aria_worlds'
        base_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
        seed_val = seed if seed is not None else world.get('environment', {}).get('seed', 'noseed')
        fname = f"world_{_sanitize_id(theme)}_{ts}_{seed_val}.json"
        path = base_dir / fname
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(world, f, indent=2)
        return str(path)
    except Exception as e:
        logger.warning(f"Failed to persist world: {e}")
        return ''

# --------------------------- Cosmos Persistence ---------------------------
@lru_cache(maxsize=1)
def _cosmos_available() -> bool:
    try:
        from shared import cosmos_client  # type: ignore
        return cosmos_client.health().get('enabled') and cosmos_client.init()
    except Exception:
        return False

def persist_world_cosmos(world: dict, theme: str) -> bool:
    """Persist world to dedicated Cosmos 'aria_worlds' container (partition key /theme_seed).

    If Cosmos unavailable or disabled returns False gracefully. Backward compatibility:
    Older container (/userId) is no longer targeted; worlds now use a dedicated container.
    """
    if not _cosmos_available():
        return False
    try:
        from shared import cosmos_client  # type: ignore
        env = world.get('environment', {})
        seed_val = env.get('seed', 'noseed')
        doc = {
            'id': f"world-{theme}-{seed_val}",
            'theme_seed': f"{theme}_{seed_val}",
            'theme': theme,
            'seed': seed_val,
            'objectCount': len(world.get('objects', {})),
            'objects': world.get('objects', {}),
            'environment': env,
            'createdUtc': env.get('generated_at'),
            'generationMethod': env.get('generation_method'),
            'type': 'aria_world'
        }
        return cosmos_client.record_world(doc)
    except Exception as e:
        logger.warning(f"Cosmos persistence error: {e}")
        return False


def fetch_world_filesystem(theme: str, seed: str | int) -> dict | None:
    """Attempt to load a persisted world from filesystem by theme + seed."""
    try:
        base_dir = REPO_ROOT / 'data_out' / 'aria_worlds'
        if not base_dir.exists():
            return None
        seed_str = str(seed)
        theme_clean = _sanitize_id(theme)
        # Pattern: world_<theme>_<timestamp>_<seed>.json
        for fp in sorted(base_dir.glob(f"world_{theme_clean}_*_" + seed_str + ".json")):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                continue
        return None
    except Exception as e:
        logger.warning(f"Filesystem world fetch error: {e}")
        return None


def fetch_world_cosmos(theme: str, seed: str | int) -> dict | None:
    """Fetch world from Cosmos by theme + seed if available; returns None on failure."""
    if not _cosmos_available():
        return None
    try:
        from shared import cosmos_client  # type: ignore
        doc = cosmos_client.get_world(theme, seed)
        return doc
    except Exception as e:
        logger.warning(f"Cosmos fetch error: {e}")
        return None


# Initialize global action parser
action_parser = AriaActionParser()


def get_stage_context() -> str:
    """Generate natural language description of current stage state for AI"""
    aria = stage_state['aria']
    objects = stage_state['objects']
    
    # Calculate distances to objects
    aria_pos = aria['position']
    nearby_objects = []
    for obj_name, obj_data in objects.items():
        # Safety check: ensure object has position data
        if not isinstance(obj_data, dict) or 'position' not in obj_data:
            continue
        obj_pos = obj_data['position']
        if not isinstance(obj_pos, dict) or 'x' not in obj_pos or 'y' not in obj_pos:
            continue
        distance = ((aria_pos['x'] - obj_pos['x'])**2 + (aria_pos['y'] - obj_pos['y'])**2)**0.5
        if distance < 30:  # Within reach
            nearby_objects.append(obj_name)
    
    context = f"""STAGE VIEW:
- Aria is at position ({aria_pos['x']}%, {aria_pos['y']}%), facing {aria['facing']}
- Expression: {aria['expression']}
- Held object: {aria['held_object'] or 'none'}
- Table is at (60%, 20%) on the right side
- Objects on table: {', '.join([k for k, v in objects.items() if isinstance(v, dict) and v.get('state') == 'on_table'])}
- Objects nearby Aria (within reach): {', '.join(nearby_objects) if nearby_objects else 'none'}
- Stage dimensions: 100% wide x 100% tall (0,0=top-left, 100,100=bottom-right)
"""
    return context

def get_stage_context() -> str:
    """Get formatted stage context for LLM"""
    aria_pos = stage_state['aria']['position']
    context_lines = [
        f"Aria position: x={aria_pos['x']}%, y={aria_pos['y']}%",
        f"Aria facing: {stage_state['aria']['facing']}",
        f"Aria expression: {stage_state['aria']['expression']}",
        "Objects on stage:"
    ]
    
    for obj_id, obj_data in stage_state['objects'].items():
        obj_pos = obj_data['position']
        obj_state = obj_data.get('state', 'unknown')
        context_lines.append(f"  - {obj_id}: x={obj_pos['x']}%, y={obj_pos['y']}%, state={obj_state}")
    
    return "\n".join(context_lines)

def determine_position_from_context(cmd: str) -> str:
    """AI-driven position determination based on command semantics and stage state"""
    aria_pos = stage_state['aria']['position']
    objects = stage_state['objects']
    table_pos = stage_state['environment']['table']['position']
    
    # Object interaction positioning - move near the object
    for obj_name in ['apple', 'book', 'cup', 'ball', 'flower', 'bear']:
        if obj_name in cmd and ('pick' in cmd or 'get' in cmd or 'grab' in cmd or 'take' in cmd):
            if obj_name in objects:
                obj_data = objects[obj_name]
                # Safety check: ensure object has position data
                if isinstance(obj_data, dict) and 'position' in obj_data:
                    obj_pos = obj_data['position']
                    if isinstance(obj_pos, dict) and 'x' in obj_pos and 'y' in obj_pos:
                        # Position slightly to the left of object
                        return f'[aria:position:{max(10, obj_pos["x"] - 10)}:{obj_pos["y"] + 10}]'
    
    # Action-based positioning
    if any(k in cmd for k in ['jump', 'leap', 'hop']):
        return '[aria:position:50:60]'  # Center for jumping
    elif any(k in cmd for k in ['dance', 'spin', 'twirl']):
        return '[aria:position:50:50]'  # Center stage for performance
    elif any(k in cmd for k in ['wave', 'greet', 'hello', 'hi']):
        return '[aria:position:30:70]'  # Front-left for greeting
    elif any(k in cmd for k in ['look', 'see', 'watch', 'observe']):
        # Look towards table
        if 'table' in cmd:
            return '[aria:position:40:60]'  # Position to see table
        return '[aria:position:20:40]'  # Left side for observing
    elif any(k in cmd for k in ['sit', 'rest', 'relax']):
        return f'[aria:position:{table_pos["x"] - 5}:{table_pos["y"] + 35}]'  # Near table to sit
    elif any(k in cmd for k in ['run', 'race', 'sprint']):
        return '[aria:position:85:70]'  # Far right for running space
    elif any(k in cmd for k in ['hide', 'crouch', 'duck']):
        return '[aria:position:10:75]'  # Corner position
    elif any(k in cmd for k in ['present', 'show', 'display']):
        return '[aria:position:50:50]'  # Center to present
    elif any(k in cmd for k in ['think', 'wonder', 'ponder']):
        return '[aria:position:25:50]'  # Contemplative left position
    elif any(k in cmd for k in ['walk left', 'go left', 'left']):
        return '[aria:position:20:70]'  # Moving to left
    elif any(k in cmd for k in ['walk right', 'go right', 'right']):
        return '[aria:position:80:70]'  # Moving to right
    elif 'add' in cmd or 'create' in cmd or 'spawn' in cmd:
        # For adding objects, position near table
        return f'[aria:position:{table_pos["x"] - 15}:{table_pos["y"] + 20}]'
    else:
        # Context-aware positioning: stay put if already in good position
        # or move to interesting area if idle
        import hashlib
        pos_hash = int(hashlib.md5(cmd.encode()).hexdigest()[:4], 16)
        x = 30 + (pos_hash % 40)  # Random between 30-70%
        y = 60 + (pos_hash % 20)  # Random between 60-80%
        return f'[aria:position:{x}:{y}]'

def generate_tags_ai(command: str) -> dict:
    """Generate tags using LLM chat provider.

    Returns dict with keys:
        - response_text: Full natural language response from LLM
        - tags: List of extracted movement/action tags
        - success: Boolean indicating if generation was successful
        - provider: Provider name used (e.g., 'azure', 'openai', 'lora', 'local', 'lmstudio')
    """
    if not LLM_AVAILABLE:
        return {'response_text': '', 'tags': [], 'success': False, 'provider': 'none'}
    
    try:
        # Prefer LoRA if adapter dir is available
        import os
        from pathlib import Path
        adapter_env = os.getenv('ARIA_LORA_ADAPTER_DIR')
        default_adapter = Path(REPO_ROOT) / 'data_out' / 'lora_training' / 'lora_adapter'
        adapter_dir = Path(adapter_env) if adapter_env else default_adapter
        provider = None
        provider_name = None

        if adapter_dir.exists() and (adapter_dir / 'adapter_config.json').exists():
            # Try LoRA provider explicitly
            provider, choice = detect_provider(explicit='lora', model_override=str(adapter_dir))
            provider_name = choice.name
        else:
            # Auto-detect (Azure/OpenAI/LMStudio/local)
            provider, choice = detect_provider()
            provider_name = choice.name
        
        # Build context-aware system prompt
        stage_context = get_stage_context()
        system_prompt = f"""You are an AI assistant that controls Aria, a 3D character.
Your task is to interpret user commands and generate movement/action tags.

Available movement tags:
- [aria:move:left] - Move left (small movement)
- [aria:move:right] - Move right (small movement)
- [aria:move:up] - Move up (small movement)
- [aria:move:down] - Move down (small movement)
- [aria:walk:left] - Walk left (larger movement)
- [aria:walk:right] - Walk right (larger movement)
- [aria:walk:up] - Walk up (larger movement)
- [aria:walk:down] - Walk down (larger movement)
- [aria:center] - Move to center stage
- [aria:wave] - Wave gesture
- [aria:jump] - Jump animation
- [aria:dance] - Dance animation

Limb control tags:
- [aria:limb:left_arm:raise] - Raise left arm
- [aria:limb:right_arm:raise] - Raise right arm
- [aria:limb:left_arm:lower] - Lower left arm
- [aria:limb:right_arm:lower] - Lower right arm
- [aria:limb:left_arm:wave] - Wave left arm
- [aria:limb:right_arm:wave] - Wave right arm
- [aria:limb:left_arm:forward] - Move left arm forward
- [aria:limb:right_arm:forward] - Move right arm forward
- [aria:limb:left_arm:back] - Move left arm back
- [aria:limb:right_arm:back] - Move right arm back

IMPORTANT: When the user says "arms" (plural) or "both arms", always generate tags for BOTH left_arm AND right_arm together.
Example: "raise arms" should generate: [aria:limb:left_arm:raise] [aria:limb:right_arm:raise]

Current stage state:
{stage_context}

Respond naturally to the user's command and include the appropriate tags in your response.
Always include at least one movement or action tag when relevant."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]
        
        # Get LLM response
        response = provider.complete(messages, stream=False)
        
        # Handle both dict and string responses
        if isinstance(response, dict):
            response_text = response.get('content', '')
        else:
            response_text = str(response)
        
        # Extract tags from response
        tags = re.findall(r'\[aria:[^\]]+\]', response_text)
        
        logger.info(f"LLM generated response: {response_text[:100]}...")
        logger.info(f"Extracted tags: {tags}")
        
        return {
            'response_text': response_text,
            'tags': tags[:3],  # Return first 3 tags max
            'success': True,
            'provider': provider_name or 'unknown',
        }
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        import traceback
        traceback.print_exc()
        return {'response_text': '', 'tags': [], 'success': False, 'provider': 'error'}

def generate_tags_fallback(command: str) -> List[str]:
    """Simple rule-based fallback tag generation with automatic positioning"""
    cmd = command.lower()
    tags = []
    
    # AI-driven automatic positioning based on command context
    # Determine optimal position for the action
    auto_position = determine_position_from_context(cmd)
    if auto_position:
        tags.append(auto_position)
    
    # Track if limb commands are detected to avoid movement conflicts
    has_limb_command = any(k in cmd for k in [
        'left arm', 'arm left', 'left hand', 'right arm', 'arm right', 'right hand',
        'left leg', 'leg left', 'right leg', 'leg right'
    ])
    
    # Special: server-side "say" / announce detection (capture original text)
    try:
        say_match = re.search(r"(?:\b(?:say|announce|shout|speak|tell)\b)(?:\s+(?:everyone|that|to))?[:\-\s]+(.+)", command, flags=re.I)
        if say_match:
            raw_msg = say_match.group(1).strip()
            # basic sanitization and length cap
            safe_msg = re.sub(r'\]', '', raw_msg)[:200]
            tags.append(f'[aria:say:{safe_msg}]')
    except Exception:
        # ignore parsing errors
        pass

    # Expressions
    if 'smile' in cmd or 'happy' in cmd:
        tags.append('[aria:expression:smile]')
    elif 'sad' in cmd:
        tags.append('[aria:expression:sad]')
    elif 'surprised' in cmd:
        tags.append('[aria:expression:surprised]')
    elif 'confused' in cmd:
        tags.append('[aria:expression:confused]')
    elif 'thinking' in cmd or 'think' in cmd:
        tags.append('[aria:expression:thinking]')
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
    
    # Limb controls and poses (AI may also emit these; fallback supports natural phrases)
    # Hands up / T-pose / Cross arms
    if 'hands up' in cmd or 'raise hands' in cmd:
        tags.append('[aria:limb:left_arm:raise]')
        tags.append('[aria:limb:right_arm:raise]')
    if 't-pose' in cmd or 'tpose' in cmd or 't pose' in cmd:
        tags.append('[aria:pose:t-pose]')
    if 'cross arms' in cmd or 'arms crossed' in cmd:
        tags.append('[aria:pose:cross_arms]')

    # Per-limb commands
    def limb_tag(part: str, action: str):
        tags.append(f'[aria:limb:{part}:{action}]')

    # Helper maps
    left_arm = any(k in cmd for k in ['left arm', 'arm left', 'left hand'])
    right_arm = any(k in cmd for k in ['right arm', 'arm right', 'right hand'])
    both_arms = any(k in cmd for k in ['both arms', 'arms', 'both hands', 'hands'])
    left_leg = any(k in cmd for k in ['left leg', 'leg left'])
    right_leg = any(k in cmd for k in ['right leg', 'leg right'])

    # Numeric angle if present (e.g., "left arm 45 degrees")
    angle_match = None
    try:
        angle_match = next((m for m in __import__('re').finditer(r'(-?\d{1,3})\s*(deg|degree|degrees)?', cmd)), None)
    except Exception:
        angle_match = None
    angle_val = angle_match.group(1) if angle_match else None

    # Arm actions
    if both_arms or left_arm or right_arm or 'arm' in cmd:
        # Choose which arms to move
        parts = []
        if both_arms and not left_arm and not right_arm:
            # When "arms" or "both arms" is specified, always move both
            parts = ['left_arm', 'right_arm']
        else:
            if left_arm:
                parts.append('left_arm')
            if right_arm:
                parts.append('right_arm')
            if not parts:
                # Default to right arm only if neither specified
                parts = ['right_arm']
        
        if any(k in cmd for k in ['wave', 'wiggle']):
            for p in parts: limb_tag(p, 'wave')
        elif any(k in cmd for k in ['raise', 'up', 'lift']):
            for p in parts: limb_tag(p, 'raise')
        elif any(k in cmd for k in ['lower', 'down']):
            for p in parts: limb_tag(p, 'lower')
        elif any(k in cmd for k in ['forward', 'front']):
            for p in parts: limb_tag(p, 'forward')
        elif any(k in cmd for k in ['back', 'backward', 'behind']):
            for p in parts: limb_tag(p, 'back')
        elif angle_val is not None:
            for p in parts: limb_tag(p, angle_val)

    # Leg actions
    if left_leg or right_leg or 'leg' in cmd:
        parts = []
        if left_leg:
            parts.append('left_leg')
        if right_leg:
            parts.append('right_leg')
        if not parts:
            parts = ['left_leg']
        if 'kick' in cmd:
            for p in parts: limb_tag(p, 'kick')
        elif any(k in cmd for k in ['forward', 'front']):
            for p in parts: limb_tag(p, 'forward')
        elif any(k in cmd for k in ['back', 'backward', 'behind']):
            for p in parts: limb_tag(p, 'back')
        elif angle_val is not None:
            for p in parts: limb_tag(p, angle_val)

    # Movement - only add if not a limb command (to avoid conflicts like "left arm" -> "move:left")
    if not has_limb_command:
        # Determine movement style
        movement_style = None
        if 'skip' in cmd:
            movement_style = 'skip'
        elif 'strut' in cmd or 'swagger' in cmd:
            movement_style = 'strut'
        elif 'run' in cmd:
            movement_style = 'run'
        elif 'walk' in cmd:
            movement_style = 'walk'
        else:
            movement_style = 'move'
        
        # Determine direction - exclude if keywords could be part of limb commands
        has_forward_limb = 'leg' in cmd or 'arm' in cmd
        if 'left' in cmd:
            tags.append(f'[aria:{movement_style}:left]')
        elif 'right' in cmd:
            tags.append(f'[aria:{movement_style}:right]')
        elif ('up' in cmd or 'forward' in cmd) and not has_forward_limb:
            tags.append(f'[aria:{movement_style}:up]')
        elif ('down' in cmd or 'back' in cmd) and not has_forward_limb:
            tags.append(f'[aria:{movement_style}:down]')
    
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
    
    # Poses (body positions)
    if 'sit' in cmd:
        tags.append('[aria:pose:sit]')
    elif 'stand' in cmd:
        tags.append('[aria:pose:stand]')
    elif 'crouch' in cmd:
        tags.append('[aria:pose:crouch]')
    elif 'lie' in cmd or 'lay' in cmd:
        tags.append('[aria:pose:lie]')
    
    # Position control - let AI determine where Aria should be
    # Format: [aria:position:x:y] where x and y are percentages (0-100)
    # Or named positions: [aria:position:center], [aria:position:left], etc.
    position_keywords = {
        'center': '[aria:position:50:50]',
        'left side': '[aria:position:15:80]',
        'right side': '[aria:position:85:80]',
        'top': '[aria:position:50:10]',
        'bottom': '[aria:position:50:90]',
        'corner': '[aria:position:10:10]',
        'stage left': '[aria:position:20:70]',
        'stage right': '[aria:position:80:70]',
        'front': '[aria:position:50:85]',
        'back': '[aria:position:50:15]'
    }
    
    # Check for position commands
    if 'position' in cmd or 'move to' in cmd or 'go to' in cmd or 'stand at' in cmd:
        for keyword, tag in position_keywords.items():
            if keyword in cmd:
                tags.append(tag)
                break
        else:
            # Try to extract numeric coordinates
            coord_match = re.search(r'(\d{1,3})%?.*?(\d{1,3})%?', cmd)
            if coord_match:
                x, y = coord_match.groups()
                tags.append(f'[aria:position:{x}:{y}]')
    
    # Object management (add/remove objects)
    if 'add' in cmd or 'create' in cmd or 'spawn' in cmd:
        object_emojis = {
            'bear': '🧸', 'teddy': '🧸',
            'cat': '🐱', 'dog': '🐶', 'bunny': '🐰', 'rabbit': '🐰',
            'star': '⭐', 'heart': '❤️', 'moon': '🌙', 'sun': '☀️',
            'tree': '🌲', 'plant': '🌿', 'mushroom': '🍄',
            'car': '🚗', 'bike': '🚲', 'plane': '✈️'
        }
        for obj_name, emoji in object_emojis.items():
            if obj_name in cmd:
                tags.append(f'[aria:interact:add:{obj_name}:{emoji}]')
                break
    
    return tags


def execute_aria_action(action: dict) -> dict:
    """
    Execute a single structured action and update stage state
    
    Args:
        action: Action dict with 'action' key and params
    
    Returns:
        Result dict with status, message, and updated state
    """
    action_type = action.get('action')
    
    if action_type not in ARIA_ACTIONS:
        return {'status': 'error', 'message': f'Unknown action: {action_type}'}
    
    try:
        if action_type == 'move':
            target = action.get('target')
            if isinstance(target, dict) and 'x' in target and 'y' in target:
                stage_state['aria']['position'] = target
                return {
                    'status': 'success',
                    'message': f'Moved to ({target["x"]}, {target["y"]})',
                    'tags': [f'[aria:position:{target["x"]}:{target["y"]}]']
                }
            elif isinstance(target, str) and target in stage_state['objects']:
                # Move to object
                obj_pos = stage_state['objects'][target]['position']
                stage_state['aria']['position'] = {'x': obj_pos['x'] - 10, 'y': obj_pos['y'] + 5}
                return {
                    'status': 'success',
                    'message': f'Moved to {target}',
                    'tags': [f'[aria:position:{obj_pos["x"] - 10}:{obj_pos["y"] + 5}]']
                }
        
        elif action_type == 'say':
            text = action.get('text', '')
            emotion = action.get('emotion', 'neutral')
            stage_state['aria']['expression'] = emotion
            return {
                'status': 'success',
                'message': f'Said: "{text}" with {emotion} emotion',
                'tags': [f'[aria:say:{text}]', f'[aria:expression:{emotion}]']
            }
        
        elif action_type == 'pickup':
            obj_id = action.get('object_id')
            if obj_id not in stage_state['objects']:
                return {'status': 'error', 'message': f'Object not found: {obj_id}'}
            
            if stage_state['aria']['held_object']:
                return {'status': 'error', 'message': 'Already holding an object'}
            
            # Check distance
            aria_pos = stage_state['aria']['position']
            obj_pos = stage_state['objects'][obj_id]['position']
            distance = ((aria_pos['x'] - obj_pos['x'])**2 + (aria_pos['y'] - obj_pos['y'])**2)**0.5
            
            if distance > 30:
                return {'status': 'error', 'message': f'Too far from {obj_id}. Move closer first.'}
            
            stage_state['aria']['held_object'] = obj_id
            stage_state['objects'][obj_id]['state'] = 'held'
            return {
                'status': 'success',
                'message': f'Picked up {obj_id}',
                'tags': [f'[aria:pickup:{obj_id}]', f'[aria:limb:right_arm:grab]']
            }
        
        elif action_type == 'drop':
            if not stage_state['aria']['held_object']:
                return {'status': 'error', 'message': 'Not holding anything'}
            
            obj_id = stage_state['aria']['held_object']
            position = action.get('position', stage_state['aria']['position'])
            
            stage_state['objects'][obj_id]['position'] = position
            stage_state['objects'][obj_id]['state'] = 'dropped'
            stage_state['aria']['held_object'] = None
            
            return {
                'status': 'success',
                'message': f'Dropped {obj_id}',
                'tags': [f'[aria:drop:{obj_id}]', '[aria:limb:right_arm:release]']
            }
        
        elif action_type == 'throw':
            if not stage_state['aria']['held_object']:
                return {'status': 'error', 'message': 'Not holding anything'}
            
            obj_id = stage_state['aria']['held_object']
            target = action.get('target', {'x': 70, 'y': 40})
            force = action.get('force', 'medium')
            
            stage_state['objects'][obj_id]['position'] = target
            stage_state['objects'][obj_id]['state'] = 'thrown'
            stage_state['aria']['held_object'] = None
            
            return {
                'status': 'success',
                'message': f'Threw {obj_id} with {force} force',
                'tags': [f'[aria:throw:{obj_id}]', '[aria:limb:right_arm:throw]', f'[aria:animation:throw_{force}]']
            }
        
        elif action_type == 'gesture':
            gesture_type = action.get('gesture_type', 'wave')
            valid_gestures = ['wave', 'bow', 'nod', 'shake', 'point', 'shrug', 'clap']
            
            if gesture_type not in valid_gestures:
                gesture_type = 'wave'  # Default fallback
            
            return {
                'status': 'success',
                'message': f'Performed {gesture_type} gesture',
                'tags': [f'[aria:gesture:{gesture_type}]', f'[aria:animation:{gesture_type}]']
            }
        
        elif action_type == 'look':
            target = action.get('target')
            if isinstance(target, str) and target in stage_state['objects']:
                # Look at object
                obj_pos = stage_state['objects'][target]['position']
                aria_pos = stage_state['aria']['position']
                facing = 'right' if obj_pos['x'] > aria_pos['x'] else 'left'
                stage_state['aria']['facing'] = facing
                return {
                    'status': 'success',
                    'message': f'Looking at {target}',
                    'tags': [f'[aria:look:{target}]', f'[aria:facing:{facing}]']
                }
            elif isinstance(target, dict) and 'x' in target:
                # Look at position
                aria_pos = stage_state['aria']['position']
                facing = 'right' if target['x'] > aria_pos['x'] else 'left'
                stage_state['aria']['facing'] = facing
                return {
                    'status': 'success',
                    'message': f'Looking at position',
                    'tags': [f'[aria:facing:{facing}]']
                }
        
        elif action_type == 'wait':
            duration = action.get('duration', 1.0)
            return {
                'status': 'success',
                'message': f'Waiting {duration}s',
                'tags': [f'[aria:wait:{duration}]']
            }
        
        return {'status': 'error', 'message': f'Action not implemented: {action_type}'}
        
    except Exception as e:
        logger.error(f"Action execution failed: {e}")
        return {'status': 'error', 'message': str(e)}


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
        """Serve static files + lightweight GET API endpoints."""
        print(f"📥 GET request: {self.path}")

        # Objects / state snapshot
        if self.path == '/api/aria/objects' or self.path == '/api/aria/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            payload = {'objects': stage_state.get('objects', {}), 'aria': stage_state.get('aria', {})}
            self.wfile.write(json.dumps(payload).encode('utf-8'))
            return

        # World retrieval: /api/aria/world/get?theme=forest&seed=12345
        if self.path.startswith('/api/aria/world/get'):
            try:
                q = parse_qs(urlparse(self.path).query)
                theme = q.get('theme', [''])[0]
                seed = q.get('seed', [''])[0]
                if not theme or not seed:
                    raise ValueError('theme and seed query params are required')
                cosmos_doc = fetch_world_cosmos(theme, seed)
                source = None
                world_data = None
                if cosmos_doc:
                    # Cosmos doc already structured; ensure objects/environment keys
                    if 'objects' in cosmos_doc and 'environment' in cosmos_doc:
                        world_data = {
                            'objects': cosmos_doc.get('objects', {}),
                            'environment': cosmos_doc.get('environment', {}),
                            'llm': cosmos_doc.get('generationMethod') == 'llm'
                        }
                        source = 'cosmos'
                if world_data is None:
                    fs_world = fetch_world_filesystem(theme, seed)
                    if fs_world:
                        world_data = fs_world
                        source = 'filesystem'
                if world_data is None:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'not_found', 'theme': theme, 'seed': seed}).encode('utf-8'))
                    return
                resp = {
                    'status': 'success',
                    'theme': theme,
                    'seed': seed,
                    'source': source,
                    'objects': world_data.get('objects', {}),
                    'environment': world_data.get('environment', {})
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp, indent=2).encode('utf-8'))
                return
            except Exception as e:
                logger.error(f"World retrieval error: {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode('utf-8'))
                return

        # World list (GET variant) - enumerate filesystem + cosmos metadata
        if self.path == '/api/aria/world/list':
            try:
                base_dir = REPO_ROOT / 'data_out' / 'aria_worlds'
                worlds_fs = []
                if base_dir.exists():
                    for f in sorted(base_dir.glob('world_*.json')):
                        parts = f.stem.split('_')
                        theme_val = parts[1] if len(parts) >= 4 else None
                        seed_val = parts[-1] if len(parts) >= 4 else None
                        worlds_fs.append({'file': str(f), 'theme': theme_val, 'seed': seed_val})
                cosmos_worlds = []
                if _cosmos_available():
                    try:
                        from shared import cosmos_client  # type: ignore
                        cosmos_worlds = cosmos_client.list_worlds(limit=50)
                    except Exception as ce:
                        logger.warning(f"Cosmos list_worlds error: {ce}")
                payload = {
                    'status': 'success',
                    'worlds': worlds_fs,
                    'cosmos': {
                        'available': _cosmos_available(),
                        'count': len(cosmos_worlds),
                        'worlds': cosmos_worlds
                    }
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(payload, indent=2).encode('utf-8'))
                return
            except Exception as e:
                logger.error(f"World list error (GET): {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode('utf-8'))
                return

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
                
                # Update stage state if provided
                if 'stage_state' in data:
                    stage_state.update(data['stage_state'])
                
                print(f"📝 Command received: {command}")
                print(f"👁️  Stage context:\n{get_stage_context()}")
                
                # Try AI first with full context, fallback to rules
                ai_result = generate_tags_ai(command)
                tags = ai_result['tags']
                response_text = ai_result.get('response_text', '')
                provider_used = ai_result.get('provider', 'unknown')
                
                if not tags:
                    tags = generate_tags_fallback(command)
                    model_used = 'fallback'
                else:
                    model_used = provider_used or 'ai'
                
                print(f"✨ Generated tags: {tags}")
                if response_text:
                    print(f"💬 LLM response: {response_text[:100]}...")
                
                response = {
                    'command': command,
                    'tags': tags,
                    'response': response_text,  # Include full LLM response
                    'model': model_used,
                    'stage_context': get_stage_context(),
                    'stage_aware': True
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
        elif self.path == '/api/aria/object' or self.path == '/api/aria/objects':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                # Support both single object ({action, object}) and bulk ({objects: {...}})
                if 'objects' in data and isinstance(data['objects'], dict):
                    # Merge supplied objects into stage_state
                    for k, v in data['objects'].items():
                        if isinstance(v, dict) and 'position' in v:
                            stage_state['objects'][k] = v
                    result = {'status': 'ok', 'objects': stage_state['objects']}
                elif 'object' in data and 'action' in data:
                    action = data['action']
                    obj = data['object']
                    obj_id = obj.get('id') or obj.get('name')
                    if not obj_id:
                        raise ValueError('object missing id/name')

                    if action == 'add':
                        position = obj.get('position', {'x': 50, 'y': 50})
                        state = obj.get('state', 'on_stage')
                        stage_state['objects'][obj_id] = {'position': position, 'state': state}
                        result = {'status': 'added', 'id': obj_id, 'object': stage_state['objects'][obj_id]}
                    elif action == 'update':
                        if obj_id not in stage_state['objects']:
                            stage_state['objects'][obj_id] = {}
                        if 'position' in obj:
                            stage_state['objects'][obj_id]['position'] = obj['position']
                        if 'state' in obj:
                            stage_state['objects'][obj_id]['state'] = obj['state']
                        result = {'status': 'updated', 'id': obj_id, 'object': stage_state['objects'][obj_id]}
                    elif action == 'remove' or action == 'delete':
                        removed = stage_state['objects'].pop(obj_id, None)
                        result = {'status': 'removed', 'id': obj_id, 'object': removed}
                    else:
                        raise ValueError(f'unknown action: {action}')

                else:
                    raise ValueError('invalid payload')

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                return
            except Exception as e:
                print(f"❌ Object API error: {e}")
                try:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                except:
                    pass
                return
        
        # /api/aria/execute - LLM-powered automatic action execution
        elif self.path == '/api/aria/execute':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                command = data.get('command', '')
                auto_execute = data.get('auto_execute', False)
                use_llm = data.get('use_llm', True)
                
                if not command:
                    raise ValueError('command is required')
                
                # Parse command into actions
                actions = action_parser.parse(command, use_llm=use_llm)
                
                if not actions:
                    result = {
                        'status': 'error',
                        'message': 'Could not parse command into actions',
                        'command': command,
                        'actions': []
                    }
                else:
                    # Execute actions if auto_execute is True
                    results = []
                    all_tags = []
                    
                    if auto_execute:
                        for action in actions:
                            exec_result = execute_aria_action(action)
                            results.append({
                                'action': action,
                                'result': exec_result
                            })
                            if exec_result.get('tags'):
                                all_tags.extend(exec_result['tags'])
                    
                    result = {
                        'status': 'success',
                        'message': f'Parsed {len(actions)} actions' + (' and executed' if auto_execute else ' (plan only)'),
                        'command': command,
                        'actions': actions,
                        'executed': auto_execute,
                        'results': results if auto_execute else None,
                        'tags': all_tags if auto_execute else None,
                        'state': stage_state if auto_execute else None
                    }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
                
                print(f"✓ Execute API: {command} -> {len(actions)} actions" + 
                      (f" (executed)" if auto_execute else " (plan only)"))
                return
                
            except Exception as e:
                print(f"❌ Execute API error: {e}")
                import traceback
                traceback.print_exc()
                try:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'error',
                        'error': str(e),
                        'message': f'Failed to execute command: {str(e)}'
                    }).encode('utf-8'))
                except:
                    pass
                return
        
        # /api/aria/world - Generate or regenerate themed world layout
        elif self.path == '/api/aria/world':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8')) if body else {}
                theme = data.get('theme', 'forest')
                count = int(data.get('count', 6))
                use_llm = bool(data.get('use_llm', True))
                seed = data.get('seed')
                spacing = int(data.get('spacing', 10))
                persist_flag_env = os.getenv('ARIA_WORLD_PERSIST', 'false').lower() == 'true'
                persist_flag = bool(data.get('persist', persist_flag_env))
                algorithm = data.get('algorithm', 'rejection')

                # Generate
                if use_llm and action_parser.provider:
                    world = generate_world_with_llm(theme, count, action_parser.provider, seed=seed, spacing=spacing, algorithm=algorithm)
                else:
                    world = generate_world_fallback(theme, count, seed=seed, spacing=spacing, algorithm=algorithm)

                # Update global stage_state (replace objects, keep aria position)
                stage_state['objects'] = {}
                for oid, obj in world['objects'].items():
                    stage_state['objects'][oid] = {
                        'position': obj['position'],
                        'state': obj.get('state', 'on_stage'),
                        'emoji': obj.get('emoji', '')
                    }
                # Update environment meta
                stage_state['environment']['theme'] = world['environment'].get('theme', theme)
                stage_state['environment']['generated_at'] = world['environment'].get('generated_at')
                stage_state['environment']['seed'] = world['environment'].get('seed')
                stage_state['environment']['generation_method'] = world['environment'].get('generation_method', 'unknown')
                stage_state['environment']['spacing'] = world['environment'].get('spacing', spacing)

                response = {
                    'status': 'success',
                    'theme': theme,
                    'count': len(world['objects']),
                    'used_llm': world.get('llm', False),
                    'objects': world['objects'],
                    'environment': world['environment']
                }
                if persist_flag:
                    persisted_path = persist_world(world, theme, seed=seed)
                    if persisted_path:
                        response['persisted_path'] = persisted_path
                        response['persisted'] = True
                    else:
                        response['persisted'] = False
                        response['persist_error'] = 'failed_to_write_file'
                    # Attempt Cosmos persistence
                    response['cosmos_persisted'] = persist_world_cosmos(world, theme)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
                logger.info(f"✓ World generated (theme={theme}, llm={response['used_llm']}, count={response['count']}, algo={algorithm})")
                return
            except Exception as e:
                logger.error(f"World generation error: {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode('utf-8'))
                return

        # /api/aria/world/list - list persisted worlds (filesystem) + cosmos status
        elif self.path == '/api/aria/world/list':
            try:
                base_dir = REPO_ROOT / 'data_out' / 'aria_worlds'
                worlds = []
                if base_dir.exists():
                    for f in sorted(base_dir.glob('world_*.json')):
                        parts = f.stem.split('_')
                        # world_<theme>_<timestamp>_<seed>.json
                        theme = parts[1] if len(parts) >= 4 else None
                        seed_val = parts[-1] if len(parts) >= 4 else None
                        worlds.append({'file': str(f), 'theme': theme, 'seed': seed_val})
                payload = {
                    'status': 'success',
                    'worlds': worlds,
                    'cosmos': {
                        'available': _cosmos_available()
                    }
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(payload, indent=2).encode('utf-8'))
                return
            except Exception as e:
                logger.error(f"World list error: {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode('utf-8'))
                return

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
