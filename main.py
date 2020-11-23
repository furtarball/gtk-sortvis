from gui import *

window = SortWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
window.generate_heights() # we need to call this *after* the widgets are drawn
Gtk.main()
