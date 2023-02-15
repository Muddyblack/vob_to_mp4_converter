import os, sys
import subprocess


def read_file(file_path):
    with open(file_path, "r") as f:
        txt_lines = f.readlines()

        for r in range(len(txt_lines)):
            txt_lines[r]= txt_lines[r].replace('\n','')

    return txt_lines

# how to use : file_text_replacer(path_of_file, [stringtext], [inline_as_integer_number])
def file_line_replacer(file, change_input, line):
    
    data = read_file(file)

    for pointing,x in enumerate(change_input):
        try:
            data[line[pointing]-1] = change_input[pointing]
        except:
            data.append("")


    with open(file, 'w', encoding="utf8") as file_to_replace:
        data_len = len(data)

        for x in data:
            if data_len > 1:
                file_to_replace.writelines(f"{x}\n")
            else:
                file_to_replace.writelines(f"{x}")
            
            data_len-=1

# ask user for the path where to convert the Videos
def pathgetter():
    global path, one_file

    command_list = ['-options', '-help', '-exit']
    suboptions_list=  ['-disable_nvidia', '-enable_nvidia', '-set_v_format', '-copy_audio', '-encode_audio']

    path = str(input(" Enter the full Path!\n  >>"))

    #If it is no absolute path #and no option --> then ask until it is
    while(os.path.isabs(path) == False and str(path) not in command_list):
        path = str(input("--------------------------\nno absolute Path try again\n--------------------------\n EXAMPLE: F:\TEST\Videos\DV YEARXYZ \n  >>"))
    
    if os.path.isdir(path):
        one_file = False
    else:
        one_file = True
    
    #options
    if(path == command_list[0]): #-options
        global ffmpeg_extra_p1, ffmpeg_extra_p2, ffmpeg_audio_coding
        global video_extension

        option = str(input("  enter the option-command\n   >>"))
        while(option not in suboptions_list):
            if(option == '-continue'):
                starter()
            else :
                print(f"  -----------------------------------------------------\n  no such command: {option}\n  Enter correct command or '-continue' to continue\n  -----------------------------------------------------")
                option = str(input("  enter the option-command\n   >>"))
        if(option == suboptions_list[0]): #-disable_nvidia
            ffmpeg_extra_p1 = ''
            ffmpeg_extra_p2 = '-c:v libx264 -vf yadif=1 '
            file_line_replacer(options_log_path, [ffmpeg_extra_p1,ffmpeg_extra_p2] , [1,2])

        elif(option == suboptions_list[1]): #-enable_nvidia
            ffmpeg_extra_p1 = ' -hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda'
            ffmpeg_extra_p2 = '-c:v h264_nvenc -vf yadif_cuda=1 '
            file_line_replacer(options_log_path, [ffmpeg_extra_p1,ffmpeg_extra_p2] , [1,2])
        
        elif(option == suboptions_list[2]): #set-v-format
            video_extension = str(input(" Enter the desired format:\n NOT YET FINISHED OPTION\n  >>"))
            file_line_replacer(options_log_path, [video_extension] , [3])
        
        elif(option == suboptions_list[3]): #-copy_audio
            ffmpeg_audio_coding = '-c:a copy'
            file_line_replacer(options_log_path, [ffmpeg_audio_coding] , [4])
        
        elif(option == suboptions_list[4]): #-encode_audio
            ffmpeg_audio_coding = '-c:a aac'
            file_line_replacer(options_log_path, [ffmpeg_audio_coding] , [4])


        print(f"  -------------------------------------------------\n  changed: {option}\n  -------------------------------------------------")
        starter()
    elif(path == command_list[1]): #-help
        helplist = ""
        helplist_suboptions = ""
        for i in range(len(command_list)): 
            helplist += f"   {command_list[i]} \n"
        for i in range(len(suboptions_list)): 
            helplist_suboptions += f"   {suboptions_list[i]} \n"


        print(f"------------\nMain commands\n------------\n {helplist}")
        print(f"-----------------\ncommands for -options\n-----------------\n {helplist_suboptions}")
        starter()
    elif(path == command_list[2]): #-exit
        sys.exit()

