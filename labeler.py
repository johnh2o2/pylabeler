import matplotlib.pyplot as plt 
from matplotlib.text import Text
from matplotlib.font_manager import FontProperties
import matplotlib.image as mpimg
import numpy as np
import os

CLICK_BBOX = dict(
	boxstyle='round,pad=0.8', fc='cyan', alpha=1.0
	)
DEFAULT_BBOX = dict(
	boxstyle='round,pad=0.8', fc='none'
	)
CHOICE_BBOX = dict(
	boxstyle='round,pad=0.8', fc='blue', alpha=0.3
	)
HOVER_BBOX = dict(
	boxstyle='round,pad=0.8', fc='green', alpha=0.3
	)
BUTTON_FONT = FontProperties(family='Bitstream Vera Sans', size=14)
MENU_TITLE_FONT = FontProperties(family='Bitstream Vera Sans', size=14, weight='bold')

class Button:
	def __init__(self, **kwargs):
		self.text = Text(**kwargs)
		self.default_bbox = DEFAULT_BBOX
		self.hovering = False
		self.chosen = False

	def place(self, axis, x=0, y=0):
		self.text.set_position((x,y))
		axis.add_artist(self.text)
		return self
		
	def unset_as_choice(self):
		self.default_bbox = DEFAULT_BBOX
		self.chosen = False
		self.text.set_bbox(self.default_bbox)
		self.text.figure.canvas.draw()

	def set_as_choice(self):
		self.default_bbox = CHOICE_BBOX
		self.chosen = True
		self.text.set_bbox(self.default_bbox)
		self.text.figure.canvas.draw()

	def set_hover(self):
		self.text.set_bbox(HOVER_BBOX)
		self.hovering = True
		self.text.figure.canvas.draw()
		

	def set_normal(self):
		self.text.set_bbox(self.default_bbox)
		self.hovering = False
		self.text.figure.canvas.draw()

def clear_axis(axis):
	for stype in axis.spines:
		axis.spines[stype].set_visible(False)

	axis.xaxis.set_major_locator(plt.NullLocator())
	axis.xaxis.set_minor_locator(plt.NullLocator())
	axis.yaxis.set_major_locator(plt.NullLocator())
	axis.yaxis.set_minor_locator(plt.NullLocator())

def simple_callback(func):
	def new_func(*args, **kwargs):
		result = func(*args, **kwargs)
		slf = args[0]
		callback_func = slf.callback_func
		if not callback_func is None:
			callback_func()
		return result
	return new_func


class Menu(object):
	def __init__(self, choices, axis, selected_choice, menu_title = None, callback_func = None, keyboard_shortcuts=None, xtopleft=0.1, ytopleft=0.75, height=None):
		nchoices = len(choices)
		if height is None: height = (ytopleft - 0.2) / nchoices

		self.axis = axis
		self.callback_func = callback_func
		self.menu_title=menu_title
		self.buttons = { choice : Button(text=choice, fontproperties=BUTTON_FONT).place(axis, xtopleft, ytopleft - i*height)  for i, choice in enumerate(choices) }
		if not self.menu_title is None: self.axis.text(xtopleft, 0.9, self.menu_title, fontproperties=MENU_TITLE_FONT)
		if not selected_choice is None: self.buttons[selected_choice].set_as_choice()
		self.keyboard_shortcuts = keyboard_shortcuts
		self.choice = selected_choice

	def clean_up_axis(self):
		clear_axis(self.axis)

	@simple_callback
	def unselect_all(self):
		for choice, button in self.buttons.iteritems():
			if button.chosen: 
				button.unset_as_choice()

	@simple_callback
	def select(self, choice):
		if self.buttons[choice].chosen:
			self.choice = None
			self.buttons[choice].unset_as_choice()
			return

		self.choice = choice
		self.buttons[choice].set_as_choice()
		for choice, button in self.buttons.iteritems():
			if not choice == self.choice and button.chosen: 
				button.unset_as_choice()

	def on_mouse_over(self, mouse_event):
		# Hover / unhover
		for choice, button in self.buttons.iteritems():
			hit, props = button.text.contains(mouse_event)
			if hit: 
				button.set_hover()
			elif button.hovering: 
				button.set_normal()

	def on_click(self, click_event):
		# Was the click inbounds for any of the buttons?
		for choice, button in self.buttons.iteritems():
			hit, props = button.text.contains(click_event)
			if hit: self.select(choice)
		
	def on_key_press(self, keyboard_event):
		if self.keyboard_shortcuts is None: 
			return
		key = keyboard_event.key
		if key in self.keyboard_shortcuts:
			choice = self.keyboard_shortcuts[key]
			self.select(choice)

	def connect(self):
		self.cidpress = self.axis.figure.canvas.mpl_connect('button_press_event', self.on_click)
		self.cidrelease = self.axis.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
		self.cidmotion = self.axis.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_over)



