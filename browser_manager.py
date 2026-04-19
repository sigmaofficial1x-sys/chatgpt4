from pathlib import Path
from typing import Optional


def launch_profile_browser(data_dir: str, proxy_ip: Optional[str] = None, login_mode: bool = False) -> None:
    """Launch an undetected Chrome session bound to a dedicated user-data directory.

    The browser stays open for manual interaction. When the user closes the browser,
    Chrome persists cookies and storage in the provided data_dir.
    """
    try:
        import undetected_chromedriver as uc
    except ImportError as exc:
        raise RuntimeError(
            "undetected_chromedriver is required. Install with: pip install undetected-chromedriver"
        ) from exc

    profile_path = Path(data_dir)
    profile_path.mkdir(parents=True, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path.resolve()}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    if proxy_ip:
        options.add_argument(f"--proxy-server={proxy_ip}")

    driver = uc.Chrome(options=options)
    target_url = "https://www.instagram.com/accounts/login/" if login_mode else "https://www.instagram.com/"
    driver.get(target_url)

    try:
        input("Browser launched. Complete actions, then close browser and press Enter to continue...")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
