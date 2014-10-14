import vtk

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


