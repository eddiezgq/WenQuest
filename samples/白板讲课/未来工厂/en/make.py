"""《未来工厂》英文版：同一套画板，英文配音（Kokoro am_michael），英文字幕在上、中文在下。给英文讲座网页用。
    python3 make.py <kokoro 模型目录> | --fake   然后  python3 ../../../../tools/whiteboard/wb.py ."""
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
import make as zh  # noqa: E402  (builds the boards)
from fastkit import main  # noqa: E402

if __name__ == "__main__":
    main(here, zh.S, zh.B, zh.TITLE, "en", say={"UDI": "U D I", "FDA": "F D A", "AI": "A I"})
