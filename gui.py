import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
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
# 0. speed, 1. change count, 2. thread stopping event, 3. are you refrBtn?,
# 4. digit for bubble and countingsort single-digit mode (used for radixsort, 0 = off),
# 5. radix sort subroutine, 6. bar order (True = descending, False = random)
addl = [60, 0, threading.Event(), False, 0, countingsort, False]
sortingThread = threading.Thread()

class Application(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id="io.github.furtarball.gtk-sortvis")
		self.handlers = {
			"onStartClick": self.start_on_click,
			"onRefrClick": self.refr_on_click,
			"onAlgSwitch": self.algs_on_change,
			"onDraw": self.on_draw,
			"onToggle": self.on_setting_change,
			"onConfigure": self.on_configure
		}
		self.builder = Gtk.Builder.new_from_file("sortwindow.ui")
		
	def do_activate(self):
		self.window = self.builder.get_object("sortWindow")
		self.startBtn = self.builder.get_object("startBtn")
		self.refrBtn = self.builder.get_object("refrBtn")
		self.algsCombo = self.builder.get_object("algsCombo")
		self.barWidthSBtn = self.builder.get_object("barWidthSBtn")
		self.gapsToggle = self.builder.get_object("gapsToggle")
		self.fillToggle = self.builder.get_object("fillToggle")
		self.speedSBtn = self.builder.get_object("speedSBtn")
		self.barOrderToggle = self.builder.get_object("barOrderToggle")
		self.rsSubrtToggle = self.builder.get_object("rsSubrtToggle")
		self.mainDArea = self.builder.get_object("mainDArea")
		self.barCountLbl = self.builder.get_object("barCountLbl")
		self.changesMadeLbl = self.builder.get_object("changesMadeLbl")
		
		self.barWidthSBtn.set_range(1, 200)
		self.barWidthSBtn.set_value(9)
		self.barWidthSBtn.set_increments(1, -1)
		self.speedSBtn.set_range(10, 18000)
		self.speedSBtn.set_value(60)
		self.speedSBtn.set_increments(10, -10)
		
		self.window.set_application(self)
		self.window.show_all()
		self.generate_heights()
		self.rsSubrtToggle.hide()
		self.builder.connect_signals(self.handlers)
		
	def generate_heights(self):
		global listToSort
		listToSort = generate_list(self.mainDArea.get_allocation().height, round(self.mainDArea.get_allocation().width / (self.barWidthSBtn.get_value() + self.gapsToggle.get_active())), addl[6])
		self.barCountLbl.set_label("Bars on screen: " + str(len(listToSort)))
		self.prevSize = [self.mainDArea.get_allocation().width, self.mainDArea.get_allocation().height]
		self.mainDArea.queue_draw()
		
	def on_draw(self, widget, cairoContext):
		nf = (not self.fillToggle.get_active()) # to make that line shorter
		bw = self.barWidthSBtn.get_value()
		baseMargin = self.mainDArea.get_allocation().width / 2 - (len(listToSort) * (bw + self.gapsToggle.get_active())) / 2
		cairoContext.set_source_rgb(0.6, 0.6, 0.6)
		cairoContext.set_line_width(1)
		cairoContext.set_antialias(1) # this stops one pixel wide bars from looking blurry
		for i in range(len(listToSort)):
			# left margin, top margin, width, height
			cairoContext.rectangle(baseMargin + nf + (bw + self.gapsToggle.get_active()) * i, self.mainDArea.get_allocation().height - listToSort[i] + nf, bw - nf, listToSort[i] - nf) 
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
		addl[4] = 0
		addl[2].clear()
		global sortingThread
		sortingThread = threading.Thread(target = choice, args = arguments, daemon = True)
		sortingThread.start()
		self.window.add_tick_callback(self.on_tick, sortingThread)
		
	def refr_on_click(self, widget):
		addl[3] = True
		addl[2].set()
		addl[1] = 0
		self.generate_heights()
		self.mainDArea.queue_draw()

	def algs_on_change(self, widget):
		addl[3] = False
		addl[2].set()
		if widget == self.algsCombo:
			# hide/show special options
			if widget.get_active() == 3:
				self.rsSubrtToggle.show()
			else:
				self.rsSubrtToggle.hide()
		else:
			if widget.get_active():
				addl[5] = bubblesort
				self.rsSubrtToggle.set_label("Subroutine: BS")
			else:
				addl[5] = countingsort
				self.rsSubrtToggle.set_label("Subroutine: CS")

	def on_setting_change(self, widget):
		addl[0] = self.speedSBtn.get_value()
		self.mainDArea.queue_draw()
		if self.barOrderToggle.get_active():
			addl[6] = True
			self.barOrderToggle.set_label("Bars: descending")
		else:
			addl[6] = False
			self.barOrderToggle.set_label("Bars: shuffled")
		if self.barWidthSBtn.get_value() < 3:
			self.fillToggle.set_active(True)
			self.fillToggle.set_sensitive(False)
		else:
			self.fillToggle.set_sensitive(True)
		if (widget == self.barWidthSBtn or widget == self.gapsToggle or widget == self.barOrderToggle) and not sortingThread.is_alive():
			self.generate_heights()
	
	def on_configure(self, widget, event):
		wdiff = abs(self.mainDArea.get_allocation().width - self.prevSize[0])
		hdiff = abs(self.mainDArea.get_allocation().height - self.prevSize[1])
		margin = self.barWidthSBtn.get_value() + self.gapsToggle.get_active()
		if ((wdiff >= margin) or (hdiff >= margin)) and not sortingThread.is_alive():
			self.generate_heights()
