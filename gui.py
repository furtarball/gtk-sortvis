import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk
from algorithms import *
import threading
import time

algsSwitcher = {
	0: bubblesort,
	1: countingsort,
	2: insertionsort,
	3: radixsort,
	4: quicksort,
	5: bogosort
}

listToSort = []
# 0. speed, 1. change count, 2. thread stopping event, 3. quicksort fast mode,
# 4. digit for bubble and countingsort single-digit mode (used for radixsort, 0 = off),
# 5. radix sort subroutine
addl = [60, 0, threading.Event(), False, 0, countingsort]
sortingThread = threading.Thread()
# random: False, descending: True
barsOrder = False

class Application(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id="io.github.furtarball.gtk-sortvis")
		handlers = {
			"onStartClick": self.start_on_click,
			"onRefrClick": self.refr_on_click,
			"onAlgSwitch": self.algs_on_change,
			"onBarsOrderToggle": self.bars_on_toggle,
			"onDraw": self.on_draw,
			"onToggle": self.on_setting_change
		}
		self.builder = Gtk.Builder.new_from_file("sortwindow.ui")
		self.builder.connect_signals(handlers)
		
	def do_activate(self):
		self.window = self.builder.get_object("sortWindow")
		self.startBtn = self.builder.get_object("startBtn")
		self.refrBtn = self.builder.get_object("refrBtn")
		self.algsCombo = self.builder.get_object("algsCombo")
		self.barWidthSBtn = self.builder.get_object("barWidthSBtn")
		self.gapsToggle = self.builder.get_object("gapsToggle")
		self.fillToggle = self.builder.get_object("fillToggle")
		self.speedSBtn = self.builder.get_object("speedSBtn")
		self.barsOrderToggle = self.builder.get_object("barsOrderToggle")
		self.qsFastToggle = self.builder.get_object("qsFastToggle")
		self.rsSubrtToggle = self.builder.get_object("rsSubrtToggle")
		self.mainDArea = self.builder.get_object("mainDArea")
		self.barsCountLbl = self.builder.get_object("barsCountLbl")
		self.changesMadeLbl = self.builder.get_object("changesMadeLbl")
		
		self.barWidthSBtn.set_range(1, 100)
		self.barWidthSBtn.set_value(9)
		self.barWidthSBtn.set_increments(1, -1)
		self.speedSBtn.set_range(10, 12000)
		self.speedSBtn.set_value(60)
		self.speedSBtn.set_increments(10, -10)
		
		self.window.set_application(self)
		self.window.show_all()
		self.generate_heights()
		self.qsFastToggle.hide()
		self.rsSubrtToggle.hide()
		
	def generate_heights(self):
		global listToSort
		listToSort = generate_list(self.mainDArea.get_allocation().height, round(self.mainDArea.get_allocation().width / (self.barWidthSBtn.get_value_as_int() + self.gapsToggle.get_active())), barsOrder)
		self.barsCountLbl.set_label("Bars on screen: " + str(len(listToSort)))
		self.mainDArea.queue_draw()
		
	def on_draw(self, widget, cairoContext):
		dontfill = (not self.fillToggle.get_active())
		cairoContext.set_source_rgb(0.6, 0.6, 0.6)
		cairoContext.set_line_width(1)
		cairoContext.set_antialias(1)
		for i in range(len(listToSort)):
			# left margin, top margin, width, height
			cairoContext.rectangle(dontfill + (self.barWidthSBtn.get_value_as_int() + self.gapsToggle.get_active()) * i, self.mainDArea.get_allocation().height - listToSort[i] + dontfill, self.barWidthSBtn.get_value_as_int() - dontfill, listToSort[i] - dontfill) 
		cairoContext.fill() if self.fillToggle.get_active() else cairoContext.stroke()
		self.changesMadeLbl.set_label("Changes made to list: " + str(addl[1]))

	def on_tick(self, widget, frameClock, thread):
		self.mainDArea.queue_draw()
		return thread.is_alive()

	def start_on_click(self, widget):
		choice = algsSwitcher[self.algsCombo.get_active()]
		arguments = (listToSort, addl)
		if choice == quicksort:
			arguments += (0, len(listToSort) - 1)
		sortingThread = threading.Thread(target = choice, args = arguments, daemon = True)
		addl[4] = 0
		addl[2].clear()
		sortingThread.start()
		self.window.add_tick_callback(self.on_tick, sortingThread)
		
	def refr_on_click(self, widget):
		addl[2].set()
		addl[1] = 0
		self.generate_heights()
		self.mainDArea.queue_draw()

	def algs_on_change(self, widget):
		addl[2].set()
		if widget.get_name() == "GtkComboBoxText":
			if widget.get_active() == 4:
				self.rsSubrtToggle.hide()
				self.qsFastToggle.show()
			elif widget.get_active() == 3:
				self.qsFastToggle.hide()
				self.rsSubrtToggle.show()
			else:
				self.qsFastToggle.hide()
				self.rsSubrtToggle.hide()
		else:
			if widget.get_active():
				addl[5] = bubblesort
				self.rsSubrtToggle.set_label("Subroutine: BS")
			else:
				addl[5] = countingsort
				self.rsSubrtToggle.set_label("Subroutine: CS")
		
	def bars_on_toggle(self, widget):
		global barsOrder
		if widget.get_active():
			barsOrder = True
			widget.set_label("Bars: descending")
		else:
			barsOrder = False
			widget.set_label("Bars: shuffled")
		print(sortingThread)
		if addl[2].is_set():
			self.generate_heights()
			
	def on_setting_change(self, widget):
		addl[0] = self.speedSBtn.get_value_as_int()
		addl[3] = self.qsFastToggle.get_active()
		if self.barWidthSBtn.get_value_as_int() < 3:
			self.fillToggle.set_active(True)
			self.fillToggle.set_sensitive(False)
		else:
			self.fillToggle.set_sensitive(True)
		self.mainDArea.queue_draw()
