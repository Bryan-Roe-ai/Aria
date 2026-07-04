import json
import random
from pathlib import Path

import numpy as np


def set_seed(s):
    random.seed(s)
    np.random.seed(s)


def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)


def save_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2))


def load_json(path):
    import json

    return json.loads(Path(path).read_text())
