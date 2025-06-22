
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json

global activeCardSelectors
activeCardSelectors = 1
global jsonToReturn
jsonToReturn = {}

def runSetupWindow():
    window = Tk()
    window.geometry("1000x1000")
    window.title("Main menu")

    window.config(background="#f2cb9b")

    label = Label(window, text = "Setup Game", font=('Impact', 40, 'bold'), fg = '#2b1a06', bg = window.cget("bg"))

    label.update_idletasks()
    label_width = label.winfo_reqwidth()
    window_width = window.winfo_width()
    center_x = (window_width - label_width) // 2

    label.place(x=center_x, y=100)

    playsFirstLbl = Label(window, text = "\u2022 Choose which player plays first", font = ('Impact', 15), fg ='#b07c38', bg=window.cget("bg"))
    rightTenth_x = (window_width - label_width) // 10
    playsFirstLbl.place(x=rightTenth_x, y=230)


    canvas = Canvas(window, width=window_width, height=5, bg=window.cget('bg'),  highlightthickness=0, bd=0)
    canvas.place(y=255)

    screenEdgeOffset = 20
    canvas.create_line(screenEdgeOffset, 2, window_width - screenEdgeOffset, 2, fill="#b07c38", width=2)
    playerNames = ['Random (default)', 'p1', 'p2']
    playerColors = ['purple', 'blue', 'red']

    def saveFirstPlayer():
        global jsonToReturn
        print("x.get(): ", x.get())
        jsonToReturn['playsFirst'] = playerNames[x.get()]


    x = IntVar()
    jsonToReturn['playsFirst'] = playerNames[0]
    radioButton_x = 10 * screenEdgeOffset
    for i in range(len(playerNames)):
        radioButton = Radiobutton(window, text = playerNames[i], font=('Impact', 15), variable=x, value=i, bg = window.cget('bg'), fg = playerColors[i], command = saveFirstPlayer, activebackground='#6e4816').place(y = 265, x = radioButton_x)
        radioButton_x += 12 * screenEdgeOffset



    typesOfPlayers = Label(window, text = "\u2022 Choose player types", font = ('Impact', 15), fg ='#b07c38', bg=window.cget("bg")).place(y=330, x = rightTenth_x)


    canvas3 = Canvas(window, width=window_width, height=5, bg=window.cget('bg'),  highlightthickness=0, bd=0)
    canvas3.place(y=355)
    canvas3.create_line(screenEdgeOffset, 2, window_width - screenEdgeOffset, 2, fill="#b07c38", width=2)

    typeLbl = Label(window, text='Type', font=('Impact'), bg=window.cget('bg'), fg='#b07c38').place(x=rightTenth_x + 120, y=370)
    p1Lbl = Label(window, text='\u2022p1:', bg=window.cget('bg'), fg='blue', font = ('Impact', 15)).place(y=400, x = rightTenth_x)
    p2Lbl = Label(window, text='\u2022p2:', bg=window.cget('bg'), fg='red', font = ('Impact', 15)).place(y=460, x = rightTenth_x)



    def p1SelectType(e):
        global depthLbl, depthComboBox, alphaBetaLbl, checkAlphaBeta, tTableLbl, checkTranspositionTable
        if not p1ComboBox.get() == 'Human':
            jsonToReturn['p1_type'] = p1ComboBox.get()

            def setAlphaBeta():
                if alphaBeta.get() == 1:
                    jsonToReturn['p1_alpthaBeta'] = True
                else:
                    jsonToReturn['p1_alpthaBeta'] = False

            def setDepth(e):
                jsonToReturn['p1_depth'] = depthComboBox.get()

            def setTTable():
                if tTable.get() == 1:
                    jsonToReturn['p1_transpositionTbale'] = True
                else:
                    jsonToReturn['p1_transpositionTbale'] = False

            depthLbl = Label(window, text='Depth', bg = window.cget('bg'), fg='#b07c38', font=('Impact'))
            depthLbl.place(y=370, x=rightTenth_x + 370)
            depthComboBox = ttk.Combobox(window, value=list(range(1, 10)), font=('Impact'), background=window.cget('bg'))
            depthComboBox.bind('<<ComboboxSelected>>', setDepth)

            depthComboBox.current(0)
            depthComboBox.place(x=rightTenth_x + 300, y=400)
            alphaBetaLbl = Label(window, text='Alpha/Beta', bg = window.cget('bg'), fg='#b07c38', font=('Impact'))
            alphaBetaLbl.place(y=370, x=rightTenth_x + 550)
            alphaBeta = IntVar(value=0)
            jsonToReturn['p1_alpthaBeta'] = False

            checkAlphaBeta = Checkbutton(window, variable=alphaBeta, onvalue=1, offvalue=0, bg=window.cget('bg'), command=setAlphaBeta, activebackground='#b07c38')
            checkAlphaBeta.place(y=400, x =rightTenth_x + 570)
            print('alphaBeta: ', alphaBeta)
            tTableLbl = Label(window, text='Tranasposition Table', bg = window.cget('bg'), fg='#b07c38', font='Impact')
            tTableLbl.place(y=370, x=rightTenth_x + 660)
            tTable = IntVar(value=0)
            jsonToReturn['p1_transpositionTbale'] = False
            checkTranspositionTable = Checkbutton(window, variable=tTable, onvalue=1, offvalue=0, bg=window.cget('bg'), command=setTTable, activebackground='#b07c38')
            checkTranspositionTable.place(y=400, x =rightTenth_x + 720)

        else:
            jsonToReturn['p1_type'] = p1ComboBox.get()
            try:
                depthLbl.place_forget()
                depthComboBox.place_forget()
                alphaBetaLbl.place_forget()
                checkAlphaBeta.place_forget()
                tTableLbl.place_forget()
                checkTranspositionTable.place_forget()
            except:
                print('NameError')


    def p2SelectType(e):
        global depthLbl2, depthComboBox2, alphaBetaLbl2, checkAlphaBeta2, tTableLbl2, checkTranspositionTable2
        if not p2ComboBox.get() == 'Human':
            jsonToReturn['p2_type'] = p2ComboBox.get()
            def setAlphaBeta():
                if alphaBeta2.get() == 1:
                    jsonToReturn['p2_alpthaBeta'] = True
                else:
                    jsonToReturn['p2_alpthaBeta'] = False

            def setDepth(e):
                jsonToReturn['p2_depth'] = depthComboBox2.get()

            def setTTable():
                if tTable2.get() == 1:
                    jsonToReturn['p2_transpositionTbale'] = True
                else:
                    jsonToReturn['p2_transpositionTbale'] = False

            depthLbl2 = Label(window, text='Depth', bg = window.cget('bg'), fg='#b07c38', font=('Impact'))
            depthLbl2.place(y=370, x=rightTenth_x + 370)
            depthComboBox2 = ttk.Combobox(window, value=list(range(1, 10)), font=('Impact'), background=window.cget('bg'))
            depthComboBox2.bind('<<ComboboxSelected>>', setDepth)

            depthComboBox2.current(0)
            depthComboBox2.place(x=rightTenth_x + 300, y=460)
            alphaBetaLbl2 = Label(window, text='Alpha/Beta', bg = window.cget('bg'), fg='#b07c38', font=('Impact'))
            alphaBetaLbl2.place(y=370, x=rightTenth_x + 550)
            alphaBeta2 = IntVar(value=0)
            jsonToReturn['p2_alpthaBeta'] = False
            checkAlphaBeta2 = Checkbutton(window, variable=alphaBeta2, onvalue=1, offvalue=0, bg=window.cget('bg'), command=setAlphaBeta, activebackground='#b07c38')
            checkAlphaBeta2.place(y=460, x =rightTenth_x + 570)

            tTableLbl2 = Label(window, text='Tranasposition Table', bg = window.cget('bg'), fg='#b07c38', font='Impact')
            tTableLbl2.place(y=370, x=rightTenth_x + 660)
            tTable2 = IntVar(value=0)
            jsonToReturn['p2_transpositionTbale'] = False
            checkTranspositionTable2 = Checkbutton(window, variable=tTable2, onvalue=1, offvalue=0, bg=window.cget('bg'), command=setTTable, activebackground='#b07c38')
            checkTranspositionTable2.place(y=460, x =rightTenth_x + 720)

        else:
            jsonToReturn['p2_type'] = p1ComboBox.get()
            try:
                depthLbl2.place_forget()
                depthComboBox2.place_forget()
                alphaBetaLbl2.place_forget()
                checkAlphaBeta2.place_forget()
                tTableLbl2.place_forget()
                checkTranspositionTable2.place_forget()
            except:
                print('nameError')

    playerTypes = ['Human', 'MinMax', 'NegaMax']
    p1ComboBox = ttk.Combobox(window, value=playerTypes, font=('Impact'))
    p1ComboBox.current(0)
    p1ComboBox.place(y=400, x = rightTenth_x + 50)
    p1ComboBox.bind('<<ComboboxSelected>>', p1SelectType)

    p2ComboBox = ttk.Combobox(window, value=playerTypes, font=('Impact'))
    p2ComboBox.current(0)
    p2ComboBox.place(y=460, x = rightTenth_x + 50)
    p2ComboBox.bind('<<ComboboxSelected>>', p2SelectType)

    chooseCardsLbl = Label(window, text="\u2022 Choose Cards for each Player", font = ('Impact', 15), fg ='#b07c38', bg=window.cget("bg"))
    chooseCardsLbl.place(x=rightTenth_x, y=530)

    canvas2 = Canvas(window, width=window_width, height=5, bg=window.cget('bg'),  highlightthickness=0, bd=0)
    canvas2.place(y=555)
    canvas2.create_line(screenEdgeOffset, 2, window_width - screenEdgeOffset, 2, fill="#b07c38", width=2)

    cardNamesList = list(json.load(open('cardsMoves.json')).keys())

    p1sCardsLbl = Label(window, text="p1's cards", font = ('Impact', 15), fg ='blue', bg=window.cget("bg")).place(x=15*screenEdgeOffset, y=578)
    p1ListBox = Listbox(window, selectmode="multiple", font=('Impact', 8))

    def getUnselectedCards(indexesToRemove) -> list:
        for i in indexesToRemove:
            del cardNamesList[i]
        return cardNamesList

    def on_select(event):
        selected = p1ListBox.curselection()
        if len(selected) > 2 and len(selected) > 0:
            # Deselect the last selected item to keep max 2 selections
            p1ListBox.selection_clear(selected[-1])
            messagebox.showinfo("Limit Reached", "You can only select up to 2 items.")


    for cardName in cardNamesList:
        p1ListBox.insert(END, cardName)

    p1ListBox.bind('<<ListboxSelect>>', on_select)
    p1ListBox.place(x=15*screenEdgeOffset, y=605)

    p2sCardsLbl = Label(window, text="p2's cards", font = ('Impact', 15), fg ='red', bg=window.cget("bg")).place(x=27*screenEdgeOffset, y=578)
    cardOutLbl = Label(window, text='Card out', font = ('Impact', 15), fg ='grey', bg=window.cget("bg")).place(x=39*screenEdgeOffset, y=578)
    defaultLbl = Label(window, text='Default', font = ('Impact', 15), fg ='Purple', bg=window.cget("bg")).place(x=3*screenEdgeOffset, y=578)


    p2ListBox = Listbox(window,selectmode="multiple", font=('Impact', 8))
    p2ListBox.bind('<<ListboxSelect>>', on_select)
    p2ListBox.place(x=27*screenEdgeOffset, y=605)


    cardOutListBox = Listbox(window, font=('Impact', 8))
    cardOutListBox.place(x=39*screenEdgeOffset, y=605)

    for cardName in cardNamesList:
        p1ListBox.insert(END, cardName)
        p2ListBox.insert(END, cardName)
        cardOutListBox.insert(END, cardName)

    jsonToReturn['randomCards'] = True
    def removeSelectedFromListsAndSave():
        
        global jsonToReturn
        if 'randomCards' in jsonToReturn:
            del jsonToReturn['randomCards']
        selected_indices = p1ListBox.curselection()
        selected_items = [p1ListBox.get(i) for i in selected_indices]
        if len(selected_items) < 2 and len(selected_items) > 0:
            p1ListBox.selection_clear(selected_indices[-1])
            messagebox.showinfo("Must choose 2 cards", "Each player must have two cards.")
        items_in_listbox2 = list(p2ListBox.get(0, END))
        for i in reversed(range(p2ListBox.size())):
            if p2ListBox.get(i) in selected_items:
                p2ListBox.delete(i)
        items_in_listbox2 = list(cardOutListBox.get(0, END))
        for i in reversed(range(cardOutListBox.size())):
            if cardOutListBox.get(i) in selected_items:
                cardOutListBox.delete(i)
        
        jsonToReturn['p1'] = selected_items

    def removeSelectedFromThirdListAndSave():
        global jsonToReturn

        selected_indices = p2ListBox.curselection()
        selected_items = [cardOutListBox.get(i) for i in selected_indices]
        if len(selected_items) < 2 and len(selected_items) > 0:
            p2ListBox.selection_clear(selected_indices[-1])
            messagebox.showinfo("Must choose 2 cards", "Each player must have two cards.")
        items_in_listbox2 = list(cardOutListBox.get(0, END))
        for i in reversed(range(cardOutListBox.size())):
            if cardOutListBox.get(i) in selected_items:
                cardOutListBox.delete(i)
        jsonToReturn['p2'] = selected_items

    def saveCardOut():
        global jsonToReturn

        selected_indices = cardOutListBox.curselection()
        selected_item = [cardOutListBox.get(i) for i in selected_indices]
        jsonToReturn['cardOut'] = selected_item
        print(jsonToReturn)


    btn1 = Button(window, text="Select", command=removeSelectedFromListsAndSave, bg='blue', fg = 'white', font=('Impact', 10))
    btn1.place(x=15*screenEdgeOffset + 40, y=780)
    btn2 = Button(window, text="Select", command=removeSelectedFromThirdListAndSave, bg='red', fg = 'white',font=('Impact', 10))
    btn2.place(x=27*screenEdgeOffset + 40, y=780)
    btn3 = Button(window, text='Select', command=saveCardOut, bg='grey', fg='white', font=('Impact', 10))
    btn3.place(x=39*screenEdgeOffset + 40, y=780)


    def deactivateOtherCardSelectorsAndSave():
        global activeCardSelectors
        activeCardSelectors *= -1
        global jsonToReturn

        if activeCardSelectors == -1:
            state = 'disabled'
        else:
            state = 'normal'
        btn1.config(state=state)
        btn2.config(state=state)
        btn3.config(state=state)
        p1ListBox.config(state=state)
        p2ListBox.config(state=state)
        cardOutListBox.config(state=state)
        if 'p1' in jsonToReturn:
            del jsonToReturn['p1']
        if 'p2' in jsonToReturn:
            del jsonToReturn['p2']
        if 'cardOut' in jsonToReturn:
            del jsonToReturn['cardOut']
        if activeCardSelectors == -1:
            jsonToReturn['randomCards'] = True
        elif 'randomCards' in jsonToReturn:
            del jsonToReturn['randomCards']

    btnRandomCards = Button(window, text='Select Random', command=deactivateOtherCardSelectorsAndSave,font=('Impact', 10), height=9, width=19, bg='white').place(x=3*screenEdgeOffset, y=606)

    startGameButton = Button(window, text='Start Game', height=2, width=25, bg='purple', command = window.destroy, activebackground= '#350d61', fg='white', font=('Impact',17, 'bold')).place(y = 880, x = 330)
    window.mainloop()
