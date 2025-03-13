import yt_dlp
import tkinter as tk
from tkinter import ttk
from tqdm import tqdm
from tkinter import scrolledtext,filedialog, Toplevel
from tkinter import *
import requests 
from tkinter import messagebox as MB
from time import sleep
import threading
import re
import customtkinter as ctk

def iniciar_descarga():
    url = entrada_url.get().strip()
    formato = formato_seleccionado.get()
    if not url:
        mostrar_mensaje("Por favor, ingresa una URL válida.")
        cerrar_ventana_progreso()
        return
    
    try:
        # Obtener información del video
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)  # Solo extraer información, no descargar
        titulo_video = info.get('title', 'video')  # Usar el título del video o un valor por defecto
    except Exception as e:
        mostrar_mensaje(f"Error al obtener información del video: {e}")
        cerrar_ventana_progreso()
        return

    extension = "mp3" if formato == "MP3" else "mp4"
    archivo = filedialog.asksaveasfilename(
        defaultextension=f".{extension}",
        initialfile=f"{titulo_video}.{extension}",  # Título del video como nombre por defecto
        filetypes=[(f"{formato} files", f"*.{extension}"), ("All files", "*.*")]
    )
    if not archivo:
        mostrar_mensaje("Operación cancelada por el usuario.")
        cerrar_ventana_progreso()
        return

    if archivo:
        # Configurar opciones según el formato seleccionado
        opciones = {
        'outtmpl': archivo,  # Ruta y nombre del archivo de salida
        'format': 'bestaudio/best' if formato == "MP3" else 'bestvideo+bestaudio/best[ext=mp4]/best[ext=mp4]', # Mejor calidad
        #'ffmpeg_location': 'C:/Users/ADMIN/Downloads/Portafolio/Programacion/Python/Youtube/bin/ffmpeg.exe',  # Ruta al FFmpeg
        'progress_hooks': [actualizar_barra_progreso],  # Hook para progreso
    }
    
    #Postprocesadores si el formato es mp4
    if formato == "MP4":
        opciones['postprocessors'] = [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convertir a MP4
            }
        ]
    
    
    # Solo agregar postprocesadores si el formato es MP3
    if formato == "MP3":
        opciones['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '328',  # Calidad MP3
                }
        ]

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        mostrar_mensaje("¡Descarga completada!")
    except Exception as e:
        mostrar_mensaje(f"Error al descargar: {e}")
    finally:
        cerrar_ventana_progreso()

def download_audio():
    mostrar_ventana_progreso()
    hilo_descarga = threading.Thread(target=iniciar_descarga)
    hilo_descarga.start()

def mostrar_mensaje(mensaje):
    area_mensajes.config(state=tk.NORMAL)
    area_mensajes.insert(tk.END, f"{mensaje}\n")
    area_mensajes.see(tk.END)
    area_mensajes.config(state=tk.DISABLED)

def mostrar_ventana_progreso():
    global ventana_progreso, barra_progreso
    ventana_progreso = ctk.CTkToplevel(ventana)
    ventana_progreso.geometry("400x150")
    ventana_progreso.title("Descargando...")
    ventana_progreso.resizable(False, False)
    
    
    etiqueta_progreso = ctk.CTkLabel(ventana_progreso, text="Descargando archivo...")
    etiqueta_progreso.pack(pady=10)

    barra_progreso = ctk.CTkProgressBar(ventana_progreso, width=350, height=20, mode="determinate")
    barra_progreso.pack(pady=10)
    barra_progreso.set(0)  # Inicializar la barra de progreso en 0
    

# Función para cerrar la ventana de progreso
def cerrar_ventana_progreso():
    if 'ventana_progreso' in globals() and ventana_progreso.winfo_exists():
        ventana_progreso.destroy()

# Función para actualizar la barra de progreso
def actualizar_barra_progreso(d):
    if 'ventana_progreso' in globals() and ventana_progreso.winfo_exists():
        if d['status'] == 'downloading':
            try:
                # Eliminar cualquier secuencia de escape ANSI y recortar espacios adicionales
                porcentaje_str = d['_percent_str'].strip()

                # Eliminar cualquier carácter no numérico (como '%', espacios, etc.)
                porcentaje_str = ''.join(filter(lambda x: x.isdigit() or x == '.', porcentaje_str))

                # Intentamos convertir el porcentaje a flotante
                if porcentaje_str:  # Verificar que la cadena no esté vacía
                    porcentaje = float(porcentaje_str)
                    barra_progreso.set(porcentaje / 100)  # CTkProgressBar usa valores entre 0 y 1
                    ventana_progreso.update_idletasks()
            except (ValueError, AttributeError) as e:
                print(f"Error al convertir el porcentaje: {porcentaje_str} - {e}")


