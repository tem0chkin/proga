"""main.py - Точка входа в программу"""

import os
from gui import MainMenu

def main():
    if os.name == 'nt':
        os.system('chcp 1251 > nul')
    
    app = MainMenu()
    app.mainloop()

if __name__ == "__main__":
    main()
