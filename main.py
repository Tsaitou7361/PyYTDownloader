import os
# import platform
import pytube
import PySimpleGUI as sg
import random
import re
# import ssl
import sys
import threading
import time

# ssl._create_default_https_content = ssl._create_stdlib_context


class Downloader:
    def __init__(self):
        self._working_path = {
            "a": f"{os.path.expanduser('~')}/Music/PyYTDownload",
            "v": f"{os.path.expanduser('~')}/Videos/PyYTDownload"
        }
        self._latest = None
        if not os.path.exists(self._working_path["a"]):
            os.mkdir(self._working_path["a"])
        if not os.path.exists(self._working_path["v"]):
            os.mkdir(self._working_path["v"])

    def dl(self, link: str, extension: str):
        yt = pytube.YouTube(link)
        title = re.sub(r"[/\\]", "-", yt.title)    # Fix filename issue
        if extension == "mp3":
            os.chdir(self._working_path["a"])
            title = title + ".mp3"
            yt.streams.filter(only_audio=True).first().download(filename=f"{title}")
            self._latest = title
        elif extension == "wav":
            os.chdir(self._working_path["a"])
            title = title + ".wav"
            yt.streams.filter(only_audio=True).first().download(filename=f"{title}")
            self._latest = title
        else:
            os.chdir(self._working_path["v"])
            title = title + ".mp4"
            yt.streams.filter().get_highest_resolution().download(filename=f"{title}")
            self._latest = title

    def get(self):
        return self._latest


class UI:
    def __init__(self):
        sg.theme("SystemDefaultForReal")
        self._font = ("Noto Sans TC", 10)
        self._main_layout = None
        self._progress = None
        self._dl_layout = None
        self.dl = None
        self.window = None
        self._link = None
        self._extension = None

    def make_win(self, arg):
        if arg == "main":
            self._main_layout = [
                [sg.Text("連結:", font=self._font),
                 sg.InputText(key="-link-", font=self._font)],

                [sg.Text("")],

                [sg.Text("格式: ", font=self._font),
                 sg.Combo(values=("mp4", "mp3", "wav"), font=self._font, default_value="mp4", key="-format-")],

                [sg.Button("送出", font=self._font, key="-submit-")]
            ]

            self.window = sg.Window("PyYTDownloader", self._main_layout, finalize=True)
            return self.window
        elif arg == "dl":
            self._progress = [
                [sg.ProgressBar(100, orientation="h", size=(20, 20), key="-progress-")]
            ]
            self._dl_layout = [
                [sg.Frame("進度", self._progress)],

                [sg.Button("Start", key="-start-", font=self._font),
                 sg.Button("Open", disabled=True, key="-open-", font=self._font),
                 sg.Cancel()]
            ]

            self.dl = sg.Window("PyYTDownloader - 下載中", self._dl_layout, finalize=True)
            return self.dl

    def mainloop(self):
        window = self.window
        while True:
            event, value = window.read()
            if event == sg.WIN_CLOSED:
                window.close()
                sys.exit()
            if event == "-submit-":
                self._link = value["-link-"]
                self._extension = value["-format-"]
                self.make_win("dl")
                self.subloop()
                window.close()

    def subloop(self):
        window = self.dl
        progressbar = window["-progress-"]
        while True:
            event, value = window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                break
            if event == "-start-":
                try:
                    t = threading.Thread(target=downloader.dl, args=(self._link, self._extension))
                    t.start()
                    window["-start-"].update(disabled=True)
                    for i in range(99):
                        progressbar.update(i + 1)
                        time.sleep(random.choice((.01, .02, .03, .04, .05, .06, .07, .08, .09, .1)))
                except Exception as e:
                    sg.popup_error(f"發生錯誤: {e}")
                finally:
                    progressbar.update(100)
                    window["-open-"].update(disabled=False)
            if event == "-open-":
                os.startfile(downloader.get())
                break
        window.close()
        self.make_win("main")


if __name__ == "__main__":
    downloader = Downloader()

    ui = UI()
    ui.make_win("main")
    ui.mainloop()
