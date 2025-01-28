"""Example usage for tgx files."""

from gm1_resource_viewer import decode_tgx, decode_tgx_to_file

# decode and show tgx file
img = decode_tgx("path/to/file.tgx")
img.show()
# decode tgx file and save to file
decode_tgx_to_file("path/to/file.tgx", "path/to/out.png")
