import vtk
import urllib2
import json
import math
import random
from operator import itemgetter

class vtkTimerCallback():
    def __init__(self):
        self.count = 0
        self.actors = []
        self.transformed_pts = []
        self.limit = 0
        self.offset = 0
        self.years = []

    def execute(self, obj, event):   
        if (self.count < self.limit): 
            for i in range(self.offset, self.actors.GetNumberOfItems()):
                actor = self.actors.GetItemAsObject(i)
	        #print "Count {0}".format(self.count)
	        pos = [self.transformed_pts[i - self.offset][len(self.transformed_pts[i-self.offset]) - (self.count + 1)][0],self.transformed_pts[i - self.offset][len(self.transformed_pts[i-self.offset]) - (self.count + 1)][1], 0]
                actor.SetPosition(pos)
	        #print "Setting position of actor {0} in {1}".format(i, pos)
	    if((self.count % 10) == 0 and self.count > 0):
		self.txt_actors[0].SetInput(self.years[len(self.years) - 2 - (self.count/10)])
                print self.count
            iren = obj
            iren.GetRenderWindow().Render()
        else:
	    self.txt_actors[0].SetInput(self.years[0]) 
            iren = obj
            iren.GetRenderWindow().Render()
        if (self.count < self.limit + 40):
            self.count = self.count + 1
        else:
            self.count = 0 
	    self.txt_actors[0].SetInput(self.years[len(self.years) - 2]) 
            iren = obj
            iren.GetRenderWindow().Render()

def create_grid():
    x_ratio = .24
    x_a = -1.2
    y_ratio = .18
    y_a = -.9
    x_as = []
    x_bs = []
    y_as = []
    y_bs = []
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")
    for j in range(40):	
        colors.InsertNextTupleValue([0, 0, 0])
    for i in range(0, 10):
        x_as.append([x_a + x_ratio, -.89, 0])
        x_bs.append([x_a + x_ratio, -.91, 0])
        y_as.append([-1.19, y_a + y_ratio, 0])
        y_bs.append([-1.21, y_a + y_ratio, 0])
        y_a += y_ratio
        x_a += x_ratio
    g_points = vtk.vtkPoints()

    for i in range(0, 10):
        g_points.InsertNextPoint(x_as[i])
        g_points.InsertNextPoint(x_bs[i])
        g_points.InsertNextPoint(y_as[i])
        g_points.InsertNextPoint(y_bs[i])

    g_lines = []
    n_pts = g_points.GetNumberOfPoints()

    axis = vtk.vtkCellArray()
    
    for i in range(0, 40, 2):
        line = vtk.vtkLine()

        if(i < 20):
	    line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i+1)
        else:
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i+1)
        axis.InsertNextCell(line) 
    #create Polydata to store everything
    axisPolyData = vtk.vtkPolyData()
    #add the points
    axisPolyData.SetPoints(g_points)
    #add the lines
    axisPolyData.SetLines(axis)
    axisPolyData.GetCellData().SetScalars(colors)
    #color them
    #axisPolyData.GetCellData().SetScalars(colors)
    return axisPolyData
    

def create_axis():
    origin = [-1.2, -.9, 0]
    x_axis = [1.2, -.9, 0]
    y_axis = [-1.2, .9, 0]
    #origin = [0, 0, 0]
    #x_axis = [2.4, 0, 0]
    #y_axis = [0, 1.8, 0]

    #create vtkPoints to store the points
    points = vtk.vtkPoints()
    points.InsertNextPoint(origin)
    points.InsertNextPoint(x_axis)
    points.InsertNextPoint(y_axis)
    #set colors of lines
    red = [255, 0, 0]
    green = [0, 255, 0]

    #colors array
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    #Add colors to the color's array
    colors.InsertNextTupleValue(red)    
    colors.InsertNextTupleValue(green)    

    #Create lines
    x_line = vtk.vtkLine()
    x_line.GetPointIds().SetId(0,0)
    x_line.GetPointIds().SetId(1,1)
    y_line = vtk.vtkLine()
    y_line.GetPointIds().SetId(0,0)
    y_line.GetPointIds().SetId(1,2)

    #cellArray to store lines
    axis = vtk.vtkCellArray()
    axis.InsertNextCell(x_line)
    axis.InsertNextCell(y_line)
    
    #create Polydata to store everything
    axisPolyData = vtk.vtkPolyData()
    #add the points
    axisPolyData.SetPoints(points)
    #add the lines
    axisPolyData.SetLines(axis)
    #color them
    axisPolyData.GetCellData().SetScalars(colors)
    return axisPolyData


def get_data_axis(indicator, country):
    url_res = urllib2.urlopen("http://api.worldbank.org/countries/" + country + "/indicators/" + indicator + "?format=json")
    json_res = url_res.read()
    res = json.loads(json_res)
    rec_total = res[0]["total"]
    rec_ppage = int(res[0]["per_page"])
    wb_data = res[1]
    if (rec_total > rec_ppage):
        count = rec_ppage
        page = 2
        while rec_total > count:
            url_res = urllib2.urlopen("http://api.worldbank.org/countries/" + country + "/indicators/" + indicator + "?format=json&page=" + str(page))
            json_res = url_res.read()
            res = json.loads(json_res)
            wb_data = res[1] + wb_data
            count += len(res[1])
            page += 1
    return wb_data

