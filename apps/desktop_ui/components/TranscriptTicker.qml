import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: ticker
    
    property string partialText: ""      // Live partial ASR (italic gray)
    property string committedText: ""    // Committed text (bright white)
    property bool isVisible: false
    
    width: parent.width
    height: 60
    color: "transparent"
    
    visible: isVisible || partialText !== "" || committedText !== ""
    
    // Background blur
    Rectangle {
        anchors.fill: parent
        color: Theme.surface
        opacity: 0.95
        radius: Theme.radiusCard
        
        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: Theme.primary
            border.width: 1
            radius: Theme.radiusCard
            opacity: partialText !== "" ? 0.5 : 0.0
            
            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.durationNormal
                }
            }
        }
    }
    
    // Content
    Column {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingMD
        anchors.rightMargin: Theme.spacingMD
        anchors.topMargin: Theme.spacingSM
        
        spacing: Theme.spacingXS
        
        // Committed text (bright white)
        Text {
            id: committed
            width: parent.width
            text: committedText
            color: Theme.textPrimary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            wrapMode: Text.Wrap
            visible: committedText !== ""
            
            // Slide-in animation
            NumberAnimation on x {
                id: slideAnim
                from: parent.width
                to: 0
                duration: Theme.durationNormal
                running: committedText !== ""
            }
        }
        
        // Partial text (italic gray)
        Text {
            id: partial
            width: parent.width
            text: partialText
            color: Theme.textSecondary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            font.italic: true
            wrapMode: Text.Wrap
            visible: partialText !== ""
            
            // Fade animation
            SequentialAnimation on opacity {
                running: partialText !== ""
                loops: Animation.Infinite
                NumberAnimation {
                    from: 0.6
                    to: 1.0
                    duration: Theme.durationSlow
                }
                NumberAnimation {
                    from: 1.0
                    to: 0.6
                    duration: Theme.durationSlow
                }
            }
        }
    }
    
    // Slide up animation when committing
    Behavior on y {
        NumberAnimation {
            duration: Theme.durationNormal
            easing.type: Easing.OutCubic
        }
    }
}


