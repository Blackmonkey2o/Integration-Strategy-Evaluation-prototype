from gui import IntegrationGUI
import ttkbootstrap as ttk

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = IntegrationGUI(root)
    root.mainloop()