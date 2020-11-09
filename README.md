# gtk-sortvis
A GTK sorting visualiser

![Screenshot](screenshot.png)

## Dependencies
* Python 3
* GTK3
* gobject-introspection
### Linux
All of the above should be already built into most Linux distros. If not, PyGObject is often packaged as `python3-gobject`, `python3-gi`, `pygobject` or as a dependency for `gobject-introspection`.
### FreeBSD
`pkg install python gtk3 gobject-introspection`
### OpenBSD
`pkg_add python py-gobject3 gtk+3`

## Running
`python main.py`
or
`python3 main.py`

## Note
Right now, you have to uncomment line 65, 66 or 67 in gui.py in order to change the visualised algorithm.
