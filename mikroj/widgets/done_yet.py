from qtpy import QtWidgets
from koil.qt import QtFuture


class DoneYetWidget(QtWidgets.QWidget):
    """A simple widget that asks the user if they are done yet."""

    def __init__(
        self,
        future: QtFuture,
        message: str,
        *args,
        **kwargs,
    ) -> None:
        """A simple widget that asks the user if they are done yet.

        Parameters
        ----------
        future : QtFuture
            The future to resolve when the user clicks the button.
        message : str
            The message to display to the user.
        """

        super().__init__(*args, **kwargs)
        self.button = QtWidgets.QPushButton(message)
        self.abort = QtWidgets.QPushButton("Abort")
        self.future = future
        self.button.clicked.connect(self.resolve)
        self.abort.clicked.connect(self.reject)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.button)
        self.hlayout.addWidget(self.abort)
        self.setLayout(self.hlayout)

    def resolve(self):
        self.future.resolve()
        self.future = None
        self.close()

    def reject(self):
        self.close()

    def closeEvent(self, e) -> None:
        if self.future:
            self.future.reject(Exception("User aborted"))
        return super().closeEvent(e)
