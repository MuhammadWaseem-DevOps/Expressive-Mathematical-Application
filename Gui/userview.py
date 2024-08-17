import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
from PIL import Image, ImageTk
import logging
from Services.expression_evaluator import ExpressionEvaluator
from Gui.login_screen import LoginScreen
from Gui.signup_screen import SignupScreen
from Gui.symbolic_computation import SymbolicComputation
from Gui.profile_management import ProfileManagement
from Services.graph_plotter import GraphPlotter
from Gui.graph_plotting import GraphPlotterFrame
from Gui.expression_evaluator import ExpressionInputFrame
from Services.authentication import AuthenticationService

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TkinterGUI(ThemedTk):
    def __init__(self, auth_service=None, expression_evaluator=None,
                 symbolic_computer=None, profile_manager=None, error_handler=None,
                 computation_history=None, data_exporter=None, db_path='my_project_database.db'):
        super().__init__()
        self.title("Expressive Mathematical Application")
        self.geometry("1200x800")
        self.set_theme("arc")

        # Initialize the services
        self.auth_service = auth_service or AuthenticationService(db_path)
        self.evaluator = expression_evaluator
        self.symbolic_computer = symbolic_computer
        self.profile_manager = profile_manager
        self.error_handler = error_handler
        self.computation_history = computation_history
        self.data_exporter = data_exporter
        self.db_path = db_path

        # Custom color theme
        self.bg_color = "#f4f4f4"
        self.sidebar_color = "#2c3e50"
        self.header_color = "#e74c3c"
        self.button_color = "#3498db"
        self.button_hover_color = "#2980b9"
        self.success_color = "#27ae60"
        self.error_color = "#e74c3c"

        # Set the main background color
        self.configure(bg=self.bg_color)

        # Initialize Sidebar (Hidden initially)
        self.sidebar_visible = False  # Track sidebar visibility
        self.sidebar = ttk.Frame(self, width=200, style='Sidebar.TFrame', relief='raised', borderwidth=2)

        # Main Content Frame
        self.content_frame = ttk.Frame(self, style='Content.TFrame', padding=(20, 20))
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Initialize Frames
        self.frames = {}
        self.init_frames()

        # Configure grid layout for the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Add a toggle button to the main window (hidden initially)
        self.toggle_button = ttk.Button(self, text="Toggle Sidebar", command=self.toggle_sidebar, style='Sidebar.TButton')
        self.toggle_button.grid(row=0, column=2, padx=(10, 20), pady=(20, 20), sticky="ne")
        self.toggle_button.grid_remove()

        self.check_login_status()

    def check_login_status(self):
        if self.auth_service.current_user_id is None:
            self.showLoginScreen()
        else:
            self.showDashboard()

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        if self.sidebar_visible:
            self.sidebar.grid_remove()  # Hide the sidebar
        else:
            self.sidebar.grid(row=0, column=0, sticky="ns", padx=(20, 0), pady=20)  # Show the sidebar

        self.sidebar_visible = not self.sidebar_visible  # Toggle the visibility state

    def init_frames(self):
        """Initialize all the frames for the application."""
        self.frames["Login Interface"] = LoginScreen(self.content_frame, self)
        self.frames["Signup Interface"] = SignupScreen(self.content_frame, self)
        self.frames["Dashboard"] = self.create_dashboard_frame()
        self.frames["Expression Input"] = ExpressionInputFrame(self.content_frame, self)
        self.frames["Graph Plotter"] = self.create_graph_plotter_frame()
        self.frames["Symbolic Computation"] = SymbolicComputation(self.content_frame, self)
        # Do not initialize Profile Management here; do it only when the user is logged in

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def create_dashboard_frame(self):
        """Create the dashboard frame."""
        frame = ttk.Frame(self.content_frame, style='Dashboard.TFrame', padding=(20, 20))

        # Add widgets to the dashboard frame
        dashboard_label = ttk.Label(frame, text="Dashboard", font=("Helvetica", 24, 'bold'), foreground="#2c3e50")
        dashboard_label.grid(row=0, column=0, padx=10, pady=10)

        return frame

    def create_graph_plotter_frame(self):
        """Create and return an instance of the GraphPlotterFrame."""
        return GraphPlotterFrame(self.content_frame)

    def init_sidebar(self):
        """Initialize the sidebar with buttons and icons."""
        sidebar_buttons = [
            {"text": "Dashboard", "icon": "icons/dashboard.png", "command": self.showDashboard},
            {"text": "Expression Input", "icon": "icons/input.png", "command": self.showExpressionInput},
            {"text": "Graph Plotter", "icon": "icons/graph.png", "command": self.showGraphPlotter},
            {"text": "Symbolic Computation", "icon": "icons/symbolic.png", "command": self.showSymbolicComputation},
            {"text": "Profile Management", "icon": "icons/profile.png", "command": self.showProfileManagement},
            {"text": "Logout", "icon": "icons/logout.png", "command": self.logout}
        ]

        row = 0
        for button_info in sidebar_buttons:
            icon_path = button_info["icon"]
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = ImageTk.PhotoImage(icon)
                button = ttk.Button(self.sidebar, text=button_info["text"], image=icon, compound=tk.LEFT, command=button_info["command"], style='Sidebar.TButton')
                button.image = icon  # Keep a reference to avoid garbage collection
            else:
                button = ttk.Button(self.sidebar, text=button_info["text"], command=button_info["command"], style='Sidebar.TButton')
                logging.warning(f"Icon not found: {icon_path}. Button created without icon.")

            button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            row += 1

    def showFrame(self, frame_name):
        """Raise the selected frame to the front."""
        logging.debug(f"Switching to frame: {frame_name}")
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()

    def showLoginScreen(self):
        """Display the login screen."""
        logging.debug("Showing login screen")
        self.showFrame("Login Interface")

    def showSignupScreen(self):
        """Display the signup screen."""
        logging.debug("Showing signup screen")
        self.showFrame("Signup Interface")

    def showDashboard(self):
        """Display the dashboard."""
        if not self.ensure_authenticated():
            return
        logging.debug("Showing main dashboard")
        self.sidebar.grid(row=0, column=0, sticky="ns")  # Show the sidebar only after login
        self.toggle_button.grid()  # Show the toggle button after login
        self.showFrame("Dashboard")
        self.init_sidebar()  # Initialize sidebar only when the user is logged in

    def showExpressionInput(self):
        """Display the expression input frame."""
        if not self.ensure_authenticated():
            return
        self.showFrame("Expression Input")

    def showGraphPlotter(self):
        """Display the graph plotter frame."""
        if not self.ensure_authenticated():
            return
        self.showFrame("Graph Plotter")

    def showSymbolicComputation(self):
        """Display the symbolic computation frame."""
        if not self.ensure_authenticated():
            return
        self.showFrame("Symbolic Computation")

    def showProfileManagement(self):
        """Display the profile management frame."""
        if not self.ensure_authenticated():
            return
        if "Profile Management" not in self.frames:
            self.frames["Profile Management"] = ProfileManagement(self.content_frame, self)
            self.frames["Profile Management"].grid(row=0, column=0, sticky="nsew")
        self.showFrame("Profile Management")

    def ensure_authenticated(self):
        if self.auth_service.current_user_id is None:
            messagebox.showerror("Error", "Please log in to continue.")
            self.showLoginScreen()
            return False
        return True

    def login(self, username, password):
        logging.debug("Attempting login")
        if self.auth_service.authenticate_user(username, password):
            self.sidebar.grid()  # Show the sidebar
            self.showDashboard()  # Show the dashboard after login
            self.frames["Login Interface"].login_button.configure(text="Logout", command=self.logout)
        else:
            self.display_error_popup("Invalid username or password. Please try again.")

    def signup(self, username, password, confirm_password, email):
        """Handle the signup process."""
        logging.debug("Attempting signup")
        if self.auth_service.validate_signup(username, password, confirm_password, email):
            if self.auth_service.create_user(username, password, email):
                self.displayResult("Signup successful! Please log in.")
                self.showLoginScreen()
            else:
                self.display_error_popup("Signup failed. Please try again.")
        else:
            self.display_error_popup("Invalid signup details. Please check your inputs.")

    def logout(self):
        """Handle the logout process."""
        logging.debug("Logging out")
        self.auth_service.logout()
        self.sidebar.grid_remove()  # Hide the sidebar on logout
        self.toggle_button.grid_remove()  # Hide the toggle button on logout
        self.frames["Login Interface"].login_button.configure(text="Login", command=self.login)
        self.showLoginScreen()

    def displayResult(self, result):
        """Display a success result message."""
        logging.debug(f"Displaying result: {result}")
        messagebox.showinfo("Success", result)

    def display_error_popup(self, message):
        """Display an error message in a popup dialog."""
        logging.debug(f"Displaying error popup: {message}")
        messagebox.showerror("Error", message)

    def upload_picture(self):
        """Handle uploading a profile picture."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                profile_image = tk.PhotoImage(file=file_path)
                self.profile_picture_image.configure(image=profile_image, text="")
                self.profile_picture_image.image = profile_image
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
            logging.debug(f"Changing password from '{old_password}' to '{new_password}'")
            messagebox.showinfo("Change Password", "Password changed successfully!")
        else:
            self.display_error_popup("Passwords do not match. Please try again.")

    def export_data(self):
        """Handle exporting user data."""
        logging.debug("Exporting data...")
        messagebox.showinfo("Export Data", "Data export functionality is not implemented yet.")
