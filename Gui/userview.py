import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
from .login_screen import LoginScreen
from .signup_screen import SignupScreen
from .symbolic_computation import SymbolicComputation

class TkinterGUI(ThemedTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("MathApp")
        self.geometry("1200x800")
        self.set_theme("arc")  # Applying a modern theme

        # Custom color theme
        self.bg_color = "#f0f4f8"  # Very light gray/white background
        self.sidebar_color = "#2c3e50"  # Dark slate blue sidebar
        self.header_color = "#34495e"  # Darker shade for headers
        self.button_color = "#3498db"  # Bright blue buttons
        self.button_hover_color = "#2980b9"  # Darker blue for hover
        self.success_color = "#27ae60"  # Green for success messages
        self.error_color = "#e74c3c"  # Red for error messages

        # Set the main background color
        self.configure(bg=self.bg_color)

        # Initialize Sidebar (Initially hidden)
        self.sidebar = ttk.Frame(self, width=250, style='Sidebar.TFrame')
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.sidebar.grid_forget()  # Hide the sidebar initially

        # Sidebar buttons
        self.sidebar_buttons = {
            "Dashboard": self.showDashboard,
            "Expression Input": self.showExpressionInput,
            "Graph Plotter": self.showGraphPlotter,
            "Symbolic Computation": self.showSymbolicComputation,
            "Profile Management": self.showProfileManagement
        }

        # Main Content Frame
        self.content_frame = ttk.Frame(self, style='Content.TFrame')
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Initialize Frames
        self.frames = {}
        self.init_frames()

        # Result/Error Display Area
        self.result_display = ttk.Label(self.content_frame, text="", font=("Helvetica", 14))
        self.result_display.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Configure grid layout for the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize Sidebar
        self.init_sidebar()

        # Show Login Screen initially
        self.showLoginScreen()

    def init_frames(self):
        self.frames["Login Interface"] = LoginScreen(self.content_frame, self)
        self.frames["Signup Interface"] = SignupScreen(self.content_frame, self)
        self.frames["Dashboard"] = self.create_dashboard_frame()
        self.frames["Expression Input"] = ttk.Frame(self.content_frame)
        self.frames["Graph Plotter"] = ttk.Frame(self.content_frame)
        self.frames["Symbolic Computation"] = SymbolicComputation(self.content_frame, self)
        self.frames["Profile Management"] = self.create_profile_management_frame()

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def create_dashboard_frame(self):
        dashboard_frame = ttk.Frame(self.content_frame, style='Dashboard.TFrame')

        # Dashboard Header
        dashboard_header = ttk.Label(dashboard_frame, text="Dashboard", font=("Helvetica", 18, "bold"), background=self.header_color, foreground="white")
        dashboard_header.pack(fill=tk.X, pady=(20, 10))

        # Welcome message
        welcome_message = ttk.Label(dashboard_frame, text="Welcome back, [User]!", font=("Helvetica", 16))
        welcome_message.pack(pady=(0, 20))

        # Recent Activities Section
        recent_activities_frame = ttk.Frame(dashboard_frame)
        recent_activities_frame.pack(fill=tk.X, padx=10, pady=10)

        recent_activities_header = ttk.Label(recent_activities_frame, text="Recent Activities", font=("Helvetica", 14, "bold"))
        recent_activities_header.pack(pady=(10, 5))

        recent_activities_content = ttk.Label(recent_activities_frame, text="No recent activities.")
        recent_activities_content.pack(pady=5)

        # Quick Access Buttons
        quick_access_frame = ttk.Frame(dashboard_frame)
        quick_access_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        quick_access_header = ttk.Label(quick_access_frame, text="Quick Access", font=("Helvetica", 14, "bold"))
        quick_access_header.pack(pady=(10, 5))

        quick_access_buttons = {
            "Expression Input": self.showExpressionInput,
            "Graph Plotter": self.showGraphPlotter,
            "Symbolic Computation": self.showSymbolicComputation,
            "Profile Management": self.showProfileManagement
        }

        for text, command in quick_access_buttons.items():
            button = ttk.Button(quick_access_frame, text=text, command=command, style='QuickAccess.TButton')
            button.pack(pady=5, fill=tk.X, padx=10)
            button.bind("<Enter>", lambda e, b=button: b.configure(style='QuickAccessHover.TButton'))
            button.bind("<Leave>", lambda e, b=button: b.configure(style='QuickAccess.TButton'))

        return dashboard_frame

    def create_profile_management_frame(self):
        profile_frame = ttk.Frame(self.content_frame, style='Profile.TFrame')
        profile_frame.grid(row=0, column=0, sticky="nsew")

        # Profile Header
        profile_header = ttk.Label(profile_frame, text="Profile Management", font=("Helvetica", 18, "bold"), background=self.header_color, foreground="white")
        profile_header.grid(row=0, column=0, sticky="ew", pady=(20, 10))

        # Profile Picture
        profile_picture_frame = ttk.Frame(profile_frame)
        profile_picture_frame.grid(row=1, column=0, pady=(10, 20), padx=10, sticky="ew")

        profile_picture_label = ttk.Label(profile_picture_frame, text="Profile Picture", font=("Helvetica", 14, "bold"))
        profile_picture_label.grid(row=0, column=0, pady=(10, 5))

        self.profile_picture_image = tk.Label(profile_picture_frame, text="No Image", width=100, height=100, bg="lightgray")
        self.profile_picture_image.grid(row=1, column=0, pady=5, padx=10)

        self.upload_picture_button = ttk.Button(profile_picture_frame, text="Upload Picture", command=self.upload_picture, style='Upload.TButton')
        self.upload_picture_button.grid(row=2, column=0, pady=5, padx=10)

        # Personal Information
        personal_info_frame = ttk.Frame(profile_frame)
        personal_info_frame.grid(row=2, column=0, padx=10, pady=(10, 20), sticky="ew")

        personal_info_header = ttk.Label(personal_info_frame, text="Personal Information", font=("Helvetica", 14, "bold"))
        personal_info_header.grid(row=0, column=0, pady=(10, 5))

        # Display personal information
        self.full_name_display = ttk.Label(personal_info_frame, text="Full Name: John Doe", font=("Helvetica", 12))
        self.full_name_display.grid(row=1, column=0, pady=5)

        self.email_display = ttk.Label(personal_info_frame, text="Email: john.doe@example.com", font=("Helvetica", 12))
        self.email_display.grid(row=2, column=0, pady=5)

        # Change Password
        password_frame = ttk.Frame(profile_frame)
        password_frame.grid(row=3, column=0, pady=(10, 20), padx=10, sticky="ew")

        password_header = ttk.Label(password_frame, text="Change Password", font=("Helvetica", 14, "bold"))
        password_header.grid(row=0, column=0, pady=(10, 5))

        self.old_password_entry = self.create_labeled_entry(password_frame, "Old Password:", show='*')
        self.new_password_entry = self.create_labeled_entry(password_frame, "New Password:", show='*')
        self.confirm_password_entry = self.create_labeled_entry(password_frame, "Confirm Password:", show='*')

        self.change_password_button = ttk.Button(password_frame, text="Change Password", command=self.change_password, style='ChangePassword.TButton')
        self.change_password_button.grid(row=4, column=0, pady=10)

        # Recent Activity
        recent_activity_frame = ttk.Frame(profile_frame)
        recent_activity_frame.grid(row=4, column=0, padx=10, pady=(10, 20), sticky="ew")

        activity_header = ttk.Label(recent_activity_frame, text="Recent Activity", font=("Helvetica", 14, "bold"))
        activity_header.grid(row=0, column=0, pady=(10, 5))

        self.activity_text = tk.Text(recent_activity_frame, height=6, wrap=tk.WORD, bg="white", fg="black")
        self.activity_text.grid(row=1, column=0, pady=5, padx=10)
        self.activity_text.insert(tk.END, "No recent activity.")  # Placeholder text

        # History View
        history_frame = ttk.Frame(profile_frame)
        history_frame.grid(row=5, column=0, padx=10, pady=(10, 20), sticky="ew")

        history_header = ttk.Label(history_frame, text="History View", font=("Helvetica", 14, "bold"))
        history_header.grid(row=0, column=0, pady=(10, 5))

        self.history_text = tk.Text(history_frame, height=6, wrap=tk.WORD, bg="white", fg="black")
        self.history_text.grid(row=1, column=0, pady=5, padx=10)
        self.history_text.insert(tk.END, "No history available.")  # Placeholder text

        # Export Data
        export_frame = ttk.Frame(profile_frame)
        export_frame.grid(row=6, column=0, padx=10, pady=(10, 20), sticky="ew")

        self.export_button = ttk.Button(export_frame, text="Export Data", command=self.export_data, style='Export.TButton')
        self.export_button.grid(row=0, column=0, pady=10, padx=10)

        # Configure row weights to make sure the layout resizes properly
        for row in range(7):
            profile_frame.grid_rowconfigure(row, weight=1)
        profile_frame.grid_columnconfigure(0, weight=1)

        return profile_frame


    def create_labeled_entry(self, parent_frame, label_text, show=None):
        frame = ttk.Frame(parent_frame)
        frame.grid(sticky="ew", pady=5)  # Use grid instead of pack

        label = ttk.Label(frame, text=label_text)
        label.grid(row=0, column=0, sticky="w")  # Use grid instead of pack

        entry = ttk.Entry(frame, show=show)
        entry.grid(row=0, column=1, sticky="ew")  # Use grid instead of pack

        return entry


    def init_sidebar(self):
        style = ttk.Style()
        style.configure('Sidebar.TFrame', background=self.sidebar_color)
        style.configure('Sidebar.TButton', background=self.sidebar_color, foreground='grey', font=("Helvetica", 12))
        style.map('Sidebar.TButton', background=[('active', self.button_hover_color)])
        top_padding_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame', height=60)  # Adjust height as needed
        top_padding_frame.grid(row=0, column=0, sticky="ew")

        row = 1
        for text, command in self.sidebar_buttons.items():
            button = ttk.Button(self.sidebar, text=text, command=command, style='Sidebar.TButton')
            button.grid(row=row, column=0, padx=20, pady=(10 if row > 1 else 0), sticky="ew")
            row += 1

    def showFrame(self, frame_name):
        print(f"Switching to frame: {frame_name}")  # Debugging statement
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()

    def showLoginScreen(self):
        print("Showing login screen")  # Debugging statement
        self.showFrame("Login Interface")

    def showSignupScreen(self):
        print("Showing signup screen")  # Debugging statement
        self.showFrame("Signup Interface")

    def showDashboard(self):
        print("Showing main dashboard")  # Debugging statement
        self.sidebar.grid(row=0, column=0, sticky="ns")  # Show the sidebar
        self.showFrame("Dashboard")

    def showExpressionInput(self):
        self.showFrame("Expression Input")

    def showGraphPlotter(self):
        self.showFrame("Graph Plotter")

    def showSymbolicComputation(self):
        self.showFrame("Symbolic Computation")

    def showProfileManagement(self):
        self.showFrame("Profile Management")

    def login(self):
        print("Attempting login")  # Debugging statement
        username = self.frames["Login Interface"].username_entry.get()
        password = self.frames["Login Interface"].password_entry.get()
        if username == "user" and password == "password":  # Replace with real authentication
            self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.showDashboard()  # Show dashboard after login
            self.frames["Login Interface"].login_button.configure(text="Logout", command=self.logout)
        else:
            self.displayError("Invalid username or password. Please try again.")

    def logout(self):
        print("Logging out")  # Debugging statement
        self.sidebar.grid_forget()  # Hide the sidebar
        self.frames["Login Interface"].login_button.configure(text="Login", command=self.login)
        self.showLoginScreen()

    def signup(self):
        print("Attempting signup")  # Debugging statement
        username = self.frames["Signup Interface"].signup_username_entry.get()
        password = self.frames["Signup Interface"].signup_password_entry.get()
        confirm_password = self.frames["Signup Interface"].signup_confirm_password_entry.get()
        if password == confirm_password:
            self.displayResult("Signup successful! Please log in.")
            self.showLoginScreen()
        else:
            self.displayError("Passwords do not match. Please try again.")

    def displayResult(self, result):
        print(f"Displaying result: {result}")  # Debugging statement
        self.result_display.configure(text=result, foreground=self.success_color)  # Green text for success
        self.result_display.grid()

    def displayError(self, message):
        print(f"Displaying error: {message}")  # Debugging statement
        self.result_display.configure(text=message, foreground=self.error_color)  # Red text for error
        self.result_display.grid()

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                profile_image = tk.PhotoImage(file=file_path)  # Load image
                self.profile_picture_image.configure(image=profile_image, text="")
                self.profile_picture_image.image = profile_image  # Keep a reference to avoid garbage collection
                messagebox.showinfo("Profile Picture", "Profile picture updated successfully!")
            except tk.TclError as e:
                messagebox.showerror("Profile Picture Error", f"Unable to load image. Error: {e}")

    def change_password(self):
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if new_password == confirm_password:
            # Simulate changing the password logic
            print(f"Changing password from '{old_password}' to '{new_password}'")
            messagebox.showinfo("Change Password", "Password changed successfully!")
        else:
            messagebox.showerror("Change Password Error", "Passwords do not match.")

    def export_data(self):
        # Simulate exporting data logic
        print("Exporting data...")
        messagebox.showinfo("Export Data", "Data export functionality is not implemented yet.")
