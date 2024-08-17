import hashlib
import re
from tkinter import messagebox
from Services.dao import SQLiteDataAccessObject
import logging  # Add this import

class AuthenticationService:
    def __init__(self, db):
        self.dao = SQLiteDataAccessObject(db_name=db)
        self.current_user_id = None  # Track the logged-in user's ID

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_user_exists(self, username: str) -> bool:
        result = self.dao.select("USER", f"username = '{username}'")
        return len(result) > 0

    def validate_email(self, email: str) -> bool:
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def validate_signup(self, username: str, password: str, confirm_password: str, email: str) -> bool:
        if not username or not password or not confirm_password or not email:
            messagebox.showwarning("Input Error", "All fields are required.")
            return False

        if password != confirm_password:
            messagebox.showwarning("Input Error", "Passwords do not match.")
            return False

        if not self.validate_email(email):
            messagebox.showwarning("Input Error", "Invalid email address.")
            return False

        if self.check_user_exists(username):
            messagebox.showwarning("Input Error", "Username already exists.")
            return False

        return True

    def create_user(self, username: str, password: str, email: str) -> bool:
        password_hash = self.hash_password(password)
        new_user = {
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'created_at': '2024-08-16 12:00:00',
            'last_login': '2024-08-16 12:00:00'
        }
        user_id = self.dao.insert('USER', new_user)
        if user_id:
            self.current_user_id = user_id  # Set the current user ID upon successful registration
            messagebox.showinfo("Success", "User created successfully.")
            return True
        else:
            messagebox.showerror("Error", "User registration failed.")
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        password_hash = self.hash_password(password)
        result = self.dao.select("USER", f"username = '{username}' AND password_hash = '{password_hash}'")
        if len(result) == 0:
            messagebox.showerror("Authentication Failed", "Invalid username or password.")
            return False
        else:
            self.current_user_id = result[0][0]  # Set the current user ID upon successful login
            logging.debug(f"User ID set to {self.current_user_id}")
            messagebox.showinfo("Login Success", "Welcome back!")
            return True

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change the user's password."""
        old_password_hash = self.hash_password(old_password)
        new_password_hash = self.hash_password(new_password)
        
        # Check if the old password is correct
        result = self.dao.select("USER", f"user_id = {user_id} AND password_hash = '{old_password_hash}'")
        if not result:
            messagebox.showerror("Error", "Old password is incorrect.")
            return False
        
        # Update the password in the database
        update_data = {"password_hash": new_password_hash}
        success = self.dao.update("USER", user_id, update_data)
        return success

    def logout(self):
        """Clear the current user ID on logout."""
        self.current_user_id = None
