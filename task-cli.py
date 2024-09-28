import json
import os
import datetime
from typing import List
import sys

DATE_FORMAT = "%d/%m/%Y, %H:%M:%S"

class Task:
    def __init__(self, description:str):
        self.id = -1
        self.description = description
        self.status = 'todo'
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.min
    
    def update(self, description):
        self.description = description
        self.updated = datetime.datetime.now()
        
    def markInProgress(self):
        self.status = 'in-progress'
        
    def markDone(self):
        self.status = 'done'
        
    def getDict(self):
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created": self.created.strftime(DATE_FORMAT),
            "updated": self.updated.strftime(DATE_FORMAT),
        }
    
    def fromDict(dict):
        t = Task(dict['description'])
        t.id = int(dict['id'])
        t.status = dict['status']
        t.created = datetime.datetime.strptime(dict['created'], DATE_FORMAT)
        t.updated = datetime.datetime.strptime(dict['updated'], DATE_FORMAT)
        
        return t

class TaskList:
    def __init__(self, path):
        self.path = path
        self.inProgress = False
        self.done = False
        
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump([], f)
                f.close()

    def getFreeId(self):
        return len(self.list())
    
    def push(self, task:Task):
        task.id = self.getFreeId()
        with open(self.path, 'r') as f:
            try:
                tasks = json.load(f)
                f.close()
            except Exception:
                tasks = []

        tasks = tasks + [json.loads(json.dumps(task.getDict()))]   
            
        with open(self.path, 'w') as outfile:
            outfile.write(json.dumps(tasks))
            outfile.close()
        
        self.nextFreeId=self.nextFreeId=+1
        
    def pop(self, id:int):
        newList = self.list()
        newDicts = []
        
        with open(self.path, 'w') as f:
            if newList:
                for task in newList:
                    if task.id != id:
                        newDicts.append(task.getDict())

            json.dump(newDicts, f)
            f.close()
            
    def modify(self, id: int, modifiedTask: Task):
        newList = self.list()
        newDicts = []

        if newList:
            for task in newList:
                if task.id == id:
                    newDicts.append(modifiedTask.getDict())
                else:
                    newDicts.append(task.getDict())

        with open(self.path, 'w') as f:
            json.dump(newDicts, f)
            f.close()
           
    def list(self) -> List[Task]:
        with open(self.path, 'r') as f:
            try:
                tasksJson = json.load(f)
            except Exception: # if JSON file is empty
                return []
            f.close()
        
        tasks = []
        for jsonTask in tasksJson:
            tasks.append(Task.fromDict(jsonTask))
            
        return tasks

    def get(self, id:int) -> Task:
        for task in self.list():
            if int(task.id) == int(id):
                return task   
        return None

def printhelp():
    print("Available commands:")
    print("add [description] - add a new task:")
    print("update [id] [description] - update a task's description")
    print("delete [id] - deletes a task")
    print("mark-in-progress [id] - marks a task as in-progress")
    print("mark-done [id] - marks a task as done")
    print("list, list [status] - lists all tasks, lists only tasks with status")

args = sys.argv[1:]

if len(args) < 1:
    print("You have to enter a commmand!")
    exit(0)

cmdName = args[0]
cmdArgs = args[1:]



taskList = TaskList('tasks.json')
queriedTask = None
  
if cmdName == "list":
    options = {'done', 'in-progress', 'todo'}
    filters = {}
    
    if len(cmdArgs) > 0:
        if cmdArgs[0] not in options:
            print(f"Options are: {', '.join(str(o) for o in options)}")
        else:
            filters={(cmdArgs[0])} # done, in-progress, todo
    else:
        filters=options # Apply all filters - return all tasks.
         
    for task in taskList.list(): 
        if task.status in filters:
            print("Id:", task.id, "Description:", task.description,
              "Status:", task.status,
              "Created on", task.created,
              "Updated on", task.updated)
    
    exit(0)
    
if len(cmdArgs) < 1: # All further commands require at least one argument
    printhelp()
    exit(0)
    
if cmdName == "add":
    taskList.push(task=Task(cmdArgs[0]))
    print("Added task")
    exit(0)

elif len(cmdArgs) > 0 and cmdArgs[0].isdigit():
    taskQueryId = int(cmdArgs[0])
    queriedTask = taskList.get(taskQueryId)

    if not queriedTask:
        print(f"Task with id {taskQueryId} does not exist.")
        exit(1)

if cmdName == "update":
    if len(cmdArgs) < 2:
        print(f"Update requires two parameters: id, description")
    queriedTask.update(description=cmdArgs[1])
    taskList.modify(taskQueryId, queriedTask)
    print(f'Updated task with id {taskQueryId} to "{cmdArgs[1]}"')
    
if cmdName == "delete":
    taskList.pop(id=taskQueryId)
    print(f"Deleted task with id {taskQueryId}")
    
if cmdName == "mark-in-progress":
    queriedTask.markInProgress()
    taskList.modify(taskQueryId, queriedTask)
    print(f"Marked task with id {taskQueryId} as in progress")

if cmdName == "mark-done":
    queriedTask.markDone()
    taskList.modify(taskQueryId, queriedTask)
    print(f"Marked task with id {taskQueryId} as done")

if cmdName == "help":
    printhelp()