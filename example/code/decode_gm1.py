"""Example usage for gm1 files."""

from gm1_resource_viewer import GM1_Reader

gm = GM1_Reader("PATH_TO_FILE.gm1")
# decode .gm1 file, throw error if unsuccessful
assert gm.decode_gm1_file()
# show gm1 content as a big image
gm.show_image()
# write gm1 big image to file
gm.to_file("path/to/bigimage.jpeg")
# write gm1 sub images to folder
gm.sub_images_to_file("folder/to/sub_images/")
