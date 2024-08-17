import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from PIL import Image, ImageTk
import io

class ProfileManagement(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_id = self.controller.auth_service.current_user_id  # Get current user's ID
        self.configure(style="ProfileManagement.TFrame")

        # Debug: Ensure user_id is correctly set
        logging.debug(f"ProfileManagement initialized for user_id: {self.user_id}")
        
        # Set up the main layout with two frames: one for profile management, one for user details
        self.left_frame = ttk.Frame(self, padding="20 20 20 20", style="LeftFrame.TFrame")
        self.right_frame = ttk.Frame(self, padding="20 20 20 20", style="RightFrame.TFrame")
        
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        if not self.controller.ensure_authenticated():
            return
        
        # Configure the grid to allow resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize the interface components
        self.setup_left_frame()
        self.setup_right_frame()

        # Load the profile data
        self.load_profile_data()

    def setup_left_frame(self):
        # Profile Details Section in the Left Frame
        ttk.Label(self.left_frame, text="Profile Details", font=("Helvetica", 16, "bold"), style="ProfileDetails.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Profile Picture and Name Fields
        self.profile_image_label = ttk.Label(self.left_frame, text="😊", font=("Helvetica", 50))
        self.profile_image_label.grid(row=1, column=0, rowspan=2, sticky="w", padx=(0, 20))
        
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
        self.registration_date = ttk.Label(self.left_frame, text="", style="ProfileDetails.TLabel")
        self.registration_date.grid(row=4, column=2, sticky="w", padx=(10, 0))

        save_button = ttk.Button(self.left_frame, text="Save Changes", command=self.save_profile, style="SaveButton.TButton")
        save_button.grid(row=5, column=2, sticky="e", pady=(20, 0))

        # Password Management Section
        ttk.Label(self.left_frame, text="Change Password", font=("Helvetica", 16, "bold"), style="PasswordManagement.TLabel").grid(row=6, column=0, columnspan=3, sticky="w", pady=(20, 10))
        
        ttk.Label(self.left_frame, text="Old Password", style="PasswordManagement.TLabel").grid(row=7, column=0, sticky="w")
        self.old_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.old_password_entry.grid(row=7, column=2, sticky="w", padx=(10, 0))

        ttk.Label(self.left_frame, text="New Password", style="PasswordManagement.TLabel").grid(row=8, column=0, sticky="w")
        self.new_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.new_password_entry.grid(row=8, column=2, sticky="w", padx=(10, 0))

        ttk.Label(self.left_frame, text="Confirm Password", style="PasswordManagement.TLabel").grid(row=9, column=0, sticky="w")
        self.confirm_password_entry = ttk.Entry(self.left_frame, width=30, show="*")
        self.confirm_password_entry.grid(row=9, column=2, sticky="w", padx=(10, 0))

        change_password_button = ttk.Button(self.left_frame, text="Change Password", command=self.change_password, style="ChangePasswordButton.TButton")
        change_password_button.grid(row=10, column=2, sticky="e", pady=(20, 0))

        # Delete Account Section
        ttk.Label(self.left_frame, text="Delete Account", font=("Helvetica", 16, "bold"), style="DeleteAccount.TLabel").grid(row=11, column=0, columnspan=3, sticky="w", pady=(20, 10))
        
        delete_account_button = ttk.Button(self.left_frame, text="Delete Account", command=self.delete_account, style="DeleteButton.TButton")
        delete_account_button.grid(row=12, column=2, sticky="w", pady=(10, 0))

    def setup_right_frame(self):
        # Right-side Frame for User Details and History
        ttk.Label(self.right_frame, text="User Profile & History", font=("Helvetica", 18, "bold"), style="RightFrame.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # User Details Section
        self.details_label = ttk.Label(self.right_frame, text="Loading...", font=("Helvetica", 14, "bold"), style="RightFrame.TLabel")
        self.details_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # View History Button
        view_history_button = ttk.Button(self.right_frame, text="View History", command=self.view_history, style="HistoryButton.TButton")
        view_history_button.grid(row=2, column=0, sticky="e", pady=(20, 0))

    def load_profile_data(self):
        """Load profile data from the database using ProfileManager."""
        if not self.controller.ensure_authenticated():
            return

        # Get the user's profile data
        profile_data = self.controller.profile_manager.getProfile(self.user_id)
        
        if profile_data:
            # Safely insert profile data into the fields
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)

            # Only insert data if it's not None
            if profile_data.get("first_name"):
                self.first_name_entry.insert(0, profile_data.get("first_name", ""))
            if profile_data.get("last_name"):
                self.last_name_entry.insert(0, profile_data.get("last_name", ""))
            if profile_data.get("created_at"):
                self.registration_date.configure(text=profile_data.get("created_at", ""))

            # Load profile picture if available
            if profile_data.get("profile_picture"):
                profile_image_data = profile_data["profile_picture"]
                image = Image.open(io.BytesIO(profile_image_data))
                self.profile_image = ImageTk.PhotoImage(image)
                self.profile_image_label.configure(image=self.profile_image)

            # Load additional user details
            details_text = f"""
            Username: {profile_data.get("username", "")}
            Email: {profile_data.get("email", "")}
            Joined: {profile_data.get("created_at", "")}
            Last Login: {profile_data.get("last_login", "")}
            """
            self.details_label.configure(text=details_text)
        else:
            # If no profile data, inform the user or simply keep the fields empty
            logging.warning(f"No profile data found for user ID {self.user_id}.")
            messagebox.showwarning("Warning", "No profile data found. Please fill in your details.")



    def save_profile(self):
        """Save profile details and preferences."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        profile_picture = self.profile_image if hasattr(self, 'profile_image') else None

        # Prepare data for update
        new_data = {
            "first_name": first_name,
            "last_name": last_name,
            "profile_picture": profile_picture
        }

        # Update profile in the database
        success = self.controller.profile_manager.updateProfile(self.user_id, new_data)
        if success:
            messagebox.showinfo("Profile Saved", f"Profile saved for {first_name} {last_name}.")
            self.load_profile_data()  # Reload the data to reflect changes
        else:
            messagebox.showerror("Error", "Failed to save profile.")

    def upload_picture(self):
        """Handle uploading a profile picture."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.profile_image_data = f.read()

                image = Image.open(io.BytesIO(self.profile_image_data))
                self.profile_image = ImageTk.PhotoImage(image)
                self.profile_image_label.configure(image=self.profile_image)
                messagebox.showinfo("Profile Picture", "Profile picture updated successfully!")
            except Exception as e:
                logging.error(f"Error loading profile picture: {e}")
                self.display_error_popup(f"Unable to load image. Error: {e}")

    def change_password(self):
        """Handle changing the user's password."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if new_password == confirm_password:
            # Implement password change logic
            success = self.controller.auth_service.change_password(self.user_id, old_password, new_password)
            if success:
                messagebox.showinfo("Change Password", "Password changed successfully!")
            else:
                self.display_error_popup("Failed to change password. Please try again.")
        else:
            self.display_error_popup("Passwords do not match. Please try again.")

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
            success = self.controller.profile_manager.delete_account(self.user_id)
            if success:
                messagebox.showinfo("Account Deleted", "Your account has been deleted.")
                self.controller.auth_service.logout()
                self.controller.showLoginScreen()
            else:
                self.display_error_popup("Failed to delete account.")

    def export_data(self):
        """Handle exporting user data."""
        messagebox.showinfo("Export Data", "Data export functionality is not implemented yet.")

    def view_history(self):
        """View the user's history of tasks."""
        messagebox.showinfo("History", "Viewing user history... (Functionality not implemented)")

    def display_error_popup(self, message):
        """Display an error message in a popup dialog."""
        logging.error(f"Error: {message}")
        messagebox.showerror("Error", message)