#get folder content
def write_ffmpeg_code(index, content_list):
    if index == None :
        index = ""
    else:
        index = "_part_" + str(index+1)

    #put the ffmpeg code together
    ffmpeg_code = f'"{current_absolute_script_path}"{ffmpeg_extra_p1} -i "concat:'  #
    for i in range(len(content_list)):
       ffmpeg_code += f"{content_list[i]}|"
       if i == len(content_list)-1:
           ffmpeg_code = ffmpeg_code[:-1]
    
    base_name = os.path.basename(os.path.normpath(path)).replace(" ", "_")
    ffmpeg_code += f'" {ffmpeg_audio_coding} {ffmpeg_extra_p2} {base_name}{index}{video_extension}'
    #end
    return(ffmpeg_code)

def one_file_code():
    print("go")
    code_list = []

    file_name = os.path.basename(os.path.normpath(path))
    ffmpeg_code = f'"{current_absolute_script_path}"{ffmpeg_extra_p1} -i {file_name} {ffmpeg_audio_coding} {ffmpeg_extra_p2}{file_name[:-4]}{video_extension}'
    code_list.append(str(ffmpeg_code))
    
    return code_list

def get_code_list():
    #dec
    content_list = []
    vid_parts_list = []

    #get folders content
    for file in os.listdir(path):
        if file.endswith(".VOB") or file.endswith(".vob"):
            if ("VIDEO_TS.VOB" or "VIDEO_TS.vob" or "video_ts.vob") not in file:
                content_list.append(file)   #absolute path: os.path.join(path, file)


    try:
        #get number of different video parts
        for i in range(len(content_list)):
            vid_parts_list.append(content_list[i][:-5])
            int(content_list[i][4:-6])
        non_standard = False
    except:
        print("No standard naming -> Merging to ONE file")
        non_standard = True

    #get different codes
    code_list = []

    if non_standard == True:
        code_list.append(write_ffmpeg_code(None, content_list))
    else:
        vid_parts_list = sorted(set(vid_parts_list), key=vid_parts_list.index)
        vid_parts_number = len(vid_parts_list)

        for i in range(vid_parts_number):
            part_list = [j for j in content_list if vid_parts_list[i] in j]

            code_list.append(write_ffmpeg_code(i, part_list))

    return(code_list)

def start_process(code_list):
    if one_file == True:
        os.chdir(os.path.dirname(path))
    else: 
        os.chdir(path)

    for i in range(len(code_list)):
        subprocess.call(code_list[i]) #, creationflags=subprocess.CREATE_NEW_CONSOLE

    print('finished')

#start CORE
#set terminal presets
os.system('color 9') 
#standard vars && create standard log if not existing
options_log_path = os.path.dirname(os.path.abspath(__file__)) + "\\options.log"

try:
    f = open(options_log_path)
    # Do something with the file
except IOError:
    print("creating new standard log")
    f = open(options_log_path, 'w')
    f.write(" -hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda\n"+
            "-c:v h264_nvenc -vf yadif_cuda=1 \n"+
            ".mp4\n"+
            "-c:a copy\n"+
            "multifileconverting")
finally:
    f.close()

log_list = read_file(options_log_path)
ffmpeg_extra_p1 = log_list[0]
ffmpeg_extra_p2 = log_list[1]
video_extension = log_list[2]
ffmpeg_audio_coding = log_list[3]

print(log_list)
#get absolute path of .exe or .py
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable) #.exe
elif __file__:
    application_path = os.path.dirname(__file__) #.py/.pyw

#set path where to find app ffmpeg
current_absolute_script_path = str(application_path).replace('\\', '\\\\') + "\\ffmpeg\\ffmpeg.exe"
#check if app ffmpeg exists else try to use environment variables
if(os.path.isfile(current_absolute_script_path)==False):
    current_absolute_script_path = str("ffmpeg")

print(f"\n Using:{current_absolute_script_path}\n\n Now starting converting")

#loop the script
def starter():
    try:
        pathgetter()
        if one_file == False:
            code_list = get_code_list()
        elif one_file == True:
            code_list = one_file_code()
        
        #if no VOB in folder ask again
        while(len(code_list) == 0):
            print("----------------------------\nERROR NO VOB FILES IN FOLDER \n----------------------------")
            pathgetter()
            code_list = get_code_list()
        print(code_list)
        start_process(code_list)
        starter()
    except Exception as e:
        print("--------------------------------------------------------------------------------------------\nError Message:")
        print(e)
        print("\nClose the window and fix the code!\n--------------------------------------------------------------------------------------------\n")
        starter()


if __name__ == "__main__":
    starter()
