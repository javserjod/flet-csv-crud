import flet as ft

from typing import Final    # to declare constants

import pandas as pd
#import os

import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart


df_dataset = []             # global variable to store the dataset (pd.Dataframe) MUTABLE
#current_headers = []       # global variable to store the current headers of the dataset (list of headers) MUTABLE
#current_rows = []          # global variable to store the current rows of the dataset   (list of rows) MUTABLE
selected_rows = []          # global variable to store the selected rows of the dataset (list of row indexes) MUTABLE
slider_creation_index = 0   # global variable to store the index selected for the new row creation (int)



snack_bar_duration: Final = 8000   # duration of the snack bar in miliseconds

#--------------------internet--------------------------------------------






'''
            print(page.overlay)
            os.environ["FLET_SECRET_KEY"] = os.urandom(12).hex()
            page.overlay[0].upload(
                        ft.FilePickerUploadFile(
                            e.files[0].name,
                            upload_url=page.get_upload_url(e.files[0].name, 600),
                        )
            )          
'''

    
        

#--------------------MAIN FUNCTION--------------------------------------------

def main(page: ft.Page):
    
    def create_datatable(e: ft.FilePickerResultEvent):  # function to create datatable from selected dataset
        if e.files:
            file_path = e.files[0].path
            print("\n\nSelected file:", file_path)
            global df_dataset
            #global current_headers, current_rows  
            df_dataset = pd.read_csv(file_path)    # asign the dataset to the global variable
   
            # if dataset does not include headers, add default headers to global dataset
            if (check_if_headers_exist()) == False:  
                default_headers = [f"Feature{i}" for i in range(0, len(df_dataset.columns))]  # create default headers
                current_headers = get_headers()    # store the current headers, which will be converted in the first row of data
                df_dataset = df_dataset.set_axis(default_headers, axis="columns")    # change the headers to the default ones           
                df_dataset = pd.concat([pd.DataFrame([current_headers], columns = default_headers), df_dataset], ignore_index=True)   # add the previous headers as the first row
                df_dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers

            datacolumns = create_datacolumns()   # create the DataColumn controls for the datatable
            datarows = create_datarows()         # create the DataRow controls for the datatable
            
            #current_headers = get_headers()   # store the current headers in global variable
            #current_rows = get_rows()         # store the current rows in global variable
    
            _datatable_space.content = ft.DataTable(                 # create the datatable
                                        columns = datacolumns, 
                                        rows = datarows,
                                        bgcolor=ft.colors.BLUE_GREY_800,
                                        heading_row_color = ft.colors.BLUE_GREY_900,
                                        heading_row_height = 70,
                                        horizontal_lines = ft.BorderSide(color=ft.colors.BLUE_GREY_900,
                                                                         width=1),
                                        #horizontal_margin = 30,
                                        show_checkbox_column = True,           # create checkbox column to select rows
                                        checkbox_horizontal_margin = 80,
                                        on_select_all = select_all_rows(),     # checkbox on the header 
                                        column_spacing = 50,
                                        #data_text_style = ft.TextStyle(size=16),                  
                                    )
            _data_window.spacing = 10   # add space between the data window columns once there is a datatable
            
            _data_window.controls[0].content.controls.append(_editing_tools)    # add the editing tools to the page (lower left corner) 
            _menu.tabs[2].content = _graph_window       # add the content to the graph tab
            refresh_info_number_of_rows()                       # show the number of rows in the dataset as info
            
            page.update()
            
            
        else:     # if no file is selected, show error message
            snack_bar_error_upload = ft.SnackBar(content=ft.Text("ERROR: No file selected"),
                                            action="OK", duration= snack_bar_duration)
            page.overlay.append(snack_bar_error_upload)
            page.add(snack_bar_error_upload)
            page.open(snack_bar_error_upload)
            page.update()


    def check_if_headers_exist() -> bool:
        # assume that if the first row contains only numbers, then there is no header
        global df_dataset
        try:
            [float(header) for header in df_dataset.columns]   # try to convert each header to float to check if it is a number
        except ValueError:  # if error occurs, we assume that there is a header, probably a string
            return True     
        return False        # there is no header if the execution was successful


    def create_datacolumns() -> list:
        # returns each feature (columns' names, headers) as a DataColumn
        global df_dataset
        return [ft.DataColumn(  ft.Container(
                                    ft.Text(header, weight = "bold"),
                                    on_click= lambda e, hi=header_index: edit_header(e, hi),
                                    #bgcolor=ft.colors.BLUE_GREY_900,
                                    ink = True,
                                    ink_color = ft.colors.BLUE_GREY_500,
                                    alignment = ft.alignment.center,  # aligned with data cells (they can't be aligned other way)
                                    #margin = ft.margin.only(left=-30),
                                    width = 100,   # width of the column and future textfields  
                                )
                              ) 
                for header_index,header in enumerate(df_dataset.columns)]
    
           
    def create_datarows() -> list:
        # returns each row as a DataRow
        global df_dataset
        rows = []
        for row_index, row in df_dataset.iterrows(): 
            rows.append(ft.DataRow(
                                    cells = [ft.DataCell(
                                                ft.Text(row[header]),
                                                show_edit_icon = False, 
                                                on_tap = lambda e, ri=row_index, hi=header_index: edit_data(e, ri, hi)  #save values for each cell with lambda function
                                                )   
                                            for header_index,header in enumerate(df_dataset.columns)
                                            ],
                                    on_select_changed = lambda e,ri=row_index: row_checkbox_change(e, ri),   # checkbox
                                    )
                        )
        return rows
        
        
    def get_headers() -> list:
        # returns the headers of the dataset as a list of values
        global df_dataset
        return df_dataset.columns.tolist()
            
    def get_rows() -> list:
        # returns the rows of the dataset as a list of list/rows
        global df_dataset
        return df_dataset.values.tolist()
 

    #--------- HEADER EDITING IN DATATABLE FUNCTIONS -------------------------------------
    def edit_header(e, header_index: int) -> None:
        global df_dataset
        old_value = e.control.content.value
        print("\nOld header name: ", old_value)
        e.control.content = ft.TextField(
                                label = old_value,
                                value = "",
                                on_submit = lambda e: save_header_edit(e, header_index, old_value),     # when pressing enter, save the new header name
                                on_blur= lambda e: cancel_header_edit(e, header_index, old_value),                  # when clicking outside the textfield, cancel the changes
                                # textfield width expanded to container (parent) width
                                content_padding=ft.Padding(left=5, top=3, right=5, bottom=3),
                                autofocus=True)                                                                     # Set focus to the TextField                        
        page.update()                                                                                               # update the page to show the textfield instead of the text
        
    def save_header_edit(e, header_index: int, old_value) -> None:
        global df_dataset
        new_value = e.control.value
        print("Proposed new header name: ", new_value)
        
        if (new_value != "") and (new_value not in df_dataset.columns):                                         # if the new value is not empty nor repeated, continue
            df_dataset.rename(columns={old_value: new_value}, inplace=True)                                     # update the dataset with the new header name
            _datatable_space.content.columns[header_index].label.content = ft.Text(new_value, weight="bold")    # update the datatable with the new header name (change textfield to text)
            page.update()                                                                                       # update the page to show the text instead of the textfield
            print(f"Saving renaming of column {header_index}: from \"{old_value}\" to \"{new_value}\"...")      # success message in terminal 
            
            # bug controlling: sometimes the new value is not shown on the datatable, so we force it to be shown
            if _datatable_space.content.columns[header_index].label.content.value == old_value:
                print("Bug happened: ", _datatable_space.content.columns[header_index].label.content.value)
                _datatable_space.content.columns[header_index].label.content.value = new_value       # force the new value to be shown in the text
                print("After bug: ", _datatable_space.content.columns[header_index].label.content.value)
                page.update()
            
        elif new_value == old_value:    # cancel the changes if the new value is the same as the old one
            print("No changes made to the header name.")
            cancel_header_edit(e, header_index, old_value)
            
        else:    # cancel the changes if the new value is empty or repeated and notify the user about error
            print("Error")
            cancel_header_edit(e, header_index, old_value)
            snack_bar_error_header_name = ft.SnackBar(content=ft.Text(f"ERROR: Invalid value name for column {header_index}. Empty or repeated names are not allowed."),
                                            action="OK", duration= snack_bar_duration)
            page.overlay.append(snack_bar_error_header_name)
            page.add(snack_bar_error_header_name)
            page.open(snack_bar_error_header_name)
            
    def cancel_header_edit(e, header_index: int, old_value) -> None:
        _datatable_space.content.columns[header_index].label.content = ft.Text(old_value, weight="bold")
        page.update()                       # update the page to show the text instead of the textfield
    
          
    #--------- DATA EDITING IN DATATABLE FUNCTIONS -------------------------------------    
    def edit_data(e, row_index:int, header_index: int) -> None:
        # function to edit the value of a cell in the datatable, changing the cell to a textfield
        global df_dataset
        old_value = e.control.content.value
        e.control.content = ft.TextField(
                                value = old_value, 
                                on_submit = lambda e: save_data_edit(e, row_index, header_index, old_value),    # when pressing enter, save the new value
                                on_blur= lambda e: cancel_data_edit(e, row_index, header_index, old_value),   # when clicking outside the textfield, cancel the changes
                                #height = 50,
                                #content_padding=ft.Padding(left=5, top=3, right=5, bottom=3),
                                autofocus=True      # Set focus to the TextField
                            )
        page.update()     # update the page to show the textfield instead of the text
        
    
    def save_data_edit(e, row_index: int, header_index: int, old_value) -> None:
        # function to save the changes made in the datatable and revert the textfield to text
        global df_dataset
        #print("\nTypes of the datatable:\n ", df_dataset.dtypes)
        if row_index > 0:   
            comparing_value = df_dataset.iloc[row_index-1, header_index]
        else:
            comparing_value = df_dataset.iloc[row_index+1, header_index]
            
        #expected_type = df_dataset.dtypes.iloc[header_index]    # data type accepted for the column
        #expected_type = type(comparing_value)    
        new_value = e.control.value              # new value to be saved
        try:
            print("\nExpected column type: ", type(comparing_value))   # data type accepted for the column, using other value as reference
            print("Inserted value type: ", type(new_value))
            if type(comparing_value) != str:
                new_value = type(comparing_value)(new_value)   # try to convert the new value to the expected type
                print("Converted successfully to type: ", type(new_value))
            else: 
                print("No need to convert to type: ", type(new_value))
            
            # update the dataset in global variable with the new value
            df_dataset.iloc[row_index, header_index] = new_value          
            # update the datatable with the new value (change textfield to text)
            _datatable_space.content.rows[row_index].cells[header_index].content = ft.Text(new_value)
            page.update()  # update the page to show the text instead of the textfield
            print(f"Saving changes made on row {row_index}, column {header_index}...")   # success message in terminal  
            
            # bug controlling: sometimes the new value is not shown on the datatable, so we force it to be shown
            if _datatable_space.content.rows[row_index].cells[header_index].content.value == old_value:
                print("Bug happened: ", _datatable_space.content.rows[row_index].cells[header_index].content.value)
                _datatable_space.content.rows[row_index].cells[header_index].content.value = new_value       # force the new value to be shown in the text
                print("After bug: ", _datatable_space.content.rows[row_index].cells[header_index].content.value)
                page.update() 
                    
        except ValueError:
            snack_bar_error_edit = ft.SnackBar(content=ft.Text(f"ERROR: Invalid value type for column {header_index}. Inserted: {type(new_value)}. Expected: {type(comparing_value)}"),
                                            action="OK", duration= snack_bar_duration)
            page.overlay.append(snack_bar_error_edit)
            page.add(snack_bar_error_edit)
            page.open(snack_bar_error_edit)
            cancel_data_edit(e, row_index, header_index, old_value)    # abort the changes made, reset to the old value
            
                                                            
    def cancel_data_edit(e, row_index: int, header_index: int, old_value) -> None:
        # reasign the old value to the cell and revert the textfield to text
        _datatable_space.content.rows[row_index].cells[header_index].content = ft.Text(old_value)
        page.update()   # update the page to show the text instead of the textfield
    
    
    
    
    #--------- EDITING TOOLS FUNCTIONS -------------------------------------    
    def refresh_info_number_of_rows() -> None:
        # function to show the number of rows in the dataset
        _editing_tools.content.controls[1].controls[0].value = f"Number of rows: {len(df_dataset)}"   # show the number of rows in the dataset as info
    
    def select_all_rows() -> None:
        # function to select all rows when the header checkbox is clicked
        # it is done automatically by the DataTable control, just executing row_checkbox_change function for each row
        pass
        
    def row_checkbox_change(e, row_index: int) -> None:
        # function to change the checkbox value of a row when clicked and reload the list of selected rows
        global selected_rows
        e.control.selected = not e.control.selected     # alternate the checkbox value when clicked
        
        if e.control.selected:                          # if row gets selected, add its index to list
            selected_rows.append(row_index)
        else:                                           # if row stops being selected, remove its index from list
            selected_rows.remove(row_index)    
        page.update()                                   # update the page to show the changes in checkboxes
        #print("\nSelected rows: ", selected_rows)    
    
    def open_deletion_dialog(e) -> None:
        # function to open the dialog to confirm the deletion of the selected rows, using refreshed value of selected rows
        _deletion_dialog.content = ft.Text("Do you really want to delete all the selected rows?:\n" + str(selected_rows))
        page.open(_deletion_dialog)
        
    def close_deletion_dialog(e) -> None:
        # function to just close the dialog to confirm the deletion of the selected rows
        page.close(_deletion_dialog)
                
    def delete_rows(e) -> None:
        # function to delete the selected rows from the datatable (after clicking Yes on dialog)
        global df_dataset, selected_rows
        close_deletion_dialog(e)    # close the deletion dialog
        #print("\nDeleting rows: " + str(selected_rows))
        #print("\nBefore:", df_dataset)
        df_dataset.drop(selected_rows, axis=0, inplace=True)    # delete the selected rows from the dataset
        df_dataset.reset_index(drop=True, inplace=True)         # reset the index of the dataset, so it starts again from 0 and goes up consecutive numbers
        #print("\nAfter: ", df_dataset)
        reload_datatable_rows()                     # reload the datatable after changes are made (call the function made for this)
    
    
    
    
    def open_creation_dialog(e) -> None:
        # function to open the dialog to confirm the creation of a new row
        _creation_dialog.content = ft.Container(
                                        ft.Column(
                                            controls = [
                                                ft.Slider(
                                                    min=0,                          # index position of start of dataset
                                                    max=len(df_dataset),            # next index after last row of dataset
                                                    divisions=len(df_dataset),      # number of divisions in the slider
                                                    label="{value}",                # label of the slider
                                                    on_change = slider_change,      # function to update the text when slider value changes
                                                ), 
                                                ft.Text(f"Index selected for new row: {0}")    # text, will be refreshed on change of slider
                                                ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        height=200,
                                        width=300,
                                        )
        page.open(_creation_dialog)
    
       
    def close_creation_dialog(e) -> None:
        # function to just close the dialog to confirm the creation of a new row
        page.close(_creation_dialog)

    def slider_change(e) -> None:
        # function to update the label of the slider when its value changes
        global slider_creation_index
        slider_creation_index = int(e.control.value)    #assign the value of the slider to the global variable
        _creation_dialog.content.content.controls[1].value = f"Index selected for new row: {slider_creation_index}"   # show the index selected for the new row
        _creation_dialog.update()   # just update the dialog, not the page
    
    def create_new_row(e) -> None:
        # function to create a new empty row in the datatable
        global df_dataset, slider_creation_index, selected_rows
        close_creation_dialog(e)    # close the creation dialog
        print("Creating new row at index: ", slider_creation_index)
        new_empty_row = pd.DataFrame([["" for _ in range(len(df_dataset.columns))]], columns=df_dataset.columns)   # create a new empty row
        df_dataset = pd.concat([df_dataset.iloc[:slider_creation_index],    # slice the dataset to insert the new row
                                new_empty_row, 
                                df_dataset.iloc[slider_creation_index:]], 
                                ignore_index=True)          # resulting axis will be numbered from 0 to n-1 (reset_index not necessary)
        #df_dataset.reset_index(drop=True, inplace=True)
        reload_datatable_rows()
    
    
    def reload_datatable_rows() -> None:
        # function to reload the datatable rows after changes are made
        global df_dataset, selected_rows
        refresh_info_number_of_rows()                   # reload the number of rows in the dataset shown as info
        selected_rows.clear()                           # clear the list of selected rows
        datarows = create_datarows()                    # create the DataRow controls for the datatable
        _datatable_space.content.rows = datarows        # update the rows of the datatable
        page.update()                                   # update the page to show the changes in the datatable
    
    
    # plotly needs pandas dataframes to plot graphs
    
    
    
    
    
    # Page properties
    page.title = "CSV Labeler"              # title of the page
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = "none"
    page.bgcolor = ft.colors.BLUE_GREY_600        # background color of the page
    page.padding = ft.padding.only(top=0, bottom=10, left=10, right=10)   # padding of the page
    page.window.min_height = 600            # minimum height of the window
    page.window.min_width = 800             # minimum width of the window
    #page.window.icon = 
     
    # AppBar -> App bar at the top of the page with the app title
    page.appbar = ft.AppBar(               # App bar at the top of the page
        title=ft.Text("CSV Labeler", color=ft.colors.WHITE, size=25, weight="w700"),
        center_title=False,
        bgcolor = ft.colors.BLUE_GREY_900,
        )
    
    #----------------- MENU TABS ---------------------------------------------
    # Horizontal navigation menu with tabs
    _menu = ft.Tabs(
                selected_index = 1,    # index of the tab to be selected by default
                animation_duration = 500,    # miliseconds of switching between tabs
                tab_alignment = ft.TabAlignment.START,  # alignment of the tabs
                #divider_height = 2,
                divider_color = page.bgcolor,   # same as background color
                indicator_color = ft.colors.BLUE_GREY_800,
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
            # Left column -> Buttons ............................
            ft.Container(
                ft.Column(
                    controls=[
                        ft.Container(
                            # Upload Data File button goes here
                            bgcolor=ft.colors.BLUE_GREY_800,
                            padding=20,
                            alignment=ft.alignment.center,
                            height = 70,   # same as header of datatable
                        ),
                        
                        # Editing Tools are added here when file is uploaded correctly
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    spacing = 10,
                ),
                #bgcolor = ft.colors.BLUE_GREY_600,   # same as page background color = not asigning color
                expand = 1,   #EXPANDABLE to cover the space left, as the datatable will be static and priorized
                #margin = ft.margin.only(right=10),
            ),
            # Right column -> Data Table ............................
            ft.Container(
                ft.Row(
                    controls = [
                        ft.Column(
                            controls=[
                                ft.Container(
                                    # Data Table goes here
                                    #expand = True,
                                ),
                            ],
                            scroll = "auto",    # Vertical scroll for data table
                        )],
                    scroll = "auto"      # Horizontal scroll for data table
                ),
                #bgcolor = ft.colors.BLUE_GREY_800,    # behind table color, not seen
                #expand = 1,   # STATIC, not expandable but always shown, over the left column
            )
        ],
        alignment=ft.MainAxisAlignment.START,   # Horizontal align of the columns
        spacing = 0,            # Space between the columns when no datatable yet (changed later when datatable is created)
    )

    # Upload Data File button (with its File Picker)
    _datatable_space = _data_window.controls[1].content.controls[0].controls[0]   # Get the space where the datatable will be placed
    file_picker = ft.FilePicker(on_result = lambda e: create_datatable(e))   # create the file picker
    page.overlay.append(file_picker)
    
    _upload_button = ft.ElevatedButton(
                                "Upload Data File",
                                on_click = lambda _: file_picker.pick_files(allow_multiple=False,    # allow only one file to be selected
                                                                            allowed_extensions=["csv"]))   # allow only csv, xls, xlsx files to be selected
    _data_window.controls[0].content.controls[0].content = _upload_button
                            


    _editing_tools = ft.Container(
                            content = ft.Column(    # Left column -> Upload File and Editing Tools
                                controls = [
                                    ft.Row(  # Editing Tools Section Title
                                        controls = [ft.Container(
                                            content = ft.Text("Editing Tools", weight="bold"), 
                                            bgcolor = ft.colors.BLUE_GREY_900,
                                            alignment = ft.alignment.center,
                                            height = 40,
                                            expand = True,   # all section width
                                            )]
                                    ),
                                    ft.Row(
                                        controls = [
                                            ft.Text(),   # number of rows in the dataset, refreshed when rows are deleted or file is uploaded
                                        ],
                                        alignment = ft.MainAxisAlignment.CENTER,
                                        
                                    )
                                    
                                    # Editing Tools buttons go here (shown, added, when file is uploaded correctly)
                                    
                                    ], 
                                alignment = ft.MainAxisAlignment.START,
                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                spacing = 30
                            ),
                            # Delete selected rows from DataTable button goes here
                            bgcolor=ft.colors.BLUE_GREY_800,
                            alignment=ft.alignment.center,
                            expand = True,  # all height of the container   
                        )



    # Create New Row button
    _creation_dialog = ft.AlertDialog(
            modal = False,    # can click outside to dismiss
            title=ft.Text("Choose the index of the new empty row"),
            content= "",   # content will be added in function open_creation_dialog (container with column with slider and text)
            actions=[
                ft.TextButton("Add row at selected index", on_click = create_new_row),      # create new row at index selected in slider
                ft.TextButton("Cancel", on_click = close_creation_dialog),                  # close the dialog
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            #on_dismiss=lambda : page.add(ft.Text("Modal dialog dismissed")),
        )
    
    _create_new_row_button = ft.ElevatedButton(
                                "Create New Row",
                                on_click = open_creation_dialog
                                )
    
    _editing_tools.content.controls.append(_create_new_row_button)
    
    
    
    # Delete Selected Rows button
    _deletion_dialog = ft.AlertDialog(
            modal = False,    # can click outside to dismiss
            title=ft.Text("Please confirm"),
            content= "",   # content added in function open_deletion_dialog, with refreshed selected_rows
            actions=[
                ft.TextButton("Yes", on_click = delete_rows),               # own function to delete the selected rows (also must close the dialog)
                ft.TextButton("No", on_click = close_deletion_dialog),      # just close dialog
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            #on_dismiss=lambda : page.add(ft.Text("Modal dialog dismissed")),
        )
            
    _delete_rows_button = ft.ElevatedButton(
                                "Delete Selected Rows",
                                on_click = open_deletion_dialog)     # open the dialog to confirm the deletion
    
    _editing_tools.content.controls.append(_delete_rows_button)
    
    

    #---------------------GRAPH TAB---------------------------------------------
    _graph_window = ft.Row(
        controls = [
            ft.Container(   # Graph parameters
                ft.Column(   
                    controls = [
                        ft.Text("Parametrization"),
                    ],
                    
                ),
                bgcolor = ft.colors.BLUE_GREY_800,
                expand = 1,
            ),
            ft.Container(   # Graph 
                ft.Column(   
                    controls = [
                        ft.Text("Graph Related Stuff"),
                    ],
                    
                ),
                bgcolor = ft.colors.BLUE_GREY_800,
                expand = 3,
            ),
            ft.Container(   # Labeling Tools
                ft.Column(
                    controls = [
                        ft.Text("Labeling Tools"),
                    ],
                    
                ),
                bgcolor = ft.colors.BLUE_GREY_800,
                expand = 1,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,   # Horizontal align of the columns
        spacing = 10,   # Space between the columns
    )
    
    
    
    
    
    
    
    
    
    
    
    
    #------------- ADD CONTENT TO THE TABS IN MENU---------------------------------------------
    _menu.tabs[0].content = _home_window
    _menu.tabs[1].content = _data_window
    #_menu.tabs[2].content = _graph_window    # the content is added when a dataset is uploaded
    _menu.tabs[2].content = ft.Column(
                    controls=[
                        ft.Container(
                            content = ft.Text(
                                "To generate graphics and label the data, please, upload a file first on the Data Tab.",
                                size = 20,
                            ),
                            bgcolor = ft.colors.BLUE_GREY_800,
                            padding = 20,
                        )
                        
                        # Editing Tools are added here when file is uploaded correctly
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    spacing = 10,
                )
    
    #-------------ADD MENU TO PAGE---------------------------------------------
    page.add(_menu)
    

    page.update()
    

   
if __name__ == "__main__":
    ft.app(target=main, upload_dir="uploads")
    
    

'''if expected_type == 'object':  # expecting a string, negative number, exponential number or complex number
                # pick other value from same column to compare
                print("Comparing value: ", comparing_value)
                print("Comparing value: ", type(comparing_value))   
                if not comparing_value.upper().isupper():    # no letters means it is not string, nor complex nor exponential -> ref: https://stackoverflow.com/questions/9072844/how-can-i-check-if-a-string-contains-any-letters-from-the-alphabet
                    if not new_value.lstrip("-").upper().isupper():  # inserted an accepted type (can be negative value)
                        pass  # allow, do nothing, add as object type
                    else: 
                        raise ValueError
                    
                elif sum(map(str.isalpha, comparing_value)) == 1 and comparing_value.count("e") == 1:   # if exponential number
                    pass 
                elif sum(map(str.isalpha, comparing_value)) == 1 and comparing_value.count("j") == 1:   # if complex number
                    pass
                else:    # other, probably a string
                    pass'''
'''if not new_value.upper().isupper():     # string has no letters -> ref: https://stackoverflow.com/questions/9072844/how-can-i-check-if-a-string-contains-any-letters-from-the-alphabet
                    print("Inserted a string without letters: negative number (not exponential nor complex)")   # assume then it is a negative number
                    raise ValueError          # it is a string composed of numbers
                elif new_value.count("e") == 1 or new_value.count("j") == 1:   # if exponential or complex number
                    pass
                
                else:    # consider as string
                    print("Inserted a string with letters: string, exponential number or complex number") 
                    try:
                        float(new_value):   # check if exponential
                    except:
                        pass'''
            
                        