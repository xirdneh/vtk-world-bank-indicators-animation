import vtk
import urllib2
import json
import math
import random
from operator import itemgetter

class GraphAnimator():
    def create_grid(self):
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
        

    def create_axis(self):
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

    def transform_data(self, data_arr, xw_size, yw_size, bounds):
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

    def get_boundaries(self, data_list):
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

    def create_circles(self, colors, radius=[.02]):
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


