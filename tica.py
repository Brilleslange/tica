#Twilight Imperium 4th Edition Faction Color Assigner (TICA)

import os
import sys
if sys.version_info[0] < 3:
    import ConfigParser as configparser
else:
    import configparser
import tkinter as tk
from tkinter import messagebox
from random import shuffle, randrange

def main():

    class Faction:

        def __init__(self, name, prio):
            #Each faction has a score for each color that indicates how much the faction "likes" that color. The default
            #scores are based on the colors of the faction tokens and faction sheets. The default scores are:
            #8   - Signature color (generally associated with faction)
            #6   - Preferred color (significant on faction token or faction sheet)
            #5-4 - Liked color (appears on faction token or faction sheet)
            #1-2 - Slightly liked color (some association with faction; no association but is pleasing; complimentary color)
            #0   - Disliked color (no association with faction; not pleasing in combination with faction token and faction sheet)
            self.name = name
            self.scores = {}
            for i in range(6):
                self.scores[colors[i]] = tk.IntVar()
                self.scores[colors[i]].set(prio[i])
            self.color = ''
            self.envy = [0,0,0,0,0,0]

    class Interface:

        players = []

        def __init__(self):
            #Initializes the GUI. The user may select from the list of factions, or choose to have the program select
            #a user-defined number of random factions. The user may also choose whether or not the program should assign
            #the speaker token to a random player. At the click of a button, the program then distributes the colors to
            #the players, as well as the speaker token if so chosen. The program uses an algorithm based on the principles
            #of envy-free item assignment.

            #Read custom color scores from configuration file, or creates said file if it does not exist.
            self.parser = configparser.ConfigParser()
            if not os.path.exists('ticaconfig.ini'):
                self.parser.add_section("CUSTOM")
                for faction in factions:
                    scoreString = ""
                    for i in range(6):
                        scoreString += "{} ".format(faction.scores[colors[i]].get())
                    self.parser.set('DEFAULT', faction.name, scoreString)
                    self.parser.set('CUSTOM', faction.name, scoreString)
                file = open("ticaconfig.ini",'w')
                self.parser.write(file)
                file.close()
            else:
                self.parser.read('ticaconfig.ini')
            for faction in factions:
                scoreList = self.parser.get('CUSTOM', faction.name).split()
                for i in range(6):
                    faction.scores[colors[i]].set((scoreList[i]))

            #Assigned colors are put here so they can be displayed nicely
            self.lines = []
            for l in range(6):
                self.lines.append([tk.StringVar(),tk.StringVar(),tk.StringVar()])
                for s in range(3):
                    self.lines[l][s].set("")
        
            #Creates and immediately hides the "assigned colors" window
            self.createWindow()
            self.window.withdraw()

            #Creates and immediately destroys the color scores window
            self.scoringWindow = tk.Toplevel()
            self.scoringWindow.destroy()

            #Frame for main window
            frame = tk.Frame(root, padx=10, pady=10)
            frame.pack(fill=tk.BOTH)

            #Frame for faction checkboxes
            factionFrame = tk.Frame(frame, padx=10, pady=10)
            factionFrame.grid(row=0, column=0, columnspan=4)

            #Create faction checkboxes
            number = 0
            for j in range(3):
                for i in range(6):
                    if number < len(factions):
                        factions[number].chosen = tk.BooleanVar()
                        factions[number].chosen.set(False)
                        tk.Checkbutton(factionFrame,
                                       text     = factions[number].name,
                                       variable = factions[number].chosen,
                                       onvalue  = True,
                                       offvalue = False,
                                       ).grid(row=i, column=j, sticky=tk.W)
                    number += 1

            #Let the user select an amount of factions for the program to randomly select
            self.rannum = tk.IntVar(); self.rannum.set(0)
            randomFrame = tk.Frame(frame, padx=10, pady=10)
            randomFrame.grid(row=1, column=0, sticky=tk.W)
            tk.Spinbox(randomFrame, from_=0, to=17, textvariable=self.rannum, width=2).grid(row=0, column=0)
            tk.Label(randomFrame, text="factions").grid(row=0, column=1)
            tk.Button(randomFrame, text = "Randomize", command = self.randomize).grid(row=0, column=2)

            #This button opens the color scores window
            tk.Button(frame, text = "Set scores", command = self.scoring).grid(row=1, column=1)

            #Let the user choose whether or not the program should randomly designate a speaker
            self.speaker = tk.BooleanVar(); self.speaker.set(True)
            tk.Checkbutton(frame,
                           text     = "Assign speaker",
                           variable = self.speaker,
                           onvalue  = True,
                           offvalue = False,
                           ).grid(row=1, column=2)

            #This button assigns the colors
            tk.Button(frame, text = "Assign colors", command = self.assign).grid(row=1, column=3)

        def createWindow(self):
            #Creates a window displaying the selected factions and their assigned colors. Also displays the speaker, if desired.
            self.window = tk.Toplevel()
            self.window.title("Color assignment")
            self.windowFrame = tk.Frame(self.window, padx=10, pady=10)
            self.windowFrame.pack(fill=tk.BOTH)
            for i in range(6):
                for j in range(3):
                    tk.Label(self.windowFrame, textvariable=self.lines[i][j]).grid(row=i, column=j, sticky=tk.W)

        def randomize(self):
            #Randomly selects a user-defined amount of factions.
            if self.rannum.get() < 0 or self.rannum.get() > 17:
                tk.messagebox.showerror("Invalid faction amount", "Amount of factions to randomize\nmust be between 1 and 17.")
            else:
                for faction in factions:
                    faction.chosen.set(False)
                num = self.rannum.get()
                while num > 0:
                    ran = randrange(17)
                    if not factions[ran].chosen.get():
                        factions[ran].chosen.set(True)
                        num -= 1

        def scoring(self):
            #Allows the user to set custom scores.
            if not self.scoringWindow.winfo_exists():
                self.scoringWindow = tk.Toplevel()
                self.scoringWindow.title("Color scores")
                scoringFrame = tk.Frame(self.scoringWindow, padx=10, pady=10)
                scoringFrame.pack(fill=tk.BOTH)
                for c in range(6):
                    tk.Label(scoringFrame, text=colors[c]).grid(row=0, column=c+1)
                    scoringFrame.columnconfigure(c+1, weight=1, uniform='score')
                for f in range(17):
                    tk.Label(scoringFrame, text=factions[f].name).grid(row=f+1, column=0, sticky=tk.W)
                    scoringFrame.rowconfigure(f+1, pad=5)
                    for s in range(6):
                        tk.Entry(scoringFrame, textvariable=factions[f].scores[colors[s]], width=2).grid(row=f+1, column=s+1)
                buttonFrame = tk.Frame(self.scoringWindow, padx=10, pady=10)
                buttonFrame.pack(fill=tk.BOTH)
                buttonFrame.columnconfigure(0, weight=1, uniform='button')
                buttonFrame.columnconfigure(1, weight=1, uniform='button')
                buttonFrame.columnconfigure(2, weight=1, uniform='button')
                tk.Button(buttonFrame, text = "Load default", command = self.defaultscores).grid(row=0, column=0)
                tk.Button(buttonFrame, text = "Load custom", command = self.loadcustom).grid(row=0, column=1)
                tk.Button(buttonFrame, text = "Save", command = self.setscores).grid(row=0, column=2)
            elif self.scoringWindow.state() != tk.NORMAL:
                self.scoringWindow.deiconify()

        def defaultscores(self):
            #Sets color scores to their default values
            for faction in factions:
                scoreList = self.parser.get('DEFAULT', faction.name).split()
                for i in range(6):
                    faction.scores[colors[i]].set((scoreList[i]))

        def loadcustom(self):
            #Sets scores to saved custom values, or, if none are found, set them to default values
            for faction in factions:
                scoreList = self.parser.get('CUSTOM', faction.name).split()
                for i in range(6):
                    faction.scores[colors[i]].set((scoreList[i]))

        def setscores(self):
            #Saves user-defined color scores to configuration file if they are valid
            valid = True
            stringList = []
            for faction in factions:
                scoreString = ""
                for i in range(6):
                    try:
                        scoreString += "{} ".format(faction.scores[colors[i]].get())
                    except:
                        valid = False
                stringList.append(scoreString)
            if not valid:
                tk.messagebox.showerror("Invalid values", "Please enter only integers.")
            else:
                for f in range(17):
                    self.parser.set('CUSTOM', factions[f].name, stringList[f])
                file = open("ticaconfig.ini",'w')
                self.parser.write(file)
                file.close()
                tk.messagebox.showinfo("Success", "Color scores successfully saved.")

        def first(self):
            #Players initially pick colors in a random order. Each player picks the color they like the most that is not already taken.
            remaining = ['Red', 'Yellow', 'Green', 'Blue', 'Purple', 'Black']
            order = []
            for p in range(len(self.players)):
                order.append(p)
            shuffle(order)
            for o in order:
                chosenColor = ''
                chosenPrio = -1
                for color in colors:
                    if color in remaining and self.players[o].scores[color].get() > chosenPrio:
                        chosenColor = color
                        chosenPrio = self.players[o].scores[color].get()
                self.players[o].color = chosenColor
                remaining.remove(chosenColor)

        def envymatrix(self):
            #For each player, their envy of each other player is calculated. Player A's envy of player B is the difference
            #between player A's score for player B's color and player A's score for their own color. A positive score
            #indicates that player A is envious of player B, i.e. likes player B's color better than their own; a negative
            #score indicates that player A does not envy player B, i.e. likes player B's color less than their own; a score
            #of zero indicates that player A likes player B's color just as much as their own.
            for player in self.players:
                for e in range(6):
                    otherplayer = self.players[e]
                    player.envy[e] = player.scores.get(self.players[e].color).get() - player.scores.get(player.color).get()

        def envious(self):
            #Checks the envy matrix to see if any two players would like to switch colors. If a pair of players is found
            #where player A and B both envy each other (their envy scores for each other are both positive), or player A
            #envies player B's color more than player B dislikes player A's color (player A's envy score for player B is
            #positive and player B's envy score for player A is negative, but the combined score is positive), then
            #player A and player B switch colors and the function returns True. Otherwise, the function returns False.
            player = 0
            found = False
            while not found and player < 6:
                otherplayer = 0
                while not found and otherplayer < 6:
                    if (self.players[player].envy[otherplayer] + self.players[otherplayer].envy[player]) > 0:
                        found = True
                        playercolor = self.players[player].color
                        othercolor  = self.players[otherplayer].color
                        self.players[player].color      = othercolor
                        self.players[otherplayer].color = playercolor
                    otherplayer += 1
                player += 1
            return found

        def assign(self):
            #Players are a assigned a color. Then, players switch colors between them until no envious pair of players is
            #found. Finally, if the speaker token is to be assigned, it is given to a random player.
            self.players = []
            for faction in factions:
                if faction.chosen.get():
                    self.players.append(faction)
            amount = len(self.players)
            if amount < 3 or amount > 6:
                tk.messagebox.showerror("Invalid player amount", "Must choose 3-6 factions.")
            else:
                #If there are fewer than 6 players, add dummy players
                if len(self.players) == 3:
                    self.players.append(player4)
                if len(self.players) == 4:
                    self.players.append(player5)
                if len(self.players) == 5:
                    self.players.append(player6)
                self.first()
                self.envymatrix()
                while self.envious():
                    self.envymatrix()
                spk = -1
                if self.speaker.get():
                    spk = randrange(amount)
                if not self.window.winfo_exists():
                    self.createWindow()
                elif self.window.state() != tk.NORMAL:
                    self.window.deiconify()
                for i in range(6):
                    if i >= amount:
                        for j in range(3):
                            self.lines[i][j].set("")
                    else:
                        self.lines[i][0].set(self.players[i].name)
                        self.lines[i][1].set(self.players[i].color)
                        if i == spk:
                            self.lines[i][2].set("(SPEAKER)")
                        else:
                            self.lines[i][2].set("")

    #Initializes main window
    root = tk.Tk()
    root.title("Twilight Imperium 4th Edition Faction Color Assigner")

    #Sets colors
    colors = ['Red', 'Yellow', 'Green', 'Blue', 'Purple', 'Black']
    #Sets factions
    factions = []
    arborec = Faction("The Arborec Symphony",       [1,6,8,1,0,1]); factions.append(arborec)
    letnev  = Faction("The Barony of Letnev",       [6,2,0,5,0,6]); factions.append(letnev)
    saar    = Faction("The Clan of Saar",           [2,6,0,0,2,5]); factions.append(saar)
    muaat   = Faction("The Embers of Muaat",        [6,5,0,0,0,5]); factions.append(muaat)
    hacan   = Faction("The Emirates of Hacan",      [6,8,0,0,0,0]); factions.append(hacan)
    sol     = Faction("The Federation of Sol",      [2,6,4,6,0,1]); factions.append(sol)
    creuss  = Faction("The Ghosts of Creuss",       [0,1,0,8,5,4]); factions.append(creuss)
    l1z1x   = Faction("The L1Z1X Mindnet",          [6,2,1,6,0,6]); factions.append(l1z1x)
    mentak  = Faction("The Mentak Coalition",       [0,6,0,0,5,6]); factions.append(mentak)
    naalu   = Faction("The Naalu Collective",       [0,6,6,0,4,2]); factions.append(naalu)
    nekro   = Faction("The Nekro Virus",            [6,0,1,1,0,6]); factions.append(nekro)
    sardakk = Faction("The Sardakk N'orr",          [6,2,5,0,0,6]); factions.append(sardakk)
    jolnar  = Faction("The Universities of Jol-Nar",[0,4,2,6,6,2]); factions.append(jolnar)
    winnu   = Faction("The Winnu",                  [4,6,2,0,6,2]); factions.append(winnu)
    xxcha   = Faction("The Xxcha Kingdom",          [0,4,6,4,1,0]); factions.append(xxcha)
    yin     = Faction("The Yin Brotherhood",        [0,5,0,0,6,6]); factions.append(yin)
    yssaril = Faction("The Yssaril Tribes",         [5,6,6,0,2,2]); factions.append(yssaril)
    #Dummy players are created to facilitate color assignment when there are fewer than 6 players
    player4 = Faction("Player 4",                   [0,0,0,0,0,0])
    player5 = Faction("Player 5",                   [0,0,0,0,0,0])
    player6 = Faction("Player 6",                   [0,0,0,0,0,0])

    #Initializes the program
    Interface()
    root.mainloop()

if __name__ == '__main__':
    main()