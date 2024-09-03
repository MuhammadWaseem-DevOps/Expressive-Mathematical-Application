import hashlib
import re
from tkinter import messagebox
from DbSetup.dao import SQLiteDataAccessObject
from Services.profile_manager import ProfileManager
import logging

class AuthenticationService:
    def __init__(self, db):
        self.dao = SQLiteDataAccessObject(db_name=db)
        self.profile_manager = ProfileManager(self.dao)
        self.current_user_id = None 

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
            self.current_user_id = user_id 
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
            self.current_user_id = result[0][0] 
            logging.debug(f"User ID set to {self.current_user_id}")
            
            profile_manager = self.profile_manager
            
            profile_data = profile_manager.getProfile(self.current_user_id) 
            
            if not profile_data:
                user_data = {
                    'user_id': self.current_user_id,
                    'first_name': result[0][4],
                    'last_name': result[0][5]   
                }
                profile_manager.createProfile(user_data)
            
            messagebox.showinfo("Login Success", "Welcome back!")
            return True

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change the user's password."""
        logging.info(f"Attempting to change password for user_id: {user_id}")
        old_password_hash = self.hash_password(old_password)
        new_password_hash = self.hash_password(new_password)
        
        logging.debug(f"Old password hash: {old_password_hash}")
        logging.debug(f"New password hash: {new_password_hash}")
        
        # Verify the old password
        result = self.dao.select("USER", f"user_id = {user_id} AND password_hash = '{old_password_hash}'")
        if not result:
            logging.error(f"Password change failed: incorrect old password for user_id {user_id}")
            messagebox.showerror("Error", "Old password is incorrect.")
            return False
        
        update_data = {"password_hash": new_password_hash}
        try:
            success = self.dao.update("USER", user_id, update_data, id_column="user_id")
            if success:
                logging.info(f"Password successfully changed for user_id: {user_id}")
            else:
                logging.error(f"Password change failed during update for user_id {user_id}")
            return success
        except Exception as e:
            logging.exception(f"Exception occurred while changing password for user_id {user_id}: {e}")
            return False
        
    def logout(self):
        """Clear the current user ID on logout."""
        self.current_user_id = None

    def get_current_user_id(self):
        """Returns the ID of the currently logged-in user."""
        return self.current_user_id
