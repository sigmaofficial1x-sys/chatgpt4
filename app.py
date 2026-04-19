import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from browser_manager import launch_profile_browser
from profile_store import ProfileStore


SIDEBAR_ITEMS = [
    "Dashboard",
    "Profiles",
    "Content Hub",
    "Omni-Inbox",
    "Growth Bot",
    "Spy Glass",
    "Settings",
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MIR Account Manager")
        self.resize(1200, 760)

        base_dir = Path("./data")
        self.profiles_root = base_dir / "profiles"
        self.store = ProfileStore(base_dir / "profiles.db")

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self._build_sidebar()
        content = self._build_content()

        layout.addWidget(sidebar)
        layout.addWidget(content, 1)

        self.setStyleSheet(self._stylesheet())
        self.refresh_table()

    def _build_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidebar")
        panel.setFixedWidth(250)
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(20, 24, 20, 24)
        vbox.setSpacing(8)

        brand = QLabel("MIR Account Manager")
        brand.setObjectName("brand")
        brand.setWordWrap(True)
        vbox.addWidget(brand)
        vbox.addSpacing(14)

        for item in SIDEBAR_ITEMS:
            btn = QPushButton(item)
            btn.setProperty("navItem", True)
            if item == "Profiles":
                btn.setProperty("active", True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            vbox.addWidget(btn)

        vbox.addStretch()
        return panel

    def _build_content(self) -> QWidget:
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(24, 24, 24, 24)
        vbox.setSpacing(16)

        title = QLabel("Profiles")
        title.setObjectName("title")

        actions = QHBoxLayout()
        self.add_profile_btn = QPushButton("Add New Profile")
        self.add_profile_btn.setObjectName("primaryButton")
        self.add_profile_btn.clicked.connect(self.add_profile)

        self.manual_login_btn = QPushButton("Launch Login Browser")
        self.manual_login_btn.clicked.connect(self.launch_manual_login)

        actions.addWidget(self.add_profile_btn)
        actions.addWidget(self.manual_login_btn)
        actions.addStretch()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Account Name", "Proxy IP", "Status", "Open Browser", "ID"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnHidden(4, True)

        vbox.addWidget(title)
        vbox.addLayout(actions)
        vbox.addWidget(self.table, 1)
        return panel

    def _status_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        if text == "Active":
            item.setForeground(QColor("#2ecc71"))
        else:
            item.setForeground(QColor("#95a5a6"))
        return item

    def refresh_table(self) -> None:
        profiles = self.store.list_profiles()
        self.table.setRowCount(len(profiles))

        for row, profile in enumerate(profiles):
            self.table.setItem(row, 0, QTableWidgetItem(profile.name))
            self.table.setItem(row, 1, QTableWidgetItem(profile.proxy_ip))
            self.table.setItem(row, 2, self._status_item(profile.status))

            launch_btn = QPushButton("Open Browser")
            launch_btn.clicked.connect(lambda _checked, pid=profile.id: self.launch_profile(pid))
            self.table.setCellWidget(row, 3, launch_btn)
            self.table.setItem(row, 4, QTableWidgetItem(str(profile.id)))

    def add_profile(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Profile", "Account Name:")
        if not ok or not name.strip():
            return

        proxy_ip, _ = QInputDialog.getText(self, "Add Profile", "Proxy IP (optional):")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip())
        data_dir = str(self.profiles_root / safe_name)

        try:
            self.store.add_profile(name.strip(), proxy_ip.strip(), data_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Unable to add profile: {exc}")
            return

        self.refresh_table()

    def launch_manual_login(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Profile", "Select a profile row first.")
            return

        profile_id = int(self.table.item(row, 4).text())
        self.launch_profile(profile_id, login_mode=True)

    def launch_profile(self, profile_id: int, login_mode: bool = False) -> None:
        profile = self.store.get_profile(profile_id)

        try:
            self.store.update_status(profile_id, "Active")
            self.refresh_table()
            launch_profile_browser(profile.data_dir, profile.proxy_ip, login_mode=login_mode)
        except Exception as exc:
            QMessageBox.critical(self, "Browser Error", str(exc))
        finally:
            self.store.update_status(profile_id, "Inactive")
            self.refresh_table()

    @staticmethod
    def _stylesheet() -> str:
        return """
        QMainWindow, QWidget {
            background: #12161c;
            color: #ecf0f1;
            font-family: Inter, Segoe UI, Arial, sans-serif;
            font-size: 14px;
        }
        #sidebar {
            background: #171c24;
            border-right: 1px solid #242a34;
        }
        #brand {
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
        }
        QPushButton[navItem="true"] {
            text-align: left;
            padding: 10px 12px;
            border: 0;
            border-radius: 8px;
            background: transparent;
            color: #b8c2cc;
        }
        QPushButton[navItem="true"][active="true"] {
            background: #1f3f6d;
            color: #63b3ff;
            font-weight: 600;
        }
        #title {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
        }
        QTableWidget {
            background: #161b22;
            border: 1px solid #2c3440;
            gridline-color: #2c3440;
            border-radius: 10px;
        }
        QHeaderView::section {
            background-color: #1d2430;
            color: #c9d1d9;
            padding: 8px;
            border: 0;
            border-right: 1px solid #2c3440;
            font-weight: 600;
        }
        QPushButton {
            background: #1e2a38;
            border: 1px solid #2f4054;
            color: #e5edf6;
            padding: 8px 12px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background: #243246;
        }
        #primaryButton {
            background: #1479ff;
            border: 1px solid #2f8fff;
            color: white;
            font-weight: 700;
            padding: 10px 14px;
        }
        #primaryButton:hover {
            background: #2f8fff;
        }
        """


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
