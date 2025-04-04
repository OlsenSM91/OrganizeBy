# 📁 OrganizeBy

**OrganizeBy** is a web-based image sorting tool that allows users to upload a `.csv` and corresponding images, automatically organizing them into folders based on team/label columns and returning a ZIP archive of the sorted output.

Ideal for photographers, schools, sports teams, and event managers who need to group photos based on identifiers like team names, class periods, or other custom tags.

---

## 🚀 Features

- 📤 Drag & drop or form-based file upload
- 📁 Automatically organizes images into subfolders using `.csv` data
- 📦 Zipped download of sorted images
- 🔐 Secure file handling with server-side extension validation
- ⚡ FastAPI + Jinja2 + JavaScript (Fully responsive)
- 🧹 Automated cleanup of expired uploads after user-defined retention (1–3 days)

---

## 🖼 Example Workflow

1. Upload a CSV with columns like `Team` and `Photo`
2. Upload the image files mentioned in the CSV
3. Choose how long the uploads should persist (max 3 days)
4. Click “Upload & Sort”
5. Get a ZIP file back with folders like:
   ```
   TeamA/
     img001.jpg
   TeamB/
     img045.jpg
     img046.jpg
   ```

---

## 🛠 Technologies

- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- Vanilla JavaScript for drag-and-drop + progress bars
- Cron jobs for automated cleanup & SSL renewal
- Nginx + Certbot for HTTPS support

---

## 🧪 Development

Start the app:

```bash
./run.sh
```

Cleanup expired uploads manually:

```bash
python3 app/cleanup.py
```

---

## 🧱 Directory Structure

```
OrganizeBy/
├── app/
│   ├── main.py
│   ├── cleanup.py
│   └── uploads/
├── static/
│   ├── favicon.ico
│   └── logo.png
├── templates/
│   └── index.html
├── run.sh
└── README.md
```

---

## 🔐 Security Notes

- Only files with the following extensions are accepted:
  - `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.psd`, `.pdf`
  - `.csv` for metadata input
- File names are preserved, but sanitized server-side
- ZIPs and sessions are deleted based on user-set retention (max 3 days)
- Upload directory is kept outside public static serving

---

## 📅 Cron Setup (for production)

| Task              | Command                                                           | Schedule |
|-------------------|--------------------------------------------------------------------|----------|
| SSL Renewal       | `certbot renew --quiet --post-hook "systemctl reload nginx"`       | Daily @ 2AM |
| Cleanup expired   | `python3 app/cleanup.py`                                           | Daily @ 1AM |
| Start on boot     | `systemctl enable --now organizeby`                                | On reboot |

---

## 🙌 Author

**Steven Olsen**  
🛠 Built with ❤️ by [Steven Olsen](https://gandh.dev)
