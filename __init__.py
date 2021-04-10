import PySimpleGUI as sg
import numpy, io, sane
from PIL import Image
from pathlib import Path
home = str(Path.home())
print("SANE version: ", sane.init())


"""Setup the UI"""
sg.theme('DarkAmber')
default_path=str(Path.home()) + '/MirScanner/latest_scan.png'
resolutionsMenu = sg.OptionMenu([75, 150, 300, 600, 1200, 2400], default_value = 600,key="resolution")

layout = [[sg.Text('Hello, World!', key="text", size=(10,1), auto_size_text=True)],
	  [sg.Text('Resolution:'), resolutionsMenu],
	  [sg.Text('Where:'), sg.InputText(default_path,key="path")],
	  [sg.Button('Scan', disabled=True)],
	  [sg.Graph((400,400),(0,0),(400,400), drag_submits = True,
    enable_events = True, key="graph")],
	[sg.Text("", size=(28,1), key='textt')]]
	  
window = sg.Window('MirScanner', layout, return_keyboard_events=True)
graph = window["graph"]

"""Variables and functions"""
noDevicesAvailable = True
isGraphEmpty = True
graphScale = 1
graph_coordinates = ((0,0),(400,400))

def scan(resolution=600,path=str(Path.home()) + "/MirScanner/latest_scan.png"):
	dev.resolution = int(resolution)
	print("Setting resolution to " + resolution)
	# dev.scan().save(path)
	# image = dev.scan()
	temp = io.BytesIO()
	image = dev.scan()
	image.save(temp, format="png")
	print("Scanned and saved to " + path)
	print(graph.draw_image(data=temp.getvalue(),location=(0,400)))
	isGraphEmpty = False
	return image

prev_pos = None
def on_click_graph(position):
	global prev_pos
	prev_pos = position
def on_hold_graph(position):
	global prev_pos
	global graph_coordinates
	if not (prev_pos is None):
		drag_vector = tuple(map(lambda i, j:i-j, position, prev_pos))
		#graph.move(drag_vector[0], drag_vector[1])
		gc = [list(graph_coordinates[0]),list(graph_coordinates[1])]
		gc[0][0] += drag_vector[0]
		gc[1][0] += drag_vector[0]
		gc[0][1] += drag_vector[1]
		gc[1][1] += drag_vector[1]
		graph_coordinates = (tuple(gc[0]),tuple(gc[1]))
		graph.change_coordinates(graph_coordinates[0], graph_coordinates[1])

	prev_pos = position
def on_unclick_graph():
	global prev_pos
	prev_pos = None

window.read(0)
graph.bind("<Enter>", '+enter')
graph.bind("<Leave>", '+leave')
window["text"].hide_row()
while True:
	devices = sane.get_devices()
	if (len(devices)!=0):
		dev = sane.open(devices[0][0])
		noDevicesAvailable = False
		window["text"].hide_row()
		window["Scan"].update(disabled=False)
		break
	else:
		window["text"].expand(True)
		window["text"].update(value=str('No scanner device available.'))
		window["text"].update(text_color="Red")
		window["text"].unhide_row()
		window['Scan'].update(disabled=True)
		print("no devices found")
		window.read(0)
wasJustClickingGraph = False
isMouseOnGraph = False
while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED:
		window.close()
		break
	if event == 'Scan':
		scan(values["resolution"], values["path"])
		isGraphEmpty = False
	if event == "graph":
		if wasJustClickingGraph:
			on_hold_graph(values["graph"])
		else:
			on_click_graph(values["graph"])
			wasJustClickingGraph = True

	elif wasJustClickingGraph:
		wasJustClickingGraph = False
		on_unclick_graph()
	if event == 'graph+enter':
		isMouseOnGraph = True
	elif event =='graph+leave':
		isMouseOnGraph = False
	if isMouseOnGraph:
		if event == 'MouseWheel:Down':
			print('scroll down')
		if event == 'MouseWheel:Up':
			print('scroll up')
	if len(event) == 1:
		window['textt'].update(value='%s - %s' % (event, ord(event)))
	if event is not (None or 'graph'):
		window['textt'].update(event)