def __init__(self, config):
    super().__init__()
    self.logger = logging.getLogger(__name__)
    self.config = config
    self.converter = ImageConverter()
    self.uploaded_images = []
    self.title("Convo-Local")
    self.geometry("1300x750")
    self.minsize(1000, 600)
    
    # Thread management
    self.max_workers = 3  # Limit concurrent operations
    self.active_threads = 0
    self.thread_queue = []
    self.cancel_threads = False
    self.thread_lock = threading.Lock()
    
    self.configure_gui()
    self.create_widgets()
    
    # Start thread manager
    self.after(100, self.manage_threads)
