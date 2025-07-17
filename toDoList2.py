import tkinter as tk
from tkinter import messagebox


def addTask():
    task = taskEntry.get()
    if task :
        task_listbox.insert(tk.END, task)
        taskEntry.delete(0, tk.END)
    else: messagebox.showwarning(
        "Warning", "Task cannot be empty"
    )
    

def removeTask():
    try:
        task_listbox.delete(
            task_listbox.curselection()[0]
        )
    except IndexError:
        messagebox.showwarning(
            "Warning ", "select a task to be deleted!"
        )
        
root = tk.Tk()
root.title('TO-DO LIST ')
root.geometry("300x400")

taskEntry = tk.Entry(root, width=30)
taskEntry.pack(pady=10)

add_button = tk.Button(root,text = "Add Task", command=addTask)
add_button.pack()

task_listbox = tk.Listbox(root,width=35,height=10)
task_listbox.pack(pady=10)

remove_button = tk.Button(root, text="Remove Task", command=removeTask)
remove_button.pack()

root.mainloop()