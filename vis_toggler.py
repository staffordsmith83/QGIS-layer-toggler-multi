# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VisToggler
                                 A QGIS plugin
 Toggle visibility of layers with keystrokes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-05-28
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Stafford Smith
        email                : staffordsmith83@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QKeySequence
from qgis.PyQt.QtWidgets import QAction, QShortcut
from qgis.core import QgsProject, Qgis
from qgis.utils import iface

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .vis_toggler_dialog import VisTogglerDialog
import os.path


class VisToggler:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VisToggler_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Layer Visibility Toggler')
        self.toolbar = self.iface.addToolBar(u'Layer Visibility Toggler')
        self.toolbar.setObjectName(u'Layer Visibility Toggler')

        # initialise these variables
        self.keylist = None
        self.shortcut_list = None
        self.comboBox_list = None

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VisToggler', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            # self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)  # this way should add to its own toolbar

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/vis_toggler/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layer Visibility Toggler'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Layer Visibility Toggler'),
                action)
            self.iface.removeToolBarIcon(action)

    def toggle_layer(self, layer):
        try:
            vis = QgsProject.instance() \
                .layerTreeRoot() \
                .findLayer(layer.id()) \
                .isVisible()
            if vis == True:
                QgsProject.instance() \
                    .layerTreeRoot() \
                    .findLayer(layer.id()) \
                    .setItemVisibilityChecked(False)
            if vis == False:
                QgsProject.instance() \
                    .layerTreeRoot() \
                    .findLayer(layer.id()) \
                    .setItemVisibilityChecked(True)

        except:
            iface.messageBar().pushMessage("Error toggling the layer. Has the assigned layer been removed?",
                                           level=Qgis.Info)

    # Shortcut Key Section
    def setup_shortcut(self, keysequence):
        shortcut = QShortcut(
            QKeySequence(keysequence),
            iface.mainWindow()
        )
        shortcut.setContext(Qt.ApplicationShortcut)
        return shortcut

    def connect_shortcut(self, shortcut, layer):
        shortcut.activated.connect(lambda: self.toggle_layer(layer))

    def disconnect_shortcut(self, shortcut):
        shortcut.activated.disconnect()

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = VisTogglerDialog()
            # first, make a list of the combobox objects in the dialog
            self.comboBox_list = [self.dlg.mMapLayerComboBox_1,
                                  self.dlg.mMapLayerComboBox_2,
                                  self.dlg.mMapLayerComboBox_3,
                                  self.dlg.mMapLayerComboBox_4,
                                  self.dlg.mMapLayerComboBox_5,
                                  self.dlg.mMapLayerComboBox_6]

            # make all the shortcuts now

            self.keylist1 = ['Q', 'W', 'E', 'A', 'S', 'D']
            self.keylist2 = ['Ctrl+Alt+Q', 'Ctrl+Alt+W', 'Ctrl+Alt+E', 'Ctrl+Alt+A', 'Ctrl+Alt+S', 'Ctrl+Alt+D']
            self.keylist3 = [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6]

            self.shortcut_list1 = []
            for key in self.keylist1:
                self.shortcut_list1.append(self.setup_shortcut(key))

            self.shortcut_list2 = []
            for key in self.keylist2:
                self.shortcut_list2.append(self.setup_shortcut(key))

            self.shortcut_list3 = []
            for key in self.keylist3:
                self.shortcut_list3.append(self.setup_shortcut(key))


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        # REFRESH:
        # immediately after opening the dialog (i.e. before the user selects anything)
        # check each combobox to see if it has an existing selection.
        # If so, disconnect the shortcut to that layer. This is because:
        # if a layer is selected in the comboBox it implies that we assigned that layer to a shortcut
        # the last time we opened the dialog.
        # IT IS POSSIBLE AN EXCEPTION COULD BE RAISED HERE as shortcuts are not yet defined...
        for counter, comboBox in enumerate(self.comboBox_list):
            if comboBox.currentLayer():
                self.disconnect_shortcut(self.shortcut_list[counter])

        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # next, define the key sequences based on these shortcuts

            if self.dlg.defaultButton.isChecked():
                self.shortcut_list = self.shortcut_list1

            if self.dlg.modifierButton_1.isChecked():
                self.shortcut_list = self.shortcut_list2

            if self.dlg.modifierButton_2.isChecked():
                self.shortcut_list = self.shortcut_list3

            # check if a layer has been selected. If so, then define it, and connect the shortcut
            for counter, comboBox in enumerate(self.comboBox_list):
                if comboBox.currentLayer():
                    self.connect_shortcut(self.shortcut_list[counter], comboBox.currentLayer())
                    message = 'Assigned shortcut for keysequence ' + self.shortcut_list[counter].key().toString()
                    iface.messageBar().pushMessage(message, level=Qgis.Success, duration=1)
