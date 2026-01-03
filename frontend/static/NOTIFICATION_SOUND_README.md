# 🔔 Kitchen Notification Sound

## Custom Notification Sound (Optional)

Jika ingin menggunakan custom notification sound (MP3/WAV) daripada beep bawaan:

### Steps:

1. **Siapkan Audio File**
   - Format: MP3, WAV, atau OGG
   - Durasi: 1-3 detik (tidak terlalu panjang)
   - Volume: Sudah normalized (tidak terlalu keras/pelan)
   - Contoh nama: `notification.mp3`

2. **Copy ke Folder Static**
   ```
   frontend/static/notification.mp3
   ```

3. **System akan otomatis fallback ke audio file jika ada**
   - Priority 1: Web Audio API (5 beeps - always works)
   - Priority 2: notification.mp3 (jika file ada)

### Recommended Audio Properties:

- **Format**: MP3 (best compatibility)
- **Bitrate**: 128 kbps
- **Sample Rate**: 44.1 kHz
- **Duration**: 1-2 seconds
- **Characteristics**: 
  - Clear, attention-grabbing
  - Not too loud or annoying
  - Professional tone
  - Quick fade out

### Example Sources for Notification Sounds:

1. **Freesound.org** (Free, requires attribution)
   - Search: "kitchen bell", "ding", "notification"
   
2. **ZapSplat** (Free for personal/commercial use)
   - https://www.zapsplat.com/
   
3. **Mixkit** (Free, no attribution required)
   - https://mixkit.co/free-sound-effects/notification/

4. **Record Your Own**
   - Use kitchen timer sound
   - Use service bell sound
   - Use phone notification sound

### Testing:

1. Add your `notification.mp3` to `frontend/static/`
2. Restart frontend container
3. Open kitchen display
4. Create test order
5. Should hear your custom sound

### Current Sound (Default):

Jika tidak ada file `notification.mp3`, system menggunakan:
- **Web Audio API**: 5 beeps sequence
- **Frequencies**: 800Hz → 1000Hz → 800Hz → 1000Hz → 1200Hz
- **Duration**: ~1 second total
- **Volume**: 30% (0.3)

Sudah optimized untuk perhatian maksimal tanpa mengganggu!

---

**Note**: Web Audio API beeps will always play first (lebih reliable). Audio file adalah fallback untuk browser yang tidak support Web Audio API (very rare).
