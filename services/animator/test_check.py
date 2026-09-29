"""The animator refuses code that could touch files, the system or its own internals."""
from app import check

OK = """from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("2.1", "惯性", "Inertia")
        t = ValueTracker(0)
        self.add(always_redraw(lambda: Dot([t.get_value(), 0, 0])))
        self.play(t.animate.set_value(2))
        self.caption("中文", "English")
"""


def test_a_normal_scene_passes():
    assert check(OK) == ""


def test_dangerous_code_is_refused():
    bad = {
        "import os": "import of 'os'",
        "from subprocess import run": "import from 'subprocess'",
        "open('/etc/passwd')": "name 'open'",
        "eval('1')": "name 'eval'",
        "getattr(Base, 'x')": "name 'getattr'",
        "().__class__": "attribute '.__class__'",
        "np.load('x.npy')": "attribute '.load'",
        "ImageMobject('/etc/hosts')": "name 'ImageMobject'",
        "config.media_dir = '/'": "name 'config'",
        "self.renderer.x = 1": "attribute '.renderer'",
        "__builtins__": "name '__builtins__'",
    }
    for line, why in bad.items():
        code = OK + "        " + line + "\n" if not line.startswith(("import", "from")) else line + "\n" + OK
        assert why in check(code), line


def test_scene_name_and_syntax():
    assert "class Lesson" in check("from wq_anim import *\nclass Other(Base):\n    pass\n")
    assert "SyntaxError" in check("class Lesson(Base):\n    def construct(self)\n")
    assert "too long" in check("#" * 50_000)
