import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: card
    
    property string intentName: ""
    property string intentIcon: "💬"
    property string timestamp: ""
    property string userCommand: ""
    property string jarvisResponse: ""
    property bool isPinned: false
    
    width: parent.width
    height: contentColumn.height + (Theme.spacingMD * 2)
    color: Theme.surface
    radius: Theme.radiusCard
    border.color: isPinned ? Theme.primary : "transparent"
    border.width: isPinned ? 2 : 0
    
    // Shadow
    layer.enabled: true
    layer.effect: DropShadow {
        transparentBorder: true
        radius: 8
        samples: 17
        color: Qt.rgba(0, 0, 0, 0.2)
        verticalOffset: 2
    }
    
    // Slide-in animation
    NumberAnimation on x {
        id: slideInAnim
        from: parent.width
        to: 0
        duration: Theme.durationNormal
        easing.type: Easing.OutCubic
    }
    
    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: Theme.spacingMD
        spacing: Theme.spacingMD
        
        // Header: Icon + Intent + Timestamp
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSM
            
            Text {
                text: intentIcon
                font.pixelSize: Theme.fontSizeBody
            }
            
            Text {
                text: intentName
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                font.bold: true
                color: Theme.textPrimary
                Layout.fillWidth: true
            }
            
            Text {
                text: timestamp
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeCaption
                color: Theme.textMuted
            }
            
            // Pin indicator
            Text {
                text: "📍"
                visible: isPinned
                font.pixelSize: Theme.fontSizeCaption
            }
        }
        
        // User command
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: userText.height + Theme.spacingSM
            color: Theme.surfaceAlt
            radius: Theme.radiusInput
            
            Text {
                id: userText
                anchors.fill: parent
                anchors.margins: Theme.spacingSM
                text: "You: " + userCommand
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                color: Theme.textPrimary
                wrapMode: Text.Wrap
            }
        }
        
        // Jarvis response
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: jarvisText.height + Theme.spacingSM
            color: Theme.primary
            opacity: 0.1
            radius: Theme.radiusInput
            
            Text {
                id: jarvisText
                anchors.fill: parent
                anchors.margins: Theme.spacingSM
                text: "Jarvis: " + jarvisResponse
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                color: Theme.textPrimary
                wrapMode: Text.Wrap
            }
        }
        
        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSM
            
            Button {
                text: "🔊 Re-speak"
                Layout.fillWidth: true
                background: Rectangle {
                    color: parent.pressed ? Qt.darker(Theme.primary, 1.2) : Theme.primary
                    radius: Theme.radiusButton
                }
                contentItem: Text {
                    text: parent.text
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                }
                onClicked: card.reSpeak()
            }
            
            Button {
                text: "📋 Copy"
                Layout.fillWidth: true
                background: Rectangle {
                    color: parent.pressed ? Qt.darker(Theme.surfaceAlt, 1.2) : Theme.surfaceAlt
                    radius: Theme.radiusButton
                }
                contentItem: Text {
                    text: parent.text
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                }
                onClicked: card.copyText()
            }
            
            Button {
                text: isPinned ? "📌 Unpin" : "📍 Pin"
                Layout.fillWidth: true
                background: Rectangle {
                    color: parent.pressed ? Qt.darker(Theme.surfaceAlt, 1.2) : Theme.surfaceAlt
                    radius: Theme.radiusButton
                }
                contentItem: Text {
                    text: parent.text
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                }
                onClicked: {
                    isPinned = !isPinned
                    card.togglePin()
                }
            }
            
            Button {
                text: "↩️ Undo"
                Layout.fillWidth: true
                background: Rectangle {
                    color: parent.pressed ? Qt.darker(Theme.critical, 1.2) : Theme.critical
                    opacity: 0.8
                    radius: Theme.radiusButton
                }
                contentItem: Text {
                    text: parent.text
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                }
                onClicked: card.undo()
            }
        }
    }
    
    // Signals
    signal reSpeak()
    signal copyText()
    signal togglePin()
    signal undo()
    
    // Helper functions
    function copyToClipboard() {
        var text = "You: " + userCommand + "\nJarvis: " + jarvisResponse
        // TODO: Implement clipboard copy via Python bridge
    }
}


