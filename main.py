import json
import logging.handlers
import os
import sys

from OpenProject import get_work_packages
from Tasks import del_tasks, write_tasks

basepath = os.path.dirname(os.path.realpath(__file__))


def handle_logging(level=logging.INFO, form="%(asctime)s - %(levelname)s: %(message)s"):
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    filename = os.path.splitext(os.path.basename(__file__))[0] + ".log"
    path = os.path.join(basepath, "logs/", filename)
    if not os.path.isdir("logs/"):
        os.makedirs("logs/")
    fh = logging.handlers.TimedRotatingFileHandler(path, when="D", interval=30)
    fh.setLevel(level)
    form = logging.Formatter(form)
    fh.setFormatter(form)
    logger.addHandler(fh)
    return logger


if __name__ == "__main__":
    filepath = os.path.join(basepath, "Resources/id_map.json")
    with open(filepath, "r+") as f:
        logger = handle_logging()
        # get old task ids
        old_ids = json.load(f)

        # get current task ids
        op_tasks = get_work_packages()
        new_ids = [str(task["id"]) for task in op_tasks]

        # filter old tasks and delete them
        tasks_to_del = [i for i in old_ids.items() if i not in new_ids]
        del_tasks(tasks_to_del)
        for task in tasks_to_del:
            old_ids.pop(task[0])

        # filter new tasks and write them
        tasks_to_write = [task for task in op_tasks if str(task["id"]) not in old_ids]
        old_ids.update(write_tasks(tasks_to_write))
        f.seek(0)
        json.dump(old_ids, f, indent=2)
        f.truncate()
        logger.info("Run finished.")
