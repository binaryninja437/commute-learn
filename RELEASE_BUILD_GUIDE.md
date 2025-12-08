# Release Build Guide - Google Play Store Submission

## Prerequisites

✅ Android Studio installed
✅ Backend deployed on Render
✅ Privacy policy hosted
✅ App tested and working

---

## Step 1: Generate Signing Keystore

### Using Android Studio (Recommended):

1. Open Android Studio
2. Open the project:
   ```bash
   cd frontend
   npx cap open android
   ```

3. Wait for Gradle sync to complete

4. Go to: **Build** → **Generate Signed Bundle / APK**

5. Select **Android App Bundle** (AAB)

6. Click **Create new...** under Key store path

7. Fill in the details:
   ```
   Key store path: C:\Users\udgar\commute-learn-keystore.jks
   Password: [CREATE STRONG PASSWORD - SAVE THIS!]
   Confirm Password: [SAME PASSWORD]

   Alias: commute-learn
   Password: [ALIAS PASSWORD - SAVE THIS!]
   Confirm: [SAME PASSWORD]

   Validity (years): 25
   Certificate:
     First and Last Name: Commute Learn Team
     Organizational Unit: Development
     Organization: Commute Learn
     City or Locality: [Your City]
     State or Province: [Your State]
     Country Code: IN
   ```

8. Click **OK**

9. ⚠️ **CRITICAL:** Save these passwords securely!
   - Key store password
   - Key alias: commute-learn
   - Alias password
   - Keystore file path

### Alternative: Using Command Line

```bash
cd commute-learn

keytool -genkey -v -keystore commute-learn-keystore.jks \
  -alias commute-learn \
  -keyalg RSA \
  -keysize 2048 \
  -validity 9125 \
  -storepass YOUR_KEYSTORE_PASSWORD \
  -keypass YOUR_KEY_PASSWORD \
  -dname "CN=Commute Learn Team, OU=Development, O=Commute Learn, L=YourCity, ST=YourState, C=IN"
```

---

## Step 2: Configure Signing in Gradle

Create a file `frontend/android/keystore.properties`:

```properties
storeFile=C:\\Users\\udgar\\commute-learn-keystore.jks
storePassword=YOUR_KEYSTORE_PASSWORD
keyAlias=commute-learn
keyPassword=YOUR_KEY_PASSWORD
```

⚠️ **Add to .gitignore** (already done):
```
android/keystore.properties
*.jks
*.keystore
```

---

## Step 3: Update build.gradle for Release Signing

The signing configuration is already set up. If you need to verify, check:

`frontend/android/app/build.gradle` should have:

```gradle
android {
    ...
    signingConfigs {
        release {
            // Read from keystore.properties
            def keystorePropertiesFile = rootProject.file("keystore.properties")
            if (keystorePropertiesFile.exists()) {
                def keystoreProperties = new Properties()
                keystoreProperties.load(new FileInputStream(keystorePropertiesFile))

                storeFile file(keystoreProperties['storeFile'])
                storePassword keystoreProperties['storePassword']
                keyAlias keystoreProperties['keyAlias']
                keyPassword keystoreProperties['keyPassword']
            }
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

---

## Step 4: Build Release AAB (Android App Bundle)

### Option A: Using Android Studio

1. In Android Studio: **Build** → **Generate Signed Bundle / APK**
2. Select **Android App Bundle**
3. Click **Next**
4. Choose your keystore file
5. Enter passwords
6. Select **release** build variant
7. Click **Finish**
8. Wait for build (2-5 minutes)
9. Click **locate** when done
10. Find AAB at: `frontend/android/app/build/outputs/bundle/release/app-release.aab`

### Option B: Using Gradle Command Line

```bash
cd frontend/android

# Build the AAB
./gradlew bundleRelease

# Or on Windows:
gradlew.bat bundleRelease
```

Output will be at:
```
frontend/android/app/build/outputs/bundle/release/app-release.aab
```

---

## Step 5: Build Release APK (Optional - for testing)

If you want to test the release APK before submitting:

```bash
cd frontend/android

# Build release APK
./gradlew assembleRelease

