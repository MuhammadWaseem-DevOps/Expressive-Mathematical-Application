import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image

class SignupScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#F5F5F5")

        left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#F5F5F5")
        left_frame.place(relx=0, rely=0.1, relwidth=0.5, relheight=0.8)
        image_path = "Gui/assets/logo.webp"
        try:
            image = Image.open(image_path)

            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            image = image.resize((int(parent.winfo_screenwidth() * 0.5), parent.winfo_screenheight()), resample_filter)
            self.logo_image = ImageTk.PhotoImage(image)
            logo_label = tk.Label(left_frame, image=self.logo_image)
            logo_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            logo_label = ctk.CTkLabel(left_frame, text="Image not found", font=("Helvetica", 22, "bold"), text_color="#333333", fg_color="#F5F5F5")
            logo_label.place(relwidth=1, relheight=1)

        right_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#FFFFFF")
        right_frame.place(relx=0.5, rely=0.1, relwidth=0.4, relheight=0.8)

        logo = ctk.CTkLabel(right_frame, text="Expressive Mathematical application", font=("Helvetica", 22, "bold"), anchor="center")
        logo.pack(pady=(20, 10))

        welcome_label = ctk.CTkLabel(right_frame, text="Create your account", font=("Helvetica", 18))
        welcome_label.pack(pady=(10, 30))

        self.signup_username_entry = ctk.CTkEntry(right_frame, placeholder_text="Username", width=250)
        self.signup_username_entry.pack(pady=(10, 10))

        self.signup_email_entry = ctk.CTkEntry(right_frame, placeholder_text="Email", width=250)
        self.signup_email_entry.pack(pady=(10, 10))

        self.signup_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=250)
        self.signup_password_entry.pack(pady=(10, 10))

        self.signup_confirm_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Confirm Password", show="*", width=250)
        self.signup_confirm_password_entry.pack(pady=(10, 20))

        signup_button = ctk.CTkButton(right_frame, text="Sign Up", command=self.handle_signup, fg_color="#28a745", hover_color="#218838")
        signup_button.pack(pady=(20, 10))

        login_button = ctk.CTkButton(right_frame, text="Back to Login", command=self.controller.showLoginScreen, fg_color="#007bff", hover_color="#0056b3")
        login_button.pack(pady=(10, 20))

    def handle_signup(self):
        username = self.signup_username_entry.get()
        email = self.signup_email_entry.get()
        password = self.signup_password_entry.get()
        confirm_password = self.signup_confirm_password_entry.get()

        if self.controller.signup(username, password, confirm_password, email):
            self.controller.showLoginScreen()
