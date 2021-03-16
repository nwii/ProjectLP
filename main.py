import launchpad_py as launchpad
import time, ast, os
from pygame import mixer
import pygame, pygame_menu

mixer.init()


def sortKeyt(e):
  return e[2]

def sortKeyb(e):
  return e[1]

def beatsaberConverter(folder, dif):
    file = open('{}/info.dat'.format(folder))
    info = ast.literal_eval(file.read())
    noteFile1 = info['_difficultyBeatmapSets']
    noteFile = ''
    for difsets in noteFile1:
        if difsets['_beatmapCharacteristicName'] == 'Standard':
            noteFile = difsets['_difficultyBeatmaps'][dif]["_beatmapFilename"]
    file.close()

    file = open('{}/{}'.format(folder, noteFile))
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
    return conversion


def initBeatmap(notemap):
    notetime = notemap
    beatmap = []
    for i in notemap:

        if i[3] < 0:
            r = i[3]+30
        else:
            r = i[3]
        if i[4] < 0:
            g = i[4]+30
        else:
            g = i[4]
        if i[5] < 0:
            b = i[5]+30
        else:
            b = i[5]

        for j in range(15, 0,-1):
            if j > 5:
                beatmap.append([[i[0], i[1], round(r/j), round(g/j), round(b/j)], i[2]-j])
            elif j > 0:
                beatmap.append([[i[0], i[1], round(r/j), round(g/j), round(b/j)], i[2]-j])
            else:
                beatmap.append([[i[0], i[1], 0, 0, 0], i[2]-j])

            #beatmap.append([[[i[0]+1, i[1], i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0]-1, i[1], i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0], i[1]+1, i[3], i[4]+10*j, i[5]]], i[2]-j])
            #beatmap.append([[[i[0], i[1]-j, round(63/j), round(63/j), round(63/j)]], i[2]-j-1])

            # beatmap.append([[[i[0]+j, i[1], 0, 0, 0]], i[2]+1])
            # beatmap.append([[[i[0], i[1]+j, 0, 0, 0]], i[2]+1])
            #beatmap.append([[[i[0], i[1]-j, 0, 0, 0]], i[2]+1-j])
            # beatmap.append([[[i[0]-j, i[1], 0, 0, 0]], i[2]+1])

        beatmap.append([[i[0], i[1], i[3], i[4], i[5]], i[2]])

        beatmap.append([[i[0], i[1], 0, 0, 0], i[2]+1])
        # beatmap.append([[[i[0]+1, i[1], 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0]-1, i[1], 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0], i[1]+1, 0, 0, 0]], i[2]+1])
        # beatmap.append([[[i[0], i[1]-1, 0, 0, 0]], i[2]+1])
    for e in range(0,round(notemap[len(notemap)-1][2]), 16):
        for k in range(0, 8):
            for f in range(0,9):
                beatmap.append([[k, 0, round(30/9*f), round(30/9*f), round(30/9*f)], e+8-f])
                #beatmap.append([[[k, 0, 0, 0, 0]], e + 8])
                #beatmap.append([[[8, k+1, 63, 63, 63]], e])
                beatmap.append([[8, k+1, round(30/9*f), round(30/9*f), round(30/9*f)], e + 8-f])


    beatmap.sort(key=sortKeyb)
    notetime.sort(key=sortKeyt)

    c = 0
    stop = False
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

def lookInput(lp, image, len = 1):
    button = lp.ButtonStateXY()

    if button != []:
        x = button[0]
        y = button[1]
        hit = []
        score = ''
        r,g,b = 0,0,0
        for lights in image:
            if lights[0] == x and lights[1] == y:
                hit = lights
                if hit[5] == 'good':
                    r, g, b = 15, 63, 15
                    score = 'good'
                elif hit[5] == 'early':
                    r, g, b = 60, 60, 10
                    score = 'early'
                elif hit[5] == 'late':
                    r, g, b = 63, 10, 10
                    score = 'late'



        if button[2] == 127:
            lp.LedCtrlXY(x, y, 63, 63, 63)
            for i in range(1, len + 1):
                lp.LedCtrlXY(x + i, y, r - (i - 1) * 10, g - (i - 1) * 10, b - (i - 1) * 10)
                lp.LedCtrlXY(x - i, y, r - (i - 1) * 10, g - (i - 1) * 10, b - (i - 1) * 10)
                lp.LedCtrlXY(x, y + i, r - (i - 1) * 10, g - (i - 1) * 10, b - (i - 1) * 10)
                lp.LedCtrlXY(x, y - i, r - (i - 1) * 10, g - (i - 1) * 10, b - (i - 1) * 10)
        else:
            lp.LedCtrlXYByCode(x, y, 0)
            for i in range(1, len + 1):
                lp.LedCtrlXYByCode(x + i, y, 0)
                lp.LedCtrlXYByCode(x - i, y, 0)
                lp.LedCtrlXYByCode(x, y + i, 0)
                lp.LedCtrlXYByCode(x, y - i, 0)


