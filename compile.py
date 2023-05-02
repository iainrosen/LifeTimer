import os
if os.path.exists("LifeTimerGUI.py"):
    os.remove("LifeTimerGUI.py")
os.system("python3 -m PyQt5.uic.pyuic LifeTimer.ui -o LifeTimerGUI.py")