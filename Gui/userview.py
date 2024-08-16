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
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TkinterGUI(ThemedTk):
    def __init__(self, parent=None, controller=None):
        super().__init__()
        self.title("Expressive Mathematical Application")
        self.geometry("1200x800")
        self.set_theme("arc")  # Using a modern and appealing theme

        # Initialize the ExpressionEvaluator
        self.evaluator = ExpressionEvaluator()

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
        self.sidebar_visible = True  # Track sidebar visibility
        self.sidebar = ttk.Frame(self, width=200, style='Sidebar.TFrame', relief='raised', borderwidth=2)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(20, 0), pady=20)

        # Main Content Frame
        self.content_frame = ttk.Frame(self, style='Content.TFrame', padding=(20, 20))
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Initialize Frames
        self.frames = {}
        self.init_frames()

        # Configure grid layout for the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initially hide the sidebar
        self.sidebar.grid_remove()
        self.sidebar_visible = False  # Set to false since we removed it

        # Add a toggle button to the main window (hidden initially)
        self.toggle_button = ttk.Button(self, text="Toggle Sidebar", command=self.toggle_sidebar, style='Sidebar.TButton')
        self.toggle_button.grid(row=0, column=2, padx=(10, 20), pady=(20, 20), sticky="ne")
        self.toggle_button.grid_remove()  # Hide the toggle button initially

        # Show Login Screen initially
        self.showLoginScreen()

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
        self.frames["Expression Input"] = ExpressionInputFrame(self.content_frame, self)  # Use the new class
        self.frames["Graph Plotter"] = self.create_graph_plotter_frame()  # Use the updated method
        self.frames["Symbolic Computation"] = SymbolicComputation(self.content_frame, self)
        self.frames["Profile Management"] = ProfileManagement(self.content_frame, self)

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
        logging.debug("Showing main dashboard")
        self.sidebar.grid(row=0, column=0, sticky="ns")  # Show the sidebar only after login
        self.toggle_button.grid()  # Show the toggle button after login
        self.showFrame("Dashboard")
        self.init_sidebar()  # Initialize sidebar only when the user is logged in

    def showExpressionInput(self):
        """Display the expression input frame."""
        self.showFrame("Expression Input")

    def showGraphPlotter(self):
        """Display the graph plotter frame."""
        self.showFrame("Graph Plotter")

    def showSymbolicComputation(self):
        """Display the symbolic computation frame."""
        self.showFrame("Symbolic Computation")

    def showProfileManagement(self):
        """Display the profile management frame."""
        self.showFrame("Profile Management")

    def display_result(self, result_text, color):
        """Display the result in the appropriate frame."""
        # Implement this method as needed in your application
        pass

    def evaluate_expression(self):
        """Evaluate the mathematical expression provided by the user."""
        # This method is now handled within the ExpressionInputFrame class
        pass

    def login(self):
        """Handle the login process."""
        logging.debug("Attempting login")
        username = self.frames["Login Interface"].username_entry.get()
        password = self.frames["Login Interface"].password_entry.get()
        if username == "user" and password == "password":
            self.sidebar.grid()  # Show the sidebar
            self.showDashboard()  # Show the dashboard after login
            self.frames["Login Interface"].login_button.configure(text="Logout", command=self.logout)
        else:
            self.display_error_popup("Invalid username or password. Please try again.")

    def logout(self):
        """Handle the logout process."""
        logging.debug("Logging out")
        self.sidebar.grid_remove()  # Hide the sidebar on logout
        self.toggle_button.grid_remove()  # Hide the toggle button on logout
        self.frames["Login Interface"].login_button.configure(text="Login", command=self.login)
        self.showLoginScreen()

    def signup(self):
        """Handle the signup process."""
        logging.debug("Attempting signup")
        username = self.frames["Signup Interface"].signup_username_entry.get()
        password = self.frames["Signup Interface"].signup_password_entry.get()
        confirm_password = self.frames["Signup Interface"].signup_confirm_password_entry.get()
        if password == confirm_password:
            self.displayResult("Signup successful! Please log in.")
            self.showLoginScreen()
        else:
            self.display_error_popup("Passwords do not match. Please try again.")

    def displayResult(self, result):
        """Display a success result message."""
        logging.debug(f"Displaying result: {result}")
        self.result_display.configure(text=result, foreground=self.success_color)
        self.result_display.grid()

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
