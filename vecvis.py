import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Slider, Button, RadioButtons


#settings
fun = lambda x, y, z: (np.sin(y) - 0.2*x, np.sin(z) - 0.2*y, np.sin(x) - 0.2*z) # vector field; look out for undefined points bc it'll mess with the colors (ie. sqrt of abs(n) instead of n)

dt = 0.2 # time step

lim = 6 # limit for plot axes
dlim = lim # distance limit for repositioning particles
speedlim = 0.1 # minimum speed for particles to be repositioned

npart = 2500 # number of particles
partsize = 2 # size of particles

streak = 0.3 # length of streaks relative to speed
linewidth = partsize # width of the streaks
alpha = 0.2 # opacity of streaks

color = 'plasma'
reverse = False # reverse the color map lets get crazy
cmap = color if color in plt.colormaps() else ListedColormap([color]) ## color as colormap if you want a single color
cmap = plt.get_cmap(cmap).reversed() if reverse else cmap
facecolor = 'black' # background color
axiscolor = 'grey' # self explanatory
axisclear = False

zoom = 1# guess
screen_ratio = 16 / 9

## function defs

def f(p):
    x = p[:, 0]
    y = p[:, 1]
    z = p[:, 2]
    return np.column_stack(np.broadcast_arrays(*fun(x, y, z)))

def mag(p): return np.sqrt(p[:, 0]**2 + p[:, 1]**2 + p[:, 2]**2)

def segments(p, streak):
    tail = p - f(p) * streak
    return np.stack((tail, p), axis=1)

# particle position

part_position = np.random.normal(loc = 0, scale = lim/3, size = (npart, 3)) #lim/3 so we dont get automatically repositioned particles lol

# figure stuff

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})

ax.set_position([0, -(screen_ratio - 1) / 2, 1, screen_ratio])

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(-lim, lim)

## figure settings (cosmetic)

ax.set_facecolor(facecolor)
fig.patch.set_facecolor(facecolor)
ax.set_axis_off() # NO GRID LINES !!!
ax.set_box_aspect(None, zoom=zoom)

x_axis, = ax.plot([-lim, lim], [0, 0], [0, 0], color=axiscolor)
y_axis, = ax.plot([0, 0], [-lim, lim], [0, 0], color=axiscolor)
z_axis, = ax.plot([0, 0], [0, 0], [-lim, lim], color=axiscolor)
axis_lines = [x_axis, y_axis, z_axis]

# trails

start_speed = mag(f(part_position))
vmax = np.percentile(start_speed, 95) # max velocity for color scaling
vmin = np.percentile(start_speed, 0) # !^

lines = Line3DCollection(segments(part_position, streak), cmap=cmap, linewidth=linewidth, alpha=alpha)
lines.set_array(start_speed) # array for color mapping
lines.set_clim(vmin, vmax)
ax.add_collection3d(lines)

# first plot
scat = ax.scatter(part_position[:,0], part_position[:,1], part_position[:,2], s=partsize, c=start_speed, cmap=cmap, vmin=vmin, vmax=vmax)

# interactive stuff

x, w = 0.04, 0.12   
box  = fig.add_axes([x, 0.020, w, 0.015])
box2 = fig.add_axes([x, 0.045, w, 0.015])
box3 = fig.add_axes([x, 0.070, w, 0.015])
box4 = fig.add_axes([x, 0.095, w, 0.015])
box5 = fig.add_axes([x, 0.120, w, 0.015])
box6 = fig.add_axes([x, 0.150, w, 0.025])
box7 = fig.add_axes([x, 0.185, w, 0.025])
box9 = fig.add_axes([x, 0.220, w, 0.050])
box8 = fig.add_axes([x, 0.280, w, 0.200])
hide_box = fig.add_axes([0.005, 0.005, 0.025, 0.015])
for b in (box, box2, box3, box4, box5):
    b.set_axis_off()
    b.patch.set_alpha(0)
    
## sliders

dt_slider = Slider(box, 'dt', 0, 2, valinit=dt)
alpha_slider = Slider(box2, 'alpha', 0, 1, valinit=alpha)
partsize_slider = Slider(box3, 'partsize', 0, 5, valinit=partsize)
streak_slider = Slider(box4, 'streak', 0, 1, valinit=streak)
npart_slider = Slider(box5, 'npart', 1, 5000, valinit=npart, valstep=1)

## buttons

color_buttons = RadioButtons(box8, ('cool', 'spring', 'plasma', 'viridis','hsv', 'pink', 'white', 'red', 'blue', 'black'), active = 3)
bgcolor_buttons = RadioButtons(box9, ('white', 'black'), active = 1)

def change_bgcolor(event=None):
    global facecolor
    facecolor = bgcolor_buttons.value_selected
    style_widgets()

bgcolor_buttons.on_clicked(change_bgcolor)

