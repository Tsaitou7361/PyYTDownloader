import ssl
import os
import platform, sys, darkdetect
import threading
from pytube import YouTube


ssl._create_default_https_content = ssl._create_stdlib_context

# generate working path
working_path = f'{os.path.expanduser("~")}/Videos/PyYTDownload'
if not os.path.exists(working_path):
    os.mkdir(working_path)
os.chdir(working_path)

class user_experience():
    def __init__(self):
        self.sg = None
        self._os = platform.system()

        if self._os == "Windows":
            if sys.getwindowsversion().build >= 22000:
                self._current_os = "Windows 11"
        elif self._os == "Darwin":
            self._current_os = "MacOS"
        else:
            self._current_os = self._os

    def personalize(self):
        if self._current_os == "Windows 11":
            import PySimpleGUIWx as sg
        else:
            import PySimpleGUI as sg
        self.sg = sg

        darkmode = darkdetect.isDark()
        if darkmode:
            self.sg.theme("DarkGrey4")
        else:
            self.sg.theme("SystemDefaultForReal")

    def get_sg(self):
        return self.sg

class UI():
    def __init__(self, sg):
        self._sg = sg
        self._layout = [
            [sg.Text("Link"), sg.InputText(key="-link-")],
            [sg.Text("Format"), sg.Combo(values=["mp4", "mp3"], default_value="mp4", key="-type-")],
            [sg.Text()],
            [sg.Button("Download")]
        ]
        self._window = None
    def make_window(self):
        self._window = self._sg.Window("PyYTDownloader", self._layout, finalize=True)
        return self._window

    def mainloop(self):
        sg = self._sg
        window = self._window
        while True:
            event, value = window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == "Download":
                link = value["-link-"]
                download_type = value["-type-"]
                download(download_type, link)
                sg.popup("Download Completed.")
                window["-link-"].update("")
        self._window.close()

def download(type:str, link: str):
    yt = YouTube(link)
    print(f"[INFO] Download stream started. link: {link}, type: {type}")
    if type == "mp4":
        yt.streams.filter().get_highest_resolution().download()
    elif type == "mp3":
        yt.streams.filter().get_audio_only().download(filename=f"{yt.title}.mp3")
    else:
        print("[ERROR] Incorrect type")
        sg.popup_error("請選擇一個可用的格式")
    print("[INFO] Download completed")



if __name__ == "__main__":
    user_exp = user_experience()
    user_exp.personalize()
    sg = user_exp.get_sg()

    ui = UI(sg)
    window = ui.make_window()

    # mainloop = threading.Thread(target=ui.mainloop)
    # mainloop.start()
    # mainloop.join()
    ui.mainloop()