class MultipleMenu(Menu):
	def __init__(self, choices, axis, selected_choices, **kwargs):
		super( MultipleMenu, self).__init__(choices, axis, None, **kwargs)
		self.selected_choices = selected_choices
		for choice in self.selected_choices: self.select(choice, update_selected=False)
		self.update_selected_choices()

	@simple_callback
	def update_selected_choices(self):
		for choice, button in self.buttons.iteritems():
			if button.chosen and not choice in self.selected_choices:
				self.selected_choices.append(choice)
			if not button.chosen and choice in self.selected_choices:
				self.selected_choices.remove(choice)

	def select(self, choice, update_selected=True):
		if not self.buttons[choice].chosen: 
			self.buttons[choice].set_as_choice()
		else:
			self.buttons[choice].unset_as_choice()
		if update_selected: self.update_selected_choices()
	
	def select_all(self):
		for choice in self.choices: 
			select(choice)

	def update_button_text(self, new_text):
		for choice, label in new_text.iteritems():
			self.buttons[choice].text.set_text(label)


def load_labels(label_file):
	if not os.path.exists(label_file): 
		return None
	labels = {}
	f = open(label_file, 'r')
	for line in f:
		ID, label = line.split()
		labels[ID] = label
	return labels

def write_labels(labels, label_file):
	f = open(label_file, 'w')	
	for hatid, label in labels.iteritems():
		f.write('%s\t%s\n'%(hatid, label))
	f.close()