def change_color(event=None):
    global color, cmap
    color = color_buttons.value_selected
    cmap = color if color in plt.colormaps() else ListedColormap([color])

color_buttons.on_clicked(change_color)

axisclear_button = Button(box7, 'axisclear', color='black' if axisclear else axiscolor)

def aclear(event=None):
    global axisclear
    axisclear = not axisclear

axisclear_button.on_clicked(aclear)

refreshButton = Button(box6, 'refresh')

def refresh(event=None):
    global scat, lines, part_position
    lines.remove()
    scat.remove()

    npart = npart_slider.val
    part_position = np.random.normal(loc = 0, scale = lim/3, size = (npart, 3))

    speed = mag(f(part_position))

    lines = Line3DCollection(segments(part_position, streak_slider.val), cmap=cmap, linewidth=partsize_slider.val, alpha=alpha_slider.val)
    lines.set_array(speed)
    lines.set_clim(vmin, vmax)
    ax.add_collection3d(lines)
    scat = ax.scatter(part_position[:,0], part_position[:,1], part_position[:,2], s=partsize_slider.val, c=speed, cmap=cmap, vmin=vmin, vmax=vmax)

refreshButton.on_clicked(refresh)

## hide button

hidden = False
hide_button = Button(hide_box, 'hide')
hide_button.label.set_fontsize(8)
control_boxes = [box, box2, box3, box4, box5, box6, box7, box8, box9]
control_widgets = [dt_slider, alpha_slider, partsize_slider, streak_slider, npart_slider, refreshButton, axisclear_button, color_buttons, bgcolor_buttons]

def toggle_hide(event=None):
    global hidden
    hidden = not hidden
    for b in control_boxes:
        b.set_visible(not hidden)
    hide_button.label.set_text('show' if hidden else 'hide')
    for wdg in control_widgets:
        wdg.active = not hidden

hide_button.on_clicked(toggle_hide)

## styling

def bw(boo): return 'white' if boo else 'black'

def style_widgets():
    test = facecolor == 'black'

    for slider in (dt_slider, alpha_slider, partsize_slider, streak_slider, npart_slider):
        slider._handle.set_visible(False)
        slider.track.set_facecolor(bw(not test))
        slider.poly.set_facecolor(bw(test))
        slider.label.set_color(bw(test))
        slider.valtext.set_color(bw(test))

    for radio in (color_buttons, bgcolor_buttons):
        radio.ax.set_facecolor('none')  # no white rectangle
        for spine in radio.ax.spines.values():
            spine.set_visible(False)  # no border
        radio.set_label_props({'color': [bw(test)] * len(radio.labels)})
        radio.set_radio_props({'edgecolor': bw(test)})  # circle outlines
        radio.activecolor = bw(test)  # color of the filled dot when you click one
        radio._buttons.set_facecolor(['none' if i != radio.index_selected else bw(test) for i in range(len(radio.labels))])

    for button in (axisclear_button, refreshButton, hide_button):
        button.color = 'none'  # no fill
        button.hovercolor = 'none'
        button.ax.set_facecolor('none')
        button.label.set_color(bw(test))
        for spine in button.ax.spines.values():
            spine.set_edgecolor(bw(test))  # border only

style_widgets()

## scroll 

def scroll(event):
    global zoom
    zoom *= 1.1 if(event.button == 'up') else (10/11)
    

fig.canvas.mpl_connect('scroll_event', scroll)

#animation stuff

def update(frame):
    global part_position
    dt = dt_slider.val
    alpha = alpha_slider.val
    partsize = partsize_slider.val
    streak = streak_slider.val

    scat.set_sizes([partsize])
    lines.set_alpha(alpha)
    lines.set_linewidth(partsize)

    part_position += f(part_position) * dt

    d = mag(part_position)
    speed = mag(f(part_position))
    repos = (d > dlim) | (speed < speedlim) # if ball is too far or too slow respawn

    part_position[repos] = np.random.normal(loc=0, scale=lim/3, size=(repos.sum(), 3))

    speed = mag(f(part_position)) # find updated speeds

    for line in axis_lines:
        line.set_visible(not axisclear)
    axisclear_button.label.set_text('show axis' if axisclear else 'axis clear')

    # update trails and particles and their colors
    scat.set_cmap(cmap)
    lines.set_cmap(cmap)
    lines.set_segments(segments(part_position, streak))
    lines.set_array(speed)
    
    ax.set_facecolor(facecolor)
    fig.patch.set_facecolor(facecolor)
    ax.set_box_aspect(None, zoom=zoom)
    
    scat._offsets3d = (part_position[:, 0], part_position[:, 1], part_position[:,2])
    scat.set_array(speed)

ani = FuncAnimation(
    fig,
    update,
    frames=100,
    interval=10,
)

plt.get_current_fig_manager().full_screen_toggle() # optional i turned this on for testing
plt.show()