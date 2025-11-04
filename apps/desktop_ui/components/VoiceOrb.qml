import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Rectangle {
    id: orb
    
    // Properties
    property real amplitude: 0.0          // 0.0 to 1.0
    property string state: "idle"          // "idle", "listening", "speaking", "processing"
    property bool breathing: true
    
    // Dimensions
    width: Theme.orbSize
    height: Theme.orbSize
    radius: width / 2
    color: getOrbColor()
    
    // Breathing animation (continuous)
    SequentialAnimation on scale {
        running: breathing && state === "idle"
        loops: Animation.Infinite
        NumberAnimation {
            from: 1.0
            to: 1.05
            duration: Theme.durationSlow
            easing.type: Easing.InOutSine
        }
        NumberAnimation {
            from: 1.05
            to: 1.0
            duration: Theme.durationSlow
            easing.type: Easing.InOutSine
        }
    }
    
    // Pulse animation (while listening)
    SequentialAnimation on scale {
        running: state === "listening"
        loops: Animation.Infinite
        NumberAnimation {
            from: 1.0
            to: 1.15 + (amplitude * 0.1)
            duration: Theme.durationNormal
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            from: 1.15 + (amplitude * 0.1)
            to: 1.0
            duration: Theme.durationNormal
            easing.type: Easing.InCubic
        }
    }
    
    // Sweep animation (while speaking)
    SequentialAnimation on scale {
        running: state === "speaking"
        loops: Animation.Infinite
        NumberAnimation {
            from: 1.0
            to: 1.2
            duration: Theme.durationFast
            easing.type: Easing.OutQuad
        }
        NumberAnimation {
            from: 1.2
            to: 1.0
            duration: Theme.durationFast
            easing.type: Easing.InQuad
        }
    }
    
    // Color transitions
    ColorAnimation on color {
        id: colorAnim
        duration: Theme.durationNormal
        easing.type: Easing.OutCubic
    }
    
    // Glow effect
    layer.enabled: state !== "idle"
    layer.effect: Glow {
        id: glow
        radius: 16 + (amplitude * 8)
        samples: 17
        color: getOrbColor()
        transparentBorder: true
        
        SequentialAnimation on radius {
            running: state === "listening" || state === "speaking"
            loops: Animation.Infinite
            NumberAnimation {
                from: 16 + (amplitude * 8)
                to: 24 + (amplitude * 12)
                duration: Theme.durationNormal
            }
            NumberAnimation {
                from: 24 + (amplitude * 12)
                to: 16 + (amplitude * 8)
                duration: Theme.durationNormal
            }
        }
    }
    
    // Inner ring (amplitude visualization)
    Rectangle {
        id: innerRing
        anchors.centerIn: parent
        width: parent.width * (0.6 + amplitude * 0.2)
        height: parent.height * (0.6 + amplitude * 0.2)
        radius: width / 2
        color: "transparent"
        border.color: Qt.lighter(parent.color, 1.3)
        border.width: 2
        opacity: amplitude > 0.1 ? 0.6 : 0
        visible: state === "listening" || state === "speaking"
        
        Behavior on opacity {
            NumberAnimation {
                duration: Theme.durationFast
            }
        }
    }
    
    // State indicator text
    Text {
        id: stateText
        anchors.centerIn: parent
        text: getStateText()
        color: Theme.textPrimary
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeCaption
        opacity: state !== "idle" ? 1.0 : 0.0
        
        Behavior on opacity {
            NumberAnimation {
                duration: Theme.durationNormal
            }
        }
    }
    
    // Helper functions
    function getOrbColor() {
        switch (state) {
            case "listening":
                return Theme.orbListening
            case "speaking":
                return Theme.orbSpeaking
            case "processing":
                return Theme.orbProcessing
            default:
                return Theme.orbIdle
        }
    }
    
    function getStateText() {
        switch (state) {
            case "listening":
                return "Listening..."
            case "speaking":
                return "Speaking..."
            case "processing":
                return "Thinking..."
            default:
                return ""
        }
    }
}


