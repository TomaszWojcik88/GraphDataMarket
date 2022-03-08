###############
### IMPORTS ###
###############

# IMPORT TKINTER #
import tkinter as tk
from tkinter.colorchooser import askcolor as tk_askcolor
from tkinter import ttk
# IMPORT PANDAS #
import pandas as pd
# IMPORT MISCELLANEOUS #
import datetime
import json
import shelve
from os import listdir as os_listdir, path as os_path, makedirs as os_makedirs, chmod as os_chmod
# IMPORT MATPLOTLIB #
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mplfinance.original_flavor import candlestick_ohlc
# IMPORT CONFIG #
import config
import download_market_data
### CONFIG ###
folder_market_data_files = config.folder_market_data_files
path_to_project = config.path_to_project
folder_market_data_full_path = config.folder_market_data_full_path


BOLDFONT = ("Verdana", 10)





class Graph(object):

	def __init__(self, graph_type, name, choosen_filename, database_name, settings):
		self.graph_type = graph_type
		self.name = name
		self.choosen_filename = choosen_filename
		self.database_name = database_name
		self.settings = settings





class MainInterface(tk.Tk):

	currently_opened_graphs = list()

	###################
	### KONSTRUKTOR ###
	###################

	def __init__(self, *args, **kwargs):
		self.main_window(*args, **kwargs)



	###################
	### BAZA DANYCH ###
	###################

	### INTERFEJS BAZY DANYCH ###
	def database_interface(self):
		### SPRAWDŹ STATUSY ###
		# ZAŁADUJ CONFIG BAZY DANYCH #
		self.load_db_info()
		self.config_database_names = list(self.config_database.keys())
		self.config_database_values = list(self.config_database.values())
		### Create FOLDERY JEŻELI NIE ISTNIEJĄ ###
		# DO FOLDERU Z BAZAMI DANYCH #
		self.database_info_frame = tk.Frame(self, height=2, bd=1, relief='sunken', background='white')
		self.database_info_frame.grid(padx=5, pady=5, row=0)
		full_market_files_path = os_path.join(path_to_project, folder_market_data_files)
		if not os_path.isdir(full_market_files_path):
			os_makedirs(full_market_files_path)
			os_chmod(full_market_files_path, 0o777)
		# DO POSZCZEGÓLNYCH PLIKÓW BAZ #
		for value in self.config_database_values:
			if value[3]:
				full_folder_path = os_path.join(path_to_project, value[2])
				if not os_path.isdir(full_folder_path):
					os_makedirs(full_folder_path)
					os_chmod(full_folder_path, 0o777)
		# LISTA ZMIENNYCH STATUSÓW #
		self.database_status_labels = dict()
		# LISTY: NAZWY BAZY DANYCH, STATUSY BAZY DANYCH, PRZYCISKI AKTUALIZUJĄCE BAZĘ #
		self.db_labels = list()
		self.db_status = list()
		self.db_buttons = list()
		self.db_modify_buttons = list()
		self.db_remove_buttons = list()
		# IINICJUJ LISTĘ ZMIENNYCH STATUSÓW BAZY DANYCH #
		for value in self.config_database_names:
			self.database_status_labels[value] = tk.StringVar(self)
		# Create LABELS I BUTTONS DLA BAZY DANYCH #
		for counter, (one_label, name) in enumerate(zip(self.config_database_names, self.config_database_names)):
			self.db_labels.append(tk.Label(self.database_info_frame, background='white', text=name))
			self.db_status.append(tk.Label(self.database_info_frame, background='white',  textvariable=self.database_status_labels[one_label], fg='black'))
			self.db_buttons.append(ttk.Button(self.database_info_frame, text="Actualize", command=lambda value_1=counter: self.download_choosen_database(value_1)))
			self.db_modify_buttons.append(ttk.Button(self.database_info_frame, text="Modify", command=lambda value_2=name: self.modify_database(value_2)))
			self.db_remove_buttons.append(ttk.Button(self.database_info_frame, text="Delete", command=lambda value_3=name: self.remove_database(value_3)))
		# Create LEGENDĘ #
		db_titles = ['DB Name\t', '', 'Current STATUS / DATA\t', '', 'Action']
		for counter, db_title in enumerate(db_titles):
			tk.Label(self.database_info_frame,backgroun='white',  text=db_title).grid(row=0, column=counter, sticky='W')
		ttk.Separator(self.database_info_frame, orient='horizontal').grid(column=0, row=1, columnspan=7, sticky='ew')
		# UMIEŚĆ NA KANWIE KAŻDY LABEL I BUTTON #
		ttk.Separator(self.database_info_frame, orient='vertical').grid(column=1, rowspan=len(self.db_labels)+2,
																		row=0, sticky='ns')
		ttk.Separator(self.database_info_frame, orient='vertical').grid(column=3, rowspan=len(self.db_labels)+2,
																		row=0, sticky='ns')
		for counter, (label, status, button, modify, remove) in enumerate(zip(self.db_labels, self.db_status, self.db_buttons, self.db_modify_buttons, self.db_remove_buttons)):
			label.grid(row=counter + 2, column=0, sticky='W')
			self.update_database_status(counter)
			status.grid(row=counter + 2, column=2, sticky='W')
			button.grid(row=counter + 2, column=4, sticky='W')
			modify.grid(row=counter + 2, column=5, sticky='W')
			remove.grid(row=counter + 2, column=6, sticky='W')
		ttk.Separator(self.database_info_frame, orient='horizontal').grid(column=0, row=counter+3, columnspan=7, sticky='ew')
		ttk.Button(self.database_info_frame, text='Add Database',
				   command=lambda: self.add_database()).grid(row=counter+4, column=0, sticky='W')
		ttk.Button(self.database_info_frame, text='Database - information',
				   command=lambda: self.db_info()).grid(row=counter + 4, column=2, sticky='W')
		return counter+3

	### POBIERZ PLIK BAZY DANYCH I PRZYGOTUJ ###
	def download_choosen_database(self, number):
		try:
			# INICJACJA OKNA #
			window_download = tk.Toplevel()
			db_filename = self.config_database_names[number]
			window_download.wm_title(''.join(['Download Database - ', db_filename]))
			db_properties = self.config_database_values[number]
			link, script, destination_folder = db_properties[0], db_properties[1], db_properties[2]
			# WYŚWIETL PODSTAWOWE INFORMACJE O BAZIE DANYCH #
			basic_info_frame = tk.Frame(window_download, height=2, bd=1, relief='sunken')
			basic_info_frame.grid(padx=5, pady=5, row=0)
			informations_values = (db_filename, link, script, destination_folder)
			informations_description = ('Database name:', 'Address:', 'Download script:', 'Destination folder:')
			for counter, (description, value) in enumerate(zip(informations_description, informations_values)):
				ttk.Label(basic_info_frame, text=''.join([description, '   ']), font=BOLDFONT).grid(row=counter, column=0, sticky='W')
				ttk.Label(basic_info_frame, text=value).grid(row=counter, column=1, sticky='W')
			ttk.Separator(window_download).grid(row=1, sticky='ew')
			# INICJUJ TYTUŁY INFORMACJI #
			status_info_frame = tk.Frame(window_download, height=2, bd=1, relief='sunken', background='white')
			status_info_frame.grid(padx=5, pady=5, row=2, sticky='W')
			self.status_informations = dict()
			self.status_labels = list()
			for counter in range(3):
				self.status_informations[counter] = tk.StringVar(status_info_frame)
				self.status_labels.append(tk.Label(status_info_frame, background='white', textvariable=self.status_informations[counter], fg='black'))
				self.status_labels[counter].grid(row=counter + 6, columnspan=2, sticky='W')
			download_market_data.choose_proper_download_function(db_filename, link, script,
		 																destination_folder, status_info_frame, self)
			# popup.destroy()
			self.update_database_status(number)
			# ttk.Button(window_download, text='OK', command=lambda: window_download.destroy()).grid(row=10, columnspan=2)
		except ValueError:
			error_message = tk.Label(window_download, text='For current Database were not declared\nall necessary variables', font=BOLDFONT, fg='red')
			error_message.grid(row=0, sticky='W')
			break_button = ttk.Button(window_download, text='Break', command=lambda: window_download.destroy())
			break_button.grid(row=1)

	### ModifyKUJ BAZĘ DANYCH ###
	def modify_database(self, db_filename):
		def modify_db_final():
			if len(name.get()) == 0 or len(destination_folder.get()) == 0 or len(time_format.get()) == 0:
				tk.messagebox.showinfo('Data enter error',
									   'Fields: Name, Destination folder and Time format cannot be empty!')
			else:
				if name.get() != db_filename:
					self.config_database.pop(db_filename, None)
				file_config = ''.join(
					['L', str(line.get()), ':D', str(D.get()), ':O', str(O.get()), ':H', str(H.get()), ':L', str(L.get()),
					 ':C', str(C.get())])
				link_final, download_script_final = link.get(), script_download.get()
				if len(link_final) == 0: link_final = False
				if len(download_script_final) == 0: download_script_final = False
				self.config_database[name.get()] = (link_final, download_script_final, destination_folder.get(),
													if_destination.get(), file_config, time_format.get())
				tk.messagebox.showinfo('Success!', 'Database has been actualized successfully!')
				self.save_db_info()
				self.database_info_frame.destroy()
				self.database_interface()
				window_modify_db.destroy()
		# Create NOWE OKNO #
		window_modify_db = tk.Toplevel()
		window_modify_db.wm_title(''.join(['Modify ', db_filename]))
		# WCZYTAJ PODSTAWOWE INFORMACJE O BAZIE DANYCH #
		name, link, script_download, destination_folder, time_format = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
		line, D, O, H, L, C = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()
		if_destination = tk.BooleanVar(window_modify_db)
		db_properties = self.config_database[db_filename]
		name.set(db_filename)
		if db_properties[0]: link.set(db_properties[0])
		if db_properties[1]: script_download.set(db_properties[1])
		if db_properties[2]: destination_folder.set(db_properties[2])
		if_destination.set(db_properties[3])
		time_format.set(db_properties[5])
		file_properties = db_properties[4].split(':')
		line.set(int(file_properties[0][1]))
		D.set(int(file_properties[1][1]))
		O.set(int(file_properties[2][1]))
		H.set(int(file_properties[3][1]))
		L.set(int(file_properties[4][1]))
		C.set(int(file_properties[5][1]))
		# PODSTAWOWE INFO #
		basic_info = tk.Frame(window_modify_db, height=2, bd=1, relief='sunken')
		basic_info.grid(padx=5, pady=5, row=1)
		tk.Label(window_modify_db, text='Basic info:').grid(row=0)
		basic_info = tk.Frame(window_modify_db, height=2, bd=1, relief='sunken')
		basic_info.grid(padx=5, pady=5, row=1)
		tk.Label(basic_info, text='Name: ').grid(row=0, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=name).grid(row=0, column=1, sticky='W')
		tk.Label(basic_info, text='Link: ').grid(row=1, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=link).grid(row=1, column=1, sticky='W')
		tk.Label(basic_info, text='Downloading script: ').grid(row=2, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=script_download).grid(row=2, column=1, sticky='W')
		tk.Label(basic_info, text='Destination folder: ').grid(row=3, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=destination_folder).grid(row=3, column=1, sticky='W')
		ttk.Checkbutton(basic_info, offvalue=False, onvalue=True, text="Czy folder wewnętrzny?", variable=if_destination).grid(row=4, columnspan=2, sticky='W')
		tk.Label(basic_info, text='Time format: ').grid(row=5, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=time_format).grid(row=5, column=1, sticky='W')
		# KONFIGURACJA POJEDYŃCZEGO PLIKU #
		tk.Label(window_modify_db, text='File:').grid(row=2)
		file_info = tk.Frame(window_modify_db, height=2, bd=1, relief='sunken')
		file_info.grid(padx=5, pady=5, sticky='W', row=3)
		tk.Label(file_info, text='Header line:').grid(row=0, column=0, sticky='W')
		tk.Entry(file_info, textvariable=line, width=5).grid(row=0, column=1, sticky='W')
		tk.Label(file_info, text='Column numbers:').grid(row=1, column=0)
		tk.Label(file_info, text='Data:').grid(row=2, column=0, sticky='W')
		tk.Entry(file_info, textvariable=D, width=5).grid(row=2, column=1, sticky='W')
		tk.Label(file_info, text='Open:').grid(row=3, column=0, sticky='W')
		tk.Entry(file_info, textvariable=O, width=5).grid(row=3, column=1, sticky='W')
		tk.Label(file_info, text='High:').grid(row=4, column=0, sticky='W')
		tk.Entry(file_info, textvariable=H, width=5).grid(row=4, column=1, sticky='W')
		tk.Label(file_info, text='Low:').grid(row=5, column=0, sticky='W')
		tk.Entry(file_info, textvariable=L, width=5).grid(row=5, column=1, sticky='W')
		tk.Label(file_info, text='Close:').grid(row=6, column=0, sticky='W')
		tk.Entry(file_info, textvariable=C, width=5).grid(row=6, column=1, sticky='W')
		# PRZYCISKI ZATWIERDZAJACE / CancelĄCE #
		ttk.Button(window_modify_db, text='Modify', command=lambda: modify_db_final()).grid(row=4, column=0, sticky='W')
		ttk.Button(window_modify_db, text='Cancel', command=lambda: window_modify_db.destroy()).grid(row=4, column=1, sticky='W')

	### USUŃ WYBRANĄ BAZĘ DANYCH ###
	def remove_database(self, db_filename):
		msgbox_title, msgbox_text = ''.join(['Remove data base - ', db_filename ]), ''.join(['Are you sure you want to remove data base:\n', db_filename, ' ?'])
		MsgBox = tk.messagebox.askquestion(msgbox_title, msgbox_text, icon='warning')
		if MsgBox == 'yes':
			self.config_database.pop(db_filename, None)
			self.save_db_info()
			self.database_info_frame.destroy()
			self.database_interface()

	### DODAJ BAZĘ DANYCH ###
	def add_database(self):
		# FUNKCJA OPERACJI DODANIA BAZY DANYCH #
		def add_db_final():
			if len(name.get()) == 0 or len(destination_folder.get()) == 0 or len(time_format.get()) == 0:
				tk.messagebox.showinfo('Entering Error', 'Fields: Name, Destination folder and Time format cannot be empty!')
			else:
				file_config = ''.join(['L', str(line.get()), ':D', str(D.get()), ':O', str(O.get()), ':H', str(H.get()), ':L', str(L.get()), ':C', str(C.get())])
				link_final, download_script_final = link.get(), script_download.get()
				if len(link_final) == 0: link_final = False
				if len(download_script_final) == 0: download_script_final = False
				self.config_database[name.get()] = (link_final, download_script_final, destination_folder.get(),
											if_destination.get(), file_config, time_format.get())
				tk.messagebox.showinfo('Success!', 'New DB entered correctly!')
				self.save_db_info()
				self.database_info_frame.destroy()
				self.database_interface()
				popup.destroy()
		# Create NOWE OKNO #
		popup = tk.Toplevel()
		popup.wm_title("Add new Database")
		# ZBIERZ PODSTAWOWE INFORMACJE O BAZIE DANYCH #
		name, link, script_download, destination_folder, time_format = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
		if_destination = tk.BooleanVar(popup)
		if_destination.set(False)
		time_format.set(config.date_format)
		tk.Label(popup, text='Basic info:').grid(row=0)
		basic_info = tk.Frame(popup, height=2, bd=1, relief='sunken')
		basic_info.grid(padx=5, pady=5, row=1)
		tk.Label(basic_info, text='Name: ').grid(row=0, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=name).grid(row=0, column=1, sticky='W')
		tk.Label(basic_info, text='Link: ').grid(row=1, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=link).grid(row=1, column=1, sticky='W')
		tk.Label(basic_info, text='Downloading script: ').grid(row=2, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=script_download).grid(row=2, column=1, sticky='W')
		tk.Label(basic_info, text='Destination folder: ').grid(row=3, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=destination_folder).grid(row=3, column=1, sticky='W')
		ttk.Checkbutton(basic_info, offvalue=False, onvalue=True, text="Does it is internal folder?", variable=if_destination).grid(row=4, columnspan=2, sticky='W')
		tk.Label(basic_info, text='Time format: ').grid(row=5, column=0, sticky='W')
		tk.Entry(basic_info, textvariable=time_format).grid(row=5, column=1, sticky='W')
		# ZBIERZ INFORMACJE O KONFIGURACJI POJEDYŃCZEGO PLIKU #
		tk.Label(popup, text='File:').grid(row=2)
		file_info = tk.Frame(popup, height=2, bd=1, relief='sunken')
		file_info.grid(padx=5, pady=5, sticky='W', row=3)
		line, D, O, H, L, C = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()
		tk.Label(file_info, text='Header line:').grid(row=0, column=0, sticky='W')
		tk.Entry(file_info, textvariable=line, width=5).grid(row=0, column=1, sticky='W')
		tk.Label(file_info, text='Column numbers:').grid(row=1, column=0)
		tk.Label(file_info, text='Data:').grid(row=2, column=0, sticky='W')
		tk.Entry(file_info, textvariable=D, width=5).grid(row=2, column=1, sticky='W')
		tk.Label(file_info, text='Open:').grid(row=3, column=0, sticky='W')
		tk.Entry(file_info, textvariable=O, width=5).grid(row=3, column=1, sticky='W')
		tk.Label(file_info, text='High:').grid(row=4, column=0, sticky='W')
		tk.Entry(file_info, textvariable=H, width=5).grid(row=4, column=1, sticky='W')
		tk.Label(file_info, text='Low:').grid(row=5, column=0, sticky='W')
		tk.Entry(file_info, textvariable=L, width=5).grid(row=5, column=1, sticky='W')
		tk.Label(file_info, text='Close:').grid(row=6, column=0, sticky='W')
		tk.Entry(file_info, textvariable=C, width=5).grid(row=6, column=1, sticky='W')
		# PRZYCISKI ZATWIERDZAJACE / CancelĄCE #
		ttk.Button(popup, text='Create', command=lambda: add_db_final()).grid(row=4, column=0, sticky='W')
		ttk.Button(popup, text='Cancel', command=lambda: popup.destroy()).grid(row=4, column=1, sticky='W')

	### WYŚWIETL INFORMACJE O BAZACH DANYCH ###
	def db_info(self):
		db_info_window = tk.Toplevel()
		db_info_window.wm_title('Informations about Databases')
		info_frame = tk.Frame(db_info_window, height=2, bd=1, relief='sunken', background='white')
		info_frame.grid(padx=5, pady=5, sticky='W', row=0)
		len_config_header = len(config.db_info_header)*2
		for counter in range(len_config_header):
			if counter % 2 == 0:
				number = int(counter / 2)
				tk.Label(info_frame, text=''.join([config.db_info_header[number], '\t']), background='white').grid(row=0, column=counter,
																						   sticky='W')
			else:
				ttk.Separator(info_frame, orient='vertical').grid(column=counter, row=0, sticky='ns')
		ttk.Separator(info_frame, orient='horizontal').grid(column=0, row=1, columnspan=len_config_header,
														  sticky='ew')
		db_names = list(self.config_database.keys())
		db_values = list(self.config_database.values())
		for counter in range(len(db_names)):
			file = db_values[counter][4].split(':')
			presentation_list = [db_names[counter], file[0][1], file[1][1], file[2][1], file[3][1], file[4][1], file[5][1],
								 db_values[counter][5], db_values[counter][2], db_values[counter][1], db_values[counter][0]]
			for counter_1 in range(len_config_header):
				if counter_1 % 2 == 0:
					number = int(counter_1 / 2)
					value = presentation_list[number]
					if isinstance(value, bool):
						value = ''
					tk.Label(info_frame, text=''.join([value, '\t']), background='white').grid(
						row=counter+2, column=counter_1,
						sticky='W')
				else:
					ttk.Separator(info_frame, orient='vertical').grid(column=counter_1, row=counter+2,
																	  sticky='ns', rowspan=len_config_header)
		ttk.Button(db_info_window, text='Close', command=lambda: db_info_window.destroy()).grid(row=1)

	### ZAKTUALIZUJ STATUS BAZY DANYCH ###
	def update_database_status(self, counter):
		# Create ŚCIERZKĘ DO BAZY DANYCH #
		db_properties = self.config_database_values[counter]
		if db_properties[3]:
			current_db_files_list = os_listdir(os_path.join(path_to_project, db_properties[2]))
			if len(current_db_files_list) > 0:
				example_file_full_path = os_path.join(path_to_project, db_properties[2], current_db_files_list[0])
			else:
				example_file_full_path = False
		else:
			if db_properties[2]:
				if os_path.isdir(db_properties[2]):
					current_db_files_list = os_listdir(db_properties[2])
					if len(current_db_files_list) > 0:
						example_file_full_path = os_path.join(db_properties[2], current_db_files_list[0])
					else:
						example_file_full_path = False
				else:
					example_file_full_path = False
			else:
				example_file_full_path = False
		# Create ZMIENNE KONFIGURUJĄCE STATUS #
		file_date, foreground, button_name = None, 'black', None
		# JEŻELI BAZA NIE ISTNIEJE, TO ZWRÓĆ ODPOWIEDNI KOMUNIKAT #
		if not example_file_full_path:
			file_date, foreground = 'NOT EXISTS', 'red'
		else:
			button_name = 'Actualize'
			# SPRAWDŹ JAK STARA JEST BAZA DANYCH ZE STRONY #
			current_time = datetime.datetime.now()
			minus_one_day = current_time - datetime.timedelta(days=1)
			minus_week = current_time - datetime.timedelta(days=7)
			minus_month = current_time - datetime.timedelta(days=28)
			file_date = os_path.getmtime(example_file_full_path)
			file_date = datetime.datetime.fromtimestamp(file_date)
			if file_date > minus_one_day:
				foreground = 'green'
			elif file_date < minus_one_day and file_date > minus_week:
				foreground = 'orange'
			elif file_date < minus_week and file_date > minus_month:
				foreground = '#cc3700'
			elif file_date < minus_month:
				foreground = 'red'
			file_date = file_date.strftime(config.datetime_format)
		self.database_status_labels[self.config_database_names[counter]].set(file_date)
		self.db_status[counter].configure(fg=foreground)



	################
	###  WYKRESY ###
	################

	### OHLC ###
	def ohlc_graph(self, window_ohlc_creator=False):
		# ZAŁADUJ DANE Z PLIKU #
		if window_ohlc_creator:
			window_ohlc_creator.destroy()
		data = self.gather_data_from_file(self.choosen_file, self.choosen_file_database)
		ohlc_name = self.choosen_file.split('.')[0]
		ohlc_frame = tk.Toplevel()
		ohlc_frame.resizable(height=True, width=True)
		ohlc_frame.wm_title(ohlc_name)
		# GEOMTERIA OKNA WYKRESU #
		ax1, f = self.graph_geometry(ohlc_frame)
		# WYKRES WŁAŚCIWY #
		candlestick_ohlc(ax1, data.values, width=0.4, colorup=self.settings['color_1'], colordown=self.settings['color_2'])
		# USTAWIENIA WYKRESU #
		self.graph_settings(ax1, f)
		# FINALNE TWORZENIE / RYSOWANIE WYKRESU #
		canvas = self.graph_final_draw(f, ohlc_frame)
		# DODANIE TOOLBARU #
		self.graph_toolbar(ohlc_frame, canvas)
		# DODAWANIE GRAFU JAKO OBIEKT DO LISTY OBIEKTÓW GRAFÓW
		self.currently_opened_graphs.append(Graph('OHLC', ohlc_name, self.choosen_file, self.choosen_file_database, dict(self.settings)))
		ohlc_frame.protocol("WM_DELETE_WINDOW", lambda object=self.currently_opened_graphs[-1], frame=ohlc_frame: self.close_single_graph(object, frame))

	def new_ohlc_creator(self):
		# INICJACJA OKNA #
		window_ohlc_creator = tk.Toplevel()
		window_ohlc_creator.wm_title('New OHLC Graph')
		database_choosen_frame = tk.Frame(window_ohlc_creator, height=2, bd=1, relief='sunken')
		database_choosen_frame.grid(padx=5, pady=5, row=0)
		# MECHANIZM BAZODANOWY I PLIKOWY #
		self.graph_creator_database_files(database_choosen_frame)
		# OPCJE KONFIGURACJI GENERALNYCH #
		self.settings = self.load_graph_settings_from_config()
		self.general_settings(window_ohlc_creator, row_parameter=1, column_parameter=0)
		# OPCJE KONFIGURACJI RESAMPLOWANIA #
		self.data_resample_settings(window_ohlc_creator, row_parameter=3, column_parameter=0)
		# OPCJE KONFIGURACJI / USTAWIEŃ
		settings_frame = tk.Frame(window_ohlc_creator, height=2, bd=1, relief='sunken')
		settings_frame.grid(padx=5, pady=5, row=2, sticky='W')
		# KOLORY #
		tk.Label(settings_frame, text='Kolor UP:').grid(row=1, column=0, sticky='W')
		color_label = tk.Label(settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['color_1'])
		ttk.Button(settings_frame, text="Change", command=lambda: self.change_color(color_label, 'color_1')).grid(row=1, column=2, sticky='W')
		color_label.grid(row=1, column=1, sticky='W')
		tk.Label(settings_frame, text='Kolor DOWN:').grid(row=2, column=0, sticky='W')
		color_label_2 = tk.Label(settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['color_2'])
		ttk.Button(settings_frame, text="Change", command=lambda: self.change_color(color_label_2, 'color_2')).grid(row=2, column=2, sticky='W')
		color_label_2.grid(row=2, column=1, sticky='W')
		# ZATWIERDŹ UTWORZENIE GRAFU / Cancel UTWORZENIU GRAFU #
		create_exit_button_frame = tk.Frame(window_ohlc_creator, height=2, bd=1, relief='sunken')
		create_exit_button_frame.grid(padx=5, pady=5, row=4)
		ttk.Button(create_exit_button_frame, text='Create', command=lambda: self.ohlc_graph(window_ohlc_creator)).grid(row=0, column=0, sticky='W')
		ttk.Button(create_exit_button_frame, text='Cancel', command=lambda: window_ohlc_creator.destroy()).grid(row=0, column=1, sticky='E')


	### ZIGZAG ###
	def zigzag_graph(self, window_zigzag_creator=False):
		# ZAŁADUJ DANE Z PLIKU #
		if window_zigzag_creator:
			window_zigzag_creator.destroy()
		data = self.gather_data_from_file(self.choosen_file, self.choosen_file_database)
		# if self.settings['if_resample']: data = self.resample_data(data)
		zigzag_name = self.choosen_file.split('.')[0]
		zigzag_frame = tk.Toplevel()
		zigzag_frame.resizable(height=True, width=True)
		zigzag_frame.wm_title(zigzag_name)

		# GEOMTERIA OKNA WYKRESU #
		ax1, f = self.graph_geometry(zigzag_frame)
		# WYKRES WŁAŚCIWY #
		ax1.plot(data['Date'], data['Close'], linewidth=self.settings['line_1'], color=self.settings['color_1'])
		# USTAWIENIA WYKRESU #
		self.graph_settings(ax1, f)
		# FINALNE TWORZENIE / RYSOWANIE WYKRESU #
		canvas = self.graph_final_draw(f, zigzag_frame)
		# DODANIE TOOLBARU #
		self.graph_toolbar(zigzag_frame, canvas)
		# DODAWANIE GRAFU JAKO OBIEKT DO LISTY OBIEKTÓW GRAFÓW
		self.currently_opened_graphs.append(Graph('ZIGZAG', zigzag_name, self.choosen_file, self.choosen_file_database, dict(self.settings)))
		zigzag_frame.protocol("WM_DELETE_WINDOW", lambda object=self.currently_opened_graphs[-1], frame=zigzag_frame: self.close_single_graph(object, frame))

	def new_zig_zag_creator(self):
		def enable_window(entry, status):
			print(status.get())
			if status.get():
				entry.config(state='normal')
			else:
				entry.config(state='disabled')
		# INICJACJA OKNA #
		window_zigzag_creator = tk.Toplevel()
		window_zigzag_creator.wm_title('New ZigZag Grph')
		database_choosen_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		database_choosen_frame.grid(padx=5, pady=5, row=0)
		# MECHANIZM BAZODANOWY I PLIKOWY #
		self.graph_creator_database_files(database_choosen_frame)
		# OPCJE KONFIGURACJI GENERALNYCH #
		self.settings = self.load_graph_settings_from_config()
		self.general_settings(window_zigzag_creator, row_parameter=1, column_parameter=0)
		# OPCJE KONFIGURACJI RESAMPLOWANIA #
		self.data_resample_settings(window_zigzag_creator, row_parameter=3, column_parameter=0)
		# OPCJE KONFIGURACJI DLA WYKRESU #
		settings_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		settings_frame.grid(padx=5, pady=5, row=2, sticky='W')
		# KOLOR WYKRESU #
		tk.Label(settings_frame, text='Color:').grid(row=1, column=0, sticky='W')
		color_label = tk.Label(settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['color_1'])
		ttk.Button(settings_frame, text="Change", command=lambda: self.change_color(color_label, 'color_1')).grid(row=1, column=2, sticky='W')
		color_label.grid(row=1, column=1, sticky='W')
		# GRUBOŚĆ LINII #
		linewidth = tk.DoubleVar()
		linewidth.set(self.settings['line_1'])
		tk.Label(settings_frame, text='Line thickness : ').grid(row=2, column=0, sticky='W')
		tk.Scale(settings_frame, variable=linewidth, from_=0, to=3, resolution=0.1, orient='horizontal',
					 command=lambda key=linewidth: self.assign_settings_variable('line_1', linewidth)).grid(row=2, column=1, columnspan=2, sticky='W')
		# # WYPEŁNIENIE GRAFU #
		# if_fullfill = tk.BooleanVar()
		# if_fullfill.set(self.settings['if_fullfill'])
		# ttk.Checkbutton(settings_frame, offvalue=False, onvalue=True, text="Wypełnienie", variable=if_fullfill,
		# 				command=lambda key=if_fullfill: self.assign_settings_variable('if_fullfill', if_fullfill)).grid(row=3, column=0, sticky='W')
		# alpha = tk.DoubleVar()
		# alpha.set(self.settings['alpha'])
		# tk.Label(settings_frame, text='Przezroczystość\nwypełnienia', ).grid(row=4, column=0, sticky='W')
		# tk.Scale(settings_frame, variable=alpha, from_=0, to=1, resolution=0.1, orient='horizontal',
		# 					   command=lambda key=alpha: self.assign_settings_variable('alpha', key)).grid(row=4, column=1, columnspan=2, sticky='W')
		# ZATWIERDŹ UTWORZENIE GRAFU / Cancel UTWORZENIU GRAFU #
		create_exit_button_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		create_exit_button_frame.grid(padx=5, pady=5, row=4)
		ttk.Button(create_exit_button_frame, text='Create', command=lambda: self.zigzag_graph(window_zigzag_creator)).grid(row=0, column=0, sticky='W')
		ttk.Button(create_exit_button_frame, text='Cancel', command=lambda: window_zigzag_creator.destroy()).grid(row=0, column=1, sticky='E')


	### ZIGZAG PODWÓJNY - PORÓWNANIE ###
	def zigzag_comparison_graph(self, window_zigzag_comparison_creator):
		# ZAŁADUJ DANE Z PLIKU #
		window_zigzag_comparison_creator.destroy()
		data_1 = self.gather_data_from_file(self.choosen_file, self.choosen_file_database)
		data_2 = self.gather_data_from_file(self.choosen_file_second, self.choosen_file_second_database)
		zigzag_frame = tk.Toplevel()
		zigzag_frame.wm_title(''.join([ self.choosen_file.split('.')[0], ' + ', self.choosen_file_second.split('.')[0]]))
		# GEOMTERIA OKNA WYKRESU #
		ax1, f = self.graph_geometry(zigzag_frame)
		# WYKRES WŁAŚCIWY #
		ax1.plot(data_1['Date'], data_1['Close'], linewidth=self.settings['line_1'], color=self.settings['color_1'], label=self.choosen_file.split('.')[0])
		ax1.plot(data_2['Date'], data_2['Close'], linewidth=self.settings['line_2'], color=self.settings['color_2'], label=self.choosen_file_second.split('.')[0])
		ax1.legend()
		# USTAWIENIA WYKRESU #
		self.graph_settings(ax1, f)
		# FINALNE TWORZENIE / RYSOWANIE WYKRESU #
		canvas = self.graph_final_draw(f, zigzag_frame)
		# DODANIE TOOLBARU #
		self.graph_toolbar(zigzag_frame, canvas)

	def new_zig_zag_double_creator(self):
		# INICJACJA OKNA #
		window_zigzag_creator = tk.Toplevel()
		window_zigzag_creator.wm_title('New ZigZag Graph')
		database_1_choosen_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		database_1_choosen_frame.grid(padx=5, pady=5, row=0)
		database_2_choosen_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		database_2_choosen_frame.grid(padx=5, pady=5, row=1)
		# MECHANIZM BAZODANOWY I PLIKOWY #
		self.graph_creator_database_files(database_1_choosen_frame)
		self.graph_creator_database_files(database_2_choosen_frame, if_additional=True)
		# OPCJE KONFIGURACJI GENERALNYCH #
		self.settings = self.load_graph_settings_from_config()
		self.general_settings(window_zigzag_creator, row_parameter=2, column_parameter=0)
		# OPCJE KONFIGURACJI / USTAWIEŃ
		settings_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		settings_frame.grid(padx=5, pady=5, row=3,  sticky='W')
		# KOLORY #
		tk.Label(settings_frame, text='Color 1:').grid(row=1, column=0, sticky='W')
		color_label = tk.Label(settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['color_1'])
		ttk.Button(settings_frame, text="Change", command=lambda: self.change_color(color_label, 'color_1')).grid(row=1, column=2, sticky='W')
		color_label.grid(row=1, column=1, sticky='W')
		tk.Label(settings_frame, text='Color 2:').grid(row=2, column=0, sticky='W')
		color_label_2 = tk.Label(settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['color_2'])
		ttk.Button(settings_frame, text="Change", command=lambda: self.change_color(color_label_2, 'color_2')).grid(row=2, column=2, sticky='W')
		color_label_2.grid(row=2, column=1, sticky='W')
		# GRUBOŚĆ LINII #
		linewidth_1 = tk.DoubleVar()
		linewidth_1.set(self.settings['line_1'])
		tk.Label(settings_frame, text='Thickness\nline 1: ').grid(row=1, column=3, sticky='W')
		tk.Scale(settings_frame, variable=linewidth_1, from_=0, to=3, resolution=0.1, orient='horizontal',
					 command=lambda key=linewidth_1: self.assign_settings_variable('line_1', key)).grid(row=1, column=4, columnspan=2, sticky='W')
		linewidth_2 = tk.DoubleVar()
		linewidth_2.set(self.settings['line_2'])
		tk.Label(settings_frame, text='Thickness\nline 2: ').grid(row=2, column=3, sticky='W')
		tk.Scale(settings_frame, variable=linewidth_2, from_=0, to=3, resolution=0.1, orient='horizontal',
					 command=lambda key=linewidth_2: self.assign_settings_variable('line_2', key)).grid(row=2, column=4, columnspan=2, sticky='W')
		# ZATWIERDŹ UTWORZENIE GRAFU / Cancel UTWORZENIU GRAFU #
		create_exit_button_frame = tk.Frame(window_zigzag_creator, height=2, bd=1, relief='sunken')
		create_exit_button_frame.grid(padx=5, pady=5, row=4)
		ttk.Button(create_exit_button_frame, text='Create', command=lambda: self.zigzag_comparison_graph(window_zigzag_creator)).grid(row=0, column=0, sticky='W')
		ttk.Button(create_exit_button_frame, text='Cancel', command=lambda: window_zigzag_creator.destroy()).grid(row=0, column=1, sticky='E')


	### GENERALNE FUNKCJE - KREATOR WYKRESÓW ###
	def gather_data_from_file(self, file, db_name):
		# ZADEKLARUJ NIEZBĘDNE ZMIENNE #
		data = self.config_database[db_name]
		data_config = data[4]
		data_datetime_config = data[5]
		# Create LISTĘ INDEKSÓW OHLC #
		data_config_array = list()
		for line in data_config.split(':'):
			data_config_array.append(int(line[1:]))
		# PRZYGOTUJ ZACZYNĄ DATAFRAME - INDEKSY #
		db_properties = self.config_database[db_name]
		if data[3]:
			full_path = os_path.join(path_to_project, data[2], file)
		else:
			full_path = os_path.join(data[2], file)
		data_readed = pd.read_csv(full_path, header=data_config_array[0]-1)
		for counter, col in enumerate(data_readed.columns):
			data_readed = data_readed.rename(columns={col: counter})
		# PRZEFORMATUJ KOLEJNOŚĆ DATAFRAME U USTAWK KOŃCOWE INDEKSY #
		data_readed = data_readed[data_config_array[1:]]
		for column_name, new_name in zip(data_readed.columns, config.dataframe_column_names):
			data_readed = data_readed.rename(columns={column_name: new_name})
		# PRZYGOTUJ DATĘ DO PREZENTACJI NA GRAFIE #
		date_col_name = config.dataframe_column_names[0]
		if self.settings['if_resample']:
			sampling = config.sampling_types[self.settings['sampling']]
			data_readed.reset_index(inplace=True)
			data_readed.set_index(config.dataframe_column_names[0], inplace=True)
			data_readed.index = pd.to_datetime(data_readed.index, format=data_datetime_config)
			data_readed = data_readed.resample(sampling).mean()
			del data_readed['index']
			data_readed['index'] = range(1, len(data_readed) + 1)
			data_readed.reset_index(inplace=True)
			data_readed.set_index('index', inplace=True)
			data_readed[date_col_name] = mdates.date2num(data_readed[date_col_name])
			return data_readed
		data_readed[date_col_name] = pd.to_datetime(data_readed[date_col_name].astype(str), format=data_datetime_config, errors='raise', yearfirst=True)
		data_readed[date_col_name] = mdates.date2num(data_readed[date_col_name])
		return data_readed

	def graph_creator_database_files(self, popup, if_additional=False):
		# ZAŁADUJ CONFIG BAZY DANYCH #
		self.config_database_names = list(self.config_database.keys())
		self.config_database_values = list(self.config_database.values())
		# LISTA BAZ DANYCH #
		db_list = tk.Listbox(popup, width=30, height=10, exportselection=0)
		loaded_list = tk.Listbox(popup, width=30, height=10, exportselection=0)
		# WYBIERZ OBECNY PLIK I ZWRÓĆ NAZWĘ #
		def CurDBFileSelect(evt, db_content_dict, current_chosen_database_name):
			if not if_additional:
				self.choosen_file = str((loaded_list.get(loaded_list.curselection())))
				self.choosen_file_database = current_chosen_database_name
			else:
				self.choosen_file_second = str((loaded_list.get(loaded_list.curselection())))
				self.choosen_file_second_database = current_chosen_database_name
			if not if_additional:
				if db_content_dict[self.choosen_file]:
					self.choosen_file = ''.join([self.choosen_file, '.', db_content_dict[self.choosen_file]])
			else:
				if db_content_dict[self.choosen_file_second]:
					self.choosen_file_second = ''.join([self.choosen_file_second, '.', db_content_dict[self.choosen_file_second]])
		# PO WYBRANIU BAZY ZAŁADUJ LISTĘ PLIKÓW #
		def CurDBSelet(evt, phrase=False):
			current_chosen_database_name = str((db_list.get(db_list.curselection())))
			self.full_path = os_path.join(path_to_project, self.config_database[current_chosen_database_name][2])
			db_content_dict = dict()
			if os_path.exists(self.full_path):
				db_content = [file.split('.') for file in os_listdir(self.full_path)]
				for line in db_content:
					if len(line) > 1:
						db_content_dict[line[0]] = line[1]
					else:
						db_content_dict[line[0]] = ''
				if phrase:
					db_content = list(filter(lambda file: phrase in file[0], db_content))
				loaded_list.delete(0, 'end')
				for counter, file_name in enumerate(db_content):
					loaded_list.insert(counter, file_name[0])
					loaded_list.bind('<<ListboxSelect>>', lambda arg_1='<<ListboxSelect>>', arg_2=db_content_dict, arg_3=current_chosen_database_name: CurDBFileSelect(arg_1, arg_2, arg_3))
		# ZAŁADUJ LISTĘ WSZYSTKICH BAZ DANYCH #
		for counter, db_name in enumerate(self.config_database_names):
			db_list.insert(counter, db_name)
			db_list.bind('<<ListboxSelect>>', CurDBSelet)
		# MECHANIZM WYSZUKIWANIA #
		tk.Label(popup, text='Search file:').grid(row=0, column=0, sticky='W')
		phrase = tk.StringVar()
		tk.Entry(popup, textvariable=phrase).grid(row=0, column=1, sticky='W')
		ttk.Button(popup, text='Search', command=lambda: CurDBSelet('<<ListboxSelect>>', phrase.get())).grid(row=0, column=1)
		# UMIEŚĆ LISTY NA SIATCE #
		db_list.grid(row=1, column=0, sticky='W')
		loaded_list.grid(row=1, column=1, sticky='W')

	def change_color(self, color_label, color_name):
		color = tk_askcolor()
		self.settings[color_name] = color[1]
		color_label.config(background=self.settings[color_name])

	def assign_settings_variable(self, type, variable):#, entry, status):
		if isinstance(variable, str):
			self.settings[type] = variable
		else:
			self.settings[type] = variable.get()
		# if status.get():
		# 	entry.config(state='normal')
		# else:
		# 	entry.config(state='disabled')

	def general_settings(self, window_creator, row_parameter, column_parameter):
		general_settings_frame = tk.Frame(window_creator, height=2, bd=1, relief='sunken')
		general_settings_frame.grid(padx=5, pady=5, row=row_parameter, column=column_parameter, sticky='W')
		# SIATKA #
		grid = tk.BooleanVar()
		grid.set(self.settings['grid'])
		ttk.Checkbutton(general_settings_frame, offvalue=False, onvalue=True, text="grid", variable=grid,
						command=lambda key=grid: self.assign_settings_variable('grid', key)).grid(row=0, column=0, sticky='W')
		# KOLOR SIATKI #
		tk.Label(general_settings_frame, text='Color:').grid(row=0, column=1, sticky='W')
		color_label = tk.Label(general_settings_frame, text='     ', borderwidth=2, relief="ridge", background=self.settings['grid_color'])
		ttk.Button(general_settings_frame, text="Change", command=lambda: self.change_color(color_label, 'grid_color')).grid(row=0, column=3, sticky='W')
		color_label.grid(row=0, column=2, sticky='W')
		# STYL SIATKI #
		tk.Label(general_settings_frame, text='Style').grid(row=0, column=4, sticky='W')
		avaliable_styles = config.grid_linestyles
		current_style = tk.StringVar()
		current_style.set(self.settings['grid_style'])
		ttk.OptionMenu(general_settings_frame, current_style, current_style.get(), *avaliable_styles,
					   command=lambda key=current_style:self.assign_settings_variable('grid_style', key)).grid(row=0, column=5, sticky='W')
		# GRUBOŚĆ SIATKI #
		tk.Label(general_settings_frame, text='Thickness:').grid(row=0, column=6, sticky='W')
		grid_width = tk.DoubleVar()
		grid_width.set(self.settings['grid_width'])
		tk.Scale(general_settings_frame, variable=grid_width, from_=0, to=1, resolution=0.1, orient='horizontal',
				 command=lambda key=grid_width: self.assign_settings_variable('grid_width', key)).grid(row=0, column=7, sticky='W')

	def data_resample_settings(self, window_creator, row_parameter, column_parameter):
		resample_data_frame = tk.Frame(window_creator, height=2, bd=1, relief='sunken')
		resample_data_frame.grid(padx=5, pady=5, row=row_parameter, column=column_parameter, sticky='W')
		# RESAMPLOWANIE #
		if_resample = tk.BooleanVar()
		if_resample.set(self.settings['if_resample'])
		ttk.Checkbutton(resample_data_frame, offvalue=False, onvalue=True, text="Do resample?", variable=if_resample,
						command=lambda key=if_resample: self.assign_settings_variable('if_resample', key)).grid(row=0, column=0, sticky='W')
		# STYL SIATKI #
		tk.Label(resample_data_frame, text='Sampling: ').grid(row=1, column=0, sticky='W')
		avaliable_samplings = config.sampling_types.keys()
		current_sampling = tk.StringVar()
		current_sampling.set(self.settings['sampling'])
		ttk.OptionMenu(resample_data_frame, current_sampling, current_sampling.get(), *avaliable_samplings,
					   command=lambda key=current_sampling: self.assign_settings_variable('sampling', key)).grid(row=1, column=1, sticky='W')


	def load_graph_settings_from_config(self):
		return config.settings


	### WYKRESY ###
	def graph_geometry(self, graph_frame):
		pad = 3
		frame_geometry = "{0}x{1}+0+0".format(graph_frame.winfo_screenwidth() - pad,
											  graph_frame.winfo_screenheight() - pad)
		x=graph_frame.winfo_screenwidth() - pad
		y=graph_frame.winfo_screenheight() - pad
		graph_frame.focus_set()
		dpi=100
		x = (x / dpi)
		y = (y / dpi) - 1
		graph_frame.geometry(frame_geometry)
		f = Figure(figsize=(x, y), dpi=dpi)
		# style.use('dark_background')
		ax1 = f.add_subplot(111)
		ax1.tick_params(direction='out', length=3, width=0.2, colors='black',
						grid_color='r', grid_alpha=0.5, labelsize=7)
		return ax1, f

	def graph_settings(self, ax1, f):
		for label in ax1.xaxis.get_ticklabels():
			label.set_rotation(20)
		ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
		ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
		if self.settings['grid']:
			ax1.grid(True, color=self.settings['grid_color'], linestyle=self.settings['grid_style'], linewidth=self.settings['grid_width'])
		ax1.axis('auto')
		f.subplots_adjust(left=0.02, bottom=0.05, right=0.98, top=0.98, wspace=0.05, hspace=0.05)

	def graph_final_draw(self, f, ohlc_frame):
		canvas = FigureCanvasTkAgg(f, ohlc_frame)
		canvas.draw()
		canvas.get_tk_widget().grid(row=1)
		return canvas

	def graph_toolbar(self, ohlc_frame, canvas):
		toolbar_frame = tk.Frame(master=ohlc_frame)
		toolbar_frame.grid(row=0)
		NavigationToolbar2Tk(canvas, toolbar_frame)

	def close_single_graph(self, graph_object, frame):
		msg_box = tk.messagebox.askquestion('CloseGraph', 'Are you sure you want to close current window?', icon='warning')
		if msg_box == 'yes':
			self.currently_opened_graphs.remove(graph_object)
			frame.destroy()




	### SESJE ###
	def save_current_session(self, remove_sessions_menu, saved_sessions_menu):
		def save_session(name, window):
			if not self.currently_opened_graphs:
				tk.messagebox.showerror("Error", "Currently you do not have any opened Graphs")
			elif not name:
				tk.messagebox.showerror("Error", "Give the name of saved session")
			sessions_file = shelve.open(os_path.join(path_to_project, config.session_filename))
			sessions_file[name] = self.currently_opened_graphs
			sessions_file.close()
			saved_sessions_menu.add_command(label=name, command=lambda key=name: self.load_session(key))
			remove_sessions_menu.add_command(label=name, command=lambda key=name: self.remove_session(key, remove_sessions_menu, saved_sessions_menu))
			window.destroy()
		# INICJACJA OKNA #
		save_session_window = tk.Toplevel()
		save_session_window.wm_title('Save the session')
		session_name = tk.Frame(save_session_window, height=2, bd=1, relief='sunken')
		session_name.grid(padx=5, pady=5, row=0)
		tk.Label(session_name, text='Session name:').grid(row=0, column=0, sticky='W')
		name_of_session = tk.StringVar()
		tk.Entry(session_name, textvariable=name_of_session).grid(row=0, column=1, sticky='W')
		### PRZYCISKI ZATWIERDZAJĄCE / CancelĄCE ###
		buttons_frame = tk.Frame(save_session_window, height=2, bd=1, relief='sunken')
		buttons_frame.grid(padx=5, pady=5, row=1)
		ttk.Button(buttons_frame, text='Save', command=lambda: save_session(name_of_session.get(), save_session_window)).grid(row=0, column=0)
		ttk.Button(buttons_frame, text='Cancel', command=lambda: save_session_window.destroy()).grid(row=0, column=1)

	def load_session(self, name):
		sessions_file = shelve.open(os_path.join(path_to_project, config.session_filename))
		graphs_to_open = sessions_file[name]
		sessions_file.close()
		for graph in graphs_to_open:
			self.settings = graph.settings
			self.choosen_file = graph.choosen_filename
			self.choosen_file_database = graph.database_name
			if graph.graph_type == 'ZIGZAG':
				self.zigzag_graph()
			if graph.graph_type == 'OHLC':
				self.ohlc_graph()

	def remove_session(self, name, remove_sessions_menu, saved_sessions_menu):
		MsgBox = tk.messagebox.askquestion('Remove session', ''.join(['Are you sure you want to remove session?', name, ' ?']), icon='warning')
		if MsgBox == 'yes':
			sessions_file = shelve.open(os_path.join(path_to_project, config.session_filename))
			sessions_file.pop(name, None)
			sessions_file.close()
			remove_sessions_menu.delete(name)
			saved_sessions_menu.delete(name)





	##################
	### USTAWIENIA ###
	##################

	def return_var(self, var):
		print(var)

	def settings_window(self):
		settings_window = tk.Toplevel()
		settings_window.wm_title('Settings')
		self.settings = self.load_graph_settings_from_config()
		### SIATKA ###
		grid_frame = tk.Frame(settings_window, height=2, bd=1, relief='sunken')
		grid_frame.grid(padx=5, pady=5, row=1)
		grid = tk.BooleanVar()
		grid.set(self.settings['grid'])
		ttk.Checkbutton(grid_frame, offvalue=False, onvalue=True, text="grid", variable=grid).grid(row=0, column=0, sticky='W')
		# KOLOR SIATKI #
		tk.Label(grid_frame, text='Color:').grid(row=0, column=1, sticky='W')
		grid_color = tk.StringVar()
		grid_color.set(self.settings['grid_color'])
		color_label = tk.Label(grid_frame, text='     ', borderwidth=2, relief="ridge",
							   background=grid_color.get())
		ttk.Button(grid_frame, text="Change", command=lambda: self.change_color(color_label, 'grid_color')).grid(row=0, column=3, sticky='W')
		color_label.grid(row=0, column=2, sticky='W')
		# STYL SIATKI #
		tk.Label(grid_frame, text='Style').grid(row=0, column=4, sticky='W')
		avaliable_styles = config.grid_linestyles
		current_style = tk.StringVar()
		current_style.set(self.settings['grid_style'])
		ttk.OptionMenu(grid_frame, current_style, current_style.get(), *avaliable_styles,
					   command=lambda key=current_style:self.assign_settings_variable('grid_style', key)).grid(row=0, column=5, sticky='W')
		# GRUBOŚĆ SIATKI #
		tk.Label(grid_frame, text='Thickness:').grid(row=0, column=6, sticky='W')
		grid_width = tk.DoubleVar()
		grid_width.set(self.settings['grid_width'])
		tk.Scale(grid_frame, variable=grid_width, from_=0, to=1, resolution=0.1, orient='horizontal',
				 command=lambda key=grid_width: self.assign_settings_variable('grid_width', key)).grid(row=0, column=7, sticky='W')

		### USTAWIENIA WYKRESÓW ###
		plot_settings_frame = tk.Frame(settings_window, height=2, bd=1, relief='sunken')
		plot_settings_frame.grid(padx=5, pady=5, row=0)
		tk.Label(plot_settings_frame, text='Graph settings:').grid(row=0)
		# STYLE GRAFÓW
		tk.Label(plot_settings_frame, text='Style').grid(row=1, column=0, sticky='W')
		avaliable_styles = plt.style.available
		current_style = tk.StringVar(settings_window)
		current_style.set(config.current_style)
		ttk.OptionMenu(plot_settings_frame, current_style, *avaliable_styles).grid(row=1, column=1, sticky='W')

		### PRZYCISKI ZATWIERDZAJĄCE / CancelĄCE ###
		buttons_frame = tk.Frame(settings_window, height=2, bd=1, relief='sunken')
		buttons_frame.grid(padx=5, pady=5, row=2)
		ttk.Button(buttons_frame, text='OK', command=lambda: self.return_var(grid.get())).grid(row=0, column=0)
		ttk.Button(buttons_frame, text='Save', command=lambda: print('Save')).grid(row=0, column=1)
		ttk.Button(buttons_frame, text='Cancel', command=lambda: settings_window.destroy()).grid(row=0, column=2)



	################################
	### SAVE / LOAD DB_INFO FILE ###
	################################

	def save_db_info(self):
		with open(os_path.join(path_to_project, config.db_info_filename), 'w') as db_file:
			json.dump(self.config_database, db_file)

	def load_db_info(self):
		with open(os_path.join(path_to_project, config.db_info_filename), 'r') as db_file:
			self.config_database = json.load(db_file)



	#############
	### RÓŻNE ###
	#############

	def quit_warning(self):
		MsgBox = tk.messagebox.askquestion('Close application', 'Do you want to quit?', icon='warning')
		if MsgBox == 'yes':
			if self.currently_opened_graphs:
				sessions_file = shelve.open(os_path.join(path_to_project, config.session_filename))
				sessions_file['ostatnia'] = self.currently_opened_graphs
				sessions_file.close()
			self.destroy()



	###############
	### MENUBAR ###
	###############

	def menubar(self):
		menubar = tk.Menu(self)
		# MENU PLIK #
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label='Exit', command=lambda: self.quit_warning())
		filemenu.add_separator()
		filemenu.add_command(label='Settings', command=lambda: self.settings_window())
		menubar.add_cascade(label='File', menu=filemenu)
		# MENU NOWY GRAF #
		new_graph_menu = tk.Menu(menubar, tearoff=0)
		new_graph_menu.add_command(label='OHLC', command=lambda: self.new_ohlc_creator())
		new_graph_menu.add_command(label='ZigZag', command=lambda: self.new_zig_zag_creator())
		new_graph_menu.add_command(label='ZigZag Compare', command=lambda: self.new_zig_zag_double_creator())
		menubar.add_cascade(label='New Graph', menu=new_graph_menu)
		# SESJE #
		session_menu = tk.Menu(menubar, tearoff=0)
		session_menu.add_command(label='Save current session', command=lambda: self.save_current_session(remove_sessions_menu, saved_sessions_menu))
		menubar.add_cascade(label="Sessions", menu=session_menu)
		# SESJE ZAPISANE #
		sessions_file = shelve.open(os_path.join(path_to_project, config.session_filename))
		saved_sessions = list(sessions_file.keys())
		saved_sessions.sort()
		sessions_file.close()
		saved_sessions_menu = tk.Menu(menubar, tearoff=0)
		remove_sessions_menu = tk.Menu(menubar, tearoff=0)
		for session in saved_sessions:
			saved_sessions_menu.add_command(label=session, command=lambda key=session: self.load_session(key))
			remove_sessions_menu.add_command(label=session, command=lambda key=session: self.remove_session(key, remove_sessions_menu, saved_sessions_menu))
		session_menu.add_cascade(label='Saved sessions', menu=saved_sessions_menu)
		session_menu.add_cascade(label='Remove session', menu=remove_sessions_menu)
		# MENU BAZY DANYCH #
		database_menu = tk.Menu(menubar, tearoff=0)
		database_menu.add_command(label='Add', command=lambda: self.add_database())
		database_menu.add_command(label='Informations', command=lambda: self.db_info())
		menubar.add_cascade(label='Databases', menu=database_menu)
		# KONFIGURUJ MENUBAR DO APLIKACJI #
		tk.Tk.config(self, menu=menubar)



	########################
	### INTERFEJS GŁÓWNY ###
	########################

	def main_window(self, *args, **kwargs):
		### ZAINICJUJ OKNO GŁÓWNE ###
		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, 'GraphDataMarket')
		self.protocol("WM_DELETE_WINDOW", lambda: self.quit_warning())
		### MENUBAR ###
		self.menubar()
		### BAZY DANYCH ###
		counter = self.database_interface()
		### PRZYCISKI KREATORA ###
		ttk.Button(self, text='New OHLC', command=lambda: self.new_ohlc_creator()).grid(row=counter, sticky='W')
		ttk.Button(self, text='New ZigZag', command=lambda: self.new_zig_zag_creator()).grid(row=counter+1,	 sticky='W')
		ttk.Button(self, text='New ZigZag Compare', command=lambda: self.new_zig_zag_double_creator()).grid(row=counter + 2, sticky='W')






#####################
### INICJALIZACJA ###
#####################

app = MainInterface()
app.geometry("525x300")
app.mainloop()
