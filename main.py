import launchpad_py as launchpad
import time, ast, os
from pygame import mixer
import pygame, pygame_menu

mixer.init()

"""
================MENU FUNCTIONS============================
"""


def initmenu():
    """
    Returns 2 Lists:
    infolist contains a list of the info.dat files of each song as a dict
    songlist contains 'nameofsong', songdifficulties, 'folderofSong'
    :return: infoList = [song1info dict, song2infodict...]
    :return: songlist = [('songName', [('diffname', 0), ('diffname2', 0)...], 'foldername'), ...]
    """
    infolist = []
    songlist = []
    for songfolder in os.listdir('Songs'):
        file = open('Songs/{}/info.dat'.format(songfolder))
        info = ast.literal_eval(file.read())
        infolist.append(info)

        songdifs = []
        for difsets in info['_difficultyBeatmapSets']:
            if difsets['_beatmapCharacteristicName'] == 'Standard':
                for dif in difsets['_difficultyBeatmaps']:
                    songdifs.append((dif['_difficulty'],0))
        songlist.append((info['_songName'], songdifs, songfolder))

    return songlist, infolist


def main_background() -> None:
    """
    Converts cover art to the background of the menu
    :return:
    """
    background = pygame_menu.baseimage.BaseImage(image_path='Songs/{}/{}'.format(FILE[0], COVERJPG[0]))
    background.draw(surface)


def setdif(value, item):
    """
    Sets the difficulty of the level when difficulty selector is adjusted
    """
    print(value)
    DIFCHOICE[0] = value[1]
    pass


def setlevel(value, difset, file):
    """
    When Level selector is adjusted:
    Set FILE[] to correct song folder
    Set background image to correct image, reads from File[0]'s info.dat
    Updates difficulty selector with the right difficulty options
    plays a preview of the song

    :param difset: [('difficultyname', 0), ('difficultyname2', 0)...]
    :param file: String 'folderinSongs'
    :return:
    """
    FILE[0] = file
    COVERJPG[0] = infolist[value[1]]['_coverImageFilename']
    d1.update_items(difset)
    print('Filename: {}'.format(file))
    print('Diffs: {}'.format(difset))
    if mixer.music.get_busy():
        mixer.music.unload()
    mixer.music.load('Songs/{}/{}'.format(file, infolist[value[1]]['_songFilename']))
    mixer.music.play(start=infolist[value[1]]['_previewStartTime'], fade_ms= 1000)
    pass


def startsong():
    """
    When Start button triggered, clear music, start the level
    :return:
    """
    mixer.music.unload()
    print('Selection: {}\n{}'.format(FILE[0], DIFCHOICE[0]))
    playSong('Songs/{}'.format(FILE[0]), DIFCHOICE[0], lp)
    pass

"""
==============Beatsaber data Conversion functions===========
"""

def sortKeyt(e):
  return e[2]

def sortKeyb(e):
  return e[1]

"""
Sort keys used in initBeatmap for beatmap and notetime
not be needed because of how playSong() processes the notes, but may improve complexity
"""

def beatsaberConverter(folder, dif):
    """
    Looks for beatsaber notes dat from info.dat
    Beatsaber notes use a 4X3 grid, convert to 8X6 grid depending on cut direction
    Depending if it was a left hand/right hand note, create a red/blue color for each note

    Resources:
    info.dat: https://bsmg.wiki/mapping/map-format.html
    difficulty.dat: https://bsmg.wiki/mapping/map-format.html#difficulty-file

    :param folder: 'foldername'
    :param dif: int
    :return:conversion = [[x, y, time*16, r,g,b], ...]
    """
    file = open('{}/info.dat'.format(folder))               #Read info.dat to find difficulty.dat
    info = ast.literal_eval(file.read())
    noteFile1 = info['_difficultyBeatmapSets']
    noteFile = ''
    for difsets in noteFile1:
        if difsets['_beatmapCharacteristicName'] == 'Standard':
            noteFile = difsets['_difficultyBeatmaps'][dif]["_beatmapFilename"]
    file.close()

    file = open('{}/{}'.format(folder, noteFile))           #Read difficulty.dat to extract list of notes
    notes = ast.literal_eval(file.read())['_notes']
    file.close()

    conversion = []
    for i in notes:
        if i['_cutDirection'] in (1,6,7):
            ypos = (i['_lineLayer']+1)*2+2
        else:
            ypos = (i['_lineLayer']+1)*2+1
        if i['_cutDirection'] in (3,5,7):
            xpos = (i['_lineIndex'])*2+1
        else:
            xpos = (i['_lineIndex'])*2
        if i['_type'] == 0:
            r,g,b = 63,0,20
        else:
            r,g,b, = 1,10,63

        conversion.append([xpos, ypos, round(i['_time']*16,0), r,g,b])
        # Prescalar = 16, effects how early lights start glowing before the note,
        # if you change this also change it in initBeatmap() (for j in range), and playSong()(while going)

    return conversion


