import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Couleurs et styles
theme_bg = "#2C3E50"
theme_fg = "#ECF0F1"
theme_button_bg = "#3498DB"
theme_button_fg = "#FFFFFF"

def importer_et_afficher():
    fichier = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv"), ("Fichiers Excel", "*.xlsx")])
    if not fichier:
        return
    
    try:
        if fichier.endswith('.csv'):
            df = pd.read_csv(fichier)
        elif fichier.endswith('.xlsx'):
            df = pd.read_excel(fichier)
        else:
            messagebox.showerror("Erreur", "Format de fichier non supporté")
            return
        
        # Afficher un aperçu des données
        apercu_text.delete("1.0", tk.END)
        apercu_text.insert(tk.END, df.head().to_string())
        
        # Afficher le nombre total d'enregistrements
        count_label.config(text=f"Nombre total d'enregistrements : {len(df)}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

# Interface graphique avec Tkinter
app = tk.Tk()
app.title("Importateur de Fichier Excel/CSV")
app.geometry("800x500")
app.configure(bg=theme_bg)

frame = tk.Frame(app, bg=theme_bg)
frame.pack(expand=True, fill='both', padx=20, pady=20)

tk.Label(frame, text="Importateur de Fichier", font=("Arial", 16, "bold"), bg=theme_bg, fg=theme_fg).pack(pady=10)
import_button = tk.Button(frame, text="Importer un fichier", command=importer_et_afficher, bg=theme_button_bg, fg=theme_button_fg, font=("Arial", 12, "bold"), padx=10, pady=5)
import_button.pack(pady=10)

count_label = tk.Label(frame, text="Nombre total d'enregistrements : ", font=("Arial", 12), bg=theme_bg, fg=theme_fg)
count_label.pack(pady=5)

apercu_text = tk.Text(frame, height=10, width=80, font=("Courier", 10), bg="#34495E", fg=theme_fg)
apercu_text.pack(pady=10, fill='both', expand=True)

app.mainloop()