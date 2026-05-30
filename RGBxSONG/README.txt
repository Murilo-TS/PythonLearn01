>> BEM-VINDO, ESSE É O MEU PROGRAMA DE TRANSFORMAÇÃO DE UMA IMAGEM PARA SOM <<

primeiro - entenda o fluxo

segundo - baixe o Python, VSCode/Pycharm e as bibliotecas

terceiro(opcional) - tem duas versões, usando tkinter e o custom tkinter


- - - - - - - - -  - - - - - - - - - - - - - -  - - - - - - - -  - - - - - - - -
			FLUXO

		IMPORTAÇÃO BIBLIOTECAS
		
		VARIAVEIS

		DEF PARA FILTRO DE AUDIO 

		DEF SPECTOGRAMA

		DEF INTERPRETAR BYTES COMO ONDAS

		DEF ENTRADA DA IMAGEM E TRANSFORMA RGB EM TONS DE CINZA
		
		DEF INTERFACE
			
			- BOTÃO PARA INPUT DA IMG
			- BOTÃO PARA ESCOLHER O TIPO DE INTERPRETADOR
			- BOTÃO PARA TRANSFORMAR EM IMG
			- VIEWER DO PROCESAMENTO(da img)
			- BOTÃO PARA TOCAR O SOM

Bibliotecas Necessárias: Bash pip install opencv-python numpy sounddevice Pillow scipy customtkinter

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - -  -
usando tkinter

import cv2
import numpy as np
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import sounddevice as sd  # reprodução direta
from scipy.signal import butter, lfilter, spectrogram

# Configuracao de áudio
fs = 44100       # Sample rate (Hz)
duration = 3     # Seconds
cutoff = 2000    # Filter cutoff frequency (Hz)
order = 5        # Filter strength/steepness

# Define Filtro Butterworth
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
# Aplica o filtro aos dados de áudio
def apply_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# INTERPRETACAO
def interpretar_como_ondas(img_gray):
    # Redimensiona para evitar áudio excessivamente longo
    img_resized = cv2.resize(img_gray, (800, 200))
    # Normaliza entre -1 e 1 (padrão de áudio float32)
    audio_wave = (img_resized.flatten() / 127.5) - 1.0
    audio_wave = apply_filter(audio_wave, cutoff, fs, order)
    return audio_wave.astype(np.float32)

def gerar_espectrograma(img_gray):
    duration = 0.05  # Duração de cada coluna de pixels em segundos
    fs = 44100       # Sample rate
    t = np.linspace(0, duration, int(fs * duration))
    audio_full = []

    # Redimensiona para controlar o range de frequências (ex: 200 frequências)
    img_small = cv2.resize(img_gray, (100, 200)) 
    
    for x in range(img_small.shape[1]): # Para cada coluna
        col_wave = np.zeros_like(t)
        for y in range(img_small.shape[0]): # Para cada linha
            intensity = img_small[y, x] / 255.0
            if intensity > 0.1:
                # Frequência baseada na posição Y
                freq = 2000 - (y * 10) 
                col_wave += intensity * np.sin(2 * np.pi * freq * t)
        audio_full.append(col_wave)
    audio_combi = np.concatenate(audio_full)
    audio_combi = apply_filter(audio_combi, cutoff, fs, order)
    return audio_combi.astype(np.float32)

ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")

