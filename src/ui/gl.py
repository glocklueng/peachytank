import wx
from OpenGL.GLUT import *
from OpenGL.GL import *
from wx import glcanvas
import logging

from domain.objects import Tank
from gl_objects import *
from gl_helpers import JGLHelpers


class Canvas(glcanvas.GLCanvas):

    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.context = glcanvas.GLContext(self)
        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0
        self.size = None
        self.last_scale = 0.0
        self.scale = 0.0
        self.xrot = self.lastrotx = 0.0
        self.yrot = self.lastroty = 0.0

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.peachy_setup = None
        self.enviroment_draw = DrawEnvironment()
        self.tank_draw = DrawTank()
        self.printer_draw = DrawPrinter()
        self.axis = Axis()
        self.jgl = JGLHelpers()
        glutInit()

    def OnEraseBackground(self, event):
        # Do nothing, to avoid flashing on MSW.
        pass

    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        # self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
        self.jgl.width = size.width
        self.jgl.height = size.height

    def OnPaint(self, event):
        # dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = evt.GetPosition()

    def OnMouseUp(self, evt):
        self.ReleaseMouse()

    def OnMouseWheel(self, evt):
        if evt.GetWheelRotation() > 0:
            self.scale += 0.01
        else:
            self.scale -= 0.01
        logging.info("New Scale: %s" % self.scale)
        self.Refresh(False)

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x = evt.GetPosition()[0]
            self.y = evt.GetPosition()[1]
            logging.debug('Diff X:Y:  %s:%s ' % (self.x - self.lastx, self.y - self.lasty))
            self.xrot += self.x - self.lastx
            self.yrot += self.y - self.lasty
            self.Refresh(False)

    def InitGL(self):
        logging.info("Initing")
        # set viewing projection
        glMatrixMode(GL_PROJECTION)
        glFrustum(-0.5, 0.5, -0.1, 0.5, 0.5, 8.0)

        # position viewer
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -2.0)

        # position object
        glRotatef(self.y, 1.0, 0.0, 0.0)
        # glRotatef(self.x, 0.0, 1.0, 0.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)


        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        # glShadeModel(GL_SMOOTH)
        # glEnable(GL_COLOR_MATERIAL)
 
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 1.5, 1.5, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.6, 0.6, 0.6, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])

        glLightfv(GL_LIGHT1, GL_POSITION, [0.0, -1.5, 1.5, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.6, 0.6, 0.6, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])

        self.DoSetViewport()

    # def show_lights(self):
    #     glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION, [1.0, 1.0, 1.0, 1.0])
    #     for light in self.lights:
    #         light_pos = light[:3]
    #         light_inv = [coord * -1 for coord in light[:3]]
    #         glTranslatef(*light_pos)
    #         glutWireSphere(0.04,  10, 10)
    #         glTranslatef(*light_inv)

    def OnDraw(self):
        if not self.init:
            return
        glMatrixMode(GL_MODELVIEW)
        logging.debug("DRAW")
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.enviroment_draw.draw(None)
        if self.peachy_setup:
            scaled_setup = self.peachy_setup.get_scaled_to_fit(1.0)
            self.tank_draw.draw(scaled_setup.tank)
            self.printer_draw.draw(scaled_setup.printer)
            self.axis.draw(None)

        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        w = max(w, 1.0)
        h = max(h, 1.0)
        xScale = 180.0 / w
        yScale = 180.0 / h
        logging.debug("X:Y: %s:%s" % (self.xrot, self.yrot))

        # Vertical Rotation Revert
        glTranslatef(0.0, 0.5, 0.0)
        glRotatef(0.0 - (self.lastroty * yScale), 1.0, 0.0, 0.0)
        glTranslatef(0.0, -0.5, 0.0)

        # Horizontal Rotation Revert
        glRotatef(0.0 - (self.lastrotx * xScale), 0.0, 1.0, 0.0)

        # Scale Revert (Z pos)
        glTranslatef(0.0, 0.0, 0.0 - self.last_scale)

        # Scale
        glTranslatef(0.0, 0.0, 0.0 + self.scale)

        # Horizontal Rotation
        glRotatef(self.xrot * xScale, 0.0, 1.0, 0.0)

        # Vertical Rotation
        glTranslatef(0.0, 0.5, 0.0)
        glRotatef(self.yrot * yScale, 1.0, 0.0, 0.0)
        glTranslatef(0.0, -0.5, 0.0)

        self.last_scale = self.scale
        self.lastrotx, self.lastroty = self.xrot, self.yrot

        self.jgl.drawString("Scale: {0:.2f}\nRotationX: {1:.2f}\nRotationY: {2:.2f}\n ".format(self.scale, self.xrot * xScale, self.yrot * yScale))

        self.SwapBuffers()
