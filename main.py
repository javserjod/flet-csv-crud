import flet as ft

import pandas as pd

import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart


global df_dataset    # global variable to store the dataset
global current_headers      # global variable to store the current headers of the dataset (list of headers)
global current_rows          # global variable to store the current rows of the dataset   (list of rows)

#--------------------FUNCTIONS--------------------------------------------

def create_datatable(page, e: ft.FilePickerResultEvent, _datatable_space):  # function to create datatable from selected dataset
        if e.files:
            file_path = e.files[0].path
            print("Selected file:", file_path)
            df_dataset = pd.read_csv(file_path)    # asign the dataset to the global variabl
            
            # if dataset does not include headers, add default headers to global dataset
            if (check_if_headers_exist(df_dataset)) == False:  
                default_headers = [f"Feature{i}" for i in range(0, len(df_dataset.columns))]  # create default headers
                current_headers = get_headers(df_dataset)    # store the current headers, which will be converted in the first row of data
                df_dataset = df_dataset.set_axis(default_headers, axis="columns")    # change the headers to the default ones           
                df_dataset = pd.concat([pd.DataFrame([current_headers], columns = default_headers), df_dataset], ignore_index=True)   # add the previous headers as the first row
                df_dataset.reset_index()   # reset the index of the dataset    

            datacolumns = create_datacolumns(df_dataset)   # create the DataColumn controls for the datatable
            datarows = create_datarows(df_dataset)         # create the DataRow controls for the datatable
            
            current_headers = get_headers(df_dataset)   # store the current headers in global variable
            current_rows = get_rows(df_dataset)         # store the current rows in global variable
    
            _datatable_space.content = ft.DataTable(                 # create the datatable
                                        columns = datacolumns, 
                                        rows = datarows,
                                        heading_row_color = ft.colors.BLUE_GREY_900,
                                        heading_row_height = 70                
                                    )   
            page.update()
            
        else:
            snack_bar_error_upload = ft.SnackBar(content=ft.Text("ERROR: No file selected"),
                                            action="OK",)
            page.overlay.append(snack_bar_error_upload)
            page.add(snack_bar_error_upload)
            page.open(snack_bar_error_upload)
            page.update()


def check_if_headers_exist(df_dataset: pd.DataFrame) -> bool:
    # assume that if the first row contains only numbers, then there is no header
    try:
        [float(header) for header in df_dataset.columns]   # try to convert each header to float to check if it is a number
    except ValueError:  # if error occurs, we assume that there is a header, probably a string
        return True     
    return False        # there is no header if the execution was successful


def create_datacolumns(df_dataset: pd.DataFrame) -> list:
    # returns each feature (columns' names, headers) as a DataColumn
    return [ft.DataColumn(ft.Text(header)) for header in df_dataset.columns]
    
def create_datarows(df_dataset: pd.DataFrame) -> list:
    # returns each row as a DataRow
    rows = []
    for _, row in df_dataset.iterrows():
        rows.append(ft.DataRow(cells = [ft.DataCell(ft.Text(row[header])) for header in df_dataset.columns]))
    return rows


def get_headers(df_dataset: pd.DataFrame) -> list:
    # returns the headers of the dataset as a list of values
    return df_dataset.columns.tolist()
    
def get_rows(df_dataset: pd.DataFrame) -> list:
    # returns the rows of the dataset as a list of list/rows
    return df_dataset.values.tolist()

    
        

