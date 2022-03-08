from tkinter import ttk
from os import listdir as os_listdir, path as os_path, remove as os_remove
import urllib.request as request
import zipfile
import config

### CONFIG ###
folder_market_data_files = config.folder_market_data_files
path_to_project = config.path_to_project
folder_market_data_full_path = config.folder_market_data_full_path



def return_error_message(popup, main_object, error_text, label_element, button_row):
	main_object.status_informations[label_element].set(error_text)
	main_object.status_labels[label_element].configure(fg='red')
	ttk.Button(popup, text='Break', command=lambda: popup.destroy()).grid(row=button_row, columnspan=2)
	return False



def get_omega_zip_file_from_bossa(database_name, link, destination_folder, popup, main_object):
	current_db_full_path = os_path.join(folder_market_data_full_path, database_name)
	unpack_folder = os_path.join(path_to_project, destination_folder)
	controller = True
	# USUŃ STARĄ BAZĘ DANYCH #
	try:
		main_object.status_informations[0].set('Checking current DB config...')
		if os_path.exists(current_db_full_path):
			os_remove(current_db_full_path)
			main_object.status_informations[0].set('Old DB removed successfully')
		else:
			main_object.status_informations[0].set('Not found previous DB versions')
	except:
		error_text ='Could not removed old DB!'
		controller = return_error_message(popup, main_object, error_text, label_element=0, button_row=9)
	# POBIERZ NOWĄ BAZĘ DANYCH #
	try:
		if controller:
			main_object.status_informations[1].set('Downloading new DB...')
			request.urlretrieve(link, current_db_full_path)
			main_object.status_informations[1].set('New DB downloaded successfully')
	except:
		error_text ='Could not download new DB!'
		controller = return_error_message(popup, main_object, error_text, label_element=1, button_row=9)
	try:
		if controller:
			main_object.status_informations[2].set('Unpacking DB...')
			with zipfile.ZipFile(current_db_full_path, 'r') as unzip_file:
				unzip_file.extractall(unpack_folder)
			main_object.status_informations[2].set('New DB ready for use')
	except:
		error_text ='Could not unpack new DB!'
		controller = return_error_message(popup, main_object, error_text, label_element=2, button_row=9)


def choose_proper_download_function(database_name, link, script, destination_folder, popup, main_object):
	if script == 'get_omega_zip_file_from_bossa':
		get_omega_zip_file_from_bossa(database_name, link, destination_folder, popup, main_object)

