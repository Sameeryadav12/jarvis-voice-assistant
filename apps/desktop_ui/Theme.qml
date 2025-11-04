import QtQuick 2.15

pragma Singleton

QtObject {
    // Color Palette (Dark-first)
    readonly property color background: "#0B0F1A"      // Near-black blue
    readonly property color surface: "#111827"         // Container
    readonly property color surfaceAlt: "#0E1624"      // Alternate surface
    readonly property color primary: "#5B8CFF"        // Electric blue (accent/orb)
    readonly property color success: "#31EE88"         // Teal-green
    readonly property color warning: "#F59E0B"        // Amber
    readonly property color critical: "#EF4444"        // Red
    readonly property color textPrimary: "#F5F7FA"    // Primary text
    readonly property color textSecondary: "#A6B0C3"   // Secondary text
    readonly property color textMuted: "#647089"       // Muted text
    
    // Typography
    readonly property string fontFamily: "Segoe UI Variable, Segoe UI, Arial"
    readonly property int fontSizeDisplay: 28          // Headlines
    readonly property int fontSizeBody: 14               // Body text
    readonly property int fontSizeCaption: 12           // Caption text
    readonly property int fontSizeLarge: 32              // Large headlines
    
    // Spacing (8-pt system)
    readonly property int spacingXS: 4
    readonly property int spacingSM: 8
    readonly property int spacingMD: 16
    readonly property int spacingLG: 24
    readonly property int spacingXL: 32
    
    // Radii
    readonly property int radiusCard: 16                // Cards
    readonly property int radiusButton: 24              // Buttons
    readonly property int radiusInput: 12               // Input fields
    
    // Shadows
    readonly property var shadowSoft: ({
        "x": 0,
        "y": 12,
        "blur": 40,
        "spread": 0,
        "color": Qt.rgba(0, 0, 0, 0.35)
    })
    
    // Animations
    readonly property int durationFast: 150             // ms
    readonly property int durationNormal: 250           // ms
    readonly property int durationSlow: 400             // ms
    readonly property var easingStandard: [0.4, 0.0, 0.2, 1.0]  // Cubic Bezier
    readonly property var easingSpring: [0.68, -0.55, 0.265, 1.55] // Spring
    
    // Elevation
    readonly property int elevation0: 0
    readonly property int elevation1: 2
    readonly property int elevation2: 4
    readonly property int elevation3: 8
    
    // Voice Orb specific
    readonly property int orbSize: 120                  // Base diameter
    readonly property color orbIdle: textMuted
    readonly property color orbListening: primary
    readonly property color orbSpeaking: success
    readonly property color orbProcessing: warning
}


