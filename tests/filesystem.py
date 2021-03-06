from bw_projects.filesystem import safe_filename, get_dir_size, md5
from pathlib import Path

fixtures_dir = Path(__file__, "..").resolve() / "fixtures"


def test_md5():
    assert md5(fixtures_dir / "lorem.txt") == "edc715389af2498a623134608ba0a55b"


def test_dir_size():
    assert get_dir_size(fixtures_dir)
    assert get_dir_size(str(fixtures_dir))


def test_safe_filename():
    assert safe_filename("Wave your hand yeah 🙋!") == "Wave-your-hand-yeah.f7952a3d4b0534cdac0e0cbbf66aac73"
    assert safe_filename("Wave your hand yeah 🙋!", add_hash=False) == "Wave-your-hand-yeah"
