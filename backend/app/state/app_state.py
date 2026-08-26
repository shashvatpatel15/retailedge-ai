class AppState:

    def __init__(self):

        # ============================================
        # EDGE AI
        # ============================================

        self.engine = None

        self.engine_thread = None

        self.startup_error = None


        # ============================================
        # CLOUD SYNC
        # ============================================

        self.cloud_sync_thread = None

        self.cloud_sync_stop_event = None

        self.cloud_sync_running = False

        self.last_cloud_sync_at = None

        self.last_cloud_sync_error = None


app_state = AppState()