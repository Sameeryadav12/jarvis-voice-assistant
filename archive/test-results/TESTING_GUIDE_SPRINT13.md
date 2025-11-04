# Sprint 13 UI Testing Guide

## ✅ Pre-Launch Tests: PASSED

All component tests successful:
- ✅ PySide6 imports
- ✅ All QML files exist
- ✅ Python modules working
- ✅ Bridge registered
- ✅ Command execution working

---

## 🧪 Manual Testing Checklist

### 1. Visual Inspection
- [ ] Window opens successfully (900x700px)
- [ ] Dark theme applied (background: #0B0F1A)
- [ ] Voice orb visible in center (blue-gray when idle)
- [ ] Orb has subtle breathing animation when idle
- [ ] Status text shows "Ready" below orb
- [ ] Quick chips visible at bottom ("Set timer", "What's the time?", etc.)
- [ ] Activity section visible (empty initially)

### 2. Voice Orb States
- [ ] Click a quick chip button (e.g., "What's the time?")
- [ ] Verify orb changes to "processing" (amber) state
- [ ] Verify orb shows "Thinking..." text
- [ ] After response, orb returns to "idle" (gray) state

**Expected**: Smooth color transitions, state text updates

### 3. Activity Cards
After clicking a quick chip:
- [ ] New activity card appears in timeline
- [ ] Card shows:
  - Icon (🕒 for time, 📅 for date, etc.)
  - Intent name (e.g., "GET_TIME")
  - Timestamp (current time, e.g., "21:11")
  - User command text
  - Jarvis response text
- [ ] Card has smooth slide-in animation from right
- [ ] Card has soft shadow effect

### 4. Activity Card Actions
Test each button on an activity card:
- [ ] 🔊 **Re-speak button**: Click (should log to console for now)
- [ ] 📋 **Copy button**: Click (should copy text - check clipboard)
- [ ] 📍 **Pin button**: Click (border should highlight, button changes to "Unpin")
- [ ] ↩️ **Undo button**: Click (should log to console)

### 5. Command Palette (Ctrl+K)
- [ ] Press **Ctrl+K** to open command palette
- [ ] Verify popup appears centered
- [ ] Type in search box (e.g., "time")
- [ ] Verify commands filter in real-time
- [ ] Use arrow keys to navigate filtered list
- [ ] Press Enter to execute selected command
- [ ] Press Escape to close palette
- [ ] Verify command executed and card added to activity

**Test Commands**:
- "time" → Should show "What's the Time?"
- "battery" → Should show "Check Battery"
- "help" → Should show "Help"

### 6. Quick Chips
Click each quick chip button:
- [ ] **"Set timer"** → Creates activity card
- [ ] **"What's the time?"** → Shows current time
- [ ] **"Create reminder"** → Creates reminder activity
- [ ] **"Open Chrome"** → Creates activity (may not execute if Chrome not found)

**Expected**: Each click executes command, orb changes state, card appears

### 7. System Tray
- [ ] Check system tray (bottom-right of Windows taskbar)
- [ ] Verify mini orb icon is visible (gray when idle)
- [ ] Right-click on tray icon
- [ ] Verify context menu appears:
  - Show Jarvis
  - 🎤 Activate Voice
  - 📋 Recent Activity
  - ⚙️ Settings
  - Quit
- [ ] Double-click tray icon → Window should show
- [ ] Close window → Tray icon should remain

### 8. Window Behavior
- [ ] Resize window → Layout should adjust
- [ ] Minimize window → Should minimize normally
- [ ] Maximize window → Components should scale appropriately
- [ ] Close window → Should close gracefully

### 9. Multiple Commands
Execute several commands in sequence:
- [ ] "what time is it"
- [ ] "what's the date"
- [ ] "check battery"
- [ ] "system info"

**Expected**: Each creates a new activity card, cards stack in timeline (newest first)

### 10. Error Handling
- [ ] Type invalid command in Command Palette
- [ ] Execute non-existent command
- [ ] Verify error message appears appropriately
- [ ] Verify app doesn't crash

---

## 🎯 Quick Test Scenarios

### Scenario 1: Get Current Time
1. Click "What's the time?" quick chip
2. Watch orb change to "processing" → "idle"
3. Check activity card appears with time response

### Scenario 2: Use Command Palette
1. Press Ctrl+K
2. Type "help"
3. Press Enter
4. Verify help command executed and card created

### Scenario 3: Pin an Activity
1. Execute any command (e.g., "what time is it")
2. Click 📍 Pin button on the activity card
3. Verify border highlights and button changes to "Unpin"

### Scenario 4: System Tray
1. Minimize window
2. Double-click tray icon
3. Window should restore

---

## 📝 What to Report

If you find issues, note:
- **Component**: Which UI element (orb, card, palette, etc.)
- **Expected**: What you expected to happen
- **Actual**: What actually happened
- **Steps**: How to reproduce

---

## ✅ Expected Behavior Summary

1. **Voice Orb**: Smooth animations, state-based colors, breathing when idle
2. **Activity Cards**: Slide in from right, show all info, action buttons work
3. **Command Palette**: Ctrl+K opens, fuzzy search works, keyboard navigation works
4. **Quick Chips**: Execute commands, update orb state, create activity cards
5. **System Tray**: Icon visible, menu works, double-click shows window
6. **Overall**: Dark theme, smooth animations, responsive layout

---

## 🚀 Ready to Test!

The UI should now be running. Follow the checklist above and let me know:
- What works well ✅
- What needs fixing ❌
- Any visual issues 🎨
- Performance observations ⚡

Happy testing! 🎉


