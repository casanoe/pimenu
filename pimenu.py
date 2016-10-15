#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import sqrt, floor, ceil
import os
from urllib import urlopen
from StringIO import StringIO
import base64
import subprocess
import yaml

import Tkconstants as TkC

from PIL import ImageTk as itk
from PIL import Image
from Tkinter import Tk, Frame, Button, Label, PhotoImage

import sys
import json

from pimenu_user import *

#-------------------------

class FlatButton(Button):
    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        # self.pack()
        self.config(
            compound=TkC.TOP,
            relief=TkC.FLAT,
            bd=0,
            bg="#b91d47",  # dark-red
            fg="white",
            activebackground="#b91d47",  # dark-red
            activeforeground="white",
            # height=118,
            #width=104,
            font='sans 12',
            highlightthickness=0
        )    
    def get_size(self):
        return self.winfo_reqwidth(), self.winfo_reqheight()
    def set_font(self, fnt):
        self.configure(font=fnt)
    def set_color(self, color):
        self.configure(
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white"
        )

#-------------------------

class PiMenu(Frame):
    doc = None
    framestack = []
    icons = {}
    path = ''
    val = {} # table of value of all current buttons
    state = {} # table of state of all current buttons

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.pack(fill=TkC.BOTH, expand=1)

        self.path= os.path.dirname(os.path.realpath(sys.argv[0]))
        with open(self.path + '/pimenu.yaml', 'r') as f:
            self.doc = yaml.load(f)
        self.show_items(self.doc)

    def show_items(self, items, upper=[]):
        """
        Creates a new page on the stack, automatically adds a back button when there are
        pages on the stack already

        :param items: list the items to display
        :param upper: list previous levels' ids
        :return: None
        """
        num = 0
        back = False
        
        localparams = {}
        if items[0]['name'] == '__localparam__':
            localparams = items[0]
            del items[0]
        
        # create a new frame
        wrap = Frame(self, bg="black")
        # when there were previous frames, hide the top one and add a back button for the new one
        if len(self.framestack):
            self.hide_top()
            #if '__back__' not in items:
            if not (self.search_any(items, 'name', '__back__')):
                back = FlatButton(
                    wrap,
                    text='back…',
                    image=self.get_icon("arrow.left.gif"),
                    command=self.go_back,
                )
                back.set_color("#00a300")  # green
                back.grid(row=0, column=0, padx=1, pady=1, sticky=TkC.W + TkC.E + TkC.N + TkC.S)
                num += 1
        # add the new frame to the stack and display it
        self.framestack.append(wrap)
        self.show_top()

        # calculate tile distribution
        all = len(items) + num
        if 'direction' in localparams and localparams['direction'] == 'horizontal':
            cols = floor(sqrt(all))
            rows = ceil(all / cols)
        else:
            rows = floor(sqrt(all))
            cols = ceil(all / rows)

        # make cells autoscale
        for x in range(int(cols)):
            wrap.columnconfigure(x, weight=1)
        for y in range(int(rows)):
            wrap.rowconfigure(y, weight=1)

        # display all given buttons
        for item in items:
            if item['name'] == '__localparam__':
                continue
            act = upper + [item['name']]
            
            if 'icon' in item:
                image = self.get_icon(item['icon'])
            elif 'image' in item:
                size = 100,100
                if 'imgwidth' in item and 'imgheight' in item:
                    size = int(item['imgwidth']), int(item['imgheight'])
                image = self.get_image(item['name'], item['image'], size)    
            else:
                image = None
            
            txt = ''
            if 'label' in item:
                txt=item['label']
            if 'title' in item:
                txt=item['title']+"\n"+txt
                
            btn = FlatButton(
                wrap,
                text=txt,
                image=image
            )

            if 'color' in item:
                btn.set_color(item['color'])
            if 'font' in item:
                btn.set_font(item['font'])
            if 'items' in item:
                btn.configure(command=lambda act=act, item=item: self.show_items(item['items'], act), text=item['label']+'…')
                btn.set_color("#2b5797")
            elif 'user' in item:
                self.go_action_user(btn, item, 'onconfigure')
                if item['name'] == '__back__':
                    action = 'ongoback'
                else:
                    action = 'onclick'
                btn.configure(command=lambda btn=btn, item=item, action=action: self.go_action_user(btn, item, action), )
            elif item['name'] == '__back__':
                btn.configure(command=self.go_back, )
            else:
                btn.configure(command=lambda act=act: self.go_action(act), )

            # add buton to the grid
            btn.grid(
                row=int(floor(num / cols)),
                column=int(num % cols),
                padx=1,
                pady=1,
                sticky=TkC.W + TkC.E + TkC.N + TkC.S
            )
            num += 1

    def search_any(self, dict, key, value):
        for d in dict:
            if d[key] == value:
                return True
        return False

    def get_icon(self, ico):
        if ico in self.icons:
            return self.icons[ico]
        if ico.lower().startswith('http://')==True or ico.lower().startswith('https://')==True:
            image_byt = urlopen(ico).read()
            image_b64 = base64.encodestring(image_byt)
            self.icons[ico] = PhotoImage(data=image_b64)
            return self.icons[ico]
        else:
            icopath = self.path + '/ico/' + ico
            if not os.path.isfile(icopath):
                icopath = self.path + '/ico/cancel.gif'
            self.icons[ico] = PhotoImage(file=icopath)
            return self.icons[ico]
    
    def get_image(self, name, file, size, _int = None):
        try:
            if file.lower().startswith('http://')==True or file.lower().startswith('https://')==True:
                response = requests.get(file)
                image1 = Image.open(StringIO(response.content))
            else:
                image1 = Image.open(file)
            image1.thumbnail(size)
            image = itk.PhotoImage(image1)
            if _int == None:
                _int = name+'__image__'
            self.icons[_int] = image
            return image
        except:
            return None

    def get_icon2(self, ico):
        if ico in self.icons:
            return self.icons[ico]
        if ico.lower().startswith('http://')==True or ico.lower().startswith('https://')==True:
            return None
            image_byt = urlopen(ico).read()
            image_b64 = base64.encodestring(image_byt)
            self.icons[ico] = itk.PhotoImage(data=image_b64)
            return self.icons[ico]
        else:
            icopath = self.path + '/ico/' + ico
            if not os.path.isfile(icopath):
                icopath = self.path + '/ico/cancel.gif'
            image1 = Image.open(icopath)
            self.icons[ico] = itk.PhotoImage(image1)
            return self.icons[ico]
        
    def hide_top(self):
        """
        hide the top page
        :return:
        """
        self.framestack[len(self.framestack) - 1].pack_forget()

    def show_top(self):
        """
        show the top page
        :return:
        """
        self.framestack[len(self.framestack) - 1].pack(fill=TkC.BOTH, expand=1)

    def destroy_top(self):
        """
        destroy the top page
        :return:
        """
        self.framestack[len(self.framestack) - 1].destroy()
        self.framestack.pop()

    def destroy_all(self):
        """
        destroy all pages except the first aka. go back to start
        :return:
        """
        while len(self.framestack) > 1:
            self.destroy_top()

    def go_action_user(self, btn, item, action):
        #print action
        name = item['name']
        tmp = {}
        params = None
        txt = ''
        if action == 'onconfigure':
            self.val[name] = None
            self.state[name] = False
        if 'func' in item['user'][0]:
            if 'params' in item['user'][0]:
                params = item['user'][0]['params'][0]
            res = globals()[item['user'][0]['func']](self.val[name], params, action)
            self.val[name] = res[0]
            self.state[name] = res[1]
            if len(res)>2:
                tmp = res[2]
            if action != 'onclick' and 'refresh' in item['user'][0]:
                btn.after(int(item['user'][0]['refresh']), lambda btn=btn, item=item: self.go_action_user(btn, item, 'onrefresh'))
        elif action == 'onclick':
            self.state[name] = not self.state[name]
        if action == 'ongoback':
            self.go_back()
        #print name, self.val[name] ,self.state[name] 
        if 'title' in item:
            txt = str(item['title'])
        if self.state[name] == True:
            tmp.update(item)
        else:
            tmp.update(item['user'][0])
        if 'app_action' in tmp:
            if tmp['app_action'] == 'go_back':
                self.go_back()
                return
        if 'label' in tmp:
            if txt != '':
                txt += "\n"
            btn.config(text=txt+str(tmp['label']))
        if 'font' in tmp:
            btn.set_font(tmp['font'])
        if 'color' in tmp:
            btn.set_color(tmp['color'])
        if 'icon' in tmp:
            btn.config(image=self.get_icon(tmp['icon']))
        elif 'image' in tmp:
            size = 100,100
            if 'imgwidth' in tmp and 'imgheight' in tmp:
                size = int(tmp['imgwidth']), int(tmp['imgheight'])
            btn.config(image=self.get_image(name, tmp['image'], size))

    def go_action(self, actions):
        """
        execute the action script
        :param actions:
        :return:
        """
        # hide the menu and show a delay screen
        self.hide_top()
        delay = Frame(self, bg="#2d89ef")
        delay.pack(fill=TkC.BOTH, expand=1)
        label = Label(delay, text="Executing...", fg="white", bg="#2d89ef", font="Sans 30")
        label.pack(fill=TkC.BOTH, expand=1)
        self.parent.update()

        # excute shell script
        subprocess.call([self.path + '/pimenu.sh'] + actions)

        # remove delay screen and show menu again
        delay.destroy()
        self.destroy_all()
        self.show_top()

    def go_back(self):
        """
        destroy the current frame and reshow the one below
        :return:
        """
        self.destroy_top()
        self.show_top()


def main():
    root = Tk()
    root.geometry("800x480")
    root.config(cursor="none")
    root.wm_title('PiMenu')
    if len(sys.argv) > 1 and sys.argv[1] == 'fs':
        root.wm_attributes('-fullscreen', True)
    app = PiMenu(root)
    root.mainloop()


if __name__ == '__main__':
    main()