def initPad():
    lp = launchpad.LaunchpadMk2()
    lp.Open()
    lp.ButtonFlush()
    lp.LedCtrlString('OK', 63, 3, 63, direction=-1, waitms=0)
    return lp

def sendNote(light, lp):
    lp.LedCtrlXY(light[0], light[1], light[2], light[3], light[4])

def checkClose(curnotes, curbeat, x, y):
    found = False
    for note in curnotes:
        if note[0] == x and note[1] == y:
            if curbeat - 1 <= note[2] <= curbeat + 1:
                return 'perfect'
            elif curbeat - 3 <= note[2] <= curbeat + 3:
                return 'good'
            elif curbeat - 6 <= note[2] <= curbeat + 5:
                return 'ok'
            elif curbeat - 10 <= note[2] <= curbeat + 7:
                return 'bad'
    return ''


def initmenu():
    folderlist = []
    infolist = []
    songlist = []
    for songfolder in os.listdir('Songs'):
        file = open('Songs/{}/info.dat'.format(songfolder))
        info = ast.literal_eval(file.read())
        folderlist.append(songfolder)
        infolist.append(info)

        songdifs = []
        for difsets in info['_difficultyBeatmapSets']:
            if difsets['_beatmapCharacteristicName'] == 'Standard':
                for dif in difsets['_difficultyBeatmaps']:
                    songdifs.append((dif['_difficulty'],0))
        songlist.append((info['_songName'], songdifs, songfolder))

    return songlist, infolist



def playSong(folder, DIFCHOICE, lp):
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
                sendNote(lights[0], lp)
                lightmap.remove(lights)

            if button != []:
                x = button[0]
                y = button[1]
                r, g, b = 0, 0, 0
                if button[2] == 127:
                    status = checkClose(curnotes, curbeat, x, y)
                    lp.LedCtrlXY(x, y, 63, 63, 63)
                    if status == 'perfect':
                        r,g,b = 20, 35, 63
                    if status == 'good':
                        r,g,b = 15, 63, 15
                    elif status == 'ok':
                        r, g, b = 63, 60, 10
                    elif status == 'bad':
                        r, g, b = 63, 10, 10

                    lp.LedCtrlXY(x + 1, y, r, g, b)
                    lp.LedCtrlXY(x - 1, y, r, g, b)
                    lp.LedCtrlXY(x, y + 1, r, g, b)
                    lp.LedCtrlXY(x, y - 1, r, g, b)

                    if (x,y) == (8,8):
                        mixer.music.unload()
                        going = False
                        lp.LedAllOn(3)
                        time.sleep(.1)
                        lp.LedAllOn(0)
                    if (x,y) == (8,7):
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



    def main_background() -> None:
        background = pygame_menu.baseimage.BaseImage(image_path='Songs/{}/{}'.format(FILE[0], COVERJPG[0]))

        background.draw(surface)


    def setdif(value, item):
        DIFCHOICE[0] = value[1]
        pass

    def setlevel(value, difset, file):
        FILE[0] = file
        COVERJPG[0] = infolist[value[1]]['_coverImageFilename']
        d1.update_elements(difset)
        if mixer.music.get_busy():
            mixer.music.unload()
        mixer.music.load('Songs/{}/{}'.format(file, infolist[value[1]]['_songFilename']))
        mixer.music.play(start=infolist[value[1]]['_previewStartTime'], fade_ms= 1000)
        pass

    def startsong():
        mixer.music.unload()
        playSong('Songs/{}'.format(FILE[0]), DIFCHOICE[0], lp)
        pass


    main_menu_theme = pygame_menu.themes.THEME_DARK.copy()
    main_menu_theme.set_background_color_opacity(0.4)
    main_menu_theme.widget_font=pygame_menu.font.FONT_HELVETICA

    menu = pygame_menu.Menu(350, 450, 'Project LP', theme=main_menu_theme)

    menu.add_selector('Song: ', songlist, onchange=setlevel)
    d1 = menu.add_selector('Difficulty: ', diffs, onchange=setdif)
    menu.add_button('START', startsong,  shadow=True, shadow_color=(0, 0, 100))
    menu.add_button('Quit', pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_RIGHT)

    pygame.display.set_caption('Project LP')
    lp = initPad()
    menu.mainloop(surface, main_background)





