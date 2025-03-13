from typing import List, Dict, Any

from googleapiclient.errors import HttpError

# Constants
MAX_RESULTS = 10

class GoogleTasksAPI:
    """Handles all interactions with the Google Tasks API."""
    
    def __init__(self, auth_manager):
        """Initialize with an auth manager."""
        self.auth_manager = auth_manager
        self._service = None
    
    @property
    def service(self):
        """Get the API service, building it if needed."""
        if not self._service:
            self._service = self.auth_manager.build_service()
        return self._service
    
    def refresh_service(self):
        """Force refresh the service with new credentials."""
        self._service = self.auth_manager.build_service(force_refresh=True)
        return self._service
    
    def get_task_lists(self) -> List[Dict[str, Any]]:
        """Retrieve task lists from Google Tasks API."""
        results = self.service.tasklists().list(maxResults=MAX_RESULTS).execute()
        return results.get("items", [])

    def get_tasks(self, tasklist_id: str) -> List[Dict[str, Any]]:
        """Retrieve tasks for a specific task list."""
        tasks = self.service.tasks().list(tasklist=tasklist_id, showCompleted=True, showHidden=True).execute()
        return tasks.get('items', [])
    
    def update_task(self, tasklist_id: str, task_id: str, task_data: dict) -> dict:
        """Update a specific task."""
        return self.service.tasks().update(
            tasklist=tasklist_id,
            task=task_id,
            body=task_data
        ).execute()
    
    def get_task(self, tasklist_id: str, task_id: str) -> dict:
        """Get a specific task."""
        return self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    
    def delete_task(self, tasklist_id: str, task_id: str) -> None:
        """Delete a specific task."""
        self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    
    def create_task(self, tasklist_id: str, task_data: dict) -> dict:
        """Create a new task."""
        return self.service.tasks().insert(tasklist=tasklist_id, body=task_data).execute()
    
    def move_task(self, tasklist_id: str, task_id: str, previous_id: str = None) -> dict:
        """Move a task within a task list."""
        if previous_id:
            return self.service.tasks().move(
                tasklist=tasklist_id,
                task=task_id,
                previous=previous_id
            ).execute()
        else:
            return self.service.tasks().move(tasklist=tasklist_id, task=task_id).execute()
    
    def delete_tasklist(self, tasklist_id: str) -> None:
        """Delete a task list."""
        self.service.tasklists().delete(tasklist=tasklist_id).execute()
        
    def create_tasklist(self, title: str) -> dict:
        """Create a new task list."""
        return self.service.tasklists().insert(body={'title': title}).execute()
    
    def update_tasklist(self, tasklist_id: str, title: str) -> dict:
        """Update a task list's title."""
        return self.service.tasklists().update(
            tasklist=tasklist_id,
            body={'title': title, 'id': tasklist_id}
        ).execute()

    def handle_api_error(self, operation, error, retry_callback=None):
        """Handle API errors, with optional retry functionality."""
        if isinstance(error, HttpError):
            # If it's a 401 or 403 error, credentials might be expired
            if error.resp.status in (401, 403):
                # Try to refresh credentials
                try:
                    self.refresh_service()
                    # If retry callback is provided, try the operation again
                    if retry_callback:
                        return retry_callback()
                except Exception as refresh_error:
                    # If refresh fails, raise the original error
                    raise error
            else:
                # For other HTTP errors, just raise them
                raise error
        else:
            # For non-HTTP errors, just raise them
            raise error
