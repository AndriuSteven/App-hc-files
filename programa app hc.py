import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class ChecklistApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Checklist App")
        self.master.geometry("800x400")

        self.logged_in = False
        self.max_activities = 10
        self.activities_count = 0
        self.activities = []
        self.create_login_widgets()
        
    def create_login_widgets(self):
        self.username_label = tk.Label(self.master, text="Usuario:")
        self.username_label.grid(row=0, column=0, pady=10)

        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, pady=10)

        self.password_label = tk.Label(self.master, text="Contraseña:")
        self.password_label.grid(row=1, column=0, pady=10)

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)

        self.login_button = tk.Button(self.master, text="Iniciar sesión", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=10)

    def create_checklist_widgets(self):
        # Limpiar widgets de inicio de sesión
        self.username_label.grid_forget()
        self.username_entry.grid_forget()
        self.password_label.grid_forget()
        self.password_entry.grid_forget()
        self.login_button.grid_forget()

        # Mostrar mensaje de bienvenida
        welcome_message = "Bienvenido a la aplicación de productividad de Hilanderías Cumbayá"
        self.welcome_label = tk.Label(self.master, text=welcome_message)
        self.welcome_label.grid(row=0, columnspan=2, pady=10)

        # Crear widgets de lista de verificación
        activity_label = tk.Label(self.master, text="Actividad para realizar:")
        activity_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.activity_entry = tk.Entry(self.master, width=30)
        self.activity_entry.grid(row=1, column=1, padx=10, pady=10)

        self.time_var = tk.StringVar()
        self.time_entry = tk.Entry(self.master, width=10, textvariable=self.time_var)
        self.time_entry.grid(row=1, column=2, padx=10, pady=10)
        self.time_entry.config(validate="key", validatecommand=(self.time_entry.register(self.validate_input), "%P"))

        time_label = tk.Label(self.master, text="minutos")
        time_label.grid(row=1, column=3, pady=10)

        self.add_button = tk.Button(self.master, text="Agregar actividad", command=self.add_activity)
        self.add_button.grid(row=1, column=4, padx=10, pady=10)

        self.save_button = tk.Button(self.master, text="Guardar", command=self.save_activities)
        self.save_button.grid(row=1, column=5, padx=10, pady=10)

        self.activities_tree = DragDropTreeview(self.master, columns=("No.", "Actividad", "Tiempo (min)", "Estado", "Temporizador", "Acción"), show="headings")
        self.activities_tree.heading("No.", text="No.")
        self.activities_tree.heading("Actividad", text="Actividad")
        self.activities_tree.heading("Tiempo (min)", text="Tiempo (min)")
        self.activities_tree.heading("Estado", text="Estado")
        self.activities_tree.heading("Temporizador", text="Temporizador")
        self.activities_tree.heading("Acción", text="Acción")
        self.activities_tree.bind("<ButtonRelease-1>", self.show_completion_popup)
        self.activities_tree.bind("<Button-3>", self.show_context_menu)
        self.activities_tree.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

        # Botones adicionales
        self.special_activity_button = tk.Button(self.master, text="Actividad Especial", command=self.special_activity)
        self.special_activity_button.grid(row=3, column=4, padx=10, pady=10)

        self.exit_button = tk.Button(self.master, text="Salida de Hilanderias Cumbayá", command=self.exit_program)
        self.exit_button.grid(row=3, column=5, padx=10, pady=10)

    def login(self):
        # Verificar usuario y contraseña
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # el usuario y la contraseña son "admin"
        if username == "admin" and password == "admin":
            self.logged_in = True
            self.create_checklist_widgets()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def add_activity(self):
        if self.activities_count < self.max_activities:
            activity_text = self.activity_entry.get().strip()
            time = self.time_entry.get().strip()
            if activity_text:
                self.activities.append({"text": activity_text, "time": int(time) * 60, "completed": False, "running": False})
                self.activities_count += 1
                self.update_activities()
                self.activity_entry.delete(0, tk.END)
                self.time_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Ya has alcanzado el máximo de actividades (10)")
    
    def toggle_activity(self, index):
        activity = self.activities[index]
        if not activity["running"]:
            activity["running"] = True
            self.start_timer(index)
        else:
            activity["running"] = False

    def start_timer(self, index):
        activity = self.activities[index]
        time_remaining = activity["time"]
        while time_remaining > 0 and activity["running"]:
            minutes = time_remaining // 60
            seconds = time_remaining % 60
            timer = self.format_time(time_remaining)
            self.activities_tree.item(index, values=(index+1, activity["text"], activity["time"]//60, "En progreso", timer, "Pausar"))
            time.sleep(1)
            time_remaining -= 1
        if time_remaining == 0:
            activity["completed"] = True
            self.activities_tree.item(index, values=(index+1, activity["text"], activity["time"]//60, "Completada", "00:00", "Iniciar"))

    def delete_activity(self, index):
        del self.activities[index]
        self.activities_count -= 1
        self.update_activities()

    def save_activities(self):
        # Guardar actividades en una base de datos o archivo
        messagebox.showinfo("Guardar", "Actividades guardadas correctamente")

    def update_activities(self):
        # Limpiar la tabla antes de actualizar
        for i in self.activities_tree.get_children():
            self.activities_tree.delete(i)

        # Actualizar la tabla con las actividades
        for index, activity in enumerate(self.activities, start=1):
            activity_text = activity["text"]
            time = activity["time"] // 60
            completed = "Completada" if activity["completed"] else "No completada"
            timer = "--:--" if not activity["running"] else self.format_time(activity["time"])
            action = "Iniciar" if not activity["running"] else "Pausar"
            self.activities_tree.insert("", "end", values=(index, activity_text, time, completed, timer, action))

    def show_completion_popup(self, event):
        selected_item = self.activities_tree.selection()
        if selected_item:
            index = int(selected_item[0][1:]) - 1
            self.show_message(index)

    def show_context_menu(self, event):
        self.activities_tree.focus()
        selected_item = self.activities_tree.identify_row(event.y)
        if selected_item:
            index = int(selected_item[1:]) - 1
            activity_text = self.activities[index]["text"]
            menu = tk.Menu(self.master, tearoff=0)
            menu.add_command(label="Iniciar actividad", command=lambda: self.start_activity(index))
            menu.post(event.x_root, event.y_root)

    def start_activity(self, index):
        self.toggle_activity(index)

    def show_message(self, index):
        activity_text = self.activities[index]["text"]
        completed = self.activities[index]["completed"]
        popup = tk.Toplevel(self.master)
        popup.title("Marcar como Completada")
        popup.geometry("250x100")
        popup.resizable(False, False)
        
        message_label = tk.Label(popup, text=f"¿Marcar como {'No ' if completed else ''}Completada la actividad '{activity_text}'?")
        message_label.pack(pady=5)
        
        toggle_button_text = "Completada" if not completed else "No Completada"
        toggle_button = tk.Button(popup, text=toggle_button_text, command=lambda: self.toggle_activity(index))
        toggle_button.pack(pady=5)

    def validate_input(self, value):
        # Validar que el valor ingresado sea un número
        if value.isdigit() or value == "":
            return True
        else:
            return False

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def special_activity(self):
        messagebox.showinfo("Actividad Especial", "Apartado para realizar una actividad especial")

    def exit_program(self):
        if messagebox.askokcancel("Salir", "¿Seguro que desea salir?"):
            self.master.destroy()

class DragDropTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<ButtonPress-1>", self.on_start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.drag_data = {"item": None, "index": None}

    def on_start_drag(self, event):
        item = self.identify_row(event.y)
        if item:
            self.drag_data["item"] = item
            self.drag_data["index"] = self.index(item)

    def on_drag(self, event):
        if self.drag_data["item"]:
            x, y = event.x, event.y
            self.coords(self.drag_data["item"], x, y)

    def on_drop(self, event):
        if self.drag_data["item"]:
            new_index = self.index("@{},{}".format(event.x, event.y))
            if new_index:
                self.move(self.drag_data["item"], "", new_index)
                self.drag_data["index"] = new_index

                

def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

