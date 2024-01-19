from pytube import YouTube
import ssl
import os

ssl._create_default_https_content = ssl._create_stdlib_context


class user_experience():
    def __init__(self):
        global platform, sys, darkdetect
        import platform, sys, darkdetect

        self.os = platform.system()
        if self.os == "Windows":
            import sys
            if sys.getwindowsversion().build >= 22000:
                self.current_os = "Windows 11"
        if self.os == "Darwin":
            self.current_os = "MacOS"
        else:
            self.current_os = self.os
    def personalize(self):
        if self.current_os == "Windows 11":
            import PySimpleGUIWx as sg
        else:
            import PySimpleGUI as sg
        global sg

        darkmode = darkdetect.isDark()
        if darkmode:
            sg.theme("Dark")
        else:
            sg.theme("SystemDefaultForReal")



user_experience().personalize()

working_path = f"{os.path.expanduser('~')}/Videos/PyYTDownload"
if not os.path.exists(working_path):
    os.mkdir(working_path)
os.chdir(working_path)

def download(type, link: str):
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

layout = [
    [sg.Text("link:"), sg.InputText(key="-link-")],
    [sg.Combo(values=["mp4", "mp3"], default_value="mp4", key="-type-")],
    [sg.Text()],
    [sg.Button("Download")]
]

window = sg.Window("PyYTDownloader", layout, finalize=True)

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

window.close()
exit()