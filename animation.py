import vtk
import urllib2
import json
import math
import random
from operator import itemgetter
from VTKTimer import vtkTimerCallback
from GraphAnimator import GraphAnimator

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
            #print data_x[i]["value"] + "," + data_y[i]["value"] + "," + data_z[i]["value"]
        years.append(data_x[i]["date"])
    for i in range(len(ret)):
        if((i + 1) <= (len(ret) - 1)):
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
        '''
        print "Country {0}".format(country)
        for j in data_arr:
            print j
        '''
        final_data.append(data_arr)
    xw_size = 2.4 #World width
    yw_size = 1.8 #World height

    final_trans_data = []
    radiuses = []
    ga = GraphAnimator()
    boundaries = ga.get_boundaries(final_data)
    #print boundaries
    for i in range(len(countries)):
        data_pts = ga.transform_data(final_data[i], xw_size, yw_size, boundaries)
        final_trans_data.append(data_pts)
        radiuses.append(data_pts[0][2])
    #print radiuses
    #print data_pts
    #create plot axis
    axisPolyData = ga.create_axis()
    gridPolyData = ga.create_grid()

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
    txt_ymed.SetInput(str(math.ceil(boundaries[2])/2))
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
    actors = ga.create_circles(colors, radiuses)
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