class Labeler(Menu):
	def __init__(self, image_files, label_file, classes, keyboard_shortcuts, buffer_number=100):
		# Initialize...
		self.all_ids = sorted(image_files.keys())
		self.ids = [ ID for ID in self.all_ids ]
		self.index = 0
		self.label_file = label_file
		self.keyboard_shortcuts = keyboard_shortcuts
		self.classes = classes
		self.buffer_number = min([buffer_number, len(self.ids)])
		self.images = None
		self.image_files = image_files

		self.available_labels = [ c for c in classes ]

		self.available_labels.append('Unlabeled')
		self.labels_to_display = [ l for l in self.available_labels ]

		# Load label file (if one exists)
		if label_file is None or not os.path.exists(label_file):
			self.labels = {}
		else:
			self.labels = load_labels(label_file)
			if self.labels is None: self.labels = {}

		# Load a (sub)set of images to memory
		self.rebuffer_images()
		nimages = len(image_files[self.ids[0]])

		# Initialize figure
		self.fig, self.axes = plt.subplots(1, nimages + 1, figsize=(15, 7))
		self.fig.subplots_adjust(hspace=0.01, bottom=0, right=1, top=1, left=0)
		self.menu_axis = self.axes[-1]
		for ax in self.axes: clear_axis(ax)

		super( Labeler, self).__init__( self.classes, self.menu_axis, None, keyboard_shortcuts=self.keyboard_shortcuts, menu_title='Classes')

		# Options menu
		self.options_menu = None
		self.options_menu = MultipleMenu(self.available_labels, self.menu_axis, self.available_labels,callback_func=self.update_option_menu, xtopleft=0.6, menu_title='Show')

		print "pylabeler instance running..."
		print "-----------------------------"
		print " * Use the < (to go to previous ID)"
		print "       and > (to go to next ID)"
		print " * Results are automatically saved to %s upon exiting"%(label_file)
		self.display()

	def update_option_menu_button_text(self):
		counts = { l : len([ ID for ID in self.all_ids if ID in self.labels and self.labels[ID] == l ]) for l in self.available_labels }
		counts['Unlabeled'] = len([ ID for ID in self.all_ids if not ID in self.labels ])

		new_button_text = { l : "%s (%d)"%(l, c) for l, c in counts.iteritems() }
		self.options_menu.update_button_text(new_button_text)


	def update_option_menu(self):
		# Ignore the initial callback
		if self.options_menu is None: return

		# Add counts next to labels
		self.update_option_menu_button_text()
		
		if len(self.ids) == 0: current_id = None

		else: current_id = self.ids[self.index]

		l = 'Unlabeled'
		if current_id in self.labels: l = self.labels[current_id]

		# Update the labels to show
		self.labels_to_display = [ c for c in self.options_menu.selected_choices ]

		# Filter ID's
		self.ids = [ ID for ID in self.all_ids if (ID in self.labels and self.labels[ID] in self.labels_to_display) or (not ID in self.labels and 'Unlabeled' in self.labels_to_display) ]
		if not current_id in self.ids:
			self.index = 0
		else:
			self.index = self.ids.index(current_id)

		self.display(update_options=False)
	def select(self, choice):
		super( Labeler, self).select( choice )

		ID = self.ids[self.index]

		if self.choice is None and ID in self.labels: del self.labels[ID]
		else: self.labels[ID] = self.choice

		

	def display(self, update_options=True):
		if update_options: self.update_option_menu()
		

		if len(self.ids) == 0: return 
	
		ID = self.ids[self.index]

		# Unselect all buttons
		self.unselect_all()

		# Rebuffer if image isnt loaded
		if not ID in self.images: self.rebuffer_images()

		# Plot it.
		for i, img in enumerate(self.images[ID]):
			ax = self.axes[i]
			ax.cla()
			clear_axis(ax)
			ax.imshow(img)

		# Select the label (if there is one)
		if ID in self.labels:
			id_label = self.labels[ID]
			if not id_label in self.classes:
				print "WARNING: ", id_label, " is not one of ", self.classes
			super( Labeler, self).select(id_label)


		# Set the figure title
		self.fig.suptitle(ID)

		self.fig.canvas.draw()

	def rebuffer_images(self):
		# Loads images surrounding the current 
		istart = self.index - self.buffer_number/2
		new_ids = [ self.ids[(i + istart)%len(self.ids)] for i in range(self.buffer_number) ]
		del self.images
		self.images = { ID : [ mpimg.imread(fname) for fname in self.image_files[ID] ] for ID in new_ids }

	def on_exit(self, event):
		print "Writing labels..."
		write_labels(self.labels, self.label_file)
		print "Done."

	def goto(self, index):
		if index > 0 and index < len(self.ids):
			self.index = index
			self.display()

	def next(self):
		self.index = (self.index + 1)%len(self.ids)
		self.display()

	def previous(self):
		self.index = (self.index - 1)%len(self.ids)
		self.display()

	def on_key_press(self, event):
		key = event.key 
		if key == '.': self.next()
		elif key == ',': self.previous()

		super(Labeler, self).on_key_press(event)

	def connect(self):

		self.cidpress = self.fig.canvas.mpl_connect('close_event',self.on_exit)
		super(Labeler, self).connect()
		self.options_menu.connect()




