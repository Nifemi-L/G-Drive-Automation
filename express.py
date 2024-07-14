from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os 
import datetime
from tkinter import Tk, Entry, Button, messagebox, Toplevel, BooleanVar

def main(): 
    root = Tk()  # initialize root window
    root.withdraw() # hide root window

    response = messagebox.askyesno("Inquiry", "Choose photos taken today?", parent=root)
    if response:
        current_date = datetime.date.today()
        date_entry = current_date.strftime('%Y_%m_%d') # format date to match EOS Utility convention
        
        print(f"Date: {date_entry}")
    else:
        date_entry = query_user("Enter desired date (yyyy_mm_dd)", "date", root)

    folder_entry = query_user("Enter desired folder name", "folder", root)

    parent_dir = "C:\\Users\\lawal\\Pictures\\Canon"
    working_dir = f'{parent_dir}\{date_entry}' # find desired path
    new_dir = f'{parent_dir}\{folder_entry}' # construct preferred path

    if os.path.exists(working_dir): 
        print(f"Path found at: {working_dir}\n")
        rename_directory(working_dir, new_dir)

        # API
        creds = authenticate()
        folder_id = create_folder(folder_entry, '1P2WI8l-nplK0OcG-tDAM1BgLXbV3s-tb', creds)

        # upload files to folder
        for file_name in os.listdir(new_dir): 
            upload_file(file_name, new_dir, folder_id, creds)
        show_message("Success", "Files successfully uploaded to google drive")
    else:
        messagebox.showerror("Error", f"Path '{working_dir}' was not found")

def query_user(title, marker, root): 
    """Display a dialog box that queries user."""
    # use toplevel to create seperate window independent of root window
    win = Toplevel(root)

    # set the title of the window
    win.title(title)

    # synchronization mechanism to wait for the user action 
    done = BooleanVar(value=False)

    # obtain screen information
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # set window size
    window_width = 350
    window_height = 100 

    # calculate x and y coordinates
    x = (screen_width / 2) - (window_width / 2) 
    y = (screen_height / 2) - (window_height / 2)

    # set the window's geometry to center it
    win.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

    win.title(title)

    return_val = []

    def myClick():
        """Print log and destroy window."""
        if marker == "date": 
            print(f"\nDate (current folder name): {input.get()}")
        elif marker == "folder": 
            print(f"Desired folder name: {input.get()}")

        return_val.append(input.get().strip())
        done.set(True)
        win.destroy()
     
    # create an input widget
    input=Entry(win, width=50, font=('Arial 24'))
    input.pack(padx=10, pady=10)

    # create a button
    button=Button(win, text="Submit", command=myClick)
    button.pack(pady=10)

    win.wait_variable(done) # wait until 'done' is true
    return return_val[0] if return_val else None

def rename_directory(old_dir, new_dir):
    """Rename a given directory."""
    os.rename(old_dir, new_dir)
    show_message("Update", f"'{old_dir}' successfully renamed to {new_dir}\n")

def show_message(title, message): 
    messagebox.showinfo(title, f'{message}')

# API
def authenticate():
    """Authenticate request."""
    SCOPES = ['https://www.googleapis.com/auth/drive']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=65258)  # using a fixed port number
    return creds

def create_folder(name, parent_id, creds):
    """Create folder."""
    service = build('drive', 'v3', credentials=creds)
    file_metadata = { 
        'name': name, 
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def upload_file(file_name, parent_dir, folder_id, creds):
    service = build('drive', 'v3', credentials=creds)
    file_path = os.path.join(parent_dir, file_name)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    try:
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'Uploaded file ID: {file.get("id")}')
    except Exception as e:
        print(f'Failed to upload {file_name}: {e}')
main()