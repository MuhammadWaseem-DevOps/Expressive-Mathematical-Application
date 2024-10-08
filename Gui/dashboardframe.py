import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import datetime
import io
import os
import logging
from tkinter.scrolledtext import ScrolledText


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.dao = self.controller.dao
        self.user_id = self.controller.auth_service.current_user_id

        self.init_ui()

    def init_ui(self):
        self.create_welcome_section()
        self.create_recent_activities_section()
        self.create_computation_statistics_section()
        self.create_saved_computations_section()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_welcome_section(self):
        welcome_frame = ttk.Frame(self, padding="20", style='Welcome.TFrame')
        welcome_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        username = self.get_user_name()
        greeting = f"Welcome back, {username}!"
        ttk.Label(welcome_frame, text=greeting, font=("Helvetica", 24, "bold")).pack(side=tk.LEFT)

        profile_image = self.get_profile_image()
        profile_label = ttk.Label(welcome_frame, image=profile_image)
        profile_label.image = profile_image
        profile_label.pack(side=tk.RIGHT, padx=20)

    def create_recent_activities_section(self):
        """creating the recent computation performed and binding them with double click to open that row"""

        activities_frame = ttk.LabelFrame(self, text="Recent Activities", padding=(20, 20))
        activities_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))

        self.recent_activities_tree = ttk.Treeview(activities_frame, columns=("Activity", "Result", "Time"), show="headings", height=5)
        self.recent_activities_tree.heading("Activity", text="Activity")
        self.recent_activities_tree.heading("Result", text="Result")
        self.recent_activities_tree.heading("Time", text="Time")
        self.recent_activities_tree.column("Activity", anchor="center", width=200)
        self.recent_activities_tree.column("Result", anchor="center", width=200)
        self.recent_activities_tree.column("Time", anchor="center", width=100)
        self.recent_activities_tree.pack(fill=tk.BOTH, expand=True)

        self.recent_activities_tree.bind("<Double-1>", self.show_activity_details)

        self.load_recent_activities()

    def create_computation_statistics_section(self):
        """creating the total number of computations performed by that user"""

        stats_frame = ttk.LabelFrame(self, text="Computation Statistics", padding="20", style='Stats.TFrame')
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        statistics = self.get_computation_statistics()
        if statistics:
            for key, value in statistics.items():
                ttk.Label(stats_frame, text=f"{key}: {value}", font=("Helvetica", 14)).pack(anchor="w", pady=2)
        else:
            ttk.Label(stats_frame, text="No statistics available.", font=("Helvetica", 14)).pack(anchor="w", pady=2)

    def create_saved_computations_section(self):
        """creating the saved computation performed and binding them with double click to open that row"""

        favorites_frame = ttk.LabelFrame(self, text="Saved & Favorite Computations", padding="20", style='Favorites.TFrame')
        favorites_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.saved_computations_tree = ttk.Treeview(favorites_frame, columns=("Equation", "Result"), show="headings", height=5)
        self.saved_computations_tree.heading("Equation", text="Equation")
        self.saved_computations_tree.heading("Result", text="Result")
        self.saved_computations_tree.column("Equation", anchor="center", width=300)
        self.saved_computations_tree.column("Result", anchor="center", width=300)
        self.saved_computations_tree.pack(fill=tk.BOTH, expand=True)

        self.saved_computations_tree.bind("<Double-1>", self.show_computation_details)

        self.load_saved_computations()

    def get_user_name(self):
        profile_data = self.controller.profile_manager.getProfile(self.user_id)
        return profile_data["full_name"] if profile_data and profile_data.get("full_name") else "User"

    def get_profile_image(self):
        """Fetching profile image data from the database
        converting that data to image"""

        try:
            profile_data = self.controller.profile_manager.getProfile(self.user_id)
            image_data = profile_data.get("profile_picture")

            if image_data:
                # Convert the binary data to an image
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                # Optional: Apply circular crop
                image = self._resize_and_crop_image(image, size=(100, 100))
                photo_image = ImageTk.PhotoImage(image)
                return photo_image
            else:
                logging.warning("No profile image found in the database. Using placeholder image.")
                # Return a placeholder image if no image data is found
                return ImageTk.PhotoImage(Image.new('RGB', (100, 100), color='gray'))
            
        except Exception as e:
            logging.error(f"Error loading profile image from database: {e}")
            # Return a placeholder image in case of any error
            return ImageTk.PhotoImage(Image.new('RGB', (100, 100), color='gray'))



    def _resize_and_crop_image(self, image, size=(100, 100)):
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        image.putalpha(mask)
        return image


    def load_recent_activities(self):
        self.recent_activities_tree.delete(*self.recent_activities_tree.get_children())

        recent_activities = self.get_recent_activities()

        for activity in recent_activities:
            self.recent_activities_tree.insert("", tk.END, iid=activity['history_id'], 
                                                values=(activity['equation'], activity['result'], self.time_since(activity['timestamp'])))

    def load_saved_computations(self):
        self.saved_computations_tree.delete(*self.saved_computations_tree.get_children())
        saved_computations = self.get_saved_computations()

        saved_computations.sort(key=lambda x: x['history_id'], reverse=True)

        for computation in saved_computations[:5]:
            self.saved_computations_tree.insert("", tk.END, iid=computation['history_id'], values=(computation['equation'], computation['result']))

    def show_activity_details(self, event):
        selected_item = self.recent_activities_tree.selection()
        if not selected_item:
            return

        activity_id = selected_item[0]

        try:
            details = self.controller.profile_manager.get_computation_details(activity_id)
        except Exception as e:
            logging.error(f"Failed to load computation details: {e}")
            return

        if not details:
            logging.error(f"No details found for activity_id: {activity_id}")
            return

        self.show_details_dialog(details)

    def show_computation_details(self, event):
        selected_item = self.saved_computations_tree.selection()
        if not selected_item:
            return

        history_id = selected_item[0]

        try:
            details = self.controller.profile_manager.get_computation_details(history_id)
        except Exception as e:
            logging.error(f"Failed to load computation details: {e}")
            return

        if not details:
            logging.error(f"No details found for computation_id: {history_id}")
            return

        self.show_details_dialog(details)
    def show_details_dialog(self, details):
        detail_frame = tk.Toplevel(self)
        detail_frame.title("Computation Details")

        ttk.Label(detail_frame, text=f"Equation: {details.get('expression', 'N/A')}", font=("Helvetica", 16)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(detail_frame, text=f"Result: {details.get('result', 'N/A')}", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(detail_frame, text=f"Full Name: {details.get('full_name', 'N/A')}", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        steps_frame = ttk.LabelFrame(detail_frame, text="Step-by-Step Solution", padding=(10, 10))
        steps_frame.pack(fill="both", expand=True, padx=10, pady=10)

        steps = details.get('steps', [])
        print("Retrieved steps:", steps)

        if not steps:
            ttk.Label(steps_frame, text="No steps available.", font=("Helvetica", 12)).pack(anchor="w")
        else:
            steps_text = ScrolledText(steps_frame, wrap=tk.WORD, font=("Helvetica", 12))
            steps_text.pack(fill="both", expand=True)

            #spliting the step into list if it is a single string
            if isinstance(steps, str):
                steps = steps.splitlines()

            print("Processed steps for display:", steps)

            full_steps = "\n\n".join(steps) 
            steps_text.insert(tk.END, full_steps)

        steps_text.config(state=tk.DISABLED)   

    def refresh_dashboard(self):
        self.load_recent_activities()
        self.load_saved_computations()

    def get_recent_activities(self):
        recent_activities = []
        for entry in self.dao.get_computation_history(self.user_id):
            recent_activities.append({
                "history_id": entry[0],  
                "equation": entry[2],    
                "result": entry[3], 
                "timestamp": entry[4]            
            })
        return recent_activities


    def get_computation_statistics(self):

        history = self.dao.get_computation_history(self.user_id)
        total_computations = len(history)
        statistics = {}

        if total_computations > 0:
            results = [entry[3] for entry in history] 
            favorite_function = max(set(results), key=results.count)

            statistics["Total Computations"] = total_computations
            statistics["Favorite Function"] = favorite_function
        else:
            statistics["Total Computations"] = 0
            statistics["Favorite Function"] = "N/A"

        return statistics

    def get_saved_computations(self):
        computations = []
        for entry in self.dao.get_computation_history(self.user_id):
            computations.append({
                "history_id": entry[0],  
                "equation": entry[2],    
                "result": entry[3]     
            })
        return computations


    def time_since(self, timestamp):
        try:
            delta = datetime.datetime.now() - datetime.datetime.fromisoformat(timestamp)
            days, seconds = delta.days, delta.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if days > 0:
                return f"{days}d"
            elif hours > 0:
                return f"{hours}h"
            elif minutes > 0:
                return f"{minutes}m"
            else:
                return "just now"
        except ValueError:
            logging.error(f"Invalid timestamp format: {timestamp}")
            return "unknown time"
