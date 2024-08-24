import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#F5F5F5")

        # Left image section
        left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#F5F5F5")
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        image_path = "./assets/img/logo-img-1.webp"
        try:
            image = Image.open(image_path)
            image = image.resize((int(parent.winfo_screenwidth() * 0.5), parent.winfo_screenheight()), Image.ANTIALIAS)
            self.logo_image = ImageTk.PhotoImage(image)
            logo_label = tk.Label(left_frame, image=self.logo_image)
            logo_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            logo_label = ctk.CTkLabel(left_frame, text="Image not found", font=("Helvetica", 22, "bold"), text_color="#333333", fg_color="#F5F5F5")
            logo_label.place(relwidth=1, relheight=1)

        # Right form section
        right_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#FFFFFF")
        right_frame.place(relx=0.5, rely=0.1, relwidth=0.4, relheight=0.8)

        logo = ctk.CTkLabel(right_frame, text="Expressive Mathematical App", font=("Helvetica", 22, "bold"), anchor="center")
        logo.pack(pady=(20, 10))

        welcome_label = ctk.CTkLabel(right_frame, text="Welcome back you've been missed!", font=("Helvetica", 18))
        welcome_label.pack(pady=(10, 30))

        self.username_entry = ctk.CTkEntry(right_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=(10, 10))

        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=(10, 10))

        remember_me_var = tk.BooleanVar()
        remember_me_check = ctk.CTkCheckBox(right_frame, text="Keep me logged in", variable=remember_me_var)
        remember_me_check.pack(pady=(10, 10))

        self.login_button = ctk.CTkButton(right_frame, text="Log in now", command=self.handle_login, fg_color="#28a745", hover_color="#218838")
        self.login_button.pack(pady=(20, 10))

        signup_button = ctk.CTkButton(right_frame, text="Create new account", command=self.controller.showSignupScreen, fg_color="#007bff", hover_color="#0056b3")
        signup_button.pack(pady=(10, 10))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.controller.login(username, password):
            # Redirect to the main app screen (e.g., dashboard)
            self.controller.showDashboard()
