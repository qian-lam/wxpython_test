import wx
import wx.lib.agw.customtreectrl as CT
import wx.lib.scrolledpanel as scrolled


# Custom panel for editing lists dynamically.
class ListEditorPanel(wx.Panel):
    def __init__(self, parent, initial_list=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # Store each entry as a tuple: (entry_panel, text_ctrl)
        self.entries = []
        
        # Sizer that holds the entry widgets.
        self.entries_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.entries_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Button to add new entries.
        self.add_button = wx.Button(self, label="Add Entry")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_entry)
        self.sizer.Add(self.add_button, 0, wx.ALL, 5)
        
        self.SetSizer(self.sizer)
        
        if initial_list:
            for value in initial_list:
                self.add_entry(value)
    
    def add_entry(self, value=""):
        # Each entry consists of a text control and a remove button.
        entry_panel = wx.Panel(self)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        text_ctrl = wx.TextCtrl(entry_panel, value=value)
        remove_button = wx.Button(entry_panel, label="Remove", size=(70, -1))
        remove_button.Bind(wx.EVT_BUTTON, lambda evt, ep=entry_panel: self.on_remove_entry(evt, ep))
        hsizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 2)
        hsizer.Add(remove_button, 0, wx.ALL, 2)
        entry_panel.SetSizer(hsizer)
        self.entries_sizer.Add(entry_panel, 0, wx.EXPAND)
        self.entries.append((entry_panel, text_ctrl))
        self.Layout()
        self.GetParent().Layout()
    
    def on_add_entry(self, event):
        self.add_entry()
    
    def on_remove_entry(self, event, entry_panel):
        for (panel, text_ctrl) in self.entries:
            if panel == entry_panel:
                self.entries_sizer.Hide(panel)
                self.entries_sizer.Remove(panel)
                self.entries.remove((panel, text_ctrl))
                panel.Destroy()
                break
        self.Layout()
        self.GetParent().Layout()
    
    def get_values(self):
        return [text_ctrl.GetValue() for (_, text_ctrl) in self.entries]


# Define your Level and Transmitter classes
class Level:
    def __init__(self, name: str, primary_valve: list, plc_addr: list, min: int, max: int, forced_value: int, forced: bool, 
                 LL_sensor_value: int, LL_sensor_address: list, LL_NC: bool, L_sensor_value: int,
                 L_sensor_address: list, L_NC: bool, M_sensor_value: int, M_sensor_address: list, M_NC: bool,
                 MH_sensor_value: int, MH_sensor_address: list, MH_NC: bool, H_sensor_value: int, H_sensor_address: list,
                 H_NC: bool, HH_sensor_value: int, HH_sensor_address: list, HH_NC: bool):
        self.name = name
        self.primary_valve = primary_valve
        self.plc_addr = plc_addr
        self.min = min
        self.max = max
        self.forced_value = forced_value
        self.force_enable = forced
        self.LL_sensor_value = LL_sensor_value
        self.LL_sensor_address = LL_sensor_address
        self.LL_NC = LL_NC
        self.L_sensor_value = L_sensor_value
        self.L_sensor_address = L_sensor_address
        self.L_NC = L_NC
        self.M_sensor_value = M_sensor_value
        self.M_sensor_address = M_sensor_address
        self.M_NC = M_NC
        self.MH_sensor_value = MH_sensor_value
        self.MH_sensor_address = MH_sensor_address
        self.MH_NC = MH_NC
        self.H_sensor_value = H_sensor_value
        self.H_sensor_address = H_sensor_address
        self.H_NC = H_NC
        self.HH_sensor_value = HH_sensor_value
        self.HH_sensor_address = HH_sensor_address
        self.HH_NC = HH_NC
        self.value = 0

class Transmitter:
    def __init__(self, name: str, primary: list):
        self.name = name
        self.primary_valve = primary

