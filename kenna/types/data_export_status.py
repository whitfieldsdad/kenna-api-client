from dataclasses import dataclass

DONE = 'done'
RUNNING = 'running'


@dataclass(frozen=True)
class DataExportStatus:
    search_id: int
    status: str

    def is_done(self):
        return self.status == DONE

    def is_running(self):
        return self.status == RUNNING
