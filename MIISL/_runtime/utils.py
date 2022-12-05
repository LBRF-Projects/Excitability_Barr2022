import os
import io
import csv

import sdl2
import sdl2.ext
import sdl2.sdlmixer as mixer


class Sound(object):
    """A class for loading and playing sound files.
    """
    def __init__(self, fileName):
        self.channel = None
        self.sample = mixer.Mix_LoadWAV(sdl2.ext.compat.byteify(fileName, "utf-8"))

    def play(self):
        self.channel = mixer.Mix_PlayChannel(-1, self.sample, 0)

    def stop(self):
        if self.channel != None:
            mixer.Mix_HaltChannel(self.channel)
            self.channel = None

    def doneYet(self):
        if self.channel == None:
            return True
        return mixer.Mix_Playing(self.channel) == 0


class DataFile(object):
    """A robust class for creating and writing to data files.

    The output file and its header are written immediately when the DataFile
    is created, and additional rows are added to the file using `write_row`.

    Each row is validated to ensure the columns match the column names defined
    in the header, avoiding issues with missing or misaligned data rows.

    Args:
        outpath (str): The path at which to create the output file.
        header (list): A list defining the names and order of columns for
            the file.
        comments (list, optional): A list of lines to append to the top of
            the file above the header. Each line will be prefixed with '# '
            so they can be easily ignored when reading in the data.
        sep (str, optional): The delimiter character to use to separate columns
            in the output file. Defaults to a single tab.

    """
    def __init__(self, outpath, header, comments=[], sep="\t"):
        self.filepath = outpath
        self.header = header
        self.comments = "\n".join(["# " + line for line in comments])
        self.sep = sep

        self._create()

    def _create(self):
        # Get header and any comments to write to top of file
        content = self.sep.join(self.header)
        if self.comments:
            content = self.comments + "\n\n" + content

        # Create new data file and write header, replacing if it already exists
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        with io.open(self.filepath, 'w+', encoding='utf-8') as out:
            out.write(sdl2.ext.compat.utf8(content + "\n"))

    def write_row(self, dat):
        """Writes a row of data to the output file.

        Args:
            dat (dict): A dictionary with fields matching each of the column
                names in the header.

        """
        # First, make sure all columns in row exist in the header
        for col in dat.keys():
            if col not in self.header:
                e = "'{0}' exists in row data but not data file header."
                raise RuntimeError(e.format(col))

        # Then, sanitize the data to make sure it's all unicode text
        out = {}
        for col in self.header:
            try:
                out[col] = sdl2.ext.compat.utf8(dat[col])
            except KeyError:
                e = "No value for column '{0}' provided."
                raise RuntimeError(e.format(col))
        
        # Finally, write the colletcted data to the file
        with io.open(self.filepath, 'a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.header, delimiter=self.sep)
            writer.writerow(out)


def init_window(fullscreen=True):
    """Sets up SDL2 and returns a window.
    """
    # Properly support HIDPI on Windows, disable minimize on focus loss
    sdl2.SDL_SetHint(b"SDL_WINDOWS_DPI_AWARENESS", b"permonitor")
    sdl2.SDL_SetHint(b"SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", b"0")

    # Initialize video and audio backends
    sdl2.ext.init(video=True, audio=True)
    mixer.Mix_Init(mixer.MIX_INIT_MP3)
    mixer.Mix_OpenAudio(44100, mixer.MIX_DEFAULT_FORMAT, 2, 1024)

    # Determine the mode and resolution for the experiment window
    display = sdl2.ext.get_displays()[0]
    mode = display.desktop_mode
    if fullscreen:
        win_flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        res = (mode.w, mode.h)
    else:
        win_flags = sdl2.SDL_WINDOW_SHOWN
        res = (1280, 720)

    # Create and show the window, hiding the mouse cursor if fullscreen
    window = sdl2.ext.Window("miisl", size=res, flags=win_flags)
    if fullscreen:
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
    sdl2.SDL_PumpEvents()

    return window

