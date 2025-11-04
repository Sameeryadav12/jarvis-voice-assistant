import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Popup {
    id: palette
    
    property var commands: []            // Array of {label, command, icon}
    property string searchText: ""
    
    width: 600
    height: 400
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    
    // Fuzzy search function
    function fuzzyMatch(text, pattern) {
        if (!pattern) return true
        pattern = pattern.toLowerCase()
        text = text.toLowerCase()
        
        var patternIndex = 0
        for (var i = 0; i < text.length; i++) {
            if (text[i] === pattern[patternIndex]) {
                patternIndex++
                if (patternIndex >= pattern.length) {
                    return true
                }
            }
        }
        return false
    }
    
    // Filtered commands
    property var filteredCommands: {
        if (!searchText) return commands
        var filtered = []
        for (var i = 0; i < commands.length; i++) {
            if (fuzzyMatch(commands[i].label, searchText) || 
                fuzzyMatch(commands[i].command, searchText)) {
                filtered.push(commands[i])
            }
        }
        return filtered
    }
    
    background: Rectangle {
        color: Theme.surface
        border.color: Theme.primary
        border.width: 2
        radius: Theme.radiusCard
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMD
        spacing: Theme.spacingMD
        
        // Title
        Text {
            text: "Command Palette"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeDisplay
            font.bold: true
            color: Theme.textPrimary
        }
        
        // Search box
        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: "Type to search commands... (Ctrl+K)"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            color: Theme.textPrimary
            background: Rectangle {
                color: Theme.surfaceAlt
                border.color: Theme.primary
                border.width: 2
                radius: Theme.radiusInput
            }
            onTextChanged: searchText = text
            
            // Auto-focus on open
            Component.onCompleted: forceActiveFocus()
            
            // Keyboard navigation
            Keys.onDown: {
                if (commandList.count > 0) {
                    commandList.currentIndex = 0
                    commandList.forceActiveFocus()
                }
            }
        }
        
        // Command list
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ListView {
                id: commandList
                model: filteredCommands
                delegate: Rectangle {
                    width: commandList.width
                    height: 50
                    color: commandList.currentIndex === index ? Theme.primary : "transparent"
                    opacity: commandList.currentIndex === index ? 0.3 : 1.0
                    radius: Theme.radiusInput
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingMD
                        anchors.rightMargin: Theme.spacingMD
                        spacing: Theme.spacingMD
                        
                        Text {
                            text: modelData.icon || "▶"
                            font.pixelSize: Theme.fontSizeBody
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingXS
                            
                            Text {
                                text: modelData.label
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeBody
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            Text {
                                text: modelData.command
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeCaption
                                color: Theme.textSecondary
                                visible: modelData.command !== modelData.label
                            }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            commandList.currentIndex = index
                            palette.executeCommand(modelData.command)
                        }
                    }
                }
                
                // Keyboard navigation
                Keys.onReturnPressed: {
                    if (currentIndex >= 0) {
                        palette.executeCommand(filteredCommands[currentIndex].command)
                    }
                }
                Keys.onEnterPressed: Keys.onReturnPressed
            }
        }
        
        // Recent commands section
        Text {
            text: "Recent Commands"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeCaption
            color: Theme.textMuted
            visible: searchText === ""
        }
    }
    
    // Signals
    signal executeCommand(string command)
    
    // Keyboard shortcut handler (Ctrl+K)
    Shortcut {
        sequence: "Ctrl+K"
        onActivated: {
            if (palette.visible) {
                palette.close()
            } else {
                palette.open()
            }
        }
    }
}