def get_data(years, indicator_x = "NY.GDP.PCAP.CD", indicator_y = "SP.DYN.LE00.IN", indicator_z = "SP.POP.TOTL", country = "us"):
    data_x = get_data_axis(indicator_x, country)
    data_y = get_data_axis(indicator_y, country)
    data_z = get_data_axis(indicator_z, country)
    #Now we have the data in a dict object, we need to transform this into an array of (x, y, z) tuples
    ret = []
    ret_extra = []
    for i in range(len(data_x)):
        if data_x[i]["value"] is not None and data_y[i]["value"] is not None:
            ret.append((float(data_x[i]["value"]), float(data_y[i]["value"]), float(data_z[i]["value"])))
	    years.append(data_x[i]["date"])
    for i in range(len(ret)):
	if((i + 1) < (len(ret) - 1)):
	    x_ratio = (ret[i][0] - ret[i + 1][0]) / 10
	    y_ratio = (ret[i][1] - ret[i + 1][1]) / 10
	    nx = ret[i][0]
	    ny = ret[i][1]
	    if(x_ratio < 0):
	        x_ratio = x_ratio * -1
		xd = -1
	    else:
		xd = 1
	    if(y_ratio < 0):
		y_ratio = y_ratio * -1
		yd = -1
	    else:
		yd = 1
	    for j in range(10):
		if(xd < 0):
		    nx = nx + x_ratio
		else:
		    nx = nx - x_ratio
		if(yd < 0):
		    ny = ny + y_ratio
		else:
		    ny = ny - y_ratio
		ret_extra.append((nx, ny, ret[i][2]))
    return ret_extra

def transform_data(data_arr, xw_size, yw_size, bounds):
    #bounds = [x_max, x_min, y_max, y_min]
    #bounds = [60000, 2000, 80, 50]
    dataX = bounds[0] - bounds[1]
    dataY = bounds[2] - bounds[3]
    x_rate = xw_size / dataX
    y_rate = yw_size / dataY
    pts = []
    for item in data_arr:
        x = (x_rate * (item[0] - bounds[1])) - (xw_size / 2)
        y = (y_rate * (item[1] - bounds[3])) - (yw_size / 2)
        z = item[2] / 3000000000
        pts.append((x, y, z))
    return pts
    #return final_pts

def get_boundaries(data_list):
    x_max = 0
    x_min = 0
    y_max = 0
    y_min = 0
    for data in data_list: 
        xmax = max(data, key=itemgetter(0))[0]
        xmin = min(data, key=itemgetter(0))[0]
        ymax = max(data, key=itemgetter(1))[1]
        ymin = min(data, key=itemgetter(1))[1]
        if(xmax > x_max or x_max == 0):
            x_max = xmax
        if(xmin < x_min or x_min == 0):
            x_min = xmin
        if(ymax > y_max or y_max == 0):
            y_max = ymax
        if(ymin < y_min or y_min == 0):
            y_min = ymin
    return [x_max, x_min, y_max, y_min]

def create_circles(colors, radius=[.02]):
    actors = []
    r = random.random()
    g = random.random()
    b = random.random()
    for i in range(len(radius)):
        circleSource = vtk.vtkRegularPolygonSource()
	circleSource.SetNumberOfSides(50)
	circleSource.SetRadius(radius[i])
	circleSource.SetCenter(0, 0, 0)
	circleSource.Update()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(circleSource.GetOutputPort())
        mapper.ScalarVisibilityOff()
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
        r = 1 - (radius[i] + random.random())
        g = 1 - (radius[i] + random.random())
        b = 1 - (radius[i] + random.random()) 
        actor.GetProperty().SetColor(r, g, b)
        colors.append((r, g, b))
        actors.append(actor)
    return actors

