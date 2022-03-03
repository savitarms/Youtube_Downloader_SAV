# pip install pytube
# pip install moviepy

import os
import glob
import pathlib
from pytube import YouTube
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import re
from moviepy.editor import *
import moviepy.editor as moviepy
import time
import threading


# Verificar se há restos na pasta temp (de algum erro), se tiver vai apagar.
local = glob.glob("./pack/temp/*")

initial_count = 0
for path in pathlib.Path("./pack/temp").iterdir():
    if path.is_file():
        initial_count += 1

if initial_count >= 1:
    for delete in local:
        os.remove(delete)


# configs
window = tk.Tk()
window.iconbitmap(default="./pack/icon.ico")
window.title("SAVDownloader")
window.geometry("560x465+800+300")
window.maxsize(560, 465)
window.minsize(560, 465)
window.resizable(width=1,  height=1)

# Background img
img_background = PhotoImage(file="./pack/background.png")
background = tk.Label(window, image=img_background)
background.pack()

# Header
header = tk.Label(text="Baixe vídeos do YouTube em 1080p", fg="white", bg="#074368", font="Calibri 20", width=40)
header.place(width=560, height=40, x=0, y=0)

# Url
url_write = tk.Label(text="Digite a URL:", fg="white", bg="#116BD1", font="Calibri 12", width=20)
url_write.place(x=45, y=80)
url = tk.Entry(window, bd=2, font="Calibri 10")


# Função para apagar o url com 1 click com o botão ESQUERDO do MOUSE
def hintText(clickevent):
    if clickevent:   
        url.delete(0, END)

url.insert(0, "Digite a URL do vídeo que deseja fazer download")
url.bind("<Button-1>", hintText)
url.place(width=445, height=25, x=45, y=110)


# Formatos
mp4_1080p = "MP4 (1080p) Vídeo e Áudio - (Slow Download)"
mp4_720p = "MP4 (720p) Vídeo e Áudio - (Fast Download)"
mp3_160kbps = "MP3 (160kbps) Áudio - (Fast Download)"

selectFormat = tk.Label(text="Selecione o Formato:", fg="white", bg="#116BD1", font="Calibri 12", width=20)
selectFormat.place(x=45, y=165)
selectValue = ttk.Combobox(window, values=[mp4_1080p, mp4_720p, mp3_160kbps], state="readonly", width=18)
selectValue.place(width=310, height=25, x=45, y=195)


# Processo de download - informando título e autor do vídeo
Process = tk.Label(text="")


# Mensagem de conclusao - (Download concluído!)
download_successfully = tk.Label(text="Download concluído!")

# MSG - (Pronto para outro download)
download_ready = tk.Label(text="Pronto para outro download.") 

