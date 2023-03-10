import tkinter as tk



def make_colab():
    global var, button
    civitlink = var.get()
    button.destroy()
    #https://github.com/etherealxx
    import os
    # import shlex
    import requests
    import tempfile
    import re
    import json
    from time import sleep
    # import nbformat
    curdir = os.getcwd()

    #check if this line exist, then will add a the new line below
    # linetocheck = '!git clone https://github.com/jexom/sd-webui-depth-lib'
    # civitlink = input("Copy the civit model link here: \n")
    linetocheck = '!git reset --hard'
    #new line to add
    #linetoadd = f'!git clone https://github.com/etherealxx/batchlinks-webui /content/stable-diffusion-webui/extensions/batchlinks-webui'
    addafter = True #if false then addbefore
    howmuch = 1  #how much line after addafter

    if addafter == True:
        valuetoadd = int(1+howmuch)
    else:
        valuetoadd = int(0)

    def calculatetabs(linetocalculate):
        indentation = 0
        for char in linetocalculate:
            if char == " ":
                indentation += 1
            elif char == "\t":
                indentation += 4 - (indentation % 4)
            else:
                break
        return indentation

    def addtabs(howmanyindent, allspace=False):
        spaces = howmanyindent % 4
        #print(spaces)
        tabs = (howmanyindent - spaces) / 4
        #print(tabs)
        finalindent = str()
        if allspace:
            for _ in range(int(howmanyindent)):
                finalindent += " "
        else:
            for _ in range(int(tabs)):
                finalindent += "\t"
            for _ in range(int(spaces)):
                finalindent += " "
        return finalindent

    #civitgetlink
    m = re.search(r'https://civitai.com/models/(\d+)', civitlink)
    model_id = m.group(1)

    api_url = "https://civitai.com/api/v1/models/" + model_id

    txt = requests.get(api_url).text
    model = json.loads(txt)

    save_directory = '/content/stable-diffusion-webui/models/Stable-diffusion'

    data_url = model['modelVersions'][0]['files'][0]['downloadUrl']
    data_filename = model['modelVersions'][0]['files'][0]['name']

    linetoadd = (
        "!aria2c --console-log-level=error "
        "-c -x 16 -s 16 -k 1M "
        f"{data_url} "
        f"-d {save_directory} "
        f"-o {data_filename}"
    )

    basenotebook = 'https://raw.githubusercontent.com/camenduru/stable-diffusion-webui-colab/main/v1.9/7th_layer_webui_colab.ipynb'
    # nbfile = basenotebook.rsplit("/")[-1]
    response = requests.get(basenotebook)
    content = response.text

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file.close()

        with open(temp_file.name, 'r') as f:
            lines = f.readlines()
        linefound = False
        for i, line in enumerate(lines.copy()):
            #print(line)
            #print(str(i) + " " + str(line))
            if i >= 1:
                if line.strip().startswith(f"\"{linetocheck}"):
                    linefound = True
                    if not lines[i+valuetoadd].strip().startswith(f"\"{linetoadd}"):
                        indent = calculatetabs(line)
                        newline = addtabs(indent, True) + f"\"{linetoadd}\\n\","
                        lines.insert(i+valuetoadd, f"{newline}\n")
                        with open(temp_file.name, 'w') as f:
                            f.write(''.join(lines))
                            notebookname = os.path.splitext(data_filename)[0]
                            userprofile = os.environ['USERPROFILE']
                            downloadfolder = os.path.join(userprofile, "Downloads")
                            new_filename = os.path.join(downloadfolder, f"{notebookname}_webui_colab.ipynb")
                            f.close()
                            import shutil
                            shutil.move(f.name, new_filename)
                        result_label = tk.Label(root, text=f"{notebookname}_webui_colab.ipynb created!")
                        result_label.pack()
                        print(f'Added the required line to the notebook {notebookname}_webui_colab.ipynb.')
                        sleep(2)
                        os.system(f"explorer.exe {downloadfolder}")
                    else:
                        print(f'The notebook {data_filename} already contains the required line.')
        if linefound == False:
            print(f'The required cell was not found in the notebook {data_filename}.')


root = tk.Tk()
root.withdraw() # Hide the window initially

root_width = root.winfo_screenwidth()
root_height = root.winfo_screenheight()

window_width = 370
window_height = 120

x_pos = int((root_width - window_width) / 2)
y_pos = int((root_height - window_height) / 2)

root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_pos, y_pos))
root.title("civit2camencolab")

label = tk.Label(root, text="Copy the civit model link here:")
label.pack(pady=5)

var = tk.StringVar()
textbox = tk.Entry(root, textvariable=var, width=40)
textbox.pack()

button = tk.Button(root, text="Make Colab", command=make_colab)
button.pack(pady=5)

root.deiconify() # Show the window after it has been centered

root.mainloop()
