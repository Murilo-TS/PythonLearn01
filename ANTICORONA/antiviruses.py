import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import logging
import psutil
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CONFIGURAÇÕES ---
LOG_FILE = "monitor_seguranca.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

class MonitorHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        if not event.is_directory:
            # Filtro para não alertar sobre o próprio arquivo de log do app
            if LOG_FILE in event.src_path:
                return
            
            tipo = event.event_type.upper()
            msg = f"ARQUIVO {tipo}: {os.path.basename(event.src_path)}"
            # Usa o schedule do tkinter para evitar erro de thread
            self.callback(msg, "ALERTA")

class AppSeguranca:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentinel Monitor v3.2")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0f0f0f")
        
        # GARANTE O FECHAMENTO TOTAL
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        
        self.rodando = False
        self.ativo = True 
        self.observer = None
        self.historico_cpu = [0] * 20

        self.setup_ui()
        self.atualizar_sistema()

    def setup_ui(self):
        # Cabeçalho
        self.header = tk.Frame(self.root, bg="#1a1a1a", height=50)
        self.header.pack(fill=tk.X)
        
        self.status_indicator = tk.Canvas(self.header, width=20, height=20, bg="#1a1a1a", highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=10)
        self.led = self.status_indicator.create_oval(5, 5, 15, 15, fill="red")
        
        self.status_label = tk.Label(self.header, text="SISTEMA OFFLINE", fg="white", bg="#1a1a1a", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)

        # Botões
        self.btn_frame = tk.Frame(self.header, bg="#1a1a1a")
        self.btn_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(self.btn_frame, text="INICIAR", command=self.iniciar, bg="#2ecc71", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="PAUSAR", command=self.pausar, bg="#e67e22", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="LIMPAR", command=self.limpar_logs, bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)

        # Layout de Painéis
        self.main_container = tk.Frame(self.root, bg="#0f0f0f")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.alert_frame = tk.LabelFrame(self.main_container, text=" ALERTAS CRÍTICOS ", fg="#ff4757", bg="#0f0f0f")
        self.alert_frame.place(relx=0, rely=0, relwidth=0.6, relheight=0.45)
        self.log_area = scrolledtext.ScrolledText(self.alert_frame, bg="#000", fg="#00ff00", font=("Consolas", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.hw_frame = tk.LabelFrame(self.main_container, text=" HARDWARE ", fg="cyan", bg="#0f0f0f")
        self.hw_frame.place(relx=0.62, rely=0, relwidth=0.38, relheight=0.45)
        self.fig, self.ax = plt.subplots(figsize=(4, 2.5), dpi=80)
        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax.set_facecolor('#000')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.hw_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.info_frame = tk.LabelFrame(self.main_container, text=" REDE E PROCESSOS ", fg="white", bg="#0f0f0f")
        self.info_frame.place(relx=0, rely=0.48, relwidth=1, relheight=0.52)
        self.info_area = scrolledtext.ScrolledText(self.info_frame, bg="#0a0a0a", fg="#bdc3c7", font=("Consolas", 9))
        self.info_area.pack(fill=tk.BOTH, expand=True)

    def adicionar_log(self, msg, tipo="INFO"):
        if not self.ativo: return
        # Função interna para ser chamada via .after (segurança de thread)
        def inserir():
            timestamp = datetime.now().strftime("%H:%M:%S")
            cor = "white"
            if tipo == "ALERTA": cor = "#ff4757"
            
            self.log_area.insert(tk.END, f"[{timestamp}] [{tipo}] {msg}\n", tipo)
            self.log_area.tag_config("ALERTA", foreground="#ff4757", font=("Consolas", 10, "bold"))
            self.log_area.see(tk.END)
            logging.info(msg)
        
        self.root.after(0, inserir)

    def atualizar_sistema(self):
        if not self.ativo: return

        if self.rodando:
            try:
                # CPU/RAM
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                self.historico_cpu.pop(0)
                self.historico_cpu.append(cpu)
                self.ax.clear()
                self.ax.plot(self.historico_cpu, color='#00ff00')
                self.ax.set_ylim(0, 100)
                self.ax.set_title(f"CPU: {cpu}% | RAM: {mem}%", color='white')
                self.canvas.draw()

                # Rede e Processos
                self.info_area.delete('1.0', tk.END)
                self.info_area.insert(tk.END, "--- CONEXÕES ATIVAS ---\n")
                
                for conn in psutil.net_connections(kind='inet'):
                    try:
                        if conn.status == 'ESTABLISHED' and conn.raddr:
                            self.info_area.insert(tk.END, f"CONEXÃO ESTABELECIDA: {conn.raddr.ip}\n", "danger")
                    except: continue
                
                self.info_area.insert(tk.END, "\n--- PROCESSOS (TOP 15) ---\n")
                for p in sorted([pr.info for pr in psutil.process_iter(['pid', 'name']) if pr.info['name']], 
                               key=lambda x: x['name'].lower())[:15]:
                    self.info_area.insert(tk.END, f"PID: {p['pid']:<6} | {p['name']}\n")

                self.info_area.tag_config("danger", foreground="#ff4757")

            except Exception as e:
                print(f"Erro Loop: {e}")

        self.root.after(2000, self.atualizar_sistema)

    def iniciar(self):
        if not self.rodando:
            self.rodando = True
            self.status_label.config(text="MONITORAMENTO ATIVO", fg="#2ecc71")
            self.status_indicator.itemconfig(self.led, fill="#2ecc71")
            
            # Inicia Watchdog
            self.observer = Observer()
            self.observer.schedule(MonitorHandler(self.adicionar_log), path=".", recursive=False)
            self.observer.start()
            self.adicionar_log("Serviço de monitoria iniciado.")

    def pausar(self):
        self.rodando = False
        self.status_label.config(text="MONITORAMENTO PAUSADO", fg="#e67e22")
        self.status_indicator.itemconfig(self.led, fill="#e67e22")
        if self.observer:
            self.observer.stop()
        self.adicionar_log("Pausado.")

    def limpar_logs(self):
        self.log_area.delete('1.0', tk.END)

    def ao_fechar(self):
        """Mata todos os processos e threads ao sair."""
        self.ativo = False
        self.rodando = False
        if self.observer:
            self.observer.stop()
            self.observer.join() # Aguarda a thread do watchdog morrer
        self.root.quit() # Encerra o mainloop
        self.root.destroy() # Destrói a janela
        os._exit(0) # Força o encerramento do processo Python no Windows

if __name__ == "__main__":
    root = tk.Tk()
    app = AppSeguranca(root)
    root.mainloop()