import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk
from algorithms import *
import threading

listToSort = []
refrRate = [60] # these are lists as a workaround for python not having pointers
changesMade = [0]

class SortWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, default_width = 600, default_height = 400)
		self.headerbar = Gtk.HeaderBar(show_close_button = True, title = "GTK Sorting Visualiser")
		self.set_titlebar(self.headerbar)
		self.mainBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 3)		
		self.mainDArea = Gtk.DrawingArea()
		self.optionsGrid = Gtk.Grid()
		
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
		self.refrButton.set_tooltip_text("Reshuffle & redraw bars")
		
		self.barWidthSBtn = Gtk.SpinButton()
		self.barWidthSBtn.set_range(1, 100)
		self.barWidthSBtn.set_value(9)
		self.barWidthSBtn.connect("value-changed", self.width_on_change)
		self.barWidthSBtn.set_increments(1, -1)
		self.barWidthSBtn.set_tooltip_text("Bar width in pixels")
		
		self.speedSBtn = Gtk.SpinButton()
		self.speedSBtn.set_range(10, 12000)
		self.speedSBtn.set_value(refrRate[0])
		self.speedSBtn.connect("value-changed", self.speed_on_change)
		self.speedSBtn.set_increments(10, -10)
		self.speedSBtn.set_tooltip_text("Delay between every write to list ^ –1")
		
		self.algsStore = Gtk.ListStore(str)
		self.algsStore.append(["Bubblesort"])
		self.algsStore.append(["Quicksort"])
		self.algsStore.append(["Bogosort"])
		self.algsStore.append(["Insertion sort"])
		self.algsStore.append(["Counting sort"])
		self.algsStore.append(["Radix sort (counting sort subroutine)"])
		self.algsStore.append(["Radix sort (bubblesort subroutine)"])
		self.algsCombo = Gtk.ComboBox.new_with_model(self.algsStore)
		self.algsRenderer = Gtk.CellRendererText()
		self.algsCombo.pack_start(self.algsRenderer, True)
		self.algsCombo.add_attribute(self.algsRenderer, "text", 0)
		self.algsCombo.set_active(0)
		
		self.gapsToggle = Gtk.CheckButton.new_with_label("Gaps")
		self.gapsToggle.set_active(True)
		self.fillToggle = Gtk.CheckButton.new_with_label("Fill")
		self.fillToggle.set_active(True)
		
		self.headerbar.pack_start(self.startButton)
		self.headerbar.pack_start(self.refrButton)
		self.headerbar.pack_end(self.algsCombo)
		
		# attach(child, left [>= 0], top [>= 0], width, height)
		self.optionsGrid.attach(Gtk.Label("Bar width (px): "), 0, 0, 1, 1)
		self.optionsGrid.attach(self.barWidthSBtn, 1, 0, 1, 1)
		self.optionsGrid.attach(self.gapsToggle, 2, 0, 1, 1)
		self.optionsGrid.attach(self.fillToggle, 3, 0, 1, 1)
		self.optionsGrid.attach(Gtk.Label("Speed (Hz): "), 0, 1, 1, 1)
		self.optionsGrid.attach(self.speedSBtn, 1, 1, 1, 1)
		
		self.barsCountLbl = Gtk.Label()
		self.changesMadeLbl = Gtk.Label()
		
		self.mainBox.pack_start(self.optionsGrid, False, False, 0)
		self.mainBox.pack_start(self.mainDArea, True, True, 0)
		self.mainDArea.connect("draw", self.on_draw)
		self.mainBox.pack_end(self.barsCountLbl, False, True, 0)
		self.mainBox.pack_end(self.changesMadeLbl, False, True, 0)
		self.add(self.mainBox)

		self.algsSwitcher = {
			0: [bubblesort, (0,)],
			1: [quicksort, (0,)],
			2: [bogosort, ()],
			3: [insertionsort, ()],
			4: [countingsort, (0,)],
			5: [radixsort, (countingsort,)],
			6: [radixsort, (bubblesort,)]
		}
		
	def generate_heights(self):
		global listToSort
		listToSort = generate_list(self.mainDArea.get_allocation().height, round(self.mainDArea.get_allocation().width / (self.barWidthSBtn.get_value_as_int() + self.gapsToggle.get_active())))
		self.barsCountLbl.set_label("Bars on screen: " + str(len(listToSort)))
		
	def on_draw(self, widget, cairoContext):
		dontfill = (not self.fillToggle.get_active())
		cairoContext.set_source_rgb(0.6, 0.6, 0.6)
		cairoContext.set_line_width(1)
		cairoContext.set_antialias(1)
		for i in range(len(listToSort)):
			# left margin, top margin, width, height
			cairoContext.rectangle(dontfill + (self.barWidthSBtn.get_value_as_int() + self.gapsToggle.get_active()) * i, self.mainDArea.get_allocation().height - listToSort[i] + dontfill, self.barWidthSBtn.get_value_as_int() - dontfill, listToSort[i] - dontfill) 
		cairoContext.fill() if self.fillToggle.get_active() else cairoContext.stroke()
		self.changesMadeLbl.set_label("Changes made to list: " + str(changesMade[0]))

	def on_timeout(self, widget, frameClock, thread):
		self.mainDArea.queue_draw()
		return thread.is_alive()

	def start_on_click(self, widget):
		self.alg = self.algsSwitcher[self.algsCombo.get_active()]
		sortingThread = threading.Thread(target = self.alg[0], args = (listToSort, refrRate, changesMade) + (self.alg[1] if self.alg[0] != quicksort else self.alg[1] + (len(listToSort) - 1,)), daemon = True)
		sortingThread.start()
		self.add_tick_callback(self.on_timeout, sortingThread)
		
	def refr_on_click(self, widget):
		self.generate_heights()
		self.mainDArea.queue_draw()
		changesMade[0] = 0
		
	def speed_on_change(self, widget):
		refrRate[0] = self.speedSBtn.get_value_as_int()
		
	def width_on_change(self, widget):
		if widget.get_value_as_int() < 3:
			self.fillToggle.set_active(True)
