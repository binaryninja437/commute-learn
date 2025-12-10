# Build APK Instructions - Speed Controls Update

## Issue: Java Version Incompatibility

Your system has **Java 25** installed, but Gradle 8.13 only supports up to **Java 23**.

---

## ✅ Solution: Build in Android Studio

Android Studio will use its own bundled JDK (Java 17), which is compatible.

### Steps:

1. **Android Studio is now opening** (or open it manually)

2. **Wait for Gradle Sync** (~2-3 minutes)
   - Let Android Studio sync the project
   - It will use its own JDK automatically

3. **Build APK:**
   - Click **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
   - Wait ~2-5 minutes
   - Click **locate** when done

4. **APK Location:**
   ```
   frontend/android/app/build/outputs/apk/debug/app-debug.apk
   ```

5. **Install on Phone:**
   - Copy APK to phone
   - Install and test speed controls!

---

## 🎮 Testing the Speed Controls:

Once installed:

1. **Open app** and play any podcast
2. **Look at bottom player bar** (right side)
3. **You'll see:** `[1x] [1.5x] [2x]` buttons
4. **Click to test:**
   - 1x = Normal speed
   - 1.5x = 50% faster
   - 2x = Double speed
5. **Active button** will be highlighted in **green**

---

## Alternative: Use Java 17

If you prefer command line, you can install Java 17:

1. **Download JDK 17:**
   - https://adoptium.net/temurin/releases/?version=17

2. **Set JAVA_HOME temporarily:**
   ```bash
   set JAVA_HOME=C:\Path\To\JDK17
   set PATH=%JAVA_HOME%\bin;%PATH%
   ```

3. **Then build:**
   ```bash
   cd frontend/android
   ./gradlew.bat assembleDebug
   ```

---

## 📦 What's New in This Build:

### Playback Speed Controls
- **1x** - Normal speed (default)
- **1.5x** - 50% faster (saves 33% time)
- **2x** - Double speed (saves 50% time)

### Multi-Voice TTS (if backend deployed)
- **Didi** - Female voice (Hindi)
- **Bhaiya** - Male voice (deeper, English-India)
- Distinct voices for better engagement

### Features:
- Speed controls in player bar
- Visual feedback (green = active)
- Instant speed change (no lag)
- Works on all podcasts

---

## 🎯 Expected Result:

After installation, students can:
- Listen faster during revision
- Save time on familiar topics
- Use normal speed for complex concepts
- Toggle between speeds seamlessly

Perfect for efficient learning during commute! 🚀

---

**Android Studio is already open. Just follow steps 2-5 above!**
