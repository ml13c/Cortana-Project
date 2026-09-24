import subprocess
import os
import signal

CHROMIUM_PATH = "/usr/bin/chromium"
browser_process = None
SITES = {
    "youtube": "https://www.youtube.com",
    "gemini": "https://gemini.google.com/app"
}


def open_site(site):
    global browser_process
    site = site.lower()
    
    if site not in SITES:
        print("Unknown site:", site)
        return
    
    # close other cortana browser
    close_browser()
    url = SITES[site]
    print(f"Opening {site}: {url}")

    browser_process = subprocess.Popen(
        [
            CHROMIUM_PATH,
            # Fullscreen Chromium browser
            "--start-fullscreen",
            # Match your 800x480 screen commented out FOR NOW
           # "--window-size=800,480",
            #"--window-position=0,0",
            # Keep Chromium startup cleaner
            "--no-first-run",
            "--noerrdialogs",
            "--disable-session-crashed-bubble",
            url
        ],
        start_new_session=True
    )


def close_browser():
    global browser_process

    if browser_process is None:
        return

    try:
        os.killpg(
            os.getpgid(browser_process.pid),
            signal.SIGTERM
        )

        browser_process.wait(timeout=3)

    except Exception as e:
        print("Error closing browser:", e)

    browser_process = None
    print("Browser closed")