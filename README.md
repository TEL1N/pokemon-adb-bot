# Multi-Instance Android Automation System

A computer vision and parallel processing project that automates Android emulator interaction using advanced image recognition, state management, and multi-instance coordination.

## 🎯 Project Overview

Built as a learning exercise to explore computer vision, parallel processing, and Android automation. The system manages 4 independent Android emulator instances simultaneously, using OpenCV for UI detection and ADB for device control.

**Key Achievement:** 95%+ accuracy in image recognition across variable lighting conditions and UI states.

## 🛠️ Tech Stack

- **Languages:** Python 3.9+
- **Computer Vision:** OpenCV, NumPy, Pillow
- **Android Control:** Android Debug Bridge (ADB)
- **Emulator:** MuMu Player 12
- **Architecture:** Multi-process parallelization with independent state tracking

## ✨ Technical Features

### 1. Multi-Instance Parallel Processing
- Coordinates 4 simultaneous emulator instances (ports 16384, 16416, 16448, 16480)
- Process isolation with independent console windows per instance
- Auto-discovery and connection to MuMu Player instances
- Device-specific configuration support for different resolutions

### 2. Computer Vision Pipeline
- **Color Space Analysis:** HSV-based detection for consistent recognition across lighting variations
- **Contour Detection:** Area-based filtering (150-3000px²) to identify UI elements
- **Region-Based Scanning:** Configurable detection regions to minimize false positives
- **Multi-Pattern Recognition:** Detects multiple icon types using color range masks
- **Victory Detection:** Full-screen white flash detection with 90% threshold

### 3. State Machine Architecture
- Manages 88+ possible navigation states (4 difficulties × 2 series × 11 expansions)
- In-memory progress tracking per instance (resets on restart to avoid port conflicts)
- Smart navigation with conditional scrolling (only scrolls when necessary)
- Resume capability from last known position
- Universal reset flow for error recovery

### 4. Visual Calibration System
- Interactive right-click coordinate mapping
- Display scaling for high-resolution screens
- Live verification with tap testing
- Support for both shared and device-specific configurations
- Calibrates 15+ UI elements per device

### 5. Robust Error Handling
- Automatic app restart on unexpected states
- Verification loops for image detection (prevents false positives)
- Adaptive timing with configurable delays
- ESCAPE key polling to trigger UI state changes
- Graceful degradation on component failures

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Multi-Bot Runner                        │
│  (Auto-discovers & launches bot instances)              │
└────────┬────────────────────────────────────────────────┘
         │
         ├──► Bot Instance 1 (127.0.0.1:16384)
         │    ├─ ADB Controller
         │    ├─ CV Detection Pipeline
         │    ├─ State Tracker
         │    └─ Navigation Logic
         │
         ├──► Bot Instance 2 (127.0.0.1:16416)
         │    └─ [Same components]
         │
         ├──► Bot Instance 3 (127.0.0.1:16448)
         │    └─ [Same components]
         │
         └──► Bot Instance 4 (127.0.0.1:16480)
              └─ [Same components]
