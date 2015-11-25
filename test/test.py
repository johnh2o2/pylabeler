# Test script that demonstrates the capabilities
# of the pylabeler library

from pylabeler.labeler import Labeler
import matplotlib.pyplot as plt

# Locations of images
image_folder = 'img'
image_filename = lambda ID : "%s/%s.jpg"%(image_folder, ID)

# Where to load/save the labels for each image
label_file = 'labels.txt'

# Allows for keyboard shortcuts (not required)
key_mapping = { '1' : 'Human', '2' : 'Lizard' }

# List of all ID's
ids = [ '001', '002', '003', '004', '005', '006' ]

# The image file(s) to show for each ID; must be a dict of lists since 
# more than one image can be used for the same ID
image_files = { ID : [ image_filename(ID) ] for ID in ids }

# Starts labeler
labeler = Labeler(image_files, label_file, sorted(key_mapping.values()), key_mapping)
labeler.connect()
plt.show(block=True)

