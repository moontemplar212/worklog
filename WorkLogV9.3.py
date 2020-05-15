#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import wx
import re
import datetime as dt
import wx.lib.scrolledpanel as scrolled
import pyodbc


class MyMainFrame(wx.Frame):
    width = 1000
    height = 600
    today = dt.date.today()
    today_date = f"{today:%A - %d %B %Y}"
    filename = f"Worklog {today_date}"
    wxTHICK_LINE_BORDER = 3
    counter = 0
    elems = None
    
    def __init__(self, parent=None, title=filename, size=(width,height - 1)):
        wx.Frame.__init__(self, parent=parent, title=title, size=size)
        self.parent = parent
        self.title = title
        self.size = size
        self.SetMinClientSize(wx.Size(300,100))
        self.BuildMenuBar()
        self.BuildStatusBar()

    def BuildMenuBar(self):
        # Menu bar
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.NewOpt = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&New\tCtrl+N')
        self.OpenOpt = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Open\tCtrl+O')
        self.ExportOpt = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Export\tCtrl+E')
        self.SaveOpt = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Save\tCtrl+S')
        self.QuitOpt = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Quit\tCtrl+Q')
        self.fileMenu.Append(self.NewOpt)
        self.fileMenu.Append(self.OpenOpt)
        self.fileMenu.Append(self.ExportOpt)
        self.fileMenu.Append(self.SaveOpt)
        self.fileMenu.Append(self.QuitOpt)
        self.Bind(wx.EVT_MENU, self.OnNew, self.NewOpt)
        self.Bind(wx.EVT_MENU, self.OnOpen, self.OpenOpt)
        self.Bind(wx.EVT_MENU, self.OnExport, self.ExportOpt)
        self.Bind(wx.EVT_MENU, self.OnSave, self.SaveOpt)
        self.Bind(wx.EVT_MENU, self.OnQuit, self.QuitOpt)
        self.menuBar.Append(self.fileMenu, '&File')
        
        self.DatabaseMenu = wx.Menu()
        self.ConnectDatabaseOpt = wx.MenuItem(self.DatabaseMenu, wx.ID_ANY, '&Connect')
        self.FetchAllDatabaseOpt = wx.MenuItem(self.DatabaseMenu, wx.ID_ANY, '&Fetch All')
        self.FetchLatestDatabaseOpt = wx.MenuItem(self.DatabaseMenu, wx.ID_ANY, '&Fetch Latest')
        self.InsertDatabaseOpt = wx.MenuItem(self.DatabaseMenu, wx.ID_ANY, '&Insert')
        self.CloseDatabaseOpt = wx.MenuItem(self.DatabaseMenu, wx.ID_ANY, '&Close')
        self.DatabaseMenu.Append(self.ConnectDatabaseOpt)
        self.DatabaseMenu.Append(self.FetchAllDatabaseOpt)
        self.DatabaseMenu.Append(self.FetchLatestDatabaseOpt)
        self.DatabaseMenu.Append(self.InsertDatabaseOpt)
        self.DatabaseMenu.Append(self.CloseDatabaseOpt)
        self.Bind(wx.EVT_MENU, self.OnConnect, self.ConnectDatabaseOpt)
        self.Bind(wx.EVT_MENU, self.OnFetchAll, self.FetchAllDatabaseOpt)
        self.Bind(wx.EVT_MENU, self.OnFetchLatest, self.FetchLatestDatabaseOpt)
        self.Bind(wx.EVT_MENU, self.OnInsert, self.InsertDatabaseOpt)
        self.Bind(wx.EVT_MENU, self.OnClose, self.CloseDatabaseOpt)
        self.menuBar.Append(self.DatabaseMenu, '&Database')

        self.HelpMenu = wx.Menu()
        self.AboutOpt = wx.MenuItem(self.HelpMenu, wx.ID_ANY, '&About')
        self.SettingsOpt = wx.MenuItem(self.HelpMenu, wx.ID_ANY, '&Settings')
        self.CopyrightOpt = wx.MenuItem(self.HelpMenu, wx.ID_ANY, '&Copyright')
        self.HelpMenu.Append(self.AboutOpt)
        self.HelpMenu.Append(self.SettingsOpt)
        self.HelpMenu.Append(self.CopyrightOpt)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.AboutOpt)
        self.Bind(wx.EVT_MENU, self.OnSettings, self.SettingsOpt)
        self.Bind(wx.EVT_MENU, self.OnCopyright, self.CopyrightOpt)
        self.menuBar.Append(self.HelpMenu, '&Help')
        
        self.SetMenuBar(self.menuBar)

    def BuildStatusBar(self):
        self.now = dt.datetime.now()
        self.now_datetime = f"{self.now:%d-%m-%y %H:%M:%S %p}"
        self.statusBar = self.CreateStatusBar()

        self.live = "OK"
        self.refresh = "Last Refresh 0m Ago"
        self.now_datetime = f"{self.now:%d-%m-%y %H:%M:%S %p}"
        self.notifier = f"Datetime: {self.now_datetime}"
        
        dc = wx.ClientDC(self.statusBar)
        dc.SetFont(self.statusBar.GetFont())
        width1, dummy = dc.GetTextExtent(self.refresh)
        width2, dummy = dc.GetTextExtent(self.notifier)

        width1 += 2*MyMainFrame.wxTHICK_LINE_BORDER
        width2 += 2*MyMainFrame.wxTHICK_LINE_BORDER
        if self.statusBar.GetWindowStyle() & wx.STB_SIZEGRIP:
            width2 += wx.STB_SIZEGRIP

        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-1, width1, width2])

        self.statusBar.SetStatusText(self.live, 0)
        self.statusBar.SetStatusText(self.refresh, 1)
        self.statusBar.SetStatusText(self.notifier, 2)
    

    def OnNew(self, e):
        # New file // reset the current instance
        self.now = dt.datetime.now()
        self.now_datetime = f"{self.now:%d-%m-%y %H:%M:%S %p}"
        self.notifier = f"Datetime: {self.now_datetime}"
        self.statusBar.SetStatusText(self.notifier, 2)

        self.frameChildren = self.GetChildren()[1] # statusBar and [ panel ]
        self.panelChildren = self.frameChildren.GetChildren()[0] # [ scrollPanel ]

        self.panelChildren.Destroy()
        scrolledPanel = MyScrolledPanel(self.frameChildren)

        self.SetSize(MyMainFrame.width-1,MyMainFrame.height)
        self.SetSize(MyMainFrame.width,MyMainFrame.height)
        
        self.Refresh()
    

    def OnOpen(self, e):
        # File dialog to open file
        self.filepath = os.path.expanduser("~")
        fileDialog = wx.FileDialog(parent = None, message = "Please select a file to open", defaultDir = self.filepath, defaultFile = "", style = wx.FD_OPEN)
        fileDialog.ShowModal()
    
    def OnExport(self, e, **kwargs):
        self.path = kwargs.get("path", None)
        exported = False
        try:
            # reset filename at the beginning
            self.filename = f"Worklog {self.today_date}"
            self.contents = []
            self.frameChildren = self.GetChildren()[1] # statusBar and [ panel ]
            self.panelChildren = self.frameChildren.GetChildren()[0] # [ scrollPanel ]
            vals = len(self.panelChildren.rowList)
            for i in range(0,vals,1):
                key = self.panelChildren.rowList[i][0].GetLabel()
                value = self.panelChildren.rowList[i][1].GetValue()
                if len(value) > 0:
                    self.contents.append(key + " " + value + "\n")
            # define the filepath
            self.filepath = ""
            if (self.path is not None):
                self.filepath = self.path
            if not os.path.exists(self.filepath):
                raise FileNotFoundError
        except FileNotFoundError as e: # goto if directory does not exist
            # Path not found so dump file to user homepath - C:\Users\<user>
            self.filepath = os.path.expanduser("~")
            self.complete_file_path = os.path.join(self.filepath, self.filename+".txt")
            try:
                while exported == False:
                    if not os.path.exists(self.complete_file_path):
                        with open(self.complete_file_path, 'w', encoding = 'utf=8') as self.f:
                            for content in self.contents:
                                self.f.write(str(content))
                        self.f.close()
                        self.now = dt.datetime.now()
                        self.notifier = f"Exported on {self.now_datetime}"
                        self.statusBar.SetStatusText(self.notifier, 2)
                        self.Refresh()
                        exported = True
                        print(f"Dumping to default home directory: {self.complete_file_path}")
                    else:
                        self.counter += 1
                        self.filename = f"Worklog {self.today_date}" + " ("+str(self.counter)+")"
                        self.complete_file_path = os.path.join(self.filepath, self.filename+".txt")                   
            except Exception as e:
                print("User homepath " + self.filepath + " not found - cannot export file")
            finally:
                self.counter = 0
        else:
            # Before write file check directory and write newest filename
            self.complete_file_path = os.path.join(self.filepath, self.filename+".txt")
            try:
                while exported == False:
                    if not os.path.exists(self.complete_file_path):
                        with open(self.complete_file_path, 'w', encoding = 'utf=8') as self.f:
                            for content in self.contents:
                                self.f.write(str(content))
                        self.f.close()
                        self.now = dt.datetime.now()
                        self.now_datetime = f"{self.now:%d-%m-%y %H:%M:%S %p}"
                        self.notifier = f"Exported on {self.now_datetime}"
                        self.statusBar.SetStatusText(self.notifier, 2)
                        self.Refresh()
                        exported = True
                        print(f"Saved file to: {self.filepath}")
                    else:
                        self.counter += 1
                        self.filename = f"Worklog {self.today_date}" + " ("+str(self.counter)+")"
                        self.complete_file_path = os.path.join(self.filepath, self.filename+".txt")
            except Exception as e:
                print("Something went wrong exporting to " + self.complete_file_path + " - cannot export file")
            finally:
                self.counter = 0


    def OnSave(self, e):
        # Save file externally in a defined filepath
        self.OnExport(e, path = "C:\\Users\\sjdav\\Desktop")


    def OnQuit(self, e):
        # Close the Frame window instance
        self.Close()


    def OnConnect(self, e):
        # Connect to database
        self.connectDatabase()

    
    def OnFetchAll(self, e):
        # Fetch all from database
        self.fetchAllFromDatabase()
    

    def OnFetchLatest(self, e):
        # Fetch latest from database
        self.fetchLatestFromDatabase()


    def OnInsert(self, e):
        # Insert to database
        self.insertDatabase()
    

    def OnClose(self, e):
        # Close database connection
        self.closeDatabase()


    def OnAbout(self, e):
        # New frame with some About info 
        frame = MyFrame(title = "About", style = wx.CLOSE_BOX | wx.CAPTION | wx.RESIZE_BORDER)
        # style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER
        # style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX    
        # style = wx.CLOSE_BOX | wx.CAPTION | wx.RESIZE_BORDER
        panel = MyPanel(frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        txtStr = "Worklog is a task logging program to help you quickly and easily take notes on tasks."
        staticText = wx.StaticText(panel, wx.ID_ANY, txtStr)
        staticText.Wrap(panel.size[0])
        sizer.Add(staticText)
        panel.SetSizer(sizer)
        panel.Layout()
        frame.SetSize(400,300)
        frame.SetSizeHints(400,300)
        frame.SetMaxClientSize((400,300))
        frame.SetMinClientSize((400,300))
        frame.Show(True)



    def OnSettings(self, e):
        # File dialog Settings including user profile management
        frame = MyFrame(title = "Settings", style = wx.CLOSE_BOX | wx.CAPTION | wx.RESIZE_BORDER)
        panel = MyPanel(frame)
        
        sizer = wx.GridBagSizer(10,10)
        
        user_text = wx.StaticText(panel, wx.ID_ANY, "User")
        user_text_control = wx.TextCtrl(panel, wx.ID_ANY)
        user_text_control.SetMaxLength(16)
        path_text = wx.StaticText(panel, wx.ID_ANY, "Path")
        path_text_control = wx.TextCtrl(panel, wx.ID_ANY)
        database_text = wx.StaticText(panel, wx.ID_ANY, "Database")
        database_text_control = wx.TextCtrl(panel, wx.ID_ANY)
        username_text = wx.StaticText(panel, wx.ID_ANY, "Username")
        username_text_control = wx.TextCtrl(panel, wx.ID_ANY)
        password_text = wx.StaticText(panel, wx.ID_ANY, "Password")
        password_text_control = wx.TextCtrl(panel, wx.ID_ANY)
        
        sizer.Add(user_text, pos = (0, 0), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(user_text_control, pos = (0, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(path_text, pos = (1, 0), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(path_text_control, pos = (1, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(database_text, pos = (2, 0), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(database_text_control, pos = (2, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(username_text, pos = (3, 0), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(username_text_control, pos = (3, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(password_text, pos = (4, 0), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        sizer.Add(password_text_control, pos = (4, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
        
        sizer.AddGrowableCol(1)
        panel.SetSizer(sizer)
        panel.Layout()
        #self.panelSizer.Add(self, pos = (0, 0), flag = wx.EXPAND, border = 0) # Add wx.Window not wx.Sizer
        frame.SetSize(640,480)
        frame.SetSizeHints(640,480)
        frame.SetMaxClientSize((640,480))
        frame.SetMinClientSize((640,480))
        frame.Show(True)


    def OnCopyright(self, e):
        # File dialog copyright
        pass

    
    def setupConnectionString(self, server, db_name, un, pw):
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'+
            'SERVER='+str(server)+';'+
            'DATABASE='+str(db_name)+';'
            'UID='+str(un)+';'+
            'PWD='+str(pw)
        )

        connection.setdecoding(pyodbc.SQL_CHAR, encoding = 'utf-8')
        connection.setdecoding(pyodbc.SQL_WCHAR, encoding = 'utf-8')
        connection.setencoding(encoding = 'utf-8')

        cursor = connection.cursor()

        self.elems = [connection, cursor]

        return self.elems


    def fetchAllFromDatabase(self):
        try:
            if(self.elems is None):
                # If connection is null
                raise TypeError
        except TypeError as e:
            # Print err msg
            print("Database is not connected! Cannot fetch!")
            print(e)
        except Exception as e:
            print("An exception was caught!")
            print(e)
        else:
            # If connection is not null
            try:
                cursor = self.elems[1]
            except Exception as e:
                print("An exception was caught!")
                print(e)
            else:
                #chunk_size = 1000
                sql = r"select * from WL.WorkLog"
                cursor.execute(sql)
                while True:
                    # chunk the fetch to one row at at time
                    row = cursor.fetchone()
                    if row is None:
                        break
                    # for offset in range(0, row, chunk_size):
                    #     chunk = cursor.execute(r"select * from WL.WorkLog limit ? offset ?", chunk_size, offset)
                    #     for row in chunk:
                    #         print(chunk) 
                    if row:
                        print(row)
                    # If a successfull fetch
                    print("Success! A fetch was made!")


    def fetchLatestFromDatabase(self):
        # Fetch data with max publishdatetime from the database table
        try:
            if(self.elems is None):
                # If connection is null
                raise TypeError
        except TypeError as e:
            # Print err msg
            print("Database is not connected! Cannot fetch!")
            print(e)
        except Exception as e:
            print("An exception was caught!")
            print(e)
        else:
            # If connection is not null
            try:
                cursor = self.elems[1]
            except Exception as e:
                print("An exception was caught!")
                print(e)
            else:
                #chunk_size = 1000
                sql = r"select * from WL.WorkLog where publishdatetime = (select MAX(publishdatetime) from WL.WorkLog)"
                cursor.execute(sql)
                while True:
                    # chunk the fetch to one row at at time
                    row = cursor.fetchone()
                    if row is None:
                        break
                    # for offset in range(0, row, chunk_size):
                    #     chunk = cursor.execute(r"select * from WL.WorkLog limit ? offset ?", chunk_size, offset)
                    #     for row in chunk:
                    #         print(chunk) 
                    if row:
                        print(row)
                    # If a successfull fetch
                    print("Success! A fetch was made!")


    def insertDatabase(self):
        try:
            # insert into table_name (cols 1, cols 2, cols 3) values (value 1, value 2, value 3)
            if(self.elems is None):
                # If connection is null (python does not have a null pointer exception error code)
                raise TypeError
            else:
                # If connection is not null
                connection = self.elems[0]
                cursor = self.elems[1]
                cursor.fast_executemany = True
                # get the max primary key value (id) from the table
                sql = r"select max(id) from WL.WorkLog"
                cursor.execute(sql)
                # return value, if None return 0
                pk_id = cursor.fetchall()[0][0]
                if pk_id is None:
                    pk_id = 0
                else:
                    pk_id = int(pk_id)
        except TypeError as e:
            print("Database connection objects do not exist! Cannnot insert!")
            print(e)
        except Exception as e:
            print(e)
            print("An error was caught! Cannot insert!")
        else:
            # for row in self.row insert values
            self.frameChildren = self.GetChildren()[1] # statusBar and [ panel ] update reference (this should be the same and unnecessary)
            self.panelChildren = self.frameChildren.GetChildren()[0] # [ scrollPanel ] update reference
            numRows = len(self.panelChildren.rowList)
            # params = [1    (publishdatetime, extractdatetime, id, username, itemno, details, completionstatus), 
            #           2    (publishdatetime, extractdatetime, id, username, itemno, details, completionstatus)      ]
            params = []
            # get a single value here so that the milliseconds does not change every loop
            publishdatetime = str(dt.datetime.now())
            for i in range(0,numRows-1,1):
                # extractdatetime is None for insert
                extractdatetime = None
                pk_id += 1
                username = 'Samuel'                
                key = self.panelChildren.rowList[i][0].GetLabel()
                value = self.panelChildren.rowList[i][1].GetValue() 
                completionstatus = 'inProgress'
                params.append((publishdatetime, extractdatetime, pk_id, username, key, value, completionstatus))
            sql = r"insert into WL.WorkLog (publishdatetime, extractdatetime, id, username, itemno, details, completionstatus) values (?, ?, ?, ?, ?, ?, ?)"
            try:
                if len(params) > 0:
                    cursor.executemany(sql, params)
                else:
                    print("Params is empty! Cannot execute cursor! Cannot insert!")
                    raise IndexError
            except IndexError as e:
                print("Index error. No index exists!")
            except pyodbc.DatabaseError as e:
                print(e)
                connection.rollback()
            except Exception as e:
                print("An exception was caught trying to execute! Cannot insert!")
                print(e)
            else:
                connection.commit()
                # If a successfull insert
                print("Success! An insert was made!")


    def connectDatabase(self):
        try:
            # If connection is already made
            if(self.elems is not None):
                # Connection already exists
                raise Exception
        except Exception as e:
            # Print err msg
            print("Database is already connected!")
            print(e)
        else:
            try:
                # Connect to database
                self.elems = self.setupConnectionString("DESKTOP-463QQ8R\SQLEXPRESS", "WL_master", "sa", "sa")
            except pyodbc.DatabaseError as e:
                print(e)
            except TimeoutError as e:
                # Print err msg
                print("Database connection timed out! Did not connect.")
                print(e)
            else:
                # If a successfull connection
                print("Success! A connection was made!")

    
    def closeDatabase(self):
        try:
            if(self.elems is not None):
                # A connection exists
                del self.elems
            else:
                # connection does not exist and cannot delete
                raise TypeError
        except TypeError as e:
            print("Database is not connected! Cannot close!")
            print(e)
        else:
            # If a successfull close
            print("Success! Database was closed.")


class MyFrame(wx.Frame):
    def __init__(self, parent=None, title="", size=(400,300), *args, **kwargs):
        wx.Frame.__init__(self, parent=parent, title=title, size=size)
        self.parent = parent
        self.title = title
        self.size = size
        self.SetMinClientSize(wx.Size(400,300))

class MyPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.size = parent.size
        panel_colour = wx.Colour(240, 240, 240, 255)
        self.SetBackgroundColour(panel_colour)
        self.Refresh()

       
class MyScrolledPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent=parent, style = wx.TAB_TRAVERSAL)
        self.parent = parent
        # self.size = parent.size
        self.width = parent.size[0]
        self.height = parent.size[1]
        scrollpanel_colour = wx.Colour(255, 255, 255, 255)
        self.SetBackgroundColour(scrollpanel_colour)
        # Call a refresh to update the UI
        self.Refresh()
        self.SetAutoLayout(True)
        self.SetupScrolling()
        self.InitUI()
        #self.Bind(wx.EVT_SCROLLWIN, self.OnScroll, self)
        self.Bind(wx.EVT_SIZE, self.OnSize, self)


    def InitUI(self):
        vgap = 0
        hgap = 0
        
        self.rowList = []

        self.n = 0
        
        self.scrollSizer = wx.GridBagSizer(vgap + 10, hgap + 10)    

        self.row = self.CreateNewRow(self.n)

        self.rowList.append(self.row)

        self.scrollSizer.Add(self.row[0], pos = (self.n, 0), flag = wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.scrollSizer.Add(self.row[1], pos = (self.n, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)

        self.scrollSizer.AddGrowableCol(1)
        self.SetSizer(self.scrollSizer)

        self.panelSizer = wx.GridBagSizer(vgap, hgap)
        self.panelSizer.AddGrowableRow(0)
        self.panelSizer.AddGrowableCol(0)
        self.panelSizer.Add(self, pos = (0, 0), flag = wx.EXPAND, border = 0) # Add wx.Window not wx.Sizer
        self.parent.SetSizer(self.panelSizer)


    def CreateNewRow(self, number):
        i = number
        self.txtStr = "%d" % (i+1)
        self.staticText = wx.StaticText(self, wx.ID_ANY, self.txtStr)
                        #pos = (x, y)
        #self.staticText.SetForegroundColour(wx.Colour(0,0,0))

        self.control = wx.TextCtrl(self, i)
        self.control.SetMaxLength(256)
        self.history_length = 0
        self.control.Bind(wx.EVT_TEXT, self.OnKeyTyped, id = i)
        #self.control = wx.TextCtrl(self, -1, pos = (x + w + 5,y) )
                        #style = wx.TE_MULTILINE
        elems = [self.staticText, self.control]
        
        return elems


    def OnSize(self, e):
        self.width, self.height = e.GetSize()
        self.SetSize((self.width, self.height))
        self.OnSizeChange()


    def OnSizeChange(self):
        # Hide the sizer
        self.Show(False)
        # Fit child elements
        self.scrollSizer.FitInside(self)
        # Fit element
        self.FitInside()
        # Resize layout
        self.Layout()
        # Show the sizer
        self.Show(True)
        self.Refresh()


    def scrollToBottom(self):
        #self.lastScrolledPanelChild = self.GetChildren()[-1] # [ scrollPanel ]
        #self.ScrollChildIntoView(self.lastScrolledPanelChild)
        self.scrollRange = self.GetScrollRange(wx.VERTICAL)
        self.scrollUnits = self.GetScrollPixelsPerUnit()
        self.scrollThumb = self.GetScrollThumb(wx.VERTICAL)
        self.Scroll(0, self.scrollRange)


    def OnKeyTyped(self, e):
        # The latest row only is bound. If the len is zero it is empty and should be deleted and the new last row rebound.
        # If the len is greater than zero it is not empty and a new row should be created and bound. The second last row should be unbound.
        self.current_length = len(e.GetString())
        if (len(self.rowList) > 0 and self.history_length >= 0 and self.current_length == 0):
            # If the row was previously not empty and is now empty remove the current row and rebind the new last row
            #self.rowList[-1][1].Bind(wx.EVT_TEXT, None, id = self.n) # Unbind the last text control  
            self.rowList[-1].pop()                                   # Remove the last row from the array
            self.rowList[-1][0].Destroy()                            # Destroy the last static text object
            self.rowList[-1][1].Destroy()                            # Destroy the last text control object
            self.n -= 1                                              # Take one off the index
            self.rowList[-1][1].Bind(wx.EVT_TEXT, self.OnKeyTyped, id = self.n) # Bind the new last text control
        elif (self.current_length > 0):
            # If the row is currently not empty then make a new row, bind it, and unbind the second last row
            self.n += 1
            self.row = self.CreateNewRow(self.n) # Create and bind the new row
            self.rowList.append(self.row)
            # Add the row to the sizer in the scrolledPanel
            self.scrollSizer.Add(self.row[0], pos = (self.n, 0), flag = wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, border = 10)
            self.scrollSizer.Add(self.row[1], pos = (self.n, 1), flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL , border = 10)
            # Unbind the second last row
            self.rowList[self.n-1][1].Bind(wx.EVT_TEXT, None, id = self.n-1)
            #self.rowList[-1][1].SetFocus() # this is very bad when you want to type more than one letter into a text ctrl :P
        else:
            pass
        #print(f"History length: {self.history_length}")
        #print(f"Current length: {self.current_length}")
        self.OnSizeChange()
        self.history_length = self.current_length
        wx.CallAfter(self.scrollToBottom)


def alignToMiddleTop(window):
    dw, dh = wx.GetDisplaySize()
    dx, dy = window.GetSize()
    x = dw/2 - dx/2
    if (dy == dh):
        y = 0
    else:
        y = 100
    window.SetPosition((int(x), int(y)))


def getScreenSize():
    width, height = wx.GetDisplaySize()
    dims = ((width, height))
    return dims


def main():
    app = wx.App(False)
    app.locale = wx.Locale(wx.Locale.GetSystemLanguage())
    frame = MyMainFrame()
    panel = MyPanel(frame)
    scrolledPanel = MyScrolledPanel(panel)
    frame.SetSize(MyMainFrame.width,MyMainFrame.height)
    alignToMiddleTop(frame)
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main()


# TODO : make user screen with profile, save directory
# TODO : Settings : set save directory
# TODO : user login
# TODO : SHA-256 password encryption
# TODO : MEGA : setup and CRUD external database