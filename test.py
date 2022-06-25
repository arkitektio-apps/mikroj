from qtpy import QtWidgets
# generate a simple pyqt application with a window showing a button
# and a text field. The button will call a function that will

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MyWindow')
        self.resize(300, 200)
        self.button = QtWidgets.QPushButton('Click Me')
        self.button.clicked.connect(self.button_clicked)
        self.text = QtWidgets.QLineEdit()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text)
        self.setLayout(layout)

# Show a di



def main():
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
