import configparser
import importlib
import json
import os
import platform
import pytube
# import PySimpleGUI as sg
import random
import re
# import ssl
import sys
import threading
import time
import yt_dlp

# ssl._create_default_https_content = ssl._create_stdlib_context


class Config:
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._configfile = "config.ini"
        if not os.path.exists(self._configfile):
            self._config.add_section("config")
            self._config.set("config", "font", "Noto Sans TC")
            self._config.set("config", "font-size", "10")
            self._config.set("config", "theme", "SystemDefaultForReal")
            self._config.set("config", "lang", "en")
            with open(self._configfile, "w", encoding="utf-8") as f:
                self._config.write(f)
                f.close()
        self._config.read(self._configfile)
    
    def get(self, option):
        try:
            return self._config.get("config", option)
        except ValueError:
            return None


class Lang:
    def __init__(self):
        self._lang_file_en = "./lang/en.json"
        self._lang_file_zh_tw = "./lang/zh_tw.json"
        self._lang_file_zh_cn = "./lang/zh_cn.json"
        with open(self._lang_file_en, "r", encoding="utf-8") as f:
            self.lang_en = json.load(f)
            f.close()
        with open(self._lang_file_zh_tw, "r", encoding="utf-8") as f:
            self.lang_zh_tw = json.load(f)
            f.close()
        with open(self._lang_file_zh_cn, "r", encoding="utf-8") as f:
            self._lang_zh_cn = json.load(f)
            f.close()
    
    def get(self, option):
        if option == "zh_tw":
            return self.lang_zh_tw
        elif option == "en":
            return self.lang_en
        elif option == "zh_cn":
            return self._lang_zh_cn
        else:
            raise ValueError(f"The option: {option} is not supported")


class System:
    def __init__(self):
        self._system = None

    def detect(self):
        if platform.system() == "Windows":
            if sys.getwindowsversion().build >= 22000:
                self._system = "Win11"
            else:
                self._system = "Win"
    
    def in_port(self):
        if self._system == "Win11":
            import PySimpleGUIWx as sg
        else:
            import PySimpleGUI as sg
        return sg
    
    @staticmethod
    def version():
        if importlib.util.find_spec("PySimpleGUIWx"):
            return "wx"
        else:
            return "tk"


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
            yt.streams.filter(only_audio=True).first().download(filename=f"{title}.mp3")
            self._latest = title
        elif extension == "webm":
            os.chdir(self._working_path["a"])
            ytd = yt_dlp.YoutubeDL({"format": "251"})
            v_dict = ytd.extract_info(link)
            title = f"{v_dict.get('title', None)} [{v_dict.get('id', None)}].webm"
            self._latest = title
        elif extension == "m4a":
            os.chdir(self._working_path["a"])
            ytd = yt_dlp.YoutubeDL({"format": "140"})
            v_dict = ytd.extract_info(link)
            title = f"{v_dict.get('title', None)} [{v_dict.get('id', None)}].m4a"
            self._latest = title
        else:
            os.chdir(self._working_path["v"])
            title = title + ".mp4"
            yt.streams.filter().get_highest_resolution().download(filename=f"{title}")
            self._latest = title

    def get(self):
        return self._latest


class UI:
    def __init__(self, font, theme):
        sg.theme(theme)
        self._font = font
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
                [sg.Text(f"{lang['main.link']}:", font=self._font),
                 sg.InputText(key="-link-", font=self._font)],

                [sg.Text("")],

                [sg.Text(f"{lang['main.format']}: ", font=self._font),
                 sg.Combo(values=("mp4", "webm", "m4a", "mp3"), font=self._font, default_value="mp4", key="-format-")],

                [sg.Button(lang['main.submit'], font=self._font, key="-submit-")]
            ]

            self.window = sg.Window("PyYTDownloader", self._main_layout, finalize=True, icon="youtube.png")
            return self.window
        elif arg == "dl":
            self._progress = [
                [sg.ProgressBar(100, orientation="h", size=(20, 20), key="-progress-")]
            ]
            self._dl_layout = [
                [sg.Frame(lang['progress.progress'], self._progress)],

                [sg.Button(lang['progress.start'], key="-start-", font=self._font),
                 sg.Button(lang['progress.open'], disabled=True, key="-open-", font=self._font),
                 sg.Cancel(lang['progress.cancel'], key="-cancel-", font=self._font)]
            ]

            self.dl = sg.Window(lang['progress.title'],
                                self._dl_layout,
                                finalize=True,
                                icon="youtube.png")
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
                if self._link and self._extension:
                    break
                else:
                    if not self._link:
                        sg.popup(lang["error.link.empty"], button_color="#FFFFFF", font=font)
                    elif not self._extension:
                        sg.popup(lang["error.format.empty"], button_color="#FFFFFF", font=font)
        window.close()
        self.window = None
        self.make_win("dl")
        self.subloop()

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
                    progressbar.Update(0)
                    for i in range(100):
                        progressbar.UpdateBar(i + 1)
                        time.sleep(random.choice((.01, .02, .03, .04, .05, .06, .07, .08, .09, .1)))
                except Exception as e:
                    progressbar.update(0)
                    sg.popup(f"{lang['error.occurred']}\n{e}", font=font)
                else:
                    progressbar.update(100)
                    window["-open-"].update(disabled=False)
                    window["-cancel-"].update(lang["progress.exit"])
            if event == "-open-":
                try:
                    os.startfile(downloader.get())
                except TypeError as e:
                    sg.popup(f"{lang['error.occurred']}\n{e}", font=font)
                finally:
                    break
        window.close()
        self.dl = None
        self.make_win("main")
        self.mainloop()


if __name__ == "__main__":
    system = System()
    system.detect()
    sg = system.in_port()
    sg_ver = system.version()
    
    config = Config()
    font = (str(config.get("font")), int(config.get("font-size")))
    theme = config.get("theme")
    current_lang = config.get("lang")
    
    lang = Lang()
    lang = lang.get(current_lang)
    
    downloader = Downloader()

    ui = UI(font, theme)
    ui.make_win("main")
    ui.mainloop()
