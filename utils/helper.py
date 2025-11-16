import json
from pathlib import Path

from utils.settings import GAME_STATE


def save_data():
    data_to_save = {
        "pass_count": GAME_STATE.get("pass_count", 0),
        "play_count": GAME_STATE.get("play_count", 0),
        "highest_score": GAME_STATE.get("highest_score", 0),
        "coins": GAME_STATE.get("coins", 0),
        "beer": GAME_STATE.get("beer", 0),
        "volume": GAME_STATE.get("volume", 5),
        "vibration": GAME_STATE.get("vibration", True)
    }

    # 获取项目根目录
    project_root = Path(__file__).resolve().parents[1]

    # 确保 data 文件夹存在
    data_dir = project_root / "data" / "game"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 写入 JSON 文件
    data_path = data_dir / "data.json"
    with data_path.open("w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)