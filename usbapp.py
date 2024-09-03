import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class BootMaker:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("BootMaker")
        self.ventana.geometry("800x600")
        self.ventana.configure(bg="#f0f0f0")
        self.ventana.resizable(False, False)

        self.frame = tk.Frame(self.ventana, bg="#ffffff", padx=20, pady=20)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.etiqueta_iso = tk.Label(self.frame, text="Archivo ISO:", bg="#ffffff", font=('Arial', 12, 'bold'))
        self.etiqueta_iso.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entrada_iso = tk.Entry(self.frame, width=60, font=('Arial', 12))
        self.entrada_iso.grid(row=0, column=1, padx=10, pady=10)

        self.boton_iso = tk.Button(self.frame, text="Seleccionar ISO", command=self.seleccionar_iso, bg="#007bff", fg="white", font=('Arial', 12, 'bold'))
        self.boton_iso.grid(row=0, column=2, padx=10, pady=10)

        self.etiqueta_usb = tk.Label(self.frame, text="Unidad USB:", bg="#ffffff", font=('Arial', 12, 'bold'))
        self.etiqueta_usb.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entrada_usb = tk.Entry(self.frame, width=60, font=('Arial', 12))
        self.entrada_usb.grid(row=1, column=1, padx=10, pady=10)

        self.boton_usb = tk.Button(self.frame, text="Seleccionar USB", command=self.seleccionar_usb, bg="#007bff", fg="white", font=('Arial', 12, 'bold'))
        self.boton_usb.grid(row=1, column=2, padx=10, pady=10)

        self.etiqueta_particion = tk.Label(self.frame, text="Tipo de Partición:", bg="#ffffff", font=('Arial', 12, 'bold'))
        self.etiqueta_particion.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.opcion_particion = tk.StringVar(value="GPT")
        self.menu_particion = tk.OptionMenu(self.frame, self.opcion_particion, "GPT", "MBR")
        self.menu_particion.config(font=('Arial', 12))
        self.menu_particion.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.etiqueta_formato = tk.Label(self.frame, text="Formato de Archivo:", bg="#ffffff", font=('Arial', 12, 'bold'))
        self.etiqueta_formato.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.opcion_formato = tk.StringVar(value="FAT32")
        self.menu_formato = tk.OptionMenu(self.frame, self.opcion_formato, "FAT32", "NTFS")
        self.menu_formato.config(font=('Arial', 12))
        self.menu_formato.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.boton_ejecutar = tk.Button(self.frame, text="Grabar ISO", command=self.ejecutar, bg="#28a745", fg="white", font=('Arial', 12, 'bold'))
        self.boton_ejecutar.grid(row=4, column=1, padx=10, pady=20, sticky="w")

    def seleccionar_iso(self):
        ruta_iso = filedialog.askopenfilename(title="Seleccionar archivo ISO", filetypes=[("Archivos ISO", "*.iso")])
        if ruta_iso:
            self.entrada_iso.delete(0, tk.END)
            self.entrada_iso.insert(0, ruta_iso)

    def seleccionar_usb(self):
        ruta_usb = filedialog.askdirectory(title="Seleccionar unidad USB")
        if ruta_usb:
            disk_id = self.obtener_identificador_disco(ruta_usb)
            if disk_id:
                self.entrada_usb.delete(0, tk.END)
                self.entrada_usb.insert(0, disk_id)

    def obtener_identificador_disco(self, ruta_usb):
        try:
            result = subprocess.run(["diskutil", "info", ruta_usb], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("Device Identifier:"):
                    return line.split(":")[1].strip()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el identificador del disco: {e}")
        return None

    def ejecutar(self):
        ruta_iso = self.entrada_iso.get()
        unidad_usb = self.entrada_usb.get()
        tipo_particion = self.opcion_particion.get()
        tipo_formato = self.opcion_formato.get()

        if not ruta_iso or not unidad_usb:
            messagebox.showwarning("Advertencia", "Debe seleccionar una ISO y una unidad USB.")
            return

        try:
            self.formatear_usb(unidad_usb, tipo_particion, tipo_formato)
            self.grabar_iso_a_usb(ruta_iso, unidad_usb)
            self.verificar_grabacion(unidad_usb)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo grabar la ISO en la USB: {e}")

    def formatear_usb(self, unidad_usb, tipo_particion, tipo_formato):
        try:
            print(f"Formateando la unidad {unidad_usb} como {tipo_particion} con formato {tipo_formato}...")
            subprocess.run(["diskutil", "unmountDisk", unidad_usb], check=True)
            subprocess.run(["diskutil", "partitionDisk", unidad_usb, tipo_particion, "Free Space", "100%"], check=True)
            if tipo_formato == "FAT32":
                subprocess.run(["diskutil", "eraseDisk", "FAT32", "Untitled", unidad_usb], check=True)
            elif tipo_formato == "NTFS":
                subprocess.run(["diskutil", "eraseDisk", "NTFS", "Untitled", unidad_usb], check=True)
            print("Formato completado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo formatear la USB: {e}")

    def grabar_iso_a_usb(self, ruta_iso, unidad_usb):
        try:
            print(f"Grabando {ruta_iso} en {unidad_usb}...")
            subprocess.run(["sudo", "dd", f"if={ruta_iso}", f"of={unidad_usb}", "bs=4m", "status=progress"], check=True)
            print("Grabación completada.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo grabar la ISO en la USB: {e}")

    def verificar_grabacion(self, unidad_usb):
        try:
            print("Verificando la grabación...")
            result = subprocess.run(["diskutil", "info", unidad_usb], capture_output=True, text=True)
            if "EFI" in result.stdout or "Microsoft Basic Data" in result.stdout:
                messagebox.showinfo("Éxito", "La USB parece ser bootable.")
            else:
                messagebox.showwarning("Advertencia", "La USB no parece ser bootable.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo verificar la grabación: {e}")

    def run(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = BootMaker()
    app.run()
