import logging

from GoogleAPI import create_service

SOURCE_LIST_ID = "V0NBVTFMZVd5aWxyUE5BYw"
service = create_service()


def parse_task(task):
    # build new task structure for Google Tasks API
    new_task = {"title": task["subject"], "notes": task["description"]["raw"]}

    # convert due date to RFC 3339 timestamp
    if task["dueDate"]:
        new_task.update({"due": task["dueDate"] + "T00:00:00.000Z"})

    return new_task


def write_tasks(tasks):
    logger = logging.getLogger(__name__)
    ids = {}
    for task in tasks:
        resp = service.tasks().insert(tasklist=SOURCE_LIST_ID, body=parse_task(task)).execute()
        ids.update({task["id"]: resp.get("id")})
        logger.info(f"Wrote Task '{resp.get('id')}': {task.get('subject')}")
    return ids


def del_tasks(tasks):
    logger = logging.getLogger(__name__)
    for task in tasks:
        resp = service.tasks().get(tasklist=SOURCE_LIST_ID, task=task[1]).execute()
        service.tasks().delete(tasklist=SOURCE_LIST_ID, task=task[1]).execute()
        logger.info(f"Deleted Task '{task}': {resp.get('title')}")
