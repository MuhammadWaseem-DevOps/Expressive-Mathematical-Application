import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image

class SignupScreen(ctk.CTkFrame):
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
            logo_label = tk.Label(left_frame, image=self.logo_image, fg_color="#F5F5F5")
            logo_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            logo_label = ctk.CTkLabel(left_frame, text="Image not found", font=("Helvetica", 22, "bold"), text_color="#333333", fg_color="#F5F5F5")
            logo_label.place(relwidth=1, relheight=1)

        # Right form section
        right_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#FFFFFF")
        right_frame.place(relx=0.5, rely=0.1, relwidth=0.4, relheight=0.8)

        logo = ctk.CTkLabel(right_frame, text="MathApp", font=("Helvetica", 22, "bold"), anchor="center")
        logo.pack(pady=(20, 10))

        welcome_label = ctk.CTkLabel(right_frame, text="Create your account", font=("Helvetica", 18))
        welcome_label.pack(pady=(10, 30))

        self.signup_username_entry = ctk.CTkEntry(right_frame, placeholder_text="Username", width=250)
        self.signup_username_entry.pack(pady=(10, 10))

        self.signup_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=250)
        self.signup_password_entry.pack(pady=(10, 10))

        self.signup_confirm_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Confirm Password", show="*", width=250)
        self.signup_confirm_password_entry.pack(pady=(10, 20))

        signup_button = ctk.CTkButton(right_frame, text="Sign Up", command=self.controller.signup, fg_color="#28a745", hover_color="#218838")
        signup_button.pack(pady=(20, 10))

        login_button = ctk.CTkButton(right_frame, text="Back to Login", command=self.controller.showLoginScreen, fg_color="#007bff", hover_color="#0056b3")
        login_button.pack(pady=(10, 20))