# INTERFACE GRÁFICA COM TKINTER
class ImageToSoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG2Song")
        
        self.root.geometry("700x550") 
        self.img_path = None
        self.audio_data = None
        
        # UI Elements
        self.btn_load = tk.Button(root, text="Carregar Imagem", command=self.load_image)
        self.btn_load.pack(pady=10)

        self.mode = tk.StringVar(value="Ondas")
        tk.OptionMenu(root, self.mode, "Ondas", "Espectrograma").pack()

        self.canvas = tk.Label(root, text="Imagem Transformada", background="lightgray") # Viewer da Imagem
        self.canvas.pack(pady=10)

        self.btn_play = tk.Button(root, text="Tocar Som", command=self.play_sound)
        self.btn_play.pack(pady=10)

        # Botão para transformar Som em Imagem
        self.btn_save_img = tk.Button(root, text="Som -> Imagem", command=self.som_para_imagem)
        self.btn_save_img.pack(pady=5)

    def load_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path:
            # OpenCV: Carrega e converte para Cinza
            img = cv2.imread(self.img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Atualiza Viewer (formato PIL)
            img_disp = cv2.resize(gray, (300, 300))
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_disp))
            self.canvas.config(image=img_tk, width=300, height=300)
            self.canvas.image = img_tk
            self.current_gray = gray

    def play_sound(self):
        if hasattr(self, 'current_gray'):
            if self.mode.get() == "Ondas":
                self.audio_data = interpretar_como_ondas(self.current_gray)
            else:
                self.audio_data = gerar_espectrograma(self.current_gray)
            
            sd.play(self.audio_data, 44100)

    def som_para_imagem(self):
        if self.audio_data is None:
            print("Nenhum som foi gerado ainda para converter!")
            return

        # Calcula o espectrograma do áudio gerado
        fs = 44100
        # f = array de frequências, t = array de tempos, Sxx = matriz de espectrograma
        f, t, Sxx = spectrogram(self.audio_data, fs)

        # Converte para escala logarítmica (dB) para melhor contraste visual
        # O 1e-10 previne erro de logaritmo de zero
        Sxx_log = 10 * np.log10(Sxx + 1e-10)

        # Normaliza a matriz para o range de uma imagem em tons de cinza (0 a 255)
        Sxx_norm = cv2.normalize(Sxx_log, None, 0, 255, cv2.NORM_MINMAX)
        img_result = np.uint8(Sxx_norm)

        # Inverte o eixo Y para que as baixas frequências fiquem na base da imagem
        img_result = cv2.flip(img_result, 0)

        # Abre o diálogo para salvar a imagem
        save_path = filedialog.asksaveasfilename(
            title="Salvar Som como Imagem",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if save_path:
            # Salva o arquivo usando OpenCV
            cv2.imwrite(save_path, img_result)
            
            # Atualiza o canvas_result na interface
            img_disp = cv2.resize(img_result, (300, 300))
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_disp))
            self.canvas.config(image=img_tk, width=300, height=300)
            self.canvas.image = img_tk # Mantém a referência para não ser apagada pelo Garbage Collector
            print(f"Imagem salva em: {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToSoundApp(root)
    root.mainloop()



USANDO CUSTOMTKINTER

import cv2
import numpy as np
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import sounddevice as sd  # reprodução direta
from scipy.signal import butter, lfilter, spectrogram

# Configuracao de áudio
fs = 44100       # Sample rate (Hz)
duration = 3     # Seconds
cutoff = 2000    # Filter cutoff frequency (Hz)
order = 5        # Filter strength/steepness

# Define Filtro Butterworth
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
# Aplica o filtro aos dados de áudio
def apply_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# INTERPRETACAO
def interpretar_como_ondas(img_gray):
    # Redimensiona para evitar áudio excessivamente longo
    img_resized = cv2.resize(img_gray, (800, 200))
    # Normaliza entre -1 e 1 (padrão de áudio float32)
    audio_wave = (img_resized.flatten() / 127.5) - 1.0
    audio_wave = apply_filter(audio_wave, cutoff, fs, order)
    return audio_wave.astype(np.float32)

def gerar_espectrograma(img_gray):
    duration = 0.05  # Duração de cada coluna de pixels em segundos
    fs = 44100       # Sample rate
    t = np.linspace(0, duration, int(fs * duration))
    audio_full = []

    # Redimensiona para controlar o range de frequências (ex: 200 frequências)
    img_small = cv2.resize(img_gray, (100, 200)) 
    
    for x in range(img_small.shape[1]): # Para cada coluna
        col_wave = np.zeros_like(t)
        for y in range(img_small.shape[0]): # Para cada linha
            intensity = img_small[y, x] / 255.0
            if intensity > 0.1:
                # Frequência baseada na posição Y
                freq = 2000 - (y * 10) 
                col_wave += intensity * np.sin(2 * np.pi * freq * t)
        audio_full.append(col_wave)
    audio_combi = np.concatenate(audio_full)
    audio_combi = apply_filter(audio_combi, cutoff, fs, order)
    return audio_combi.astype(np.float32)

ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")

# INTERFACE GRÁFICA COM TKINTER
class ImageToSoundApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PNG2Song")
        self.geometry("800x600")
        
        # Configuração de Grid para Layout Responsivo
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Painel Lateral de Controles) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="PNG2Song", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.btn_load = ctk.CTkButton(self.sidebar_frame, text="Carregar Imagem", command=self.load_image)
        self.btn_load.pack(pady=10, padx=20)

        self.label_mode = ctk.CTkLabel(self.sidebar_frame, text="Modo de Conversão:")
        self.label_mode.pack(pady=(20, 5))
        
        self.mode_var = ctk.StringVar(value="Ondas")
        self.mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Ondas", "Espectrograma"], variable=self.mode_var)
        self.mode_menu.pack(pady=10, padx=20)

        self.btn_save_img = ctk.CTkButton(self.sidebar_frame, text="Som -> Imagem", 
                                          fg_color="transparent", border_width=2, 
                                          command=self.som_para_imagem)
        self.btn_save_img.pack(pady=20, padx=20)

        # --- Main Content (Visualizador) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.canvas_label = ctk.CTkLabel(self.main_frame, text="Imagem Transformada", 
                                         fg_color="#2b2b2b", corner_radius=10)
        self.canvas_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Botão de Play com destaque
        self.btn_play = ctk.CTkButton(self.main_frame, text="▶ Tocar Som", 
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      height=45, fg_color="#2fa572", hover_color="#106a43",
                                      command=self.play_sound)
        self.btn_play.grid(row=1, column=0, pady=20)

    def load_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path:
            # OpenCV: Carrega e converte para Cinza
            img = cv2.imread(self.img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Atualiza Viewer (formato PIL)
            img_disp = cv2.resize(gray, (300, 300))
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_disp))
            self.canvas_label.configure(image=img_tk, width=300, height=300)
            self.canvas_label.image = img_tk
            self.current_gray = gray

    def play_sound(self):
        if hasattr(self, 'current_gray'):
            if self.mode_var.get() == "Ondas":
                self.audio_data = interpretar_como_ondas(self.current_gray)
            else:
                self.audio_data = gerar_espectrograma(self.current_gray)
            
            sd.play(self.audio_data, 44100)

    def som_para_imagem(self):
        if self.audio_data is None:
            print("Nenhum som foi gerado ainda para converter!")
            return

        # Calcula o espectrograma do áudio gerado
        fs = 44100
        # f = array de frequências, t = array de tempos, Sxx = matriz de espectrograma
        f, t, Sxx = spectrogram(self.audio_data, fs)

        # Converte para escala logarítmica (dB) para melhor contraste visual
        # O 1e-10 previne erro de logaritmo de zero
        Sxx_log = 10 * np.log10(Sxx + 1e-10)

        # Normaliza a matriz para o range de uma imagem em tons de cinza (0 a 255)
        Sxx_norm = cv2.normalize(Sxx_log, None, 0, 255, cv2.NORM_MINMAX)
        img_result = np.uint8(Sxx_norm)

        # Inverte o eixo Y para que as baixas frequências fiquem na base da imagem
        img_result = cv2.flip(img_result, 0)

        # Abre o diálogo para salvar a imagem
        save_path = filedialog.asksaveasfilename(
            title="Salvar Som como Imagem",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if save_path:
            # Salva o arquivo usando OpenCV
            cv2.imwrite(save_path, img_result)
            
            # Atualiza o canvas_result na interface
            img_disp = cv2.resize(img_result, (300, 300))
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_disp))
            self.canvas_label.configure(image=img_tk, width=300, height=300)
            self.canvas_label.image = img_tk # Mantém a referência para não ser apagada pelo Garbage Collector
            print(f"Imagem salva em: {save_path}")

if __name__ == "__main__":
    app = ImageToSoundApp()
    app.mainloop()

