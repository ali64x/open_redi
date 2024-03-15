import subprocess
import os
import sys 
import time
import argparse
import requests
from termcolor import colored
import threading
from concurrent.futures import ThreadPoolExecutor

output_lock = threading.Lock()
output_lock2 = threading.Lock()

#tools paths
# httpx_exe_file = os.path.join(os.path.dirname(__file__),"httpx", "httpx.exe")
does_m_file= os.path.join(os.path.dirname(__file__),"does_m.cpp")
does_m_executable = os.path.join(os.path.dirname(__file__),"does_m.exe")
paramhunter_exe = os.path.join(os.path.dirname(__file__),"paramhunter.exe")
paramhunter_file = os.path.join(os.path.dirname(__file__),"paramhunter.cpp")
merge_file = os.path.join(os.path.dirname(__file__),"merge.cpp")
merge_exe = os.path.join(os.path.dirname(__file__),"merge.exe")

#output paths
meregd_files_out = os.path.join(os.path.dirname(__file__),"result_files","merged_files_out.txt")
does_m_out = os.path.join(os.path.dirname(__file__),"result_files","does_m_out.txt")
waymore_out = os.path.join(os.path.dirname(__file__),"result_files","waymore_out.txt")
waybackurl_out = os.path.join(os.path.dirname(__file__),"result_files","waybackurl_out.txt")
hakrawler_out = os.path.join(os.path.dirname(__file__),"result_files","hakrawler_out.txt")
gau_out = os.path.join(os.path.dirname(__file__),"result_files","gau_out.txt")
paramhunter_out = os.path.join(os.path.dirname(__file__),"result_files","paramhunter_out.txt")
vurlnable_urls = os.path.join(os.path.dirname(__file__),"result_files","vurlnable_urls.txt")
maybe_vurlnable = os.path.join(os.path.dirname(__file__),"result_files","maybe_vurlnable_urls.txt")

def waymore (domain,output_file):
    try :
        subprocess.run(['waymore','-i',domain,'-oU',output_file])
    except  Exception as e:
        print("waymore : ",e)
        
def waybackurl (doamin,output_file):
    try :
        subprocess.run(['waybackurl',doamin ,'-o',output_file])
    except Exception as e:
        print("waybackurl : ",e)
        
def hakrawler (domain,output_file) :
    try :
        subprocess.run([domain,'|','hakrawler','>',output_file],shell=True)
    except Exception as e:
        print(f"hakrawler : {e}")
        
def gau (domain,output_file):
    try :
        subprocess.run(['gau',domain,'-o',output_file])
    except Exception as e:
        print(f'Gau exception : {e}')

def filter_the_output (input_files,output_file,executable=paramhunter_exe,file=paramhunter_file):
    try:
        if not os.path.exists(executable) or os.path.getmtime(file) > os.path.getmtime(executable):
            print("Compiling...")
            compile_c_file(file, executable)
            print("Compilation successful!")
        else :
            print("exe is uptodate , skipping compilation ...")    
        print("Removing urls with no parameters ...")
        for input_file in input_files :
            subprocess.run([executable, input_file, output_file])
        
    except Exception as e:
        print(f"Filtering the output with paramhunters failed : {str(e)}")
    
def does_m (input_file_path,output_file_path,payload=None):
    with open(does_m_out,'w',encoding='utf-8') as f:
        f.write("")
    try:
        if not os.path.exists(does_m_executable) or os.path.getmtime(does_m_file) > os.path.getmtime(does_m_executable):
            print("Compiling...")
            compile_c_file(does_m_file, does_m_executable)
            print("Compilation successful!")
        else :
            print("exe is uptodate , skipping compilation ...")    
        print("Running the program...")

        subprocess.run([does_m_executable,input_file_path,output_file_path,payload])
        
        print(f"process has been completed ,check {output_file_path} for results .")
        
    except Exception as e:
        print("Error:", e)

def compile_c_file(filename, outputpath):
    compile_process = subprocess.run(['g++',filename,outputpath])
    compile_error = compile_process.communicate()
    if compile_process.returncode != 0:
        print("Compilation failed:", compile_error.decode('utf-8'))
        return None
    
def check_redirect(url, target_location, output_file_vul,output_file_res):
    try:
        response = requests.get(url, allow_redirects=False)
        redirected = False
        if response.status_code in [301, 302, 303, 307, 308]:
            redirected = True
            location = response.headers.get('Location', '')
            if target_location in location:
                with output_lock:
                    print(colored("[+] Redirected : ",'red'), colored(url,'green') )
                    with open (output_file_vul,"a") as file:
                        file.writelines(url.strip()+'\n')
            else:
                with output_lock2 :
                    with open (output_file_res,"a") as file:
                        file.writelines(url.strip()+ '\n')

    except requests.RequestException as e:
        print(f"Error occurred in check-redirect: {e}")

def merge_files (outputfile,input_files,executable=merge_exe,file=merge_file):
    try:
        if not os.path.exists(executable) or os.path.getmtime(file) > os.path.getmtime(executable):
            print("Compiling...")
            compile_c_file(file, executable)
            print("Compilation successful!")
        else :
            print("exe is uptodate , skipping compilation ...")    
        print("Removing urls with no parameters ...")
        
        subprocess.run([executable,'-o',outputfile] + [input_files])
        
    except Exception as e:
        print(f"Filtering the output with paramhunters failed : {str(e)}")
        
def main():
    parser = argparse.ArgumentParser(description="Mining URLs from dark corners of Web Archives ")
    parser.add_argument("-d", "--domain", help="enter the domain you want to fuzz .")
    parser.add_argument("-p", "--payload", help="enter the payload you want to replace the parameter's value with .",default="https://google.com")
    parser.add_argument("-o", "--output", help="provide output file path , default path is 'output.txt' .", default = vurlnable_urls )
    # parser.add_argument("-e", "--email", help="provide email if you want to recieve updates about the progress .", default = None)
    # parser.add_argument("-c", "--continues", help="continue previouse work of the last file (True To Enable) .", default = False)
    args = parser.parse_args()
    
    # list of files containing urls
    files=[waymore_out,waybackurl_out,hakrawler_out,gau_out]
    
    # tools to run
    waymore(args.domain,waybackurl_out)
    waybackurl(args.domain,waybackurl_out)
    hakrawler(args.domain,hakrawler_out)
    gau(args.domain,gau_out)
    
    # filtering results
    filter_the_output(waymore_out)
    filter_the_output(waybackurl_out)
    filter_the_output(hakrawler_out)
    filter_the_output(gau_out)
    
    # merging all the files obtained
    merge_files(meregd_files_out,files)
    
    # loading the payload and removing the duplicates 
    does_m(meregd_files_out,does_m_out,args.payload)
    
    # clean up 
    print(colored("Cleaning up to save space please wait ...",'yellow'))
    
    with open (waymore_out,'w',encoding= 'utf-8') as wm, \
         open (waybackurl_out,'w',encoding= 'utf-8') as wbu,\
         open (hakrawler_out,'w', encoding='utf-8') as hr,\
         open (gau_out,'w', encoding='utf-8') as g:
             wm.write("")
             wbu.write('')
             hr.write('')
             g.write('')
    print(colored("Done Cleaning !","green"))
    
    # checking for redirects 
    with ThreadPoolExecutor(max_workers=5) as executor:
        with open (does_m_out,"r",encodings='UTF-8') as dm :
            url = dm.readline().strip()
            while url :
                future=executor.submit(check_redirect,url,args.payload,vurlnable_urls,maybe_vurlnable)
                url = dm.readline().strip()

    print(colored("Done!",'blue'))

if __name__ == "__main__":
    main()