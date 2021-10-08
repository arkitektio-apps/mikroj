from qtpy import QtWidgets
from arkitekt.agents.qt import QtAgent
from arkitekt.messages.postman.provide.bounced_provide import BouncedProvideMessage


class ProvisionsWidget(QtWidgets.QWidget):

    def __init__(self, qt_agent: QtAgent = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.agent = qt_agent
        self.layout = QtWidgets.QVBoxLayout()
        self.listWidget = QtWidgets.QListWidget()
        self.layout.addWidget(self.listWidget)

        self.setLayout(self.layout)
        self.provisions = {}

        self.agent.signals.provide.connect(self.provision_in)

    def provision_in(self, provide: BouncedProvideMessage):
        self.provisions[provide.meta.reference] = provide

        self.listWidget.clear()
        print(self.provisions)
        for key, provide in self.provisions.items():
            self.listWidget.addItem(f"{self.agent.approvedActors[provide.data.template].__name__} used by {provide.meta.context.user}")
