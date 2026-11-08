# Desktop Wallpaper Architecture & Curation Standards

## 1. Hardware Context & Display Specifications
- **Display Resolution:** 1440p QHD (`2560x1440`).
- **Slideshow Directory:** `E:\Onedrive\OneDrive - yui high school\Pictures\Latest Wallpaper`.
- **Slideshow Management Rule:** Never alter Windows Personalization slideshow settings (interval, shuffle, mode) unless explicitly requested. All wallpapers must reside flat in the target directory for seamless Windows rotation and OneDrive cloud synchronization.

---

## 2. Quality & Resolution Governance
- **Strict Resolution Floor:** Minimum `2560x1440` (1440p). Wallpapers in 4K (`3840x2160`), 5K (`5120x2880`), and 8K are preferred.
- **Substandard File Elimination:** Any wallpapers with dimensions `< 2560x1440` (e.g. 1080p, 1200p) must be pruned from the folder to prevent blurry rendering on the 1440p panel.
- **Upscaling Standard:** For clean vector art or stylized pixel art (e.g. Patapon, Dave the Diver), apply high-quality Lanczos resampling (`Image.Resampling.LANCZOS`) with center-crop to exactly `2560x1440`.
- **Encoding Standard:** Save as high-fidelity JPEG (`quality=96`, `subsampling=0`, RGB color space) to maintain virtually lossless image quality while keeping individual file sizes reasonable (1–4 MB) for OneDrive background syncing.

---

## 3. Game Catalog & Aesthetic Preferences
The user maintains a curated 10-wallpaper collection per game across 8 favorite titles:

1. **Total War: Warhammer 3 (`TW_Warhammer_3_Wallpaper_##.jpg`):**
   - Epic battlegrounds, faction art, Legendary Lords, Warhammer fantasy landscapes (2K to 6K native).
2. **Red Dead Redemption 2 (`RDR2_Wallpaper_##.jpg`):**
   - Natural scenery, open frontier landscapes, Grizzlies mountains, campfire, Arthur Morgan riding horse in nature.
   - *Negative Constraint:* Strictly avoid generic red-background promo posters or monotonous silhouette teaser art.
3. **Euro Truck Simulator 2 (`ETS2_Wallpaper_##.jpg`):**
   - Scenic European highway routes, mountain passes, customized Scania/Volvo trucks (4K to 8K native).
4. **American Truck Simulator (`ATS_Wallpaper_##.jpg`):**
   - Scenic Western American highways, desert vistas, Peterbilt/Kenworth rigs on open asphalt.
   - *Negative Constraint:* Strictly avoid in-game UI menus, configuration screens, or trailer purchase interfaces.
5. **Warhammer 40,000: Space Marine 2 (`Space_Marine_2_Wallpaper_##.jpg`):**
   - Titus, Ultramarines, Tyranid/Chaos battles, grimdark gothic architecture (4K to 5K native).
6. **Cult of the Lamb (`Cult_of_the_Lamb_Wallpaper_##.jpg`):**
   - Vibrant cult rituals, dark whimsical fanart, boss battles, community illustrations (4K native).
7. **Dave the Diver (`Dave_the_Diver_Wallpaper_##.jpg`):**
   - Blue hole undersea exploration, coral reefs, Bancho sushi bar, marine wildlife, serene pixel art.
   - *Negative Constraint:* Strictly avoid images with giant yellow "DAVE THE DIVER" title logos plastered across the center.
8. **Patapon 1 & Patapon 2 (`Patapon_Wallpaper_##.jpg`):**
   - Iconic rhythm-tribal silhouette artwork, crisp remastered vectors, drum god marches (2K QHD).

---

## 4. Ingestion Pipelines & Source Repositories
- **Wallhaven API:**
  - Endpoint: `https://wallhaven.cc/api/v1/search?q={query}&atleast=2560x1440&sorting=favorites`
  - High fidelity source for RDR2 scenery, Warhammer 40k, Total War, and ETS2.
- **SCS Software Official Press Kits:**
  - Endpoints: `https://scssoft.com/press/sheet.php?p=american_truck_simulator` and `euro_truck_simulator_2`
  - Direct access to uncompressed, original marketing captures (`/images/###.jpg`) in native 2560x1440 and 4K without watermarks.
- **WallpaperCave Scraper:**
  - Required headers: `User-Agent` + `Referer: https://wallpapercave.com/`.
  - Automated yellow-pixel threshold analysis (`R>200, G>180, B<90` in center frame) to filter out title-card watermarks before saving.
- **Alpha Coders (Wallpapers Abyss):**
  - High resolution pixel art and game illustrations (`https://images#.alphacoders.com/.../thumb-1920-###.ext`).
