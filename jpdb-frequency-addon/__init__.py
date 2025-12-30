"""
JPDB Frequency Addon for Anki
Fills frequency data from local JPDB.txt file into Anki cards.
"""

from aqt import mw, gui_hooks
from aqt.qt import QAction, QMenu
from aqt.browser import Browser

from . import utils


def on_browser_menus_did_init(browser: Browser):
    """Add menu items to the browser's Edit menu."""
    menu = browser.form.menuEdit

    # Add separator
    menu.addSeparator()

    # Add JPDB submenu
    jpdb_menu = QMenu("JPDB Frequency", browser)
    menu.addMenu(jpdb_menu)

    # Fill frequency action
    fill_action = QAction("Fill Frequency for Selected", browser)
    fill_action.triggered.connect(lambda: utils.fill_frequency_for_selected_cards(browser))
    jpdb_menu.addAction(fill_action)

    # Select frequency file action
    select_file_action = QAction("Select JPDB.txt File...", browser)
    select_file_action.triggered.connect(lambda: utils.select_frequency_file(browser))
    jpdb_menu.addAction(select_file_action)

    # Clear cache action
    clear_cache_action = QAction("Clear Frequency Cache", browser)
    clear_cache_action.triggered.connect(utils.clear_frequency_cache)
    jpdb_menu.addAction(clear_cache_action)


# Register the hook
gui_hooks.browser_menus_did_init.append(on_browser_menus_did_init)
