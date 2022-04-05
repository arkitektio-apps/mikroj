import imagej
import scyjava


class ImageJ:
    def __init__(
        self,
        headless=False,
        version="/home/jhnnsrs/Fiji.app",
        plugins_dir="/home/jhnnsrs/Fiji.app/plugins",
    ) -> None:
        # concatenade version plus plugins
        # build = [version] + plugins if len(plugins) > 0 else version
        # if plugins_dir:
        #   path = os.path.join(os.getcwd(),plugins_dir)
        #    scyjava.config.add_option(f'-Dplugins.dir={path}')

        self.headless = headless
        print(f"Initializing with version {version}")
        scyjava.config.add_option(f"-Dplugins.dir={plugins_dir}")

        self._ij = imagej.init(version, headless=headless)
        if not headless:
            self._ij.ui().showUI()
        super().__init__()

    @property
    def py(self):
        return self._ij.py

    @property
    def ui(self):
        return self._ij.ui()

    @property
    def ij(self):
        return self._ij
