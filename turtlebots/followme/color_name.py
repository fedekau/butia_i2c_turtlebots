
d = {
'black': (0, 0, 0),
'white': (255, 255, 255),
'red': (255,0,0),
'lime': (0,255,0),
'blue': (0,0,255),
'yellow': (255,255,0),
'cyan': (0,255,255),
'magenta': (255,0,255),
'silver': (192,192,192),
'gray': (128,128,128),
'maroon': (128,0,0),
'olive': (128,128,0),
'green': (0,128,0),
'purple': (128,0,128),
'teal': (0,128,128),
'navy': (0,0,128)
}


def get_color_name(color, dist):
    min_colors = {}
    for name, key in d.items():
        r_c, g_c, b_c = key
        rd = (r_c - color[0]) ** 2
        gd = (g_c - color[1]) ** 2
        bd = (b_c - color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    m = min(min_colors.keys())
    if m < dist:
        return min_colors[m]
    else:
        return -1

