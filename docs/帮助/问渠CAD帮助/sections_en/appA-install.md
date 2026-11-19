---
id: appA
title: Appendix A Installing WenQuest CAD
lead: One installer for Windows 10 / 11 (64-bit); ready to use when it finishes. The beta needs a one-year beta licence code (free for registered users).
---

### Download and licence {#appA-dl}

On the website's Downloads page (wenquestrobotics.com/download): sign in, click “Get a one-year beta licence” and copy the code; download the WenQuest CAD installer (about 1 GB).

### Install {#appA-install}

<ol class="steps">
<li>Run the installer. Windows may say “Windows protected your PC / unknown publisher” (the beta has no code-signing certificate): click <b>More info → Run anyway</b>.</li>
<li>Choose a language → accept the licence → choose a folder (the default is fine) → Install, about 3–5 minutes.</li>
<li>Double-click “WenQuest CAD” on the desktop. On first start a box asks for the licence code (for the WenQuest workbenches such as AI Parts); paste it and click OK — it is not asked again. Without a code FreeCAD itself still works, the WenQuest workbenches just do not load.</li>
<li>The first start also shows a Welcome page: choose English, unit system “Standard (mm, kg, s)” and navigation style “CAD” (this course always uses CAD).</li>
</ol>

### Troubleshooting {#appA-fix}

- **Nothing happens on double-click**: Windows Smart App Control may be blocking it (Windows Security → App &amp; browser control). On a company PC ask your administrator.
- **Antivirus warning**: the beta is not code-signed and some antivirus products report it by mistake; check the installer against the SHA-256 on the download page.
- **Interface in the wrong language**: Edit → Preferences → General → Language, then restart.
