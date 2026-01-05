import os
import win32com.client

def create_startup_shortcut(target_filename, shortcut_name, description):
    # Paths
    startup_path = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
    target_path = os.path.join(os.getcwd(), target_filename)
    shortcut_path = os.path.join(startup_path, f"{shortcut_name}.lnk")
    
    # Create shortcut using Shell Object
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Description = description
    shortcut.IconLocation = target_path
    shortcut.save()
    
    print(f"✅ Success! {shortcut_name} added to Windows Startup.")
    print(f"Path: {shortcut_path}")

if __name__ == "__main__":
    # Add Tracker
    create_startup_shortcut(
        "run_hidden.vbs", 
        "FocusFlowTracker", 
        "Starts the AI Focus Tracker on login"
    )
    
    # Add Web Dashboard
    create_startup_shortcut(
        "run_web_hidden.vbs", 
        "FocusFlowDashboard", 
        "Starts the FocusFlow Web Dashboard on login"
    )