# Or on Windows:
gradlew.bat assembleRelease
```

Output at: `frontend/android/app/build/outputs/apk/release/app-release.apk`

**Test this APK on a real device before Play Store submission!**

---

## Step 6: Verify the AAB

```bash
# Get AAB info
bundletool build-apks --bundle=app-release.aab --output=app.apks

# Or check file size (should be 3-5 MB)
ls -lh app-release.aab
```

---

## Step 7: Play Store Submission Checklist

### Before Uploading:

- [ ] Privacy policy is live and accessible
- [ ] Backend is deployed and working
- [ ] Test the release APK on real device
- [ ] All features working (upload, process, play, download)
- [ ] No crashes or bugs
- [ ] Screenshots prepared (1080x1920, 2-8 images)
- [ ] Feature graphic created (1024x500)
- [ ] App icon looks good
- [ ] Keystore safely backed up (CRITICAL!)
- [ ] Passwords saved in password manager

### Upload to Play Store:

1. Go to: https://play.google.com/console
2. Click **Create app**
3. Fill in app details:
   - App name: Commute & Learn
   - Default language: English (India)
   - App or game: App
   - Free or paid: Free
4. Accept declarations
5. Create app
6. Complete all required sections:
   - App content
   - Store listing
   - Main store listing
   - Pricing & distribution
7. Upload AAB file to **Production** or **Internal testing**
8. Fill in release notes
9. Submit for review

---

## Step 8: What Happens After Submission

1. **Review Process:** 1-7 days
2. **Status:** Check Play Console for updates
3. **Possible Outcomes:**
   - ✅ Approved → App goes live!
   - ⚠️ Needs changes → Fix and resubmit
   - ❌ Rejected → Address issues and resubmit

---

## Important Files to Keep Safe

### Must Keep Forever:
```
commute-learn-keystore.jks          # Keystore file
keystore-passwords.txt              # Passwords (encrypted)
```

### Must Not Commit to Git:
```
*.jks
*.keystore
keystore.properties
*passwords.txt
```

---

## Updating the App Later

When you want to release an update:

1. Update version in `frontend/android/app/build.gradle`:
   ```gradle
   versionCode 2           // Increment by 1
   versionName "1.2.0"     // Update version
   ```

2. Rebuild and sync:
   ```bash
   cd frontend
   npm run cap:build
   ```

3. Build new AAB:
   ```bash
   cd android
   ./gradlew bundleRelease
   ```

4. Upload to Play Console → Create new release

---

## Common Issues & Solutions

### Issue: "Upload failed - signature mismatch"
**Solution:** You must use the SAME keystore for all updates. Never lose the keystore!

### Issue: "Missing privacy policy"
**Solution:** Ensure privacy policy URL is accessible and linked in Play Console

### Issue: "App crashes on startup"
**Solution:** Test the release APK first, check ProGuard rules if needed

### Issue: "Bundle too large"
**Solution:** Check that code shrinking is enabled (minifyEnabled true)

---

## Testing the Release Build

Before submitting, test the release APK:

```bash
# Install release APK on device
adb install frontend/android/app/build/outputs/apk/release/app-release.apk

# Check logs
adb logcat | grep CommuteLearn

# Test all features:
# 1. Upload PDF/image
# 2. Process file
# 3. Play audio
# 4. Download MP3
# 5. Library management
```

---

## Backup Strategy

1. **Keystore File:**
   - Keep 3 copies: Local, Cloud (encrypted), USB drive
   - Never commit to GitHub
   - Store passwords in password manager (1Password, LastPass, etc.)

2. **AAB Files:**
   - Keep all release AABs archived
   - Name format: `commute-learn-v1.1.0-release.aab`

---

## Need Help?

- Play Console Help: https://support.google.com/googleplay/android-developer
- Android Developers: https://developer.android.com/studio/publish
- Stack Overflow: Tag `android-app-bundle`

---

## Quick Reference Commands

```bash
# Build React app
cd frontend
npm run build

# Sync with Android
npx cap sync android

# Open in Android Studio
npx cap open android

# Build release AAB (in android directory)
./gradlew bundleRelease

# Build release APK (for testing)
./gradlew assembleRelease

# List connected devices
adb devices

# Install release APK
adb install -r app-release.apk
```

---

**Good luck with your Play Store submission! 🚀**
