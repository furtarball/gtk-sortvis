import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from algorithms import *
import threading

algsSwitcher = {
	0: bubblesort,
	1: countingsort,
	2: insertionsort,
	3: radixsort,
	4: quicksort,
	5: bogosort
}

listToSort = []
# 0. speed, 1. change count, 2. thread stopping event, 3. who's setting the event?
# (True = refrBtn, False = algsCombo), 4. digit for bubble and countingsort single-digit
# mode (used for radixsort, 0 = off) 5. radix sort subroutine, 6. bar order
# (True = descending, False = random)
addl = [60, 0, threading.Event(), False, 0, countingsort, False]
sortingThread = threading.Thread()

class Application(Adw.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id="io.github.furtarball.gtk-sortvis")
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

		self.startBtn.connect("clicked", self.start_on_click)
		self.refrBtn.connect("clicked", self.refr_on_click)
		self.algsCombo.connect("changed", self.algs_on_change)
		self.rsSubrtToggle.connect("toggled", self.rs_subrt_on_toggle)
		
		self.barWidthSBtn.connect("value-changed", self.bar_width_on_change)
		self.speedSBtn.connect("value-changed", self.speed_on_change)
		self.gapsToggle.connect("toggled", self.gaps_on_toggle)
		self.fillToggle.connect("toggled", self.fill_on_toggle)
		self.barOrderToggle.connect("toggled", self.order_on_toggle)
		
		self.mainDArea.connect("resize", self.on_configure)
		self.mainDArea.set_draw_func(self.on_draw)
		self.algsCombo.set_active(0)
		self.barWidthSBtn.set_range(1, 200)
		self.barWidthSBtn.set_value(9)
		self.barWidthSBtn.set_increments(1, -1)
		self.speedSBtn.set_range(10, 18000)
		self.speedSBtn.set_value(60)
		self.speedSBtn.set_increments(10, -10)
		
		self.window.set_application(self)
		self.window.present()
		
	def generate_heights(self):
		global listToSort
		listToSort = generate_list(self.mainDArea.get_allocation().height, round(self.mainDArea.get_allocation().width / (self.barWidthSBtn.get_value() + self.gapsToggle.get_active())), addl[6])
		self.barCountLbl.set_label("Bars on screen: " + str(len(listToSort)))
		self.prevSize = [self.mainDArea.get_allocation().width, self.mainDArea.get_allocation().height]
		self.mainDArea.queue_draw()
		
	def on_configure(self, widget, w, h):
		wdiff = abs(w - self.prevSize[0])
		hdiff = abs(h - self.prevSize[1])
		margin = self.barWidthSBtn.get_value() + self.gapsToggle.get_active()
		if ((wdiff >= margin) or (hdiff >= margin)) and not sortingThread.is_alive():
			self.generate_heights()
			
	def on_draw(self, widget, cairoContext, w, h):
		nf = (not self.fillToggle.get_active())
		bw = self.barWidthSBtn.get_value()
		baseMargin = w / 2 - (len(listToSort) * (bw + self.gapsToggle.get_active())) / 2
		cairoContext.set_source_rgb(0.6, 0.6, 0.6)
		cairoContext.set_line_width(1)
		cairoContext.set_antialias(1) # this stops one pixel wide bars from looking blurry
		for i in range(len(listToSort)):
			# left margin, top margin, width, height
			cairoContext.rectangle(baseMargin + nf + (bw + self.gapsToggle.get_active()) * i, h - listToSort[i] + nf, bw - nf, listToSort[i] - nf) 
			cairoContext.fill() if self.fillToggle.get_active() else cairoContext.stroke()

	def on_tick(self, widget, frameClock, thread):
		self.mainDArea.queue_draw()
		self.changesMadeLbl.set_label("Changes made to list: " + str(addl[1]))
		return thread.is_alive()

	def start_on_click(self, widget):
		choice = algsSwitcher[self.algsCombo.get_active()]
		arguments = (listToSort, addl)
		if choice == quicksort:
			arguments += (0, len(listToSort) - 1)
			global sortingThread
		if not sortingThread.is_alive():
			addl[4] = 0
			addl[2].clear()
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
			if widget.get_active() == 3:
				self.rsSubrtToggle.show()
			else:
				self.rsSubrtToggle.hide()

	def rs_subrt_on_toggle(self, widget):
		addl[3] = False
		addl[2].set()
		if widget.get_active():
			addl[5] = bubblesort
			self.rsSubrtToggle.set_label("Subroutine: BS")
		else:
			addl[5] = countingsort
			self.rsSubrtToggle.set_label("Subroutine: CS")

	def bar_width_on_change(self, widget):
		if self.barWidthSBtn.get_value() < 3:
			self.fillToggle.set_active(True)
			self.fillToggle.set_sensitive(False)
		else:
			self.fillToggle.set_sensitive(True)
		if not sortingThread.is_alive():
			self.generate_heights()
		self.mainDArea.queue_draw()

	def speed_on_change(self, widget):
		addl[0] = self.speedSBtn.get_value()
		self.mainDArea.queue_draw()

	def gaps_on_toggle(self, widget):
		if not sortingThread.is_alive():
			self.generate_heights()
		self.mainDArea.queue_draw()

	def fill_on_toggle(self, widget):
		self.mainDArea.queue_draw()

	def order_on_toggle(self, widget):
		if self.barOrderToggle.get_active():
			addl[6] = True
			self.barOrderToggle.set_label("Bars: descending")
		else:
			addl[6] = False
			self.barOrderToggle.set_label("Bars: shuffled")
		if not sortingThread.is_alive():
			self.generate_heights()
		self.mainDArea.queue_draw()
