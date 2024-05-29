import os
import tkinter as tk
from tkinter import ttk, messagebox
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

# Funzione di validazione per accettare solo numeri negli Entry
def is_numeric(value):
    return value.isdigit() or value == ""

# Calcolo del TDEE usando la formula Mifflin-St Jeor
def calculate_tdee(weight, height, eta, gender, wo):
    if gender == "Maschio":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * eta)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * eta)

    # Fattore di attività basato sull'attività fisica selezionata
    if wo == "Meno di 2 ore settimanali":
        multiplier = 1.2
    elif wo == "Da 3 a 5 ore settimanali":
        multiplier = 1.375
    else:
        multiplier = 1.55

    return bmr * multiplier

# Funzione per stimare la variazione del peso
def weight_projection(weight, goal):
    months = range(1, 7)  # Proiezione per i prossimi 6 mesi
    estimated_weights = []

    # Stima del cambiamento di peso in base all'obiettivo
    for month in months:
        if goal == "Definizione":  # Obiettivo di perdita di peso
            estimated_weights.append(weight - (0.5 * month))  # Perdita di circa 0.5 kg al mese
        elif goal == "Mantenimento":  # Obiettivo di mantenimento del peso
            estimated_weights.append(weight)  # Peso stabile
        elif goal == "Aumentare massa muscolare":  # Obiettivo di aumento del peso
            estimated_weights.append(weight + (0.3 * month))  # Aumento di circa 0.3 kg al mese
    
    return months, estimated_weights

# Funzione per generare e salvare il grafico come PNG
def save_weight_graph(weight, goal):
    months, estimated_weights = weight_projection(weight, goal)
    
    plt.figure()
    plt.plot(months, estimated_weights, marker='o', linestyle='-', color='b')
    plt.title("Peso nei prossimi 6 mesi")
    plt.xlabel("Mese")
    plt.ylabel("Peso (kg)")
    plt.grid(True)
    
    # Salva il grafico come file PNG
    graph_filename = "weight_projection.png"
    plt.savefig(graph_filename)
    plt.close()  # Chiudi il grafico per evitare problemi con la memoria
    
    return graph_filename

# Funzione per generare il piano nutrizionale
def generate_nutrition_plan(weight, height, goal, wo, eta, gender):
    api_key = os.environ.get("MISTRAL_API_KEY")
    model = "open-mistral-7b"

    if not api_key:
        messagebox.showerror("Errore", "MISTRAL_API_KEY non trovato nell'ambiente.")
        return None

    client = MistralClient(api_key=api_key)

    chat_response = client.chat(
        model=model,
        messages=[
            ChatMessage(
                role="user",
                content=f"Ecco le informazioni su una persona che ha {eta} anni: Peso: {weight} kg, Altezza: {height} cm, Genere: {gender}, Obiettivo: {goal}. Crea un piano nutrizionale giornaliero che includa colazione, pranzo, cena e spuntini."
            )
        ],
    )

    return chat_response.choices[0].message.content

# Funzione per gestire il click sul pulsante "Genera"
def submit_info():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        goal = goal_combobox.get()
        wo = wo_combobox.get()
        eta = int(eta_entry.get())
        gender = gender_combobox.get()

        # Calcola il TDEE
        tdee = calculate_tdee(weight, height, eta, gender, wo)
        
        plan = generate_nutrition_plan(weight, height, goal, wo, eta, gender)
        
        # Salva il piano generato
        save_plan(plan)
        
        # Mostra il fabbisogno calorico giornaliero
        tdee_label.config(text=f"Fabbisogno calorico giornaliero: {tdee:.2f} kcal")
        
        # Salva il grafico del peso
        graph_filename = save_weight_graph(weight, goal)
        
        # Mostra il grafico nella GUI
        update_graph(graph_filename)
    
    except ValueError:
        messagebox.showerror("Errore", "Assicurati che i campi di peso, altezza, e età contengano solo numeri.")

# Funzione per aggiornare il grafico nella GUI
def update_graph(graph_filename):
    img = Image.open(graph_filename)
    img = img.resize((300, 300))  # Ridimensiona l'immagine se necessario
    img_tk = ImageTk.PhotoImage(img)
    graph_canvas.create_image(150, 150, image=img_tk, anchor=tk.CENTER)
    graph_canvas.image = img_tk  # Mantieni una referenza per evitare che l'immagine venga rimossa

def save_plan(plan):
    file_name = "dieta.txt"
    with open(file_name, "w") as file:
        file.write(plan)
    messagebox.showinfo("Successo", f"Il piano nutrizionale è stato salvato in {file_name}")

# Creazione della GUI
root = tk.Tk()
root.title("NutrizionAItor")

validate_command = (root.register(is_numeric), "%P")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky=tk.W + tk.E)

# Etichette e campi di input
ttk.Label(frame, text="Peso (kg):").grid(row=0, column=0, padx=5, pady=5)
weight_entry = ttk.Entry(frame, validate="key", validatecommand=validate_command)
weight_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Altezza (cm):").grid(row=1, column=0, padx=5, pady=5)
height_entry = ttk.Entry(frame, validate="key", validatecommand=validate_command)
height_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame, text="Genere:").grid(row=2, column=0, padx=5, pady=5)
gender_combobox = ttk.Combobox(frame, values=["Maschio", "Femmina"], state="readonly")
gender_combobox.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame, text="Età (anni):").grid(row=3, column=0, padx=5, pady=5)
eta_entry = ttk.Entry(frame, validate="key", validatecommand=validate_command)
eta_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame, text="Attività Fisica:").grid(row=4, column=0, padx=5, pady=5)
wo_combobox = ttk.Combobox(frame, values=["Meno di 2 ore settimanali", "Da 3 a 5 ore settimanali", "Più di 5 ore settimanali"], state="readonly")
wo_combobox.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(frame, text="Obiettivo:").grid(row=5, column=0, padx=5, pady=5)
goal_combobox = ttk.Combobox(frame, values=["Definizione", "Mantenimento", "Aumentare massa muscolare"], state="readonly")
goal_combobox.grid(row=5, column=1, padx=5, pady=5)

# Bottone di invio
submit_button = ttk.Button(frame, text="Genera", command=submit_info)
submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Etichetta per il TDEE
tdee_label = ttk.Label(frame, text="")
tdee_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Aggiungi un Canvas per mostrare il grafico
graph_canvas = tk.Canvas(frame, width=300, height=300, bg="white")
graph_canvas.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()