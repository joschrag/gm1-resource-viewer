import pathlib

import pytest

import gm1_resource_viewer as gm1_rv
from gm1_resource_viewer import GM1_Datatype


@pytest.mark.parametrize("filename", ["killing_pits.gm1", "pitch_ditches.gm1"])
def test_decode_tiles_image(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.TilesObject


@pytest.mark.parametrize("filename", ["interface_icons2.gm1", "icons_front_end.gm1"])
def test_decode_interface(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.Interface


@pytest.mark.parametrize("filename", ["body_wolf.gm1", "body_ghost.gm1"])
def test_decode_animation(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.Animations


@pytest.mark.parametrize("filename", ["tile_walls.gm1"])
def test_decode_no_compression(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.No_Compression


@pytest.mark.parametrize("filename", ["tile_rivers.gm1"])
def test_decode_no_compression1(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.No_Compression1


@pytest.mark.parametrize("filename", ["army_units.gm1", "body_gate.gm1"])
def test_decode_const_size(filename: str) -> None:
    file_path = pathlib.Path.cwd() / "tests" / "gm1" / filename
    gm = gm1_rv.GM1_Reader(file_path)
    assert gm.decode_gm1_file()
    assert gm.gm_header.data_type == GM1_Datatype.TGX_Const_Size
