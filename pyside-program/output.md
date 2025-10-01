```bash
pyinstaller --onefile --windowed --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui .\app.py

```