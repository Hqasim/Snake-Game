from snake_game.persistence import load_high_score, save_high_score


def test_load_high_score_defaults_to_zero_when_file_missing(tmp_path):
    assert load_high_score(tmp_path / "does_not_exist.json") == 0


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "nested" / "highscore.json"
    save_high_score(path, 42)
    assert load_high_score(path) == 42


def test_load_high_score_defaults_to_zero_on_corrupt_file(tmp_path):
    path = tmp_path / "highscore.json"
    path.write_text("not valid json", encoding="utf-8")
    assert load_high_score(path) == 0