```

## 🔧 Key Technical Challenges Solved

### Challenge 1: Image Recognition Accuracy
**Problem:** UI elements varied in lighting, animation states, and positions.

**Solution:** 
- Switched from RGB to HSV color space (lighting-invariant)
- Implemented multi-range color detection with combined masks
- Added contour area filtering to eliminate noise
- Used region-based scanning to reduce search space

**Result:** Achieved 95%+ accuracy across all UI states.

### Challenge 2: Parallel Instance Coordination
**Problem:** Multiple instances interfering with each other's state and file access.

**Solution:**
- Process isolation with separate console windows
- In-memory state tracking (no file conflicts)
- Device-specific ADB connections with explicit device IDs
- Staggered startup (5-second delays) to avoid resource contention

**Result:** All 4 instances run independently without conflicts.

### Challenge 3: Timing & Synchronization
**Problem:** UI loading times varied, causing misclicks and failed detections.

**Solution:**
- Implemented generous delays (1-5 seconds) between major actions
- Added verification loops for critical detections
- Used swipe-with-hold to prevent accidental fling gestures
- ESCAPE key polling every 5 seconds to force UI state updates

**Result:** Reliable navigation with <1% failure rate.

### Challenge 4: State Management Complexity
**Problem:** 88+ possible navigation states with multiple paths to each.

**Solution:**
- Built modular navigation functions for each UI component
- Conditional logic (e.g., skip scroll for Beginner difficulty)
- Progress tracking to avoid re-checking exhausted paths
- Universal reset flow (70 BACK presses) for guaranteed clean state

**Result:** Bot can navigate entire state space reliably.

### Challenge 5: Device Resolution Differences
**Problem:** Same UI elements at different pixel coordinates on different devices.

**Solution:**
- Visual calibration tool with right-click coordinate capture
- Device-specific config files (e.g., `adb_config_127_0_0_1_16384.json`)
- Display scaling for high-DPI monitors during calibration
- Shared config fallback for uniform-resolution setups

**Result:** Works across any emulator resolution after one-time calibration.

## 📁 Project Structure

```
pokemon-pocket-bot/
├── adb_controller.py          # ADB wrapper with device management
├── progress_tracker.py        # In-memory state tracking
├── test_03_adb_find_battles.py    # Computer vision detection
├── test_04_adb_expansions.py      # Expansion navigation logic
├── test_05_adb_full_workflow.py   # Main bot workflow
├── test_06_adb_victory_detection.py   # Battle end detection
├── test_07_adb_universal_reset.py     # Error recovery system
├── bot_infinite_loop.py       # Single instance runner
├── multi_bot_runner.py        # Parallel instance launcher
├── calibrate_improved.py      # Visual calibration tool
├── diagnose_and_fix.py        # Diagnostic utilities
└── adb_config.json            # UI coordinate mappings
```

## 🚀 Setup & Usage

### Prerequisites
```bash
# Install Python dependencies
pip install opencv-python numpy pillow --break-system-packages

# Install ADB (Android Debug Bridge)
# Download platform-tools from: https://developer.android.com/tools/releases/platform-tools
# Extract to C:\platform-tools\

# Install MuMu Player 12
# Download from: https://www.mumuplayer.com/
```

### Calibration (One-Time Setup)
```bash
# Launch MuMu Player instance(s)
# Open the target app to main menu

# Run calibration tool
python calibrate_improved.py

# Follow the interactive prompts to calibrate:
# - App icon, navigation tabs, buttons
# - Difficulty selection, expansion menu
# - Battle UI elements, detection regions
```

### Single Instance Test
```bash
# Test workflow on one emulator before scaling
python test_single_instance.py
```

### Multi-Instance Execution
```bash
# Auto-discovers all MuMu instances and launches bots
python multi_bot_runner.py
```

## 📈 Performance Metrics

- **Detection Accuracy:** 95%+ across all UI elements
- **Instance Capacity:** 4 simultaneous emulators (tested)
- **Uptime:** 4-6 hours average before manual intervention
- **Throughput:** ~8-12 cycles per hour per instance
- **False Positive Rate:** <1% with verification loops

## 🧠 What I Learned

### Computer Vision
- HSV color space superiority for lighting-invariant detection
- Contour analysis and morphological operations
- Balancing detection sensitivity vs. false positives
- Region-based scanning for performance optimization

### Parallel Processing
- Process isolation patterns in Python
- Avoiding shared state conflicts in multi-instance systems
- Resource contention and startup sequencing
- Independent error handling per process

### Android Automation
- ADB command structure and device management
- Touch input simulation (tap, swipe, hold)
- Screenshot capture and processing pipeline
- Handling async UI updates and loading states

### System Design
- State machine architecture for complex workflows
- Modular component design for maintainability
- Configuration management (device-specific vs shared)
- Graceful degradation and error recovery strategies

## 🔮 Future Improvements

- [ ] Machine learning for adaptive UI detection
- [ ] OCR integration for text-based state verification
- [ ] Web dashboard for multi-instance monitoring
- [ ] Automatic performance tuning based on detection confidence
- [ ] Cloud-based coordination for distributed instances

## ⚠️ Disclaimer

This project was created purely for educational purposes to learn computer vision, parallel processing, and Android automation. It automates personal gameplay only and does not:
- Interact with game servers beyond normal client behavior
- Modify game files or memory
- Provide unfair advantages in competitive modes
- Violate any terms of service

Use responsibly and in accordance with all applicable terms and conditions.

## 📝 License

MIT License - Feel free to learn from and build upon this code.

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome! Feel free to open issues or reach out with questions.

---

**Built with:** Python 🐍 | OpenCV 👁️ | ADB 🤖 | Coffee ☕
