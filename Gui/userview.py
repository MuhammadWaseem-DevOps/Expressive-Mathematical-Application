import tkinter as tk
import customtkinter as ctk
from Interfaces.user_interface import IUserInterface

class TkinterGUI(tk.Tk, IUserInterface):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("MathApp")
        self.geometry("1000x700")
        self.configure(bg="#F5F5F5")  # Light gray background

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#333333")  # Dark sidebar
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#FFFFFF")  # White content frame
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Initialize Frames
        self.frames = {}
        self.init_frames()

        # Result/Error Display Area
        self.result_display = ctk.CTkLabel(self.content_frame, text="", font=("Helvetica", 14), text_color="#000000", fg_color="#FFFFFF")
        self.result_display.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Configure grid layout for the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Show Login Screen initially
        self.showLoginScreen()

    def init_frames(self):
        frame_names = [
            "Login Interface",
            "Dashboard",
            "Expression Input",
            "Graph Plotter",
            "Symbolic Computation",
            "Profile Management"
        ]
        for name in frame_names:
            frame = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="#FFFFFF")
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

            # Add some content to each frame for testing
            label = ctk.CTkLabel(frame, text=f"This is the {name}", font=("Helvetica", 24, "bold"), text_color="#333333")
            label.pack(pady=20)

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Initialize Sidebar
        self.init_sidebar()

    def init_sidebar(self):
        sidebar = self.sidebar
        logo = ctk.CTkLabel(sidebar, text="MathApp", font=("Helvetica", 22, "bold"), anchor="w", text_color="#FFFFFF", fg_color="#333333")
        logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_buttons = {
            "Login Interface": self.showLoginScreen,
            "Dashboard": self.showMainDashboard,
            "Expression Input": self.showExpressionInput,
            "Graph Plotter": self.showGraphPlotter,
            "Symbolic Computation": self.showSymbolicComputation,
            "Profile Management": self.showProfileManagement,
        }

        row = 1
        for text, command in self.sidebar_buttons.items():
            button = ctk.CTkButton(sidebar, text=text, command=command, height=40, corner_radius=10, fg_color="#444444", hover_color="#555555")
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
        login_frame = self.frames["Login Interface"]

        for widget in login_frame.winfo_children():
            widget.destroy()

        title_label = ctk.CTkLabel(login_frame, text="Login", font=("Helvetica", 28, "bold"), text_color="#333333")
        title_label.pack(pady=(30, 10))

        username_label = ctk.CTkLabel(login_frame, text="Username:", text_color="#333333")
        username_label.pack(pady=(10, 5))
        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Enter your username")
        self.username_entry.pack(pady=(0, 20))

        password_label = ctk.CTkLabel(login_frame, text="Password:", text_color="#333333")
        password_label.pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Enter your password", show="*")
        self.password_entry.pack(pady=(0, 20))

        login_button = ctk.CTkButton(login_frame, text="Login", command=self.login, fg_color="#28a745", hover_color="#218838")
        login_button.pack(pady=(20, 10))

        signup_button = ctk.CTkButton(login_frame, text="Sign Up", command=self.signup, fg_color="#007bff", hover_color="#0056b3")
        signup_button.pack(pady=(10, 20))

    def showMainDashboard(self):
        print("Showing main dashboard")  # Debugging statement
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
        # Simulate login process
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "user" and password == "password":  # Replace with real authentication
            self.showMainDashboard()
        else:
            self.displayError("Invalid username or password. Please try again.")

    def signup(self):
        # Handle signup logic here
        print("Sign up button clicked")  # Debugging statement
        pass

    def evaluate_expression(self):
        # Handle expression evaluation logic here
        print("Evaluating expression")  # Debugging statement
        pass

    def displayResult(self, result):
        print(f"Displaying result: {result}")  # Debugging statement
        self.result_display.configure(text=result, text_color="#28a745")  # Green text for success
        self.result_display.grid()

    def displayError(self, message):
        print(f"Displaying error: {message}")  # Debugging statement
        self.result_display.configure(text=message, text_color="#dc3545")  # Red text for error
        self.result_display.grid()

