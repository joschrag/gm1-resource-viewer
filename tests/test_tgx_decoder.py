import pathlib

import pytest
from PIL import Image

import gm1_resource_viewer as gm1_rv


@pytest.mark.parametrize("filename", ["armys1.tgx", "armys10.tgx"])
def test_decode_tgx_data(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "tgx" / filename
    img = gm1_rv.decode_tgx_data(file_path.read_bytes())
    assert isinstance(img, Image.Image)


@pytest.mark.parametrize("filename", ["armys1.tgx", "armys10.tgx"])
def test_decode_tgx(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "tgx" / filename
    img = gm1_rv.decode_tgx(file_path)
    assert isinstance(img, Image.Image)


@pytest.mark.parametrize("filename", ["armys1.tgx", "armys10.tgx"])
def test_decode_tgx_to_file(filename: str, tmp_path: pathlib.Path) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "tgx" / filename
    tmp_path = tmp_path / filename
    gm1_rv.decode_tgx_to_file(file_path, tmp_path)
    assert tmp_path.with_suffix(".png").exists()
