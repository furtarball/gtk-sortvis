from gui import *

window = SortWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
