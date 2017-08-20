import tkinter as tk
from tkinter import ttk

def select_all_callback(event):
    # select text
    event.widget.select_range(0, 'end')
    # move cursor to the end
    event.widget.icursor('end')

def filter_notes(event):
    print(event.widget.get())

root = tk.Tk()
root.title("Notes")


scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=0,
               column=1,
               sticky=tk.N + tk.S + tk.W + tk.E
              )

text = tk.Text(root, height=25)
scrollbar.config(command=text.yview)
text.config(yscrollcommand=scrollbar.set)

for i in range(0, 10000):
    text.insert(tk.END, "today: %s\n" % i)

text.grid(row=0,
          column=0,
          sticky=tk.N + tk.S + tk.W + tk.E
         )

filter_entry = tk.Entry(root)
filter_entry.grid(row=1,
                  column=0,
                  sticky=tk.W + tk.E
                 )
filter_entry.bind('<Control-KeyRelease-a>', select_all_callback)
filter_entry.bind('<Return>', filter_notes)
filter_entry.focus()

root.style = ttk.Style()
root.style.theme_use("alt")
root.mainloop()