def main():
    #get data from the world bank
    countries = ["us", "mx", "gb", "jp", "br", "es"]
    final_data = []
    years = []
    for country in countries:
        if(len(years) == 0):
            data_arr = get_data(years, country = country)
        else:
	    data_arr = get_data([], country = country)
        final_data.append(data_arr)
    #print data_arr
    xw_size = 2.4 #World width
    yw_size = 1.8 #World height
    final_trans_data = []
    radiuses = []
    boundaries = get_boundaries(final_data)
    #print boundaries
    for i in range(len(countries)):
        data_pts = transform_data(final_data[i], xw_size, yw_size, boundaries)
        final_trans_data.append(data_pts)
        radiuses.append(data_pts[0][2])
    #print radiuses
    #print data_pts
    #create plot axis
    axisPolyData = create_axis()
    gridPolyData = create_grid()

    axisMapper = vtk.vtkPolyDataMapper()
    axisMapper.SetInput(axisPolyData)
    gridMapper = vtk.vtkPolyDataMapper()
    gridMapper.SetInput(gridPolyData)
    axisActor = vtk.vtkActor()
    axisActor.SetMapper(axisMapper)
    gridActor = vtk.vtkActor()
    gridActor.SetMapper(gridMapper)

    #create render Window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(800,600)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(axisActor)
    renderer.AddActor(gridActor)
    #ASSIGN ACTORS
    txt_title = vtk.vtkTextActor()
    txt_title.SetInput(years[len(years) -1 ])
    txt_title_prop = txt_title.GetTextProperty()
    txt_title_prop.SetFontSize(18)
    txt_title_prop.SetColor(0, 0, 0)
    txt_title.SetDisplayPosition(400, 580)

    txt_xmin = vtk.vtkTextActor()
    txt_xmin.SetInput(str(boundaries[1]))
    txt_xmin_prop = txt_xmin.GetTextProperty()
    txt_xmin_prop.SetFontSize(12)
    txt_xmin_prop.SetColor(0, 0, 0)
    txt_xmin.SetDisplayPosition(10, 5)

    txt_xmed = vtk.vtkTextActor()
    txt_xmed.SetInput(str(boundaries[0] / 2))
    txt_xmed_prop = txt_xmed.GetTextProperty()
    txt_xmed_prop.SetFontSize(12)
    txt_xmed_prop.SetColor(0, 0, 0)
    txt_xmed.SetDisplayPosition(370, 5)

    txt_xmax = vtk.vtkTextActor()
    txt_xmax.SetInput(str(boundaries[0]))
    txt_xmax_prop = txt_xmax.GetTextProperty()
    txt_xmax_prop.SetFontSize(12)
    txt_xmax_prop.SetColor(0, 0, 0)
    txt_xmax.SetDisplayPosition(750, 5)

    txt_ymin = vtk.vtkTextActor()
    txt_ymin.SetInput(str(math.ceil(boundaries[3])))
    txt_ymin_prop = txt_ymin.GetTextProperty()
    txt_ymin_prop.SetFontSize(12)
    txt_ymin_prop.SetColor(0, 0, 0)
    txt_ymin.SetDisplayPosition(5, 20)

    txt_ymed = vtk.vtkTextActor()
    txt_ymed.SetInput(str(math.ceil(boundaries[3])/2))
    txt_ymed_prop = txt_ymed.GetTextProperty()
    txt_ymed_prop.SetFontSize(12)
    txt_ymed_prop.SetColor(0, 0, 0)
    txt_ymed.SetDisplayPosition(5, 280)

    txt_ymax = vtk.vtkTextActor()
    txt_ymax.SetInput(str(math.ceil(boundaries[2])))
    txt_ymax_prop = txt_ymax.GetTextProperty()
    txt_ymax_prop.SetFontSize(12)
    txt_ymax_prop.SetColor(0, 0, 0)
    txt_ymax.SetDisplayPosition(5, 580)

    txt_actors = []
    txt_actors.append(txt_title)
    txt_actors.append(txt_xmin)
    renderer.AddActor(txt_title)
    renderer.AddActor(txt_xmin)
    renderer.AddActor(txt_xmax)
    renderer.AddActor(txt_xmed)
    renderer.AddActor(txt_ymax)
    renderer.AddActor(txt_ymed)
    renderer.AddActor(txt_ymin)
    colors = []
    actors = create_circles(colors, radiuses)
    for ci in range(len(colors)):
        txt_country = vtk.vtkTextActor()
        txt_country.SetInput(countries[ci])
	txt_country_prop = txt_country.GetTextProperty()
	txt_country_prop.SetFontSize(16)
	txt_country_prop.SetColor(colors[ci][0], colors[ci][1], colors[ci][2])
	txt_country.SetDisplayPosition(750, 200 + (ci * 25))
	renderer.AddActor(txt_country)
    for actor in actors:
        renderer.AddActor(actor)

    renderer.SetBackground(1, 1, 1)

    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(0, 0, 0)
    camera.Dolly(.28)

    renderWindow.Render()
    style = vtk.vtkInteractorStyleTrackballCamera()
    renderWindowInteractor.SetInteractorStyle(style)
    renderWindowInteractor.Initialize()

    #SETUP TIMER EVENTS
    
    actrs = renderer.GetActors()
    cb = vtkTimerCallback()
    cb.actors = actrs
    cb.transformed_pts = final_trans_data
    cb.limit = len(final_trans_data[0])
    cb.offset = 2
    cb.years = years
    cb.txt_actors = txt_actors
    #for itm in final_trans_data:
    #    print itm
    for i in range(actrs.GetNumberOfItems()):
        actor = actrs.GetItemAsObject(i)
	#print "actor {0}".format(i)
        if(i > 1):
	    pos = [final_trans_data[i - 2][len(final_trans_data[i-2]) - 1][0], final_trans_data[i - 2][len(final_trans_data[i-2]) - 1][1], 0]
            actor.SetPosition(pos)
	    #print "Setting position of actor {0} in {1}".format(i, pos)

    renderWindow.Render()
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    timerId = renderWindowInteractor.CreateRepeatingTimer(100)
    renderWindowInteractor.Start()

if __name__ == '__main__':
   main()
