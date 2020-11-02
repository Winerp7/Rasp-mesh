from git import Repo
import subprocess
import shutil

RASPHOME = '/home/pi/'
GIT_DIRECTORY = RASPHOME + 'raspmesh'
GIT_URL = 'https://github.com/Winerp7/Rasp-mesh.git'

if __name__ == '__main__':
    
    # Ping google to check internet connection
    ping_command = ['ping', '-c', '1', 'google.com']
    has_internet = subprocess.call(ping_command) == 0

    if has_internet:
        # Delete the current directory
        try:
            shutil.rmtree(GIT_DIRECTORY)
        except:
            print('Failed to delete the directory')

        # Download the newest repository
        try:
            Repo.clone_from(GIT_URL, GIT_DIRECTORY)
        except:
            print('Failed to clone the repository')

        # Pip install all requirements    
        try:
            requirements_path = GIT_DIRECTORY + '/' + 'requirements.txt'
            subprocess.call(['pip3', 'install', '-r', requirements_path])
        except:
            print('Failed to install pip requirements')