def initBeatmap(notemap):
    """
    Creates array for lightshow of the song (beatmap), independent of user input
    creates timing for notes(notetiming), used for checking if user input is early/late compared to note time
    :param notemap: [[xpos, ypos, round(i['_time']*16,0), r,g,b], ...]
    :return beatmap: [ [[x, y, r, g, b], time], ...]
    :return notetime: notemap (may be changed in future for complexity)

    """
    notetime = notemap
    beatmap = []

    for i in notemap:
        r = i[3]
        g = i[4]
        b = i[5]
        for j in range(16-1, 0,-1):
            """
            Determines colors leading up to the note
            """
            # Prescalar = 16, effects how early lights start glowing before the note,
            # if you change this also change it in Beatsaberconverter() (conversion.append), and playSong()(while going)
            if j > 5:
                beatmap.append([[i[0], i[1], round(r/j), round(g/j), round(b/j)], i[2]-j])
            elif j > 0:
                beatmap.append([[i[0], i[1], round(r/j), round(g/j), round(b/j)], i[2]-j])
            else:
                beatmap.append([[i[0], i[1], 0, 0, 0], i[2]-j])
            """
            Determines color of actual note
            """
            beatmap.append([[i[0], i[1], i[3], i[4], i[5]], i[2]])
            beatmap.append([[i[0], i[1], 0, 0, 0], i[2] + 1])

            #beatmap.append([[[i[0]+1, i[1], i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0]-1, i[1], i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0], i[1]+1, i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0], i[1]-j, round(63/j), round(63/j), round(63/j)]], i[2]-j-1])

            # beatmap.append([[[i[0]+j, i[1], 0, 0, 0]], i[2]+1])
            # beatmap.append([[[i[0], i[1]+j, 0, 0, 0]], i[2]+1])
            #beatmap.append([[[i[0], i[1]-j, 0, 0, 0]], i[2]+1-j])
            # beatmap.append([[[i[0]-j, i[1], 0, 0, 0]], i[2]+1])


        # beatmap.append([[[i[0]+1, i[1], 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0]-1, i[1], 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0], i[1]+1, 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0], i[1]-1, 0, 0, 0]], i[2]+1])
    for e in range(0,round(notemap[len(notemap)-1][2]), 16):
        """
        pulsing circle button colors
        """
        for k in range(0, 8):
            for f in range(0,9):
                beatmap.append([[k, 0, round(30/9*f), round(30/9*f), round(30/9*f)], e+8-f])
                #beatmap.append([[[k, 0, 0, 0, 0]], e + 8])
                #beatmap.append([[[8, k+1, 63, 63, 63]], e])
                beatmap.append([[8, k+1, round(30/9*f), round(30/9*f), round(30/9*f)], e + 8-f])

    """
    uncomment these 2 lines to use sortkeys
    """
    beatmap.sort(key=sortKeyb)
    notetime.sort(key=sortKeyt)

    #c = 0
    #stop = False
    # while stop is False:
    #     a = beatmap[c][0]
    #     if beatmap[c][1] == beatmap[c+1][1]:
    #         beatmap[c][0] = beatmap[c][0].append(beatmap[c+1][0][0])
    #         beatmap[c][0] = a
    #         del beatmap[c+1]
    #     if len(beatmap) >= c:
    #         stop = True
    #     c = c+1
    return beatmap, notetime



"""
============Level playback Options=============
"""

def initPad():
    """
    Sets up launchpad using launchpad_py
    Currently supports LaunchpadMk2(), can be edited, but may require user input troubleshooting
    :Resources: https://github.com/FMMT666/launchpad.py
    :return: Launchpad instance
    """

    if launchpad.LaunchpadMk2().Check(0):
        lp = launchpad.LaunchpadMk2()
        if lp.Open(0):
            print("Launchpad Mk2")
            mode = "Mk2"

    elif launchpad.LaunchpadMiniMk3().Check(1):
        lp = launchpad.LaunchpadMiniMk3()
        if lp.Open(1):
            print("Launchpad Mini Mk3")
            mode = "Pro"

    if mode is None:
        print("Did not find any Launchpads, meh...")

    lp.ButtonFlush()
    lp.LedCtrlString('OK', 63, 3, 63, direction=-1, waitms=0)
    return lp