#--------------------MAIN FUNCTION--------------------------------------------
def main(page: ft.Page):
    # Page properties
    page.title = "CSV Labeler"              # title of the page
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "none"
    page.bgcolor = ft.colors.BLUE_GREY_600        # background color of the page
    page.padding = 10
    
    page.window.min_height = 600            # minimum height of the window
    page.window.min_width = 800             # minimum width of the window
    #page.window.icon = 
     
    # AppBar -> App bar at the top of the page with the app title
    page.appbar = ft.AppBar(               # App bar at the top of the page
        title=ft.Text("CSV Labeler", color=ft.colors.WHITE, size=25, weight="w700"),
        center_title=False,
        bgcolor = ft.colors.BLUE_GREY_900,
        )
    
    # Tabs -> Horizontal navigation menu with tabs
    _menu = ft.Tabs(
                selected_index = 1,    # index of the tab to be selected by default
                animation_duration = 500,    # miliseconds of switching between tabs
                tab_alignment = ft.TabAlignment.START,  # alignment of the tabs
                #divider_height = 2,
                divider_color = page.bgcolor,   # same as background color
                indicator_padding = 5,
                indicator_tab_size = True,   # For indicator to take entire tab
                
                tabs = [
                    ft.Tab(
                        text = "Home",
                        icon = ft.icons.HOME,
                    ),
                    ft.Tab(
                        text = "Data",
                        icon = ft.icons.DATASET_OUTLINED, 
                    ),
                    ft.Tab(
                        text = "Graph",
                        icon = ft.icons.AUTO_GRAPH
                    ),
                ],
                expand = True
        )
    
    
    #-------------HOME TAB---------------------------------------------
    _home_window = ft.Container(
                            content = ft.Text("This is Tab 1"), 
                            alignment = ft.alignment.center
                        )
    
    
    
    
    #-------------DATA TAB---------------------------------------------
    _data_window = ft.Row(
        controls=[
            # Left column -> Buttons
            ft.Container(
                ft.Column(
                    controls=[
                        ft.Container(
                            # Upload Data File button goes here
                            bgcolor=ft.colors.BLUE_GREY_800,
                            padding=10,
                            alignment=ft.alignment.center,
                            expand=1,  # 1/4 of the left column height for the button
                        ),
                        ft.Container(
                            bgcolor=ft.colors.BLUE_GREY_800,
                            content=ft.Text("Editing Tools"),
                            alignment=ft.alignment.center,
                            expand=4,  # 4/4 of the left column height for the editing tools   
                        ),
                    ],
                    alignment=ft.alignment.center,
                    spacing = 10,
                ),
                bgcolor = ft.colors.BLUE_GREY_600,
                expand = 1,
                #margin = ft.margin.only(right=10),
            ),
            # Right column -> Data Table
            ft.Container(
                ft.Row(
                    controls = [
                        ft.Column(
                            controls=[
                                ft.Container(
                                    # Data Table goes here
                                    bgcolor=ft.colors.BLUE_GREY_800,
                                    #expand = True,
                                ),
                            ],
                            scroll = "auto",    # Vertical scroll for data table
                        )],
                    scroll = "auto"      # Horizontal scroll for data table
                ),
                bgcolor = ft.colors.BLUE_GREY_800,
                #expand=1,   # 3/4 of the page width for the right column
            )
        ],
        alignment=ft.MainAxisAlignment.START,   # Horizontal align of the columns
        spacing = 10,   # Space between the columns
        #expand=True,
    )



    # FilePicker of the Upload Data from File button
    _datatable_space = _data_window.controls[1].content.controls[0].controls[0]   # Get the space where the datatable will be placed
    file_picker = ft.FilePicker(on_result = lambda e: create_datatable(page, e, _datatable_space))   # create the file picker
    page.overlay.append(file_picker)
    
    
    # Upload Data File button
    _upload_button = ft.ElevatedButton(
                                "Upload Data File",
                                on_click = lambda _: file_picker.pick_files(allow_multiple=False,    # allow only one file to be selected
                                                                                allowed_extensions=["csv"]))   # allow only csv, xls, xlsx files to be selected
    _data_window.controls[0].content.controls[0].content = _upload_button
                            

    # Edit datatable





    #---------------------GRAPH TAB---------------------------------------------
    _graph_window = ft.Text("This is Tab 3")
    
    
    
    
    
    
    
    
    
    
    
    
    #-------------ADD TABS TO MENU---------------------------------------------
    _menu.tabs[0].content = _home_window
    _menu.tabs[1].content = _data_window
    _menu.tabs[2].content = _graph_window
    
    
    #-------------ADD MENU TO PAGE---------------------------------------------
    page.add(_menu)
    

    page.update()
    

   
if __name__ == "__main__":
    ft.app(target=main, upload_dir="uploads")
    
    
    
   
'''


def updateOnTap(e):
       e.control.content.value = "Hello John"
       page.update()
       
       
ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("First name")),
                            ft.DataColumn(ft.Text("Last name")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("John"), show_edit_icon=True, on_tap=updateOnTap),
                                    ft.DataCell(ft.Text("Smith")),
                                ],
                            ),
                        ],
                    ),
'''