def salir():
    resultado = MB.askquestion("Salir", "¿Estás seguro de que quieres salir?")
    if resultado == "yes":ventana.destroy()
    
# Función que muestra el menú contextual al hacer clic derecho
def mostrar_menu(event):
    menu_contextual.post(event.x_root, event.y_root)

# Funciones para manejar las opciones del menú contextual
def copiar():
    # Copiar el texto seleccionado al portapapeles
    ventana.clipboard_clear()
    ventana.clipboard_append(entrada_url.get())

def cortar():
    # Cortar el texto (copiar y borrar)
    ventana.clipboard_clear()
    ventana.clipboard_append(entrada_url.get())
    entrada_url.delete(0, tk.END)

def pegar():
    # Pegar el texto desde el portapapeles
    entrada_url.insert(tk.END, ventana.clipboard_get())
    
# Función para confirmar la salida
def confirmar_salida():
    respuesta = MB.askyesno("Salir", "¿Estás seguro de que quieres salir?")
    if respuesta:
        ventana.destroy()  # Cierra la ventana

# Configurar el tema
ctk.set_appearance_mode("system")  # Modo
ctk.set_default_color_theme("green")  # Tema

# Crear la ventana principal
ventana = ctk.CTk()
ventana.title("Cute Converter")
ventana.geometry("800x600")
ventana.resizable(False, False)

# Crear un frame
frame = ctk.CTkFrame(ventana)
frame.pack(fill="both", expand=True, pady=20, padx=20)

#Definir la fuente de CTK
fuente_nombrein = ctk.CTkFont(family="BigFlorida", size=40)
fuente_url = ctk.CTkFont(family="Roboto", size=14)

# Etiqueta de introducción
etiqueta_titulo = ctk.CTkLabel(frame, text="Project Converter", font=fuente_nombrein, text_color="white")
etiqueta_titulo.pack(pady=6, padx=4)

# Entrada para la URL
etiqueta_url = ctk.CTkLabel(frame, text="Ingresa la URL:", font=fuente_url, text_color="white")
etiqueta_url.pack(fill="y", side="top", pady=10, padx=15)

# Campo para ingresar la URL
entrada_url = ctk.CTkEntry(frame, width=200)
entrada_url.pack(pady=10, padx=10)

# Crear un menú contextual
menu_contextual = tk.Menu(ventana, tearoff=0, bg="gray", font=("Roboto"))
menu_contextual.add_command(label="Copiar", command=copiar)
menu_contextual.add_command(label="Cortar", command=cortar)
menu_contextual.add_command(label="Pegar", command=pegar)

# Asignar la función al evento de cerrar la ventana
ventana.protocol("WM_DELETE_WINDOW", confirmar_salida)

# Asociar el evento de clic derecho al campo de entrada
entrada_url.bind("<Button-3>", mostrar_menu)

# Botón para iniciar la descarga
boton_descargar = ctk.CTkButton(frame, text="Descargar", command=download_audio)
boton_descargar.pack(pady=14, padx=10)

#Propociona un area suficiente para todos los mensajes
area_mensajes = scrolledtext.ScrolledText(frame, width=50, height=5, state=tk.DISABLED)
area_mensajes.pack(fill="y", pady=2, padx=2)

#Barra para elegir formato
formato_seleccionado = ctk.StringVar(value="MP3")
combobox = ctk.CTkComboBox(frame, variable=formato_seleccionado, values=["MP4", "MP3", "WAV"],state="readonly", font=fuente_url)
combobox.pack(side="top", fill="y", pady=8, padx=10)

#Boton para salir
boton_salir = ctk.CTkButton(frame, text="Salir", command=salir)
boton_salir.pack(fill="y", pady=18, padx=10)

#Determina espacio entre widgets
for child in frame.winfo_children(): 
    child.pack_configure(padx=15, pady=15)

# Iniciar el bucle principal
ventana.mainloop()
