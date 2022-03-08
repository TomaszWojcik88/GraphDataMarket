from os import path as os_path

databases = {
				'omegacgl.zip': ('https://info.bossa.pl/pub/ciagle/omega/omegacgl.zip', 'get_omega_zip_file_from_bossa', 'bossa_files', True, 'L1:D1:O2:H3:L4:C5', '%Y%m%d'),
				'omegaobl.zip': ('https://info.bossa.pl/pub/ciagle/omega/omegaobl.zip', 'get_omega_zip_file_from_bossa', 'bossa_omega_obl_files', True, 'L1:D1:O2:H3:L4:C5', '%Y%m%d'),
				'metaobl.zip': ('https://info.bossa.pl/pub/ciagle/mstock/metaobl.zip', 'get_omega_zip_file_from_bossa', 'meta_obl', True, 'L1:D1:O2:H3:L4:C5', '%Y%m%d'),
} # END OF DATABASES #

settings = {'color_1': '#77d879', 'color_2': '#db3f3f', 'grid': True, 'grid_color': 'gray', 'grid_style': '--', 'grid_width': 0.5, 'line_1': 0.5, 'line_2': 0.5, 'if_resample': False, 'sampling': 'Yearly'}
grid_linestyles = ['-', '--', '-.', ':']
datetime_format = '%d/%m/%Y   %H:%M:%S'
date_format = '%Y-%m-%d'
dataframe_column_names = ['Date', 'Open', 'High', 'Low', 'Close']
current_style = ''
db_info_filename = 'db_info.json'
db_info_header = ['Name', 'Header', 'Data', 'Open', 'High', 'Low', 'Close', 'Time format', 'Destination folder', 'Download script', 'Link']
session_json_folder = 'sessions'
session_filename = 'sessions.db'
sampling_types = {
					'Yearly': 'A',
					'Monthly': 'M',
					'Weekly': 'W'
					}


folder_market_data_files = 'market_files'
path_to_project = os_path.dirname(os_path.realpath(__file__))
folder_market_data_full_path = os_path.join( path_to_project, folder_market_data_files )


grid = True
