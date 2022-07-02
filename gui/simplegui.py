import tkinter as tk


class MainWindow(tk.Frame):
    def __init__(self, program):
        super().__init__(tk.Tk())
        self.master.title(type(program).__name__)
        self.pack(fill=tk.BOTH, expand=True)

        self.btntxt = tk.StringVar()
        self.btntxt.set("Start/Stop")
        tk.Button(self, textvariable=self.btntxt, command=self.execute).pack(side=tk.BOTTOM)
        self.program = program
        self.program.setup_UI(self)

    def execute(self):
        if self.program.active:
            self.program.stop()
        else:
            self.program.run()

    def run(self):
        self.master.mainloop()
        


