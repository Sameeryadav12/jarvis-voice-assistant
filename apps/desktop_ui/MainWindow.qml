import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import com.jarvis.theme 1.0
import "components"

ApplicationWindow {
    id: window
    
    // Properties (bound to bridge)
    property real audioAmplitude: jarvisBridge ? jarvisBridge.audioAmplitude : 0.0
    property string orbState: jarvisBridge ? jarvisBridge.orbState : "idle"
    property string statusText: jarvisBridge ? jarvisBridge.statusText : "Ready"
    property var activityHistory: jarvisBridge ? jarvisBridge.activityHistory : []
    
    // Window properties
    width: 900
    height: 700
    visible: true
    title: "Jarvis - Voice Assistant"
    color: Theme.background
    
    // Main layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingLG
        
        // Transcript Ticker (top)
        TranscriptTicker {
            id: ticker
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            isVisible: orbState !== "idle"
            partialText: ""  // TODO: Connect to STT partial results
            committedText: "" // TODO: Connect to committed transcript
        }
        
        // Voice Orb (center)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            
            VoiceOrb {
                id: voiceOrb
                anchors.centerIn: parent
                amplitude: window.audioAmplitude
                state: window.orbState
                breathing: orbState === "idle"
            }
            
            // Status pill (bottom-left of orb)
            Rectangle {
                anchors.top: voiceOrb.bottom
                anchors.topMargin: Theme.spacingMD
                anchors.horizontalCenter: voiceOrb.horizontalCenter
                width: statusTextItem.width + Theme.spacingMD
                height: 32
                color: Theme.surface
                radius: height / 2
                border.color: Theme.primary
                border.width: 1
                
                Text {
                    id: statusTextItem
                    anchors.centerIn: parent
                    text: window.statusText
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeCaption
                    color: Theme.textPrimary
                }
            }
        }
        
        // Quick Chips
        Flow {
            Layout.fillWidth: true
            spacing: Theme.spacingSM
            
            Repeater {
                model: [
                    {label: "Set timer", command: "set timer"},
                    {label: "What's the time?", command: "what time is it"},
                    {label: "Create reminder", command: "create reminder"},
                    {label: "Open Chrome", command: "open chrome"}
                ]
                
                Button {
                    text: modelData.label
                    padding: Theme.spacingSM
                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(Theme.primary, 1.2) : Theme.primary
                        radius: Theme.radiusButton
                    }
                    contentItem: Text {
                        text: parent.text
                        color: Theme.textPrimary
                        horizontalAlignment: Text.AlignHCenter
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeBody
                    }
                    onClicked: {
                        if (jarvisBridge) {
                            jarvisBridge.executeCommand(modelData.command)
                        }
                    }
                }
            }
        }
        
        // Activity Cards (scrollable)
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ColumnLayout {
                width: window.width - (Theme.spacingLG * 2)
                spacing: Theme.spacingMD
                
                Text {
                    text: "Activity"
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeDisplay
                    font.bold: true
                    color: Theme.textPrimary
                    Layout.fillWidth: true
                }
                
                Repeater {
                    model: window.activityHistory
                    ActivityCard {
                        Layout.fillWidth: true
                        intentName: modelData.intentName || "Unknown"
                        intentIcon: modelData.intentIcon || "💬"
                        timestamp: modelData.timestamp || ""
                        userCommand: modelData.userCommand || ""
                        jarvisResponse: modelData.jarvisResponse || ""
                        isPinned: modelData.isPinned || false
                        
                        onReSpeak: {
                            // TODO: Re-speak response
                            console.log("Re-speak:", modelData.jarvisResponse)
                        }
                        
                        onCopyText: {
                            // TODO: Copy to clipboard
                            console.log("Copy text")
                        }
                        
                        onTogglePin: {
                            // TODO: Toggle pin state
                            console.log("Toggle pin")
                        }
                        
                        onUndo: {
                            // TODO: Undo action
                            console.log("Undo")
                        }
                    }
                }
                
                // Empty state
                Text {
                    text: "No activity yet. Try saying 'Hey Jarvis' or click a quick chip above."
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeBody
                    color: Theme.textMuted
                    Layout.fillWidth: true
                    Layout.topMargin: Theme.spacingLG
                    horizontalAlignment: Text.AlignHCenter
                    visible: window.activityHistory.length === 0
                }
            }
        }
    }
    
    // Command Palette
    CommandPalette {
        id: commandPalette
        commands: [
            {label: "Set Timer", command: "set timer", icon: "⏱️"},
            {label: "What's the Time?", command: "what time is it", icon: "🕒"},
            {label: "Check Battery", command: "check battery", icon: "🔋"},
            {label: "System Info", command: "system info", icon: "💻"},
            {label: "Create Reminder", command: "create reminder", icon: "📝"},
            {label: "Open Chrome", command: "open chrome", icon: "🌐"},
            {label: "Help", command: "help", icon: "❓"}
        ]
        
        onExecuteCommand: {
            console.log("Executing command:", command)
            commandPalette.close()
            if (jarvisBridge) {
                jarvisBridge.executeCommand(command)
            }
        }
    }
    
    // Keyboard shortcut: Ctrl+K for command palette
    Shortcut {
        sequence: "Ctrl+K"
        onActivated: {
            if (commandPalette.visible) {
                commandPalette.close()
            } else {
                commandPalette.open()
            }
        }
    }
    
    // Status bar simulation (can be replaced with real status bar)
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 30
        color: Theme.surface
        border.color: Theme.surfaceAlt
        border.width: 1
        
        Text {
            anchors.left: parent.left
            anchors.leftMargin: Theme.spacingMD
            anchors.verticalCenter: parent.verticalCenter
            text: "Status: " + window.statusText
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeCaption
            color: Theme.textSecondary
        }
    }
}