# Main configuration frame with a split window.
class ConfigFrame(wx.Frame):
    def __init__(self, parent, title):
        super(ConfigFrame, self).__init__(parent, title=title, size=(800, 600))
        
        # Create a splitter window for left (tree) and right (configuration) panels
        self.splitter = wx.SplitterWindow(self)
        self.leftPanel = wx.Panel(self.splitter)
        # Use a scrolled panel for the right side
        self.rightPanel = scrolled.ScrolledPanel(self.splitter, style=wx.TAB_TRAVERSAL)
        self.rightPanel.SetupScrolling()

        self.splitter.SplitVertically(self.leftPanel, self.rightPanel, 250)

        self.create_left_panel()
        self.create_right_panel()

        self.Centre()
        self.Show()

    def create_left_panel(self):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        # Use CustomTreeCtrl for a modern tree view.
        self.tree = CT.CustomTreeCtrl(self.leftPanel, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        # Create a hidden root node and two child nodes.
        root = self.tree.AddRoot("Root")
        self.level_node = self.tree.AppendItem(root, "Level")
        self.transmitter_node = self.tree.AppendItem(root, "Transmitter")
        self.tree.ExpandAll()

        # Bind the tree selection event to update the right panel.
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)
        left_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 5)
        self.leftPanel.SetSizer(left_sizer)

    def create_right_panel(self):
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.rightPanel.SetSizer(self.right_sizer)
        # Add a default message.
        self.show_default_message()

    def show_default_message(self):
        self.clear_right_panel()
        default_text = wx.StaticText(self.rightPanel, label="Select an option from the left panel.")
        self.right_sizer.Add(default_text, 0, wx.ALL, 10)
        self.rightPanel.Layout()
        self.rightPanel.SetupScrolling()

    def clear_right_panel(self):
        # Remove all child widgets from the right panel.
        for child in self.rightPanel.GetChildren():
            child.Destroy()
        self.rightPanel.Layout()

    def on_tree_selection(self, event):
        item = event.GetItem()
        label = self.tree.GetItemText(item)
        self.clear_right_panel()
        if label == "Level":
            self.show_level_configuration()
        elif label == "Transmitter":
            self.show_transmitter_configuration()
        else:
            self.show_default_message()

    def show_level_configuration(self):
        panel = self.rightPanel
        grid = wx.FlexGridSizer(rows=0, cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)

        # Define Level settings along with their type.
        fields = [
            ("name", "str"),
            ("primary_valve", "list"),
            ("plc_addr", "list"),
            ("min", "int"),
            ("max", "int"),
            ("forced_value", "int"),
            ("force_enable", "bool"),
            ("LL_sensor_value", "int"),
            ("LL_sensor_address", "list"),
            ("LL_NC", "bool"),
            ("L_sensor_value", "int"),
            ("L_sensor_address", "list"),
            ("L_NC", "bool"),
            ("M_sensor_value", "int"),
            ("M_sensor_address", "list"),
            ("M_NC", "bool"),
            ("MH_sensor_value", "int"),
            ("MH_sensor_address", "list"),
            ("MH_NC", "bool"),
            ("H_sensor_value", "int"),
            ("H_sensor_address", "list"),
            ("H_NC", "bool"),
            ("HH_sensor_value", "int"),
            ("HH_sensor_address", "list"),
            ("HH_NC", "bool")
        ]

        self.level_controls = {}
        for field, field_type in fields:
            lbl = wx.StaticText(panel, label=field)
            if field_type == "bool":
                ctrl = wx.CheckBox(panel)
            elif field_type == "list":
                ctrl = ListEditorPanel(panel)
            else:
                ctrl = wx.TextCtrl(panel)
            self.level_controls[field] = ctrl
            grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(ctrl, 1, wx.EXPAND)

        self.right_sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 10)
        panel.Layout()
        panel.SetupScrolling()

    def show_transmitter_configuration(self):
        panel = self.rightPanel
        grid = wx.FlexGridSizer(rows=0, cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)

        # Define Transmitter settings.
        fields = [
            ("name", "str"),
            ("primary_valve", "list")
        ]

        self.transmitter_controls = {}
        for field, field_type in fields:
            lbl = wx.StaticText(panel, label=field)
            if field_type == "list":
                ctrl = ListEditorPanel(panel)
            else:
                ctrl = wx.TextCtrl(panel)
            self.transmitter_controls[field] = ctrl
            grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(ctrl, 1, wx.EXPAND)

        self.right_sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 10)
        panel.Layout()
        panel.SetupScrolling()

# Application entry point.
class ConfigApp(wx.App):
    def OnInit(self):
        self.frame = ConfigFrame(None, "Transmitter and Level Configuration")
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = ConfigApp(False)
    app.MainLoop()