def checkClose(curnotes, curbeat, x, y):
    """
    Checks if user's input is close to actual note
    :param curnotes: notes to check
    :param curbeat: User's input time
    :param x: User's input x
    :param y: User's input y
    :return: string 'rating'
    """
    for note in curnotes:
        if note[0] == x and note[1] == y:
            if curbeat - 1 <= note[2] <= curbeat + 1:
                return 'perfect'
            elif curbeat - 3 <= note[2] <= curbeat + 3:
                return 'good'
            elif curbeat - 5 <= note[2] <= curbeat + 5:
                return 'ok'
            elif curbeat - 7 <= note[2] <= curbeat + 7:
                return 'bad'
    return ''


def playSong(folder, DIFCHOICE, lp):
    """
    Main function to play the level
    Works using magic spaghetti code
    :param folder: 'songfolder'
    :param DIFCHOICE: int
    :param lp: launchpad
    :return:
    """
    restart = True
    while restart:
        notes = beatsaberConverter('Songs/{}'.format(FILE[0]), DIFCHOICE)

        file = open('{}/info.dat'.format(folder))
        info = ast.literal_eval(file.read())
        songfile = '{}/{}'.format(folder, info['_songFilename'])
        SpB = 1/(info['_beatsPerMinute']/60)
        file.close()

        lightmap, notemap = initBeatmap(notes)

        restart = False
        mixer.music.load(songfile)
        mixer.music.play()
        time.sleep(info['_songTimeOffset']/1000)

        startTime = time.perf_counter()
        going = True
        while going:
            button = lp.ButtonStateXY()
            curbeat = (time.perf_counter() - startTime)*16/SpB
            curlight = [x for x in lightmap if x[1] <= curbeat]
            curnotes = [x for x in notemap if x[2] <= curbeat+7]

            for lights in curlight:
                lp.LedCtrlXY(lights[0][0], lights[0][1], lights[0][2], lights[0][3], lights[0][4])
                lightmap.remove(lights)

            if button != []:
                """
                Checks if user presses a button
                """
                x = button[0]
                y = button[1]
                r, g, b = 0, 0, 0
                if button[2]:
                    status = checkClose(curnotes, curbeat, x, y)
                    lp.LedCtrlXY(x, y, 63, 63, 63)
                    """
                    chooses 'hit' color based on timing
                    """
                    if status == 'perfect':
                        r,g,b = 10, 17, 31
                    if status == 'good':
                        r,g,b = 7, 31, 7
                    elif status == 'ok':
                        r, g, b = 31, 30, 5
                    elif status == 'bad':
                        r, g, b = 31, 5, 5

                    lp.LedCtrlXY(x + 1, y, r, g, b)
                    lp.LedCtrlXY(x - 1, y, r, g, b)
                    lp.LedCtrlXY(x, y + 1, r, g, b)
                    lp.LedCtrlXY(x, y - 1, r, g, b)

                    if (x,y) == (8,8):      #quick stop button
                        mixer.music.unload()
                        going = False
                        lp.LedAllOn(3)
                        time.sleep(.1)
                        lp.LedAllOn(0)

                    if (x,y) == (8,7):      #quick restart button
                        mixer.music.unload()
                        going = False
                        restart = True
                        lp.LedAllOn(6)
                        time.sleep(.1)
                        lp.LedAllOn(0)

                else:
                    lp.LedCtrlXYByCode(x, y, 0)
                    lp.LedCtrlXYByCode(x + 1, y, 0)
                    lp.LedCtrlXYByCode(x - 1, y, 0)
                    lp.LedCtrlXYByCode(x, y + 1, 0)
                    lp.LedCtrlXYByCode(x, y - 1, 0)

            for n in curnotes:
                if n[2] <= curbeat - 17:
                    notemap.remove(n)
            if len(notemap) == 0:
                time.sleep(1)
                going = False
                lp.LedCtrlString('l', 63, 63, 63, direction=-1, waitms=0)
                lp.LedCtrlString('l', 63, 63, 63, direction=1, waitms=0)
                lp.LedAllOn(0)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DIFCHOICE = [0]
    FILE = ['0cb1b38c96b71676db359a95353dca50ba54b183']
    COVERJPG = ['cover.jpg']

    diffs = [('None', 0)]
    songlist, infolist = initmenu()

    pygame.init()
    surface = pygame.display.set_mode((600, 600))

    main_menu_theme = pygame_menu.themes.THEME_DARK.copy()
    main_menu_theme.set_background_color_opacity(0.4)
    main_menu_theme.widget_font=pygame_menu.font.FONT_HELVETICA

    menu = pygame_menu.Menu('Project LP', 350, 450, theme=main_menu_theme)

    menu.add.selector('Song: ', songlist, onchange=setlevel)
    d1 = menu.add.selector('Difficulty: ', diffs, onchange=setdif)
    menu.add.button('START', startsong,  shadow_width=10, shadow_color=(0, 0, 100))
    menu.add.button('Quit', pygame_menu.events.EXIT)

    pygame.display.set_caption('Project LP')

    lp = initPad()
    menu.mainloop(surface, main_background)





