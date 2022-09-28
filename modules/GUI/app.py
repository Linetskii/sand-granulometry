class App:
    """Main window"""
    tk_window = None
    __notebook = None
    __sample = None
    __compare_samples = None
    __settings = None
    add_smpl_tab_title = 'Add the sample'
    compare_smpl_title = 'Compare samples'
    settings_title = 'Settings'

    def __init__(self, notebook, sample, compare_samples, settings):
        self.__notebook = notebook
        self.__sample = sample
        self.__compare_samples = compare_samples
        self.__settings = settings

    def start(self):
        """
        Starts the app. Adds all tabs to the main window.
        """
        # TODO: move config values to config.txt. Will be a plus - make config class to pre configuration APP
        self.__notebook.pack(fill='both', expand=True)
        # Create notebook
        # Create tabs
        # Add tabs to notebook
        self.__notebook.add(self.__sample.frame, text=self.add_smpl_tab_title)
        self.__notebook.add(self.__compare_samples.frame, text=self.compare_smpl_title)
        self.__notebook.add(self.__settings.frame, text=self.settings_title)