# Ao apertar o Botão de download recebe essa função.
def download_video():
    geturl = url.get()
    if geturl:
        try: # Verificar se a url digitada existe.
            yt_url = YouTube(geturl)

            # Titulo formatado sem alguns símbolos
            title_video = re.sub(u'[\/:*?"<>,.|\\\]', '', yt_url.title)

            # Barra de progresso
            progressBar = ttk.Progressbar(window, maximum=15, length=100, mode="determinate") # (Sim a barra de progresso não era pra estar aqui (só deixei mesmo))
            progressBar.place(width=390, height=25, x=80, y=330)
        except:
            print("URL NÃO ENCONTRADA")
            messagebox.showerror("URL inválida", "URL inválida ou vídeo não encontrado!")
            return 0
        else:   
            Process.pack()
            Process.config(text=title_video + '\n' + yt_url.author)

            # download_successfully.pack()
            # download_successfully.config(text="Baixando...", bg="grey", fg="white") 

            # download_ready.pack()
            # download_ready.config(text="")
            

        # MP4 - Selecionar o formato de download - Se a opção for "mp4", ele vai fazer os download separado do audio com o video para vir em 1080p. E depois ele vai juntar esses 2 arquivos em um só e colocar na pasta downloads.
        if selectValue.current() >= 1:
            if selectValue.get() == mp4_1080p :   
                while True:
                    try: # MP4 - 1080p (Download - 137) 
                        apply = 137

                        # Mensagem avisando que o download começou!
                        download_successfully.pack()
                        download_successfully.config(text="Baixando...", bg="grey", fg="white") 
                        download_ready.pack()
                        download_ready.config(text="")
                        progressBar.start() # Iniciar barra de progresso
                        ###########################################
                        
                        stream = yt_url.streams.get_by_itag(apply)
                        stream.download('./pack/temp')

                        print("Arquivo mp4 baixado.")
                    
                    except:
                        print("Error")
                        messagebox.showerror("Vídeo restrito", "Não foi possível fazer o download desse vídeo.")
                        return 0
                    
                    else: # Download - 251 | + Convertendo webm para mp3
                        apply = 251
                        stream = yt_url.streams.get_by_itag(apply)
                        stream.download('./pack/temp')

                        print("Arquivo webm baixado.")

                        # Conversão webm para mp3
                        filename = f"./pack/temp/{title_video}" 

                        initial_file = f'{filename}.webm'
                        output_file = f'{filename}.mp3'

                        clip = moviepy.AudioFileClip(initial_file)
                        clip.write_audiofile(output_file)

                        if output_file: # Unir o audio no video que estão separados.
                            print("Webm foi convertido para Mp3!")

                            video_clip = VideoFileClip(f"{filename}.mp4")
                            audio_clip = AudioFileClip(f"{filename}.mp3")

                            new_audio_clip = CompositeAudioClip([audio_clip]) 
                            video_clip.audio = new_audio_clip
                            video_clip.write_videofile(f"./downloads/{title_video} - SAVDownloads.mp4") # Nome que vai ser dado ao arquivo que vai ser gerado.

                            clip.close()    # (arrumar os downloads que falham)
                            time.sleep(1)
                            os.remove(filename + ".mp3")  # remover os arquivos utilizados para a conversão(/pack/temp)
                            os.remove(filename + ".mp4")  # remover os arquivos utilizados para a conversão(/pack/temp)
                            os.remove(filename + ".webm")  # remover os arquivos utilizados para a conversão(/pack/temp)

                            progressBar.stop() # Parar barra de progresso
                            progressBar.destroy() # Destruir o progressBar após o download ser concluído.
                        break

            # MP4 - 720p Fast Download
            if selectValue.get() == mp4_720p :
                apply = 22

                # Mensagem avisando que o download começou!
                download_successfully.pack()
                download_successfully.config(text="Baixando...", bg="grey", fg="white") 
                download_ready.pack()
                download_ready.config(text="")
                progressBar.start() # Iniciar barra de progresso
                ###########################################

                stream = yt_url.streams.get_by_itag(apply)
                stream.download('./downloads')

                print("Arquivo mp4 fast download baixado.")

                progressBar.stop() # Parar barra de progresso
                progressBar.destroy() # Destruir o progressBar após o download ser concluído.

            # MP3
            if selectValue.get() == mp3_160kbps :
                apply = 251
                
                # Mensagem avisando que o download começou!
                download_successfully.pack()
                download_successfully.config(text="Baixando...", bg="grey", fg="white") 
                download_ready.pack()
                download_ready.config(text="")
                progressBar.start() # Iniciar barra de progresso
                ###########################################

                stream = yt_url.streams.get_by_itag(apply)
                stream.download('./pack/temp')

                print("Arquivo webm baixado.")

                # Conversão webm para mp3
                filename = f"./pack/temp/{title_video}" 

                initial_file = f'{filename}.webm'
                output_file = f'{filename}.mp3'

                clip = moviepy.AudioFileClip(initial_file)
                clip.write_audiofile(f"./downloads/{title_video} - SAVDownloads.mp3")
                
                clip.close()
                os.remove(filename + ".webm")  # remover os arquivos utilizados para a conversão(/pack/temp)

                progressBar.stop() # Parar barra de progresso
                progressBar.destroy() # Destruir o progressBar após o download ser concluído.

        else: 
            print("Não selecionou um tipo de formato.")
            messagebox.showerror("Formato de download inválido", "Selecione um formato de download.")
            return 0


        # Aviso que o download foi concluído e está pronto para o próximo.
        download_successfully.pack()
        download_successfully.config(text="Download Concluído!", bg="green", fg="white")

        download_ready.pack()
        download_ready.config(text="Pronto para outro download.", fg="black")
        

    else:
        print("URL - Campo vazio")
        messagebox.showerror("Campo vazio", "Digite uma URL válida!")
        return 0


# Threading - ao apertar o botão de download executa isso primeiro e depois a função "download_video"
def startDownload():
    threading.Thread(target=download_video).start()

# Botão para fazer o download.
confirm = tk.Button(text="Download", font="Calibri 16", bg="#116BD1", fg="white", command=startDownload)
confirm.place(width=130, height=40, x=215, y=250)

window.mainloop()