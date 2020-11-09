import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk
from algorithms import *
import threading

listToSort = []
barWidth = 3
refrRate = 90

class SortWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, default_width = 600, default_height = 400)
		self.headerbar = Gtk.HeaderBar(show_close_button = True, title = "GTK Sorting Visualiser")
		self.set_titlebar(self.headerbar)
		
		self.mainDArea = Gtk.DrawingArea()
		self.add(self.mainDArea)
		self.mainDArea.connect("draw", self.on_draw)
		
		self.startButton = Gtk.Button()
		self.startIcon = Gio.ThemedIcon(name = "media-playback-start-symbolic")
		self.startIconImage = Gtk.Image.new_from_gicon(self.startIcon, 4)
		self.startButton.add(self.startIconImage)
		self.startButton.connect("clicked", self.start_on_click)
		self.startButton.set_tooltip_text("Start sorting")
		
		self.refrButton = Gtk.Button()
		self.refrIcon = Gio.ThemedIcon(name = "view-refresh-symbolic")
		self.refrIconImage = Gtk.Image.new_from_gicon(self.refrIcon, 4)
		self.refrButton.add(self.refrIconImage)
		self.refrButton.connect("clicked", self.refr_on_click)
		self.refrButton.set_tooltip_text("Reshuffle bars")
		
		self.barWidthSBtn = Gtk.SpinButton()
		self.barWidthSBtn.set_range(1, 10)
		self.barWidthSBtn.set_value(3)
		self.barWidthSBtn.set_increments(1, -1)
		self.barWidthSBtn.set_tooltip_text("Bar width in pixels")
		
		self.headerbar.pack_start(self.startButton)
		self.headerbar.pack_start(self.refrButton)
		self.headerbar.pack_end(self.barWidthSBtn)
		
		self.generate_heights()
	
	def generate_heights(self):
		global listToSort
		global barWidth
		barWidth = self.barWidthSBtn.get_value_as_int()
		listToSort = generate_list(self.get_size()[1], round(self.get_size()[0] / (barWidth + 1)))
	
	def on_draw(self, widget, cairoContext):
		cairoContext.set_source_rgb(0.6, 0.6, 0.6)
		for i in range(len(listToSort)):
			# left margin, top margin, width, height
			cairoContext.rectangle((barWidth + 1) * i, self.get_size()[1] - listToSort[i], barWidth, listToSort[i]) 
		cairoContext.fill()

	def on_timeout(self, *data):
		self.mainDArea.queue_draw()
		return True

	def start_on_click(self, widget):
		sortingThread = threading.Thread(target=quicksort, args=(listToSort, 0, len(listToSort) - 1, refrRate), daemon = True)
		#sortingThread = threading.Thread(target=bubblesort, args=(listToSort, refrRate), daemon = True)
		#sortingThread = threading.Thread(target=bogosort, args=(listToSort, refrRate), daemon = True)
		sortingThread.start()
		timeoutId = GLib.timeout_add(1 / refrRate * 1000, self.on_timeout, None)
		
	def refr_on_click(self, widget):
		self.generate_heights()
		self.mainDArea.queue_draw()
