import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

class ProfileManagement(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="ProfileManagement.TFrame")
        
        # Set up the main layout with two frames: one for profile management, one for user details
        self.left_frame = ttk.Frame(self, padding="20 20 20 20", style="LeftFrame.TFrame")
        self.right_frame = ttk.Frame(self, padding="20 20 20 20", style="RightFrame.TFrame")
        
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        # Configure the grid to allow resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize the interface components
        self.setup_left_frame()
        self.setup_right_frame()

    def setup_left_frame(self):
        # Profile Details Section in the Left Frame
        ttk.Label(self.left_frame, text="Profile Details", font=("Helvetica", 16, "bold"), style="ProfileDetails.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Profile Picture and Name Fields
        self.profile_image = ttk.Label(self.left_frame, text="😊", font=("Helvetica", 50))
        self.profile_image.grid(row=1, column=0, rowspan=2, sticky="w", padx=(0, 20))
        
        upload_button = ttk.Button(self.left_frame, text="Upload Picture", command=self.upload_picture, style="UploadButton.TButton")
        upload_button.grid(row=1, column=1, sticky="e", pady=(0, 10))

        ttk.Label(self.left_frame, text="First Name", style="ProfileDetails.TLabel").grid(row=2, column=1, sticky="w")
        self.first_name_entry = ttk.Entry(self.left_frame, width=30)
        self.first_name_entry.grid(row=2, column=2, sticky="w", padx=(10, 0))
        
        ttk.Label(self.left_frame, text="Last Name", style="ProfileDetails.TLabel").grid(row=3, column=1, sticky="w")
        self.last_name_entry = ttk.Entry(self.left_frame, width=30)
        self.last_name_entry.grid(row=3, column=2, sticky="w", padx=(10, 0))
        
        # Registration Date (Display only)
        ttk.Label(self.left_frame, text="Registration Date", style="ProfileDetails.TLabel").grid(row=4, column=1, sticky="w")
        self.registration_date = ttk.Label(self.left_frame, text="Fri 16 Aug 2024", style="ProfileDetails.TLabel")
        self.registration_date.grid(row=4, column=2, sticky="w", padx=(10, 0))

        save_button = ttk.Button(self.left_frame, text="Save Changes", command=self.save_profile, style="SaveButton.TButton")
        save_button.grid(row=5, column=2, sticky="e", pady=(20, 0))

        # Separator Line
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=(20, 20))

        # Password Management Section
        ttk.Label(self.left_frame, text="Change Password", font=("Helvetica", 16, "bold"), style="PasswordManagement.TLabel").grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        ttk.Label(self.left_frame, text="Old Password", style="PasswordManagement.TLabel").grid(row=8, column=0, sticky="w")
        self.old_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.old_password_entry.grid(row=8, column=2, sticky="w", padx=(10, 0))

        ttk.Label(self.left_frame, text="New Password", style="PasswordManagement.TLabel").grid(row=9, column=0, sticky="w")
        self.new_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.new_password_entry.grid(row=9, column=2, sticky="w", padx=(10, 0))

        ttk.Label(self.left_frame, text="Confirm Password", style="PasswordManagement.TLabel").grid(row=10, column=0, sticky="w")
        self.confirm_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.confirm_password_entry.grid(row=10, column=2, sticky="w", padx=(10, 0))

        change_password_button = ttk.Button(self.left_frame, text="Change Password", command=self.change_password, style="ChangePasswordButton.TButton")
        change_password_button.grid(row=11, column=2, sticky="e", pady=(20, 0))

        # Separator Line
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=12, column=0, columnspan=3, sticky="ew", pady=(20, 20))

        # Clear Data Section
        ttk.Label(self.left_frame, text="Clear Data", font=("Helvetica", 16, "bold"), style="ClearData.TLabel").grid(row=13, column=0, columnspan=3, sticky="w", pady=(0, 10))

        practice_clear_button = ttk.Button(self.left_frame, text="Clear Practice Data", command=self.clear_practice_data, style="ClearButton.TButton")
        practice_clear_button.grid(row=14, column=0, sticky="w", pady=(10, 0))

        notebook_clear_button = ttk.Button(self.left_frame, text="Clear Notebook Data", command=self.clear_notebook_data, style="ClearButton.TButton")
        notebook_clear_button.grid(row=14, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        # Separator Line
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=15, column=0, columnspan=3, sticky="ew", pady=(20, 20))

        # Export Data Section
        ttk.Label(self.left_frame, text="Export Data", font=("Helvetica", 16, "bold"), style="ExportData.TLabel").grid(row=16, column=0, columnspan=3, sticky="w", pady=(0, 10))

        export_data_button = ttk.Button(self.left_frame, text="Export Data", command=self.export_data, style="ExportButton.TButton")
        export_data_button.grid(row=17, column=0, sticky="w", pady=(10, 0))

        # Separator Line
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=18, column=0, columnspan=3, sticky="ew", pady=(20, 20))

        # Delete Account Section
        ttk.Label(self.left_frame, text="Delete Account", font=("Helvetica", 16, "bold"), style="DeleteAccount.TLabel").grid(row=19, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        delete_account_button = ttk.Button(self.left_frame, text="Delete Account", command=self.delete_account, style="DeleteButton.TButton")
        delete_account_button.grid(row=20, column=0, sticky="w", pady=(10, 0))

    def setup_right_frame(self):
        # Right-side Frame for User Details and History
        ttk.Label(self.right_frame, text="User Profile & History", font=("Helvetica", 18, "bold"), style="RightFrame.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # User Details Section
        ttk.Label(self.right_frame, text="Profile Information", font=("Helvetica", 14, "bold"), style="RightFrame.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        profile_image = ttk.Label(self.right_frame, text="😊", font=("Helvetica", 50))
        profile_image.grid(row=2, column=0, rowspan=2, sticky="w", pady=(10, 10))

        details_text = """
        Username: johndoe
        Email: johndoe@example.com
        Joined: 16 Aug 2023
        Last Login: 15 Aug 2024
        """
        ttk.Label(self.right_frame, text=details_text, style="RightFrame.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 10))

        # View History Button
        view_history_button = ttk.Button(self.right_frame, text="View History", command=self.view_history, style="HistoryButton.TButton")
        view_history_button.grid(row=5, column=0, sticky="e", pady=(20, 0))

    def save_profile(self):
        """Save profile details and preferences."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        print(f"Profile saved for {first_name} {last_name}")

        messagebox.showinfo("Profile Saved", f"Profile saved for {first_name} {last_name}.")

    def clear_practice_data(self):
        """Clear practice data."""
        messagebox.showinfo("Data Cleared", "Practice data has been cleared.")

    def clear_notebook_data(self):
        """Clear notebook data."""
        messagebox.showinfo("Data Cleared", "Notebook data has been cleared.")

    def delete_account(self):
        """Delete the user's account."""
        confirm = messagebox.askyesno("Delete Account", "Are you sure you want to delete your account? This action cannot be undone.")
        if confirm:
            messagebox.showinfo("Account Deleted", "Your account has been deleted.")

    def export_data(self):
        """Handle exporting user data."""
        messagebox.showinfo("Export Data", "Data export functionality is not implemented yet.")

    def upload_picture(self):
        """Handle uploading a profile picture."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                profile_image = tk.PhotoImage(file=file_path)
                self.profile_image.configure(image=profile_image, text="")
                self.profile_image.image = profile_image
                messagebox.showinfo("Profile Picture", "Profile picture updated successfully!")
            except tk.TclError as e:
                logging.error(f"Error loading profile picture: {e}")
                self.display_error_popup(f"Unable to load image. Error: {e}")

    def change_password(self):
        """Handle changing the user's password."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if new_password == confirm_password:
            messagebox.showinfo("Change Password", "Password changed successfully!")
        else:
            self.display_error_popup("Passwords do not match. Please try again.")

    def view_history(self):
        """View the user's history of tasks."""
        messagebox.showinfo("History", "Viewing user history... (Functionality not implemented)")

    def display_error_popup(self, message):
        """Display an error message in a popup dialog."""
        logging.error(f"Error: {message}")
        messagebox.showerror("Error", message)
