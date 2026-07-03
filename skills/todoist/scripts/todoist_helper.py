#!/usr/bin/env python3
"""
Todoist API helper — shared utility for all Todoist operations.
Import: from todoist_helper import TodoistHelper
Usage:
    h = TodoistHelper()
    h.list_tasks()
    h.add_task("Buy milk", priority=2)
    h.complete_task(task_id)
"""

import os
from todoist_api_python.api import TodoistAPI


def iterate_paginator(paginator):
    """Convert ResultsPaginator to a flat list."""
    results = []
    for chunk in paginator:
        if isinstance(chunk, list):
            results.extend(chunk)
        else:
            results.append(chunk)
    return results


class TodoistHelper:
    def __init__(self, token=None):
        if token is None:
            token = os.getenv("TODOIST_API_TOKEN")
        if not token:
            raise ValueError("TODOIST_API_TOKEN not set in environment. Set it in ~/.hermes/profiles/collector/.env")
        self.api = TodoistAPI(token)

    # ── Tasks ──────────────────────────────────────────────

    def list_tasks(self, project_id=None, label=None, query=None):
        """List tasks. Use query for natural language filter (e.g. 'today', 'priority:1')."""
        if query:
            tasks = iterate_paginator(self.api.filter_tasks(query=query))
        elif project_id:
            tasks = iterate_paginator(self.api.get_tasks(project_id=project_id))
        elif label:
            tasks = iterate_paginator(self.api.get_tasks(label=label))
        else:
            tasks = iterate_paginator(self.api.get_tasks())
        return tasks

    def add_task(self, content, description=None, project_id=None,
                 section_id=None, due_date=None, due_string=None,
                 priority=1, labels=None, assignee_id=None):
        """Add a task. Returns the Task object."""
        return self.api.add_task(
            content=content,
            description=description,
            project_id=project_id,
            section_id=section_id,
            due_date=due_date,
            due_string=due_string,
            priority=priority,
            labels=labels,
            assignee_id=assignee_id,
        )

    def complete_task(self, task_id):
        """Mark a task as complete."""
        self.api.complete_task(task_id)

    def uncomplete_task(self, task_id):
        """Reopen a completed task."""
        self.api.uncomplete_task(task_id)

    def delete_task(self, task_id):
        """Delete a task permanently."""
        self.api.delete_task(task_id)

    def update_task(self, task_id, **kwargs):
        """Update task fields. Valid: content, description, project_id, section_id,
        due_date, due_string, priority, labels, assignee_id."""
        self.api.update_task(task_id, **kwargs)

    def move_task(self, task_id, project_id=None, section_id=None, parent_id=None):
        """Move a task to a different project/section."""
        self.api.move_task(task_id, project_id=project_id, section_id=section_id, parent_id=parent_id)

    # ── Projects ───────────────────────────────────────────

    def list_projects(self):
        return iterate_paginator(self.api.get_projects())

    def get_project(self, project_id):
        return self.api.get_project(project_id)

    def add_project(self, name, description=None, is_favorite=False):
        return self.api.add_project(name=name, description=description, is_favorite=is_favorite)

    def update_project(self, project_id, **kwargs):
        self.api.update_project(project_id, **kwargs)

    def archive_project(self, project_id):
        self.api.archive_project(project_id)

    # ── Labels ─────────────────────────────────────────────

    def list_labels(self):
        return iterate_paginator(self.api.get_labels())

    def add_label(self, name, color="gray"):
        return self.api.add_label(name=name, color=color)

    def update_label(self, label_id, **kwargs):
        self.api.update_label(label_id, **kwargs)

    def delete_label(self, label_id):
        self.api.delete_label(label_id)

    # ── Sections ───────────────────────────────────────────

    def list_sections(self, project_id):
        return iterate_paginator(self.api.get_sections(project_id=project_id))

    def add_section(self, project_id, name):
        return self.api.add_section(project_id=project_id, name=name)

    def delete_section(self, section_id):
        self.api.delete_section(section_id)

    # ── Formatters ─────────────────────────────────────────

    @staticmethod
    def format_task(task):
        """Format a task for display."""
        due = task.due.date if task.due else "none"
        priority_map = {1: "🔵", 2: "🟠", 3: "🔴", 4: "⚫"}
        prio = priority_map.get(task.priority, "🔵")
        labels = ", ".join(task.labels) if task.labels else ""
        return f"{prio} [{task.id}] {task.content} | due: {due} | {labels}"

    @staticmethod
    def format_project(project):
        return f"[{project.id}] {project.name}"
