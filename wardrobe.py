import wx
from PIL import  Image, ImageDraw, ImageFont
import time
from rembg import remove, new_session
from wx.lib.inspection import InspectionTool
import os
import wx.adv as adv
import threading
import psycopg2
connection = psycopg2.connect(dbname="Digital Wardrobe", user="postgres", password="chinenye_onyeka@2009", host="localhost", port=5432)

class DigitalFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Digital Clothing Planner", size=(800, 600))
        self.panel = DigitalPanel(self)
        self.Show()
       
#PARENT PANEL
class DigitalPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor = connection.cursor()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sixer = wx.BoxSizer(wx.HORIZONTAL)
        top_bar_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        side_panel_sixer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel_sizer = wx.BoxSizer(wx.VERTICAL)
       

        top_bar = wx.Panel(self)
        top_bar.SetBackgroundColour("violet")
        top_bar.SetMinSize((-1, 50))
        self.search_text = wx.TextCtrl(top_bar, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.search_text.SetHint("Search Wardrobe")
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.on_search_enter)
        self.config = wx.Config("Digital Clothing Planner")
        self.audio_enabled = self.config.ReadBool("audio_enabled", True)
        sound_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sounds", "click2.wav")
        self.click_sound = None
        if os.path.exists(sound_folder):
            sounds = adv.Sound(sound_folder)
            if sounds.IsOk():
                self.click_sound = sounds
        
        wardrobe_button = wx.Button(top_bar, label="Setting")
        wardrobe_button.Bind(wx.EVT_BUTTON, self.change_audio)

        upload_button = wx.Button(top_bar, label="+Upload")
        upload_button.Bind(wx.EVT_BUTTON, self.on_click)



        body_panel = wx.Panel(self)
        body_panel.SetBackgroundColour("grey")
        side_panel = wx.Panel(body_panel)
        side_panel.SetBackgroundColour(wx.Colour("#E6D2FF"))
        side_panel.SetMinSize((80, -1))
        side_button = wx.Button(side_panel, label="Canvas")
        side_button.Bind(wx.EVT_BUTTON, self.on_click, side_button)
        ward_button = wx.Button(side_panel, label="Wardrobe")
        ward_button.Bind(wx.EVT_BUTTON, self.on_click,ward_button)
        cal_btn = wx.Button(side_panel, label="Calendar")
        cal_btn.Bind(wx.EVT_BUTTON, self.on_click,cal_btn)
        rec_btn = wx.Button(side_panel, label="Recents")
        rec_btn.Bind(wx.EVT_BUTTON, self.on_click, rec_btn)
        self.content_panel = wx.Panel(body_panel)
        self.content_panel.SetBackgroundColour("light grey")
        self.canvas_page = CanvasPage(self.content_panel)
        self.wardrobe_page = WardrobePage(self.content_panel, self.canvas_page)
        self.wardrobe_page.search_text = self.search_text
        self.calendar_page = CalendarPage(self.content_panel)
        self.recent_page = RecentsPage(self.content_panel)


        main_sizer.Add(top_bar, proportion=0, flag=wx.EXPAND)
        main_sizer.Add(body_panel, proportion=1, flag=wx.EXPAND)
        h_sixer.Add(side_panel, proportion=0, flag=wx.EXPAND)
        h_sixer.Add(self.content_panel, proportion=1, flag=wx.EXPAND)
        top_bar_hsizer.Add(self.search_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        top_bar_hsizer.Add(wardrobe_button, proportion=0, flag=wx.ALL, border=5)
        top_bar_hsizer.Add(upload_button, proportion=0, flag=wx.ALL, border=5)
        side_panel_sixer.Add(side_button, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        side_panel_sixer.Add(ward_button, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        side_panel_sixer.Add(cal_btn, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        side_panel_sixer.Add(rec_btn, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        self.homescreen = Homepage(self.content_panel)
        self.content_panel_sizer.Add(self.homescreen, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.wardrobe_page, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.canvas_page, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.calendar_page, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.recent_page, proportion=1, flag=wx.EXPAND)
        self.homescreen.Show()
        #Hides these pages on startup
        self.canvas_page.Hide()
        self.wardrobe_page.Hide()
        self.calendar_page.Hide()
        self.recent_page.Hide()

        self.content_panel.Layout()
        

        side_panel.SetSizer(side_panel_sixer)
        self.content_panel.SetSizer(self.content_panel_sizer)
        body_panel.SetSizer(h_sixer)
        top_bar.SetSizer(top_bar_hsizer)

        self.SetSizer(main_sizer)
        self.Layout()
        
    def on_click(self, event):
        button_click = event.GetEventObject().GetLabel()
        self.play_sound()
        print(f"You clicked on {button_click}")
        
        if button_click == "+Upload":
            self.canvas_page.Hide()
            self.calendar_page.Hide()
            self.recent_page.Hide()
            if hasattr (self, 'homescreen'):
                self.homescreen.Hide()
            self.wardrobe_page.Show()
            self.content_panel.Layout()
            self.wardrobe_page.connect_upload_button()
            return

        self.canvas_page.Hide()
        self.wardrobe_page.Hide()
        self.calendar_page.Hide()
        self.recent_page.Hide()
        if hasattr (self, 'homescreen'):
            self.homescreen.Hide()

        if button_click == "Canvas":
            self.canvas_page.Show()

        elif button_click == "Wardrobe":
            self.wardrobe_page.Show()

        elif button_click == "Calendar":
            self.calendar_page.Show()

        elif button_click == "Recents":
            self.recent_page.Show()
            self.recent_page.recent_wears()

        else:
            return
       
        self.content_panel.Layout()

    def change_audio(self, event):
        dlg = CustomSettings(self, self.audio_enabled )
        if dlg.ShowModal() ==  wx.ID_OK:
            self.audio_enabled = dlg.check.GetValue()
            self.config.WriteBool("audio_enabled", self.audio_enabled)
            self.config.Flush()
                    
        dlg.Destroy()

    def play_sound(self):
        if not self.audio_enabled or self.click_sound is None:
            return
        try:
            self.click_sound.Play(adv.SOUND_ASYNC)
        except Exception as e:
            print("could not play sound", e)

    def on_search_enter(self, event):
        self.homescreen.Hide()
        self.canvas_page.Hide()
        self.calendar_page.Hide()
        self.recent_page.Hide()
        self.wardrobe_page.Show()
        self.content_panel.Layout()
        self.wardrobe_page.on_search()
class Homepage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour("white")
        self.load_image()

    
    def load_image(self):
        image = wx.Image("Homepage.jpg", wx.BITMAP_TYPE_ANY)
        image = image.Scale(700, 600, quality=wx.IMAGE_QUALITY_HIGH)
        self.image_ctrl = wx.StaticBitmap(self, bitmap=wx.Bitmap(image))
        welcome_text = wx.StaticText(self, label="Welcome To Your Wardrobe!")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        welcome_text.SetFont(font)

        home_sizer = wx.BoxSizer(wx.VERTICAL)
        home_sizer.AddStretchSpacer(1)
        home_sizer.Add(self.image_ctrl, 1, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        home_sizer.Add(welcome_text, 0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.SetSizer(home_sizer)





#FOR CREATING CANVAS AREA
class CanvasPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour("#D8B4FE"))
        canvas_text = wx.StaticText(self, label="Outfit Canvas")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        canvas_text.SetFont(font)
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer.Add(canvas_text, proportion=0,flag=wx.ALIGN_CENTER, border=5)
        self.SetSizer(canvas_sizer)

        self.canvas_board = wx.Panel(self)
        self.canvas_board.SetBackgroundColour("white")
        canvas_sizer.Add(self.canvas_board, proportion=1, flag=wx.ALL | wx.EXPAND, border=20)
        self.canvas_board.Bind(wx.EVT_RIGHT_DOWN, self.remove_outfit_canvas)
    

        self.smooth_item = None
        self.drag_x = 0
        self.drag_y = 0

        self.canvas_items = []
        self.canvas_board.Bind(wx.EVT_PAINT, self.on_paint)
        
            
        self.canvas_board.Bind(wx.EVT_LEFT_DOWN, self.left_down)
        self.canvas_board.Bind(wx.EVT_MOTION, self.on_move)
        self.canvas_board.Bind(wx.EVT_LEFT_UP, self.left_up)
    def add_images_canvas(self, image_path):
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(100, 100, quality=wx.IMAGE_QUALITY_HIGH)
                
        test_img = wx.Bitmap(img)
        self.canvas_items.append((test_img, 50, 50))
        self.canvas_board.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas_board)
        #dc.SetBackgroundColor("grey")

        for Bitmap, x, y in self.canvas_items:
            dc.DrawBitmap(bitmap=Bitmap, x=x, y=y)
#for freeform movement of objects
    def left_down(self, event):
        pos = event.GetPosition()
        #the loop = so if images overlap, you grab the top one
        for item in reversed(self.canvas_items):
            bitmap, x, y = item
            w = bitmap.GetWidth()
            h = bitmap.GetHeight()
        # To check if the click is inside the box
            if x <= pos.x <= x + w and y <= pos.y <= y + h:
                self.smooth_item = item
                self.drag_x = pos.x - x
                self.drag_y = pos.y - y
                break 

    def on_move(self, event):
        pos = event.GetPosition()
        if event.Dragging() and self.smooth_item is not None:
            bitmap, _, _ = self.smooth_item
            new_x = pos.x - self.drag_x
            new_y = pos.y - self.drag_y
            new_item = (bitmap, new_x, new_y)
            idx = self.canvas_items.index(self.smooth_item)
            self.canvas_items[idx] = new_item
            self.smooth_item = new_item

            self.canvas_board.Refresh()

    def left_up(self, event):
        self.smooth_item = None

    def remove_outfit_canvas(self, event):
        response = wx.MessageBox(message="Confirm delete?", caption="Confirm Removal", style=wx.YES_NO | wx.ICON_WARNING)
        if response == wx.YES:
            move_x, move_y = event.GetPosition()

            for item in self.canvas_items:
                img, x, y = item
                width = img.GetWidth()
                height = img.GetHeight()

                if x <= move_x <= (x + width) and y <= move_y <= (y + height):
                    self.canvas_items.remove(item)
                    self.canvas_board.Refresh()
                    break 
        else:
            return




class WardrobePage(wx.Panel):
    def __init__(self, parent, canvas_page):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.canvas_page = canvas_page
        self.SetBackgroundColour(wx.Colour("#4A0E17"))
        wardrobe_text = wx.StaticText(self, label="Clothing Closet")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        wardrobe_text.SetFont(font)
        wardrobe_text.SetForegroundColour(wx.Colour("#FFFFFF"))
        wardobe_sizer = wx.BoxSizer(wx.VERTICAL)
        self.w_sizer = wx.WrapSizer(wx.HORIZONTAL, flags=0)
        cat_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #created on the first upload so that it can be reused
        self.rembg_session = None
        self.rembg_lock = threading.Lock()
        threading.Thread(target=self.load_rembg, daemon=True).start()
        #stops a second upload while one is still running
        self.uploading = False
        #for isbusy function
        self.busy = None
        
        cat_button = wx.Button(self, label="All")
        cat_button.Bind(wx.EVT_BUTTON, self.on_category)
        t_button = wx.Button(self, label="Tops")
        t_button.Bind(wx.EVT_BUTTON, self.on_category)
        b_button = wx.Button(self, label="Bottoms")
        b_button.Bind(wx.EVT_BUTTON, self.on_category)
        s_button = wx.Button(self, label="Shoes")
        s_button.Bind(wx.EVT_BUTTON, self.on_category)
        A_button = wx.Button(self, label="Accessories")
        A_button.Bind(wx.EVT_BUTTON, self.on_category)
        
        wardobe_sizer.Add(wardrobe_text, proportion=0,flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(wardobe_sizer)
        cat_sizer.Add(cat_button, proportion=0, flag=wx.ALL, border=5)
        cat_sizer.Add(t_button, proportion=0, flag=wx.ALL, border=5)
        cat_sizer.Add(b_button, proportion=0, flag=wx.ALL, border=5)
        cat_sizer.Add(s_button, proportion=0, flag=wx.ALL, border=5)
        cat_sizer.Add(A_button, proportion=0, flag=wx.ALL, border=5)
        wardobe_sizer.Add(cat_sizer, proportion=0, flag=wx.ALL, border=5)
       
        
        # to make sure wardrobe never rus out of space
        self.scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL)
        wardobe_sizer.Add(self.scrolled, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.scrolled.SetScrollRate(5, 5)
        self.scrolled.SetSizer(self.w_sizer)

        self.cursor.execute("""SELECT id, name, category, image_path  FROM wardrobe""")
        self.display_cat_items(self.cursor.fetchall())
        self.w_sizer.Layout()
        self.scrolled.FitInside()
       
        self.Layout()

    def add_clothing(self, image_path, label_text):
        cloth = wx.Image(image_path, wx.BITMAP_TYPE_ANY)                
        if not cloth.IsOk():
            print(f"failed to return {image_path}")
            return 
        image_bg = self.scrolled.GetBackgroundColour()
        card = wx.Panel(self.scrolled)
        card.SetBackgroundColour(image_bg)
        card.SetMinSize((150, 190))
        card.SetMaxSize((150, 190))
        cloth_sizer = wx.BoxSizer(wx.VERTICAL)

        ratio = min(120 / cloth.GetWidth(), 120/cloth.GetHeight())
        new_w = max(1, int(cloth.GetWidth() * ratio))
        new_h = max(1, int(cloth.GetHeight() * ratio))
        cloth = cloth.Scale(new_w, new_h, quality=wx.IMAGE_QUALITY_HIGH)
        cloth_img = wx.Bitmap(cloth)
        btp_item = wx.StaticBitmap(card, bitmap=cloth_img)
        btp_item.SetBackgroundColour(image_bg)
        btp_text = wx.StaticText(card, label=label_text)
        btp_text.SetBackgroundColour(image_bg)
        btp_text.SetForegroundColour(wx.Colour("#000000"))
        cloth_sizer.Add(btp_item, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        cloth_sizer.Add(btp_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL , border=5)
        self.w_sizer.Add(card, proportion=0, flag=wx.ALL, border=10)
        card.SetSizer(cloth_sizer)
        self.scrolled.Layout()


    def connect_upload_button(self):
        if self.uploading:
            return
        import_photos = "Image files (*.jpg; *.png; *.jpeg) | *.jpg; *.png; *.jpeg"
        with wx.FileDialog(self, "Choose a file", wildcard=import_photos, style=wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                #ask user for label
                dlg = wx.TextEntryDialog(self, "Enter a label: Clothing name")
                label = dlg.GetValue() if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() else "New Clothing"
                dlg.Destroy()
                #ask user for category  
                categories = ["Tops", "Bottoms", "Shoes", "Accessories"]
                cat_dlg = wx.SingleChoiceDialog(self, "Select a category:", "Category", categories)
                if cat_dlg.ShowModal() == wx.ID_OK:
                    cat_path = cat_dlg.GetStringSelection()
                else:
                    cat_dlg.Destroy()
                    return cat_dlg.Destroy()
                self.uploading = True
                self.busy = wx.BusyInfo("Removing Background currently")
                threading.Thread(target=self.upload_thread, args=(path, label, cat_path), daemon=True).start()
                
            #helps in backgrond slower tasks
    def upload_thread(self, path, label, cat_path):
        new_path = None
        error = None
        try:
            new_path = self.remove_background(path, label, cat_path)
        except Exception as e:
            error = e
        wx.CallAfter(self.upload_done, new_path, label,cat_path, error)

    def upload_done(self, new_path, label, cat_path, error):
        self.busy = None
        self.uploading = False
        if error is not None:
            return wx.MessageBox("Could not process image: {error}", "Upload Images", style=wx.OK | wx.ICON_WARNING)
        try:
            self.cursor = connection.cursor()
            self.cursor.execute("""INSERT INTO wardrobe (name, category, image_path) VALUES(%s, %s, %s)""",(label, cat_path, new_path,))
            connection.commit()
            self.cursor.close()
        except Exception as e:
            connection.rollback()
            wx.MessageBox(f"could not save to database: {e}", "Upload", wx.OK | wx.ICON_ERROR)
            return
        self.add_clothing(new_path, label)
        self.scrolled.FitInside()
        #self.scrolled.SetupScrolling()
        self.scrolled.Refresh()

    def remove_background(self, image_path, label_text, category):
        upl_image = Image.open(image_path)
        upl_image.thumbnail((512, 512))
        self.load_rembg()
        try:
            down_image = remove(upl_image, session=self.rembg_session)
        except Exception as e:
            print("rembg failed:", e)
            down_image = upl_image
        closet_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Digital Closet")
        os.makedirs(closet_folder, exist_ok=True)
        safe_name = "".join(c for c in label_text if c.isalnum or c.isspace()).rstrip().replace(" ", "_")
        picture_path = os.path.join(closet_folder, f"{safe_name}_{int(time.time())}.png")
        down_image.save(picture_path, "PNG")
        return picture_path

    def load_rembg(self):
        with self.rembg_lock:
            #create rembg sessio once and reuse it
            if self.rembg_session is None:
                self.rembg_session = new_session("u2netp")



    def on_category(self, event):
            self.cursor = connection.cursor()
            cat_click = event.GetEventObject().GetLabel()
            
            
            if cat_click == "All":
                self.cursor.execute("""SELECT id, name, category, image_path  FROM wardrobe""")
            else:
                self.cursor.execute("""SELECT id, name, category, image_path FROM wardrobe WHERE category = %s""", (cat_click,))
            
              
            rows = self.cursor.fetchall()
            self.display_cat_items(rows)
            for item in rows:
                print(item)
            
    def display_cat_items(self, rows):
        print("rows:", len(rows))
        self.w_sizer.Clear(delete_windows=True)

        for item_id, item_name, category, image_path in rows:
            #connect wardrobe to canvas   
           
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY).Scale(100, 100, quality=wx.IMAGE_QUALITY_HIGH)
            card_bitmap = wx.StaticBitmap(self.scrolled, bitmap=wx.Bitmap(img))
            card_bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event, path=image_path: self.canvas_display(path, id))
            self.w_sizer.Add(card_bitmap, proportion=0, flag=wx.ALL, border=5)

        self.w_sizer.Layout()
        self.scrolled.FitInside()
        self.scrolled.Refresh()
        
    #for connecting wardrobe to canvas
    def canvas_display(self, image_path, item_id):
        print("Canvas display called!", image_path)
        self.canvas_page.add_images_canvas(image_path)
    #search wardrobe
    def on_search(self):
        self.cursor = connection.cursor()
        query = self.search_text.GetValue().strip()
        try:
            if query:
                search_query = "%" + query + "%"
                self.cursor.execute("SELECT id, name, category, image_path FROM wardrobe WHERE name ILIKE %s OR category ILIKE %s", (search_query, search_query))
            else:
                self.cursor.execute("SELECT id, name, category, image_path FROM wardrobe")
            rows = self.cursor.fetchall()
            self.cursor.close()
            self.display_cat_items(rows)
            if query and not rows:
                wx.MessageBox("No items match search word", "Search", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            connection.rollback()
            print("no results", e)

            
       




class CalendarPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.SetBackgroundColour(wx.Colour("#C4A484"))
        self.cale_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plan_sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.hcale_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.calendar = adv.CalendarCtrl(self, id=wx.ID_ANY, date=wx.DateTime.Now(), style=adv.CAL_SHOW_HOLIDAYS | adv.CAL_SUNDAY_FIRST)
        self.calendar_text = wx.StaticText(self, label="Calendar")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        self.calendar_text.SetFont(font)
        self.cale_sizer.Add(self.calendar_text, proportion=0, flag= wx.ALL | wx.ALIGN_CENTER, border=5 )
        self.hcale_sizer.Add(self.calendar, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        self.hcale_sizer.Add(self.right_sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        self.calendar.SetMinSize((300, 300))
        self.SetSizer(self.cale_sizer)
       
        self.calendar.Bind(adv.EVT_CALENDAR_SEL_CHANGED, self.date_click)
        self.Layout()
        self.cale_panel = wx.Panel(self)
        self.cale_panel.SetBackgroundColour("white")
        self.cale_text = wx.StaticText(self, label="Planned Outfit")
        self.right_sizer.Add(self.cale_text, proportion=0, flag=wx.ALL, border=5)
        self.right_sizer.Add(self.cale_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        self.cale_sizer.Add(self.hcale_sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        self.picker_panel = wx.Panel(self)
        self.picker_panel.SetBackgroundColour("grey")
        self.picker_panel.SetMinSize((150, 150))
        self.picker_sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.cale_sizer.Add(self.picker_panel, proportion=0, flag=wx.ALL | wx.EXPAND, border=3)
        
        self.cale_panel.SetSizer(self.plan_sizer)
        self.picker_panel.SetSizer(self.picker_sizer)
        self.select_date = wx.DateTime.Now().Format("%Y-%m-%d")
        self.load_date(self.select_date)
        self.load_picker()


    def date_click(self, event):
        dates = event.GetDate()
        dates_str = dates.Format("%B-%d-%Y")
        self.select_date = dates.Format("%Y-%m-%d")
        self.calendar_text.SetLabel(f"Selected Date: {dates_str}")
        self.load_date(self.select_date)

    def load_date(self, dates_str):
        print("loading plan for:", self.select_date)
        self.plan_sizer.Clear(delete_windows=True)
        self.cursor.execute("""SELECT wardrobe.name, wardrobe.category, wardrobe.image_path, wardrobe.id FROM outfit_plans
                                INNER JOIN wardrobe ON outfit_plans.wardrobe_id = wardrobe.id
                                WHERE outfit_plans.plan_date = %s""", (dates_str,))
        rows = self.cursor.fetchall()
        if not rows:
            empty = wx.StaticText(self.cale_panel, label="Nothing Planned")
            self.plan_sizer.Add(empty, proportion=0, flag=wx.ALL, border=5)
            #view planned outfits   
        for item_name, category, image_path, item_id in rows:
            if not os.path.exists(image_path):
                print("missing image file:", image_path)
                continue
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY).Scale(100, 100, quality=wx.IMAGE_QUALITY_HIGH)
            cal_bitmap = wx.StaticBitmap(self.cale_panel, bitmap=wx.Bitmap(img))
            cal_bitmap.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.remove_outfit(item_id))
            self.plan_sizer.Add(cal_bitmap, proportion=0, flag=wx.ALL, border=5)
        self.cale_panel.Layout()
        self.Layout()
        self.Refresh()

    
    def load_picker(self):
        
        self.cursor.execute("""SELECT id, image_path  FROM wardrobe""")
        rows = self.cursor.fetchall()
        for item_id, image_path in rows:
            if not os.path.exists(image_path):
                print("missing image file:", image_path)
                continue
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY).Scale(100, 100, quality=wx.IMAGE_QUALITY_HIGH)
            pick_bitmap = wx.StaticBitmap(self.picker_panel, bitmap=wx.Bitmap(img))
            self.picker_sizer.Add(pick_bitmap, proportion=0, flag=wx.ALL, border=2)

            pick_bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event, item_id=item_id: self.add_to_cal(item_id))
            
        self.picker_panel.Layout()
        self.Layout()
        self.Refresh()

    def add_to_cal(self, item_id):
       
        try:
            self.cursor.execute("INSERT INTO outfit_plans(plan_date, wardrobe_id) VALUES(%s, %s) ON CONFLICT DO NOTHING", (self.select_date, item_id))
            connection.commit()
            self.load_date(self.select_date)
        except Exception as e:
            connection.rollback()
            print("Insertion error: couldn't save outfit", e)

    def remove_outfit(self, item_id):
        answer = wx.MessageBox(message="Confirm delete?", caption="Confirm Removal", style=wx.YES_NO | wx.ICON_WARNING)
        if answer == wx.YES:
            try:
                self.cursor.execute("DELETE FROM outfit_plans WHERE plan_date = %s AND wardrobe_id = %s", (self.select_date, item_id))
                connection.commit()
                wx.CallAfter(self.load_date, self.select_date)
                print("Item deleted")
            except Exception as e:
                connection.rollback()
                print("Insertion error: couldn't delete outfit", e)
        else:
            return
       
            



class RecentsPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.SetBackgroundColour(wx.Colour("#120817"))
        
        self.rchild_panel = wx.Panel(self)
        self.rchild_panel.SetBackgroundColour("white")
        
        
        self.r_sizer = wx.BoxSizer(wx.VERTICAL)
        self.rchild_sizer = wx.WrapSizer(wx.HORIZONTAL, 0)
        
        self.r_text = wx.StaticText(self, label="Recents")
        self.r_text.SetForegroundColour("yellow")
        self.r_sizer.Add(self.r_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        
        self.r_sizer.Add(self.rchild_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.r_sizer)
        self.rchild_panel.SetSizer(self.rchild_sizer)

    def recent_wears(self):
        self.rchild_sizer.Clear(delete_windows=True)
        
        self.cursor.execute(
                """SELECT MAX(outfit_plans.plan_date) AS worn, wardrobe.image_path, wardrobe.id FROM outfit_plans
                                INNER JOIN wardrobe ON outfit_plans.wardrobe_id = wardrobe.id
                                WHERE outfit_plans.plan_date <= CURRENT_DATE
                                GROUP BY wardrobe.id
                                ORDER BY worn DESC
                                LIMIT 10""")
        rows = self.cursor.fetchall()
        if not rows:
            self.row_text = wx.StaticText(self.rchild_panel, label="No recents yet")
            self.rchild_sizer.Add(self.row_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        for worn, image_path, item_id in rows:
            if not os.path.exists(image_path):
                print("missing image file:", image_path)
                continue
            self.image_child_panel = wx.Panel(self.rchild_panel)
            self.image_child_panel.SetBackgroundColour("white")
            self.image_child_panel.SetMinSize((200, 200))
            self.image_sizer = wx.BoxSizer(wx.VERTICAL)
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY).Scale(150, 150, quality=wx.IMAGE_QUALITY_HIGH)
            rec_bitmap = wx.StaticBitmap(self.image_child_panel, bitmap=wx.Bitmap(img))
            label_date = worn.strftime("%b %d, %Y")
            self.image_text = wx.StaticText(self.image_child_panel, label=(f"Last worn: {label_date}"))
            self.image_sizer.Add(rec_bitmap, proportion=0, flag=wx.ALL, border=5)
            self.image_sizer.Add(self.image_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
            self.image_child_panel.SetSizer(self.image_sizer)
            self.rchild_sizer.Add(self.image_child_panel, proportion=0, flag=wx.ALL, border=5)
        self.rchild_panel.Layout()
        self.Layout()
        self.Refresh()

                   
class CustomSettings(wx.Dialog):
        def __init__(self, parent, current_settings=False):
            super().__init__(parent, title="Audio Settings", size=(200, 200))
            set_sizer = wx.BoxSizer(wx.VERTICAL)
            self.current_settings = current_settings
            self.audio_enables =False
            self.check = wx.CheckBox(self, label="Enable Audio")
            self.check.SetValue(self.current_settings)
            question = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
            set_sizer.Add(self.check, proportion=0, flag=wx.ALL, border=5)
            set_sizer.Add(question, proportion=0, flag=wx.ALL, border=5)
            self.SetSizer(set_sizer)

       


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = DigitalFrame()
    app.MainLoop()

