import triangulate

# xlp = 549
# ylp = 380
# xrp = 394
# yrp = 392

camera_distance = 0.1
actual_distance = 1

pixel_width = 640
pixel_height = 480
angle_width = 62.2

angle_height = None

pixel_left = [(252, 286), (381, 279), (140, 291)]
pixel_right = [(385, 266), (509, 256), (274, 264)]

angler = triangulate.Frame_Angles(pixel_width,pixel_height,angle_width,angle_height)
angler.build_frame()

def distance_calculation(xlp, ylp, xrp, yrp):
    xlangle,ylangle = angler.angles_from_center(xlp,ylp,top_left=True,degrees=True)
    xrangle,yrangle = angler.angles_from_center(xrp,yrp,top_left=True,degrees=True)
    X,Y,Z,D = angler.location(camera_distance,(xlangle,ylangle),(xrangle,yrangle),center=True,degrees=True)
    return D


# triangulate
for i in range(len(pixel_left)):
    D = distance_calculation(pixel_left[i][0],pixel_left[i][1], pixel_right[i][0], pixel_right[i][1])
    print("{}".format(D))
# print("{}, {}".format(D,Y))
# pdiff = (D-actual_distance)/actual_distance*100
# print("Error: {:.2f}%".format(pdiff))