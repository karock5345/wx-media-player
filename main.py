import wx
import wx.media
import os

class VideoPlayer(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Video Player', size=(800, 600))
        self.panel = wx.Panel(self)
        
        # Create media control
        try:
            self.media_ctrl = wx.media.MediaCtrl(self.panel)
        except NotImplementedError:
            wx.MessageBox("Media playback not supported on this platform", "Error")
            self.Destroy()
            return

        # Create buttons
        self.open_btn = wx.Button(self.panel, label='Open File')
        self.play_btn = wx.Button(self.panel, label='Play')
        self.stop_btn = wx.Button(self.panel, label='Stop')
        self.mute_btn = wx.Button(self.panel, label='Mute')
        
        # Create progress slider
        self.progress = wx.Slider(self.panel, value=0, minValue=0, maxValue=1000)
        
        # Create volume slider
        self.volume = wx.Slider(self.panel, value=100, minValue=0, maxValue=100, 
                              style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        
        # Create sizers for layout
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        control_sizer.Add(self.open_btn, 0, wx.ALL, 5)
        control_sizer.Add(self.play_btn, 0, wx.ALL, 5)
        control_sizer.Add(self.stop_btn, 0, wx.ALL, 5)
        control_sizer.Add(self.mute_btn, 0, wx.ALL, 5)
        control_sizer.Add(wx.StaticText(self.panel, label="Volume:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        control_sizer.Add(self.volume, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.media_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(control_sizer, 0, wx.EXPAND)
        
        self.panel.SetSizer(main_sizer)
        
        # Bind events
        self.open_btn.Bind(wx.EVT_BUTTON, self.on_open)
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_pause)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.mute_btn.Bind(wx.EVT_BUTTON, self.on_mute)
        self.progress.Bind(wx.EVT_SLIDER, self.on_seek)
        self.volume.Bind(wx.EVT_SLIDER, self.on_volume)
        
        # Timer for updating progress
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        
        self.is_playing = False
        self.is_muted = False
        self.previous_volume = 100  # Store volume level before muting
        self.filename = None
        
        # Center the frame
        self.Center()
        
    def on_open(self, event):
        """Handle opening video file"""
        dlg = wx.FileDialog(
            self, 
            "Choose a video file", 
            wildcard="Video files (*.mp4;*.avi;*.mkv)|*.mp4;*.avi;*.mkv|All files (*.*)|*.*",
            style=wx.FD_OPEN
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            if self.media_ctrl.Load(self.filename):
                self.stop_btn.Enable()
                self.play_btn.Enable()
                self.mute_btn.Enable()
                self.volume.Enable()
                self.progress.SetValue(0)
                self.timer.Start(100)  # Update every 100ms
            else:
                wx.MessageBox("Unable to load the file", "Error")
        dlg.Destroy()

    def on_play_pause(self, event):
        """Handle play/pause button"""
        if not self.filename:
            return
            
        if not self.is_playing:
            if self.media_ctrl.Play():
                self.play_btn.SetLabel('Pause')
                self.is_playing = True
        else:
            self.media_ctrl.Pause()
            self.play_btn.SetLabel('Play')
            self.is_playing = False

    def on_stop(self, event):
        """Handle stop button"""
        if self.media_ctrl.GetState() != wx.media.MEDIASTATE_STOPPED:
            self.media_ctrl.Stop()
            self.play_btn.SetLabel('Play')
            self.is_playing = False
            self.progress.SetValue(0)

    def on_mute(self, event):
        """Handle mute button"""
        if not self.filename:
            return
            
        if not self.is_muted:
            self.previous_volume = self.volume.GetValue()
            self.media_ctrl.SetVolume(0)
            self.mute_btn.SetLabel('Unmute')
            self.is_muted = True
        else:
            self.media_ctrl.SetVolume(self.previous_volume / 100.0)
            self.mute_btn.SetLabel('Mute')
            self.is_muted = False

    def on_seek(self, event):
        """Handle progress slider movement"""
        if self.filename and self.media_ctrl.GetState() != wx.media.MEDIASTATE_STOPPED:
            position = self.progress.GetValue()
            length = self.media_ctrl.Length()
            new_pos = (position * length) // 1000
            self.media_ctrl.Seek(new_pos)

    def on_volume(self, event):
        """Handle volume changes"""
        if self.filename and not self.is_muted:
            volume = self.volume.GetValue() / 100.0  # Convert to 0.0-1.0 scale
            self.media_ctrl.SetVolume(volume)

    def on_timer(self, event):
        """Update progress bar"""
        if self.is_playing and self.media_ctrl.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.media_ctrl.Length()
            position = self.media_ctrl.Tell()
            if length > 0:
                slider_pos = (position * 1000) // length
                self.progress.SetValue(slider_pos)
            if position >= length:
                self.on_stop(None)

    def Destroy(self):
        """Clean up before closing"""
        self.timer.Stop()
        return super().Destroy()

def play_video():
    app = wx.App()
    frame = VideoPlayer()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    play_video()