import time
import tkinter as tk
from threading import Thread
from tkinter import ttk
import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression


# Partie visuel des widgets

class visual_content:
    def __init__(self):
        """
        :return : returns the app and the widgets contained within itself
        """
        self.app = tk.Tk()

        # frame contenamt les boutosn et menu
        self.frame_window_top_left = tk.Frame(self.app, highlightbackground="black", highlightthickness=1)

        # frame contenant les valeurs que nous voulons afficher
        self.frame_window_top_right = tk.Frame(self.app, highlightbackground="black", highlightthickness=1)

        # frame contenant le graphique
        self.frame_window_center = tk.Frame(self.app, highlightbackground="black", highlightthickness=1)

        # frame pour laisser un espace pour l'esthetique?
        self.frame_window_bottom = tk.Frame(self.app, bg="black", borderwidth=2)

        # ce bouton permettra de lancer la fonction de webscrapping ( si l'algo est eteint, le graph va stagner,
        # au relancement du programme, reinitialiser le graph)
        self.button_launch_program = ttk.Button(self.frame_window_top_left)
        self.button_webscrap_string = tk.StringVar()

        # ce bouton permettra de faire afficher le graphique ou non
        self.button_display_graph = ttk.Button(self.frame_window_top_left)
        self.button_graph_string = tk.StringVar()

        # ce bouton permet de fermer
        self.button_quit = tk.Button(self.frame_window_top_left, text="Close app", command=self.app.quit)

        # menu ou l'on pourra choisir ou non de faire afficher tel valeur (min max, moy...)
        self.value_menu = tk.Menubutton(self.frame_window_top_left, text="value(s) to be displayed?",
                                        activebackground="grey")

        # variables activating or desactivating value apearance in the top right label
        self.var_max = tk.IntVar()
        self.var_min = tk.IntVar()
        self.var_moy = tk.IntVar()
        self.var_std = tk.IntVar()
        self.var_last = tk.IntVar()
        self.var_pred = tk.IntVar()

        # text that will appear in the top right label label
        self.last_value_pred_btc_label_text = tk.StringVar()
        self.std_avg_10_last_label_text = tk.StringVar()
        self.max_min_btc_label_text = tk.StringVar()

        # labels to insert in mainframe grid used to show graph useful values (order by row configuration)
        self.label_max_min = tk.Label(self.frame_window_top_right)
        self.label_max_min.config(justify='center')
        self.label_moy_std = tk.Label(self.frame_window_top_right)
        self.label_moy_std.config(justify='center')
        self.label_last_pred = tk.Label(self.frame_window_top_right)
        self.label_last_pred.config(justify='center')

    def organise_widgets(self):
        """
        parameters :
        - the application
        - its widgets

        :return:
            - application configuration
            - frame configuration
            - button configuration
            - menu configuration
        """

        self.app.title("this is launched with a class")
        self.app.geometry('1440x790')
        self.app.rowconfigure(0, weigh=2)
        self.app.rowconfigure(1, weigh=6)
        self.app.rowconfigure(2, weigh=1)
        self.app.columnconfigure(0, weigh=1)
        self.app.columnconfigure(1, weigh=8)

        self.frame_window_top_left.grid(column=0, row=0, sticky='nesw')
        self.frame_window_top_left.rowconfigure(0, weight=1)
        self.frame_window_top_left.rowconfigure(1, weight=1)
        self.frame_window_top_left.rowconfigure(2, weight=1)
        self.frame_window_top_left.rowconfigure(3, weight=1)
        self.frame_window_top_left.columnconfigure(0, weight=1)


        self.frame_window_top_right.grid(column=1, row=0, sticky='nesw')
        self.frame_window_center.grid(row=1, column=0, columnspan=2, sticky='nesw')
        self.frame_window_bottom.grid(row=3, column=0, columnspan=2, sticky='nesw')


        self.button_quit.grid(row=0, column=0, sticky='nesw')
        self.button_launch_program.grid(row=1, column=0, sticky='nesw')
        self.button_launch_program.configure(textvariable=self.button_webscrap_string)
        self.button_launch_program.bind("<ButtonRelease-1>", th_web_scrap)


        self.button_display_graph.grid(row=2, column=0, sticky='nesw')
        self.value_menu.grid(row=3, column=0, sticky='nesw')
        self.button_display_graph.configure(textvariable=self.button_graph_string)
        self.button_display_graph.bind("<ButtonRelease-1>", on_click_button_updating_graph)


        self.value_menu.menu = tk.Menu(self.value_menu, tearoff=0)
        self.value_menu["menu"] = self.value_menu.menu
        self.value_menu.menu.add_checkbutton(label="Max", offvalue=0, onvalue=1, variable=self.var_max)
        self.value_menu.menu.add_checkbutton(label="Min", offvalue=0, onvalue=1, variable=self.var_min)
        self.value_menu.menu.add_checkbutton(label="Moy", offvalue=0, onvalue=1, variable=self.var_moy)
        self.value_menu.menu.add_checkbutton(label="std", offvalue=0, onvalue=1, variable=self.var_std)
        self.value_menu.menu.add_checkbutton(label="last", offvalue=0, onvalue=1, variable=self.var_last)
        self.value_menu.menu.add_checkbutton(label="pred", offvalue=0, onvalue=1, variable=self.var_pred)

        self.label_max_min.configure(textvariable=self.max_min_btc_label_text)
        self.label_moy_std.configure(textvariable=self.std_avg_10_last_label_text)
        self.label_last_pred.configure(textvariable=self.last_value_pred_btc_label_text)


# the following variable are used for the functions 'web_scrapping' & 'webscrap_to_graph_update'

std_btc = 0
last_value = 0
avg_10_last = 0
min_btc = 0
max_btc = 0
# self.std_btc_label = tk.IntVar()
# self.last_value_label = tk.IntVar()
# self.avg_10_last_label = tk.IntVar()
# self.min_btc_label = tk.IntVar()
# self.max_btc_label = tk.IntVar()

pred = None

dF_bitcoin = pd.Series(["date_time", "Value (USD", ""])
list_value_bitcoin = []
dot_counter = 0  # number of samples
time_btw_dot = 3  # time between samples ( 60 = 1 min )

thread1 = None  # thread to be attributed Thread() when needed
launch1 = False


########################################################################################################
def update_value_appearance():
    """
    this functions dynamically places or removes data recovered from
        - web_scrapping
        - usefull_value
        - prediction_with_Lin_reg

        each label contains 2 data for presentation purposes
    :return:
        - packs labels in 'application.frame_window_top_right' if user wants to display data
        - unpacks labels in 'application.frame_window_top_right' if user removes all data
    """
    global pred
    usefull_value()  # get data

    # get prediction if it can be done
    if pred is not None:
        x = pred
    else:
        x = [0, 0]

    # if no data is asked to be displayed
    if application.var_min.get() == 0 and application.var_max.get() == 0:
        # reset label's text
        application.max_min_btc_label_text.set("")
        # unpack label
        application.label_max_min.pack_forget()

    if application.var_std.get() == 0 and application.var_moy.get() == 0:
        application.std_avg_10_last_label_text.set("")
        application.label_moy_std.pack_forget()

    if application.var_last.get() == 0 and application.var_pred.get() == 0:
        application.last_value_pred_btc_label_text.set("")
        application.label_last_pred.pack_forget()
    
    ##############################################

    # if data1 is asked to be displayes
    if application.var_max.get() == 1:
        application.max_min_btc_label_text.set("maximum value of btc : " + str(max_btc))
        print(application.max_min_btc_label_text.get())

        # if data2 is asked to be displayed
        if application.var_min.get() == 1:
            application.max_min_btc_label_text.set(
                application.max_min_btc_label_text.get() + "\n\n\nminimum value of btc : " + str(min_btc))
        # pack label
        application.label_max_min.pack(side='left', fill='both', anchor='w')

    if application.var_min.get() == 1 and application.var_max.get() == 0:
        application.max_min_btc_label_text.set("minimum value of btc : " + str(min_btc))
        application.label_max_min.pack(side='left', fill='both', anchor='w')
    ##############################################

    if application.var_std.get() == 1:
        application.std_avg_10_last_label_text.set("\tstd value of btc : " + str(std_btc) + "\t ")

        if application.var_moy.get() == 1:
            application.std_avg_10_last_label_text.set(
                application.std_avg_10_last_label_text.get() + "\t\n\n\naverage value of btc : " + str(avg_10_last))
        application.label_moy_std.pack(side='left', fill='both', anchor='w')

    if application.var_moy.get() == 1 and application.var_std.get() == 0:
        application.std_avg_10_last_label_text.set("\taverage value of btc : " + str(avg_10_last) + "\t ")
        application.label_moy_std.pack(side='left', fill='both', anchor='w')
    ##############################################

    if application.var_last.get() == 1:
        application.last_value_pred_btc_label_text.set("\tcurrent btc value : " + str(last_value) + "\t ")
        # print(application.max_min_btc_label_text.get())

        if application.var_pred.get() == 1:
            application.last_value_pred_btc_label_text.set(
                application.last_value_pred_btc_label_text.get() + "\t\n\n\npossible future btc value : " + str(
                    x[-1]))
        application.label_last_pred.pack(side='left', fill='both', anchor='w')

    if application.var_pred.get() == 1 and application.var_last.get() == 0:
        application.last_value_pred_btc_label_text.set("\tpossible fture btc value : " + str(x[-1]) + "\t ")
        application.label_last_pred.pack(side='left', fill='both', anchor='w')


def th_web_scrap(event):
    """
    :return: activation or interrumption 'web_scrapping' depending on the value of 'launch1'[Bool]
    """

    global launch1, thread1

    if thread1 is None:
        launch1 = True
        button_webscrap_string.set("stop program")
        # print("thread webscraping lauch")

        thread1 = Thread(target=web_scrapping)  # launch 'webs_crapping'
        thread1.start()

    else:
        thread1 = None
        launch1 = False
        button_webscrap_string.set("launch program")
        # print("thread webscraping stop")


########################################################################################################
# program webscrapping

def web_scrapping():
    """
    webscrapping function
    :return:
        - dot_counter [int] : number of samples
        - np_list_value_bitcoin_array [array] : contains values of Bitcoin (USD)
    """

    global dot_counter, launch1, time_btw_dot, np_list_value_bitcoin_array
    while launch1:
        print("On commence a scrap")
        page = rq.get('https://www.boursorama.com/bourse/devises/cryptomonnaies-bitcoin-dollar-BTC-USD/')
        # transformer données sous forme xml
        soup = BeautifulSoup(page.text, 'lxml')
        # retirer la valeur interessante
        element = soup.find('div', class_="c-faceplate__body").find('span',
                                                                    class_="c-instrument c-instrument--last")
        # retirer espace pour eviter les erreurs par la suite
        element_text = element.text.replace(" ", "")

        # affichage dans la console pour etre sur que ca marche (et ca marche!)
        print("Valeur BTC : ", element_text)
        # ajouter la valeur du bitcoin dans la liste
        list_value_bitcoin.append(float(element_text))
        np_list_value_bitcoin_array = np.array(list_value_bitcoin)
        # print(np_list_value_bitcoin_array)

        dot_counter = dot_counter + 1
        """
        waiting time to avoid getting grounded by the websites' robot 
        as well as to check the interruption in order to avoid the app to 'freeze'
        """
        for _ in range(time_btw_dot):
            update_value_appearance()

            # dormir une seconde
            time.sleep(time_btw_dot)

            if not launch1:
                np.savetxt('btc.csv', np_list_value_bitcoin_array, fmt='%s')  # save data to csv file

                break


# value to display
def usefull_value():
    global std_btc, last_value, avg_10_last, min_btc, max_btc, list_value_bitcoin
    std_btc = np.std(np.array(list_value_bitcoin))
    
    last_value = list_value_bitcoin[-1]
    min_btc = np.min(np.array(list_value_bitcoin))
    max_btc = np.max(np.array(list_value_bitcoin))
    if len(list_value_bitcoin) > 10:
        last_10 = list_value_bitcoin[-10]
        np_last_10 = np.array(last_10)
        avg_10_last = np.sum(np_last_10) / 10


###################################################################################
# Linear reg

"""cette parti modifie les arrays histoires qu'ils puissent etre utilisé par
les bonne fonctions.
Pour utilisé la linear regresion sur une courbe il faut que la target soit 
l'élément suivant : X[i+1]=target = Y[i]. exemple :
    X = 1,2,3,4
    Y = 2,3,4
De plus il faut que len(X)=Len(Y). On enléve donc le derniére element de X. étape (1)
Puis il faut transformé les array en matice column de type float. étape (2)
Et enfin on lance la regrésion linéaire. étape (3)

"""


def prediction_with_Lin_reg():
    # print('reg lancé')
    global dot_counter, list_value_bitcoin
    # (1)
    list_value_bitcoin_plus_un = []
    np_list_value_bitcoin_array = np.array(list_value_bitcoin)
    for i in range(0, len(list_value_bitcoin) - 1):
        list_value_bitcoin_plus_un.append(list_value_bitcoin[i + 1])
    np_list_value_bitcoin_array_plus_un = np.array(list_value_bitcoin_plus_un)

    # (2)
    np_pred = np_list_value_bitcoin_array.reshape(-1, 1)
    np_pred = np_pred.astype(float)
    np_list_value_bitcoin_array = np.delete(np_list_value_bitcoin_array, len(np_list_value_bitcoin_array) - 1)
    np_list_value_bitcoin_array = np_list_value_bitcoin_array.astype(float)
    np_list_value_bitcoin_array_plus_un = np_list_value_bitcoin_array_plus_un.astype(float)
    np_list_value_bitcoin_array_plus_un = np_list_value_bitcoin_array_plus_un.reshape(-1, 1)
    np_list_value_bitcoin_array = np_list_value_bitcoin_array.reshape(-1, 1)

    # lancement de la régrésion linéaire (3)
    reg = LinearRegression()
    reg.fit(np_list_value_bitcoin_array, np_list_value_bitcoin_array_plus_un)  # fit du model
    prediction_space = np.linspace(min(np_list_value_bitcoin_array), max(np_list_value_bitcoin_array),
                                   dot_counter)  # intervale de prediciton
    Y_pred = reg.predict(prediction_space)  # prediction
    # score = reg.score(np_pred,Y_pred)

    #   print('score : ',score)

    futur_list = np_list_value_bitcoin_array  # courbe du btc

    if len(Y_pred) >= 10:
        new_Y_pred = Y_pred[:10]
        return new_Y_pred  # array of btc curve + 10 next prediction
    else:
        return Y_pred


#################################################################################

# program graphique
update_graph = False
nb_plot_counter = 1


# self.canvas.get_tk_widget().pack(fill="both", expand=1)
def on_click_button_updating_graph(event):
    """
    :return: activation or interrumption of 'webscrap_to_graph_update'
             dependint on the value of 'update_graph'[Bool]
    """

    global update_graph
    if not update_graph:
        update_graph = True
        button_graph_string.set("Stop graph")
        webscrap_to_graph_update()
    else:
        update_graph = False
        button_graph_string.set("Launch graph")


def webscrap_to_graph_update():
    """
    function retrieving 'web_scrapping' values and inserting them into the graph
    :return: updated graph (every 2 sec) while 'updated_graph' is True
    """
    global update_graph, ax, pred
    global std_btc, last_value, avg_10_last, min_btc, max_btc

    if not update_graph:
        print("je m'arrete d'update")
        return

    global dot_counter, launch1, time_btw_dot, \
        np_list_value_bitcoin_array, nb_plot_counter, ax

    """
    - takes 'web_scrapping' number of samples and values attributes to them
    - updates ax's subplot ( configuration at the end )
    """
    pred = prediction_with_Lin_reg()  # we lauch the prediction
    np.delete(pred, 0)
    y = np_list_value_bitcoin_array
    y = np.concatenate((y, pred), axis=None)
    x = np.arange(len(y))  # axe X du graph
    fig_plot_container.delaxes(ax)
    ax = fig_plot_container.add_subplot(111)
    # ax.lines.pop(0)  # deletes previous line
    # IL FAUT suprimer les point bleu

    ax.grid()
    # nb_plot_counter is used in for the possibility that we have ++ samples to show the evolution neatly
    ax.plot(x[:nb_plot_counter], y[:nb_plot_counter], c="black")  # creates new line

    # Add below threshold markers
    if len(x) > 15:
        below_threshold = x > x[-10]
        ax.plot(x[below_threshold], y[below_threshold], color='skyblue')
    ax.set_xlabel("sample number + 10 linear regresion prediction ")
    ax.set_ylabel("bitcoin value (USD)+ 10 linear regresion prediction")
    # fig_plot_container.add_axes(ax)
    canvas.draw()
    nb_plot_counter += 1
    application.app.after(2000, webscrap_to_graph_update)  # call la fonction apres 2000 ms
    # application.app.after(1000, webscrap_to_graph_update)


number_grid_column_used = 0

# application.label_00.grid(row=0, column=0)
# for w in application.frame_window_top_right.grid_slaves(): print(w)


# creation of the application & its configuration
application = visual_content()
application.organise_widgets()

"""
    - creating variable string to change buttons "label"
    - binding
        . application.button_launch_program --> th_web_scrap
        . application.button_display_graph --> button_graph_string
"""
button_webscrap_string = tk.StringVar()
application.button_launch_program.configure(textvariable=button_webscrap_string)
button_webscrap_string.set("launch scrap")
application.button_launch_program.bind("<ButtonRelease-1>", th_web_scrap)

button_graph_string = tk.StringVar()
application.button_display_graph.configure(textvariable=button_graph_string)
button_graph_string.set("launch graph")
application.button_display_graph.bind("<ButtonRelease-1>", on_click_button_updating_graph)

"""
Creation of ( hierarchy order ) :
    - canvas --> ( like a container )
    - fig_plot_container --> which will contain the plot
    - ax --> contains plot more or less
"""
fig_plot_container = Figure()
canvas = FigureCanvasTkAgg(fig_plot_container, master=application.frame_window_center)
canvas.get_tk_widget().pack(fill='both', side='bottom', expand=True)
ax = fig_plot_container.add_subplot(111)
ax.grid() #put a grid
ax.plot([], [])

canvas.draw()
#
# launch application
application.app.mainloop()
