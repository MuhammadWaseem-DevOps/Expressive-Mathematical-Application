import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from PIL import Image, ImageTk, ImageOps, ImageDraw
import io
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.scrolledtext import ScrolledText  # Import ScrolledText

class ProfileManagement(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_id = self.controller.auth_service.current_user_id
        self.history_frame = None

        logging.debug(f"ProfileManagement initialized for user_id: {self.user_id}")

        # Set up the main layout with two frames: one for profile management, one for user details
        self.left_frame = ttk.Frame(self, padding="5 5", style="LeftFrame.TFrame")
        self.right_frame = ttk.Frame(self, padding="5 5", style="RightFrame.TFrame")
        
        self.left_frame.grid(row=0, column=0, sticky="nw", padx=(5, 5), pady=(5, 5))
        self.right_frame.grid(row=0, column=1, sticky="nw", padx=(5, 5), pady=(5, 5))

        if not self.controller.ensure_authenticated():
            return
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(2, weight=1)

        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Initialize the interface components
        self.setup_left_frame()
        self.setup_right_frame()

        # Load the profile data
        self.load_profile_data()

    def setup_left_frame(self):
        # Profile Details Section
        ttk.Label(self.left_frame, text="Profile Details", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="nw")

        # Profile Picture and Upload Button
        self.profile_image_label = ttk.Label(self.left_frame)
        self.profile_image_label.grid(row=1, column=0, sticky="nw", padx=(0, 5), pady=(5, 5))

        upload_button = ttk.Button(self.left_frame, text="Upload Picture", command=self.upload_picture)
        upload_button.grid(row=1, column=1, sticky="nw", pady=(5, 5))

        # Name Fields
        ttk.Label(self.left_frame, text="First Name").grid(row=2, column=0, sticky="w")
        self.first_name_entry = ttk.Entry(self.left_frame, width=25)
        self.first_name_entry.grid(row=2, column=1, sticky="w", padx=(5, 0))
        
        ttk.Label(self.left_frame, text="Last Name").grid(row=3, column=0, sticky="w")
        self.last_name_entry = ttk.Entry(self.left_frame, width=25)
        self.last_name_entry.grid(row=3, column=1, sticky="w", padx=(5, 0))
        
        # Registration Date (Display only)
        ttk.Label(self.left_frame, text="Registration Date").grid(row=4, column=0, sticky="w")
        self.registration_date = ttk.Label(self.left_frame, text="")
        self.registration_date.grid(row=4, column=1, sticky="w", padx=(5, 0))

        save_button = ttk.Button(self.left_frame, text="Save Changes", command=self.save_profile)
        save_button.grid(row=5, column=1, sticky="w", pady=(5, 5))

        # Password Management Section
        ttk.Label(self.left_frame, text="Change Password", font=("Helvetica", 16, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=(5, 5))
        
        ttk.Label(self.left_frame, text="Old Password").grid(row=7, column=0, sticky="w")
        self.old_password_entry = ttk.Entry(self.left_frame, width=25, show="*")
        self.old_password_entry.grid(row=7, column=1, sticky="w", padx=(5, 0))

        ttk.Label(self.left_frame, text="New Password").grid(row=8, column=0, sticky="w")
        self.new_password_entry = ttk.Entry(self.left_frame, width=25, show="*")
        self.new_password_entry.grid(row=8, column=1, sticky="w", padx=(5, 0))

        ttk.Label(self.left_frame, text="Confirm Password").grid(row=9, column=0, sticky="w")
        self.confirm_password_entry = ttk.Entry(self.left_frame, width=25, show="*")
        self.confirm_password_entry.grid(row=9, column=1, sticky="w", padx=(5, 0))

        change_password_button = ttk.Button(self.left_frame, text="Change Password", command=self.change_password)
        change_password_button.grid(row=10, column=1, sticky="w", pady=(5, 5))

        # Delete Account Section
        ttk.Label(self.left_frame, text="Delete Account", font=("Helvetica", 16, "bold")).grid(row=11, column=0, columnspan=2, sticky="w", pady=(5, 5))
        
        delete_account_button = ttk.Button(self.left_frame, text="Delete Account", command=self.delete_account)
        delete_account_button.grid(row=12, column=1, sticky="w", pady=(5, 0))

    def setup_right_frame(self):
        # Right-side Frame for User Details and History
        ttk.Label(self.right_frame, text="User Profile & History", font=("Helvetica", 16, "bold")).grid(row=0, column=0, sticky="nw", pady=(5, 5))

        # User Details Section with Separation
        self.add_label_value(self.right_frame, "Username:", "username", row=1)
        self.add_label_value(self.right_frame, "Email:", "email", row=2)
        self.add_label_value(self.right_frame, "Full Name:", "full_name", row=3)
        self.add_label_value(self.right_frame, "Joined:", "created_at", row=4)
        self.add_label_value(self.right_frame, "Last Login:", "last_login", row=5)
        self.add_label_value(self.right_frame, "Last Profile Update:", "profile_last_updated", row=6)
        self.add_label_value(self.right_frame, "Preferences:", "preferences", row=7)

        # View History Button (Aligned to the right)
        view_history_button = ttk.Button(self.right_frame, text="View History", command=self.show_history_frame)
        view_history_button.grid(row=8, column=0, sticky="nw", pady=(5, 5), padx=(5, 5))

    def add_label_value(self, frame, label_text, data_key, row):
        """Helper function to add label and value pairs."""
        ttk.Label(frame, text=label_text, font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky="w")
        self.details_label = ttk.Label(frame, text="", font=("Helvetica", 12))
        self.details_label.grid(row=row, column=1, sticky="w", padx=(5, 0))
        setattr(self, f"{data_key}_label", self.details_label)  # Store reference to the label for later update

    def load_profile_data(self):
        """Load profile data from the database using ProfileManager."""
        if not self.controller.ensure_authenticated():
            return

        profile_data = self.controller.profile_manager.getProfile(self.user_id)
        
        if profile_data:
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)

            if profile_data.get("first_name"):
                self.first_name_entry.insert(0, profile_data.get("first_name", ""))
            if profile_data.get("last_name"):
                self.last_name_entry.insert(0, profile_data.get("last_name", ""))
            if profile_data.get("created_at"):
                self.registration_date.configure(text=profile_data.get("created_at", ""))

            if profile_data.get("profile_picture"):
                profile_image_data = profile_data["profile_picture"]
                image = Image.open(io.BytesIO(profile_image_data))
                image = self._resize_and_crop_image(image, size=(120, 120))  # Adjust size for thumbnail
                self.profile_image = ImageTk.PhotoImage(image)
                self.profile_image_label.configure(image=self.profile_image)

            # Update the details labels with the correct data
            self.username_label.configure(text=profile_data.get("username", ""))
            self.email_label.configure(text=profile_data.get("email", ""))
            self.full_name_label.configure(text=profile_data.get("full_name", ""))
            self.created_at_label.configure(text=profile_data.get("created_at", ""))
            self.last_login_label.configure(text=profile_data.get("last_login", ""))
            self.profile_last_updated_label.configure(text=profile_data.get("profile_last_updated", ""))
            self.preferences_label.configure(text=profile_data.get("preferences", ""))
        else:
            logging.warning(f"No profile data found for user ID {self.user_id}.")
            messagebox.showwarning("Warning", "No profile data found. Please fill in your details.")

    def _resize_and_crop_image(self, image, size=(120, 120)):
        """Resize and crop the image to a circular thumbnail."""
        image = ImageOps.fit(image, size, Image.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        image.putalpha(mask)
        return image

    def save_profile(self):
        """Save profile details and preferences."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        profile_picture = self.profile_image_data if hasattr(self, 'profile_image_data') else None

        new_data = {
            "first_name": first_name,
            "last_name": last_name,
            "profile_picture": profile_picture
        }

        success = self.controller.profile_manager.updateProfile(self.user_id, new_data)
        if success:
            messagebox.showinfo("Profile Saved", f"Profile saved for {first_name} {last_name}.")
            self.load_profile_data()
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
                image = self._resize_and_crop_image(image, size=(120, 120))
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
            success = self.controller.auth_service.change_password(self.user_id, old_password, new_password)
            if success:
                messagebox.showinfo("Change Password", "Password changed successfully!")
            else:
                self.display_error_popup("Failed to change password. Please try again.")
        else:
            self.display_error_popup("Passwords do not match. Please try again.")

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

    def show_history_frame(self):
        """Show the computation history frame."""
        if self.history_frame is not None:
            self.history_frame.destroy()
        
        self.history_frame = tk.Toplevel(self)
        self.history_frame.title("Computation History")

        # Search bar
        search_frame = ttk.Frame(self.history_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        search_label = ttk.Label(search_frame, text="Search Equation:")
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_button = ttk.Button(search_frame, text="Search", command=lambda: self.search_computation(search_entry.get()))
        search_button.pack(side=tk.LEFT, padx=(10, 0))

        # Table for displaying computation history
        columns = ("ID", "Full Name", "Equation", "Result", "Date")
        self.history_table = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, anchor="center")

        self.history_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.history_table.bind("<Double-1>", self.show_computation_details)

        # Load more button
        load_more_button = ttk.Button(self.history_frame, text="Load More", command=self.load_more_history)
        load_more_button.pack(side=tk.BOTTOM, pady=10)

        # Load initial history
        self.load_history()

    def load_history(self, offset=0, limit=15):
        """Load computation history from the database."""
        history = self.controller.profile_manager.get_computation_history(self.user_id, offset, limit)
        for entry in history:
            self.history_table.insert("", "end", values=(entry[0], entry[1], entry[2], entry[3], entry[4]))

    def load_more_history(self):
        """Load more computation history."""
        current_items = len(self.history_table.get_children())
        self.load_history(offset=current_items)

    def search_computation(self, query):
        """Search computation history for the given query."""
        for item in self.history_table.get_children():
            self.history_table.delete(item)

        history = self.controller.profile_manager.search_computation_history(self.user_id, query)
        for entry in history:
            self.history_table.insert("", "end", values=(entry[0], entry[1], entry[2], entry[3], entry[4]))

    def show_computation_details(self, event):
        """Show detailed view of the selected computation."""
        selected_item = self.history_table.selection()
        if not selected_item:
            return

        item_values = self.history_table.item(selected_item, "values")
        computation_id = item_values[0]

        # Fetch computation details
        try:
            details = self.controller.profile_manager.get_computation_details(computation_id)
        except Exception as e:
            self.display_error_popup(f"Failed to load computation details: {str(e)}")
            return

        # Create a new window for computation details
        detail_frame = tk.Toplevel(self)
        detail_frame.title("Computation Details")

        # Display the basic details (full name, equation, result)
        ttk.Label(detail_frame, text=f"Full Name: {details.get('full_name', '')}", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(detail_frame, text=f"Equation: {details.get('expression', '')}", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(detail_frame, text=f"Result: {details.get('result', '')}", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        # Display the symbolic steps if available
        steps_frame = ttk.LabelFrame(detail_frame, text="Steps", padding=(10, 10))
        steps_frame.pack(fill="both", expand=True, padx=10, pady=10)

        steps = details.get('steps', [])
        if not steps:
            ttk.Label(steps_frame, text="No steps available.", font=("Helvetica", 12)).pack(anchor="w")
        else:
            # Use ScrolledText to display the steps
            steps_text = ScrolledText(steps_frame, wrap="word", font=("Helvetica", 12))
            steps_text.pack(fill="both", expand=True)

            # Insert steps line by line
            steps_text.insert("1.0", steps)

            steps_text.config(state="disabled")  # Make text read-only

        # Check if there is graph data and display it
        if 'graph_data' in details:
            graph_frame = ttk.LabelFrame(detail_frame, text="Graph", padding=(10, 10))
            graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Decode the graph image from the byte data
            image_data = io.BytesIO(details['graph_data']['image'])
            img = Image.open(image_data)
            img_tk = ImageTk.PhotoImage(img)

            # Display the graph image
            graph_label = ttk.Label(graph_frame, image=img_tk)
            graph_label.image = img_tk  # Keep a reference to the image
            graph_label.pack()

        # If there's numerical graph data (x, y values), display it using matplotlib
        if 'graph_data' in details and 'x' in details['graph_data'] and 'y' in details['graph_data']:
            numerical_graph_frame = ttk.LabelFrame(detail_frame, text="Graph Data", padding=(10, 10))
            numerical_graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

            figure = plt.Figure(figsize=(5, 4))
            ax = figure.add_subplot(111)
            ax.plot(details['graph_data']['x'], details['graph_data']['y'])
            ax.set_title(details['expression'])
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            canvas = FigureCanvasTkAgg(figure, master=numerical_graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def display_error_popup(self, message):
        """Display an error message in a popup dialog."""
        messagebox.showerror("Error", message)
