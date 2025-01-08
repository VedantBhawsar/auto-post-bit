import instaloader
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import schedule

# Configuration
SOURCE_USERNAME = "source_account_username"  
TARGET_USERNAME = "techno475"     
TARGET_PASSWORD = "technoserver"     
DOWNLOAD_FOLDER = "instagram_videos/"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_latest_video():
    """
    Downloads the latest post (video) from the source account.
    """
    try:
        loader = instaloader.Instaloader(download_videos=True, save_metadata=False)
        loader.download_post(instaloader.Profile.from_username(loader.context, SOURCE_USERNAME).get_posts().__next__(), DOWNLOAD_FOLDER)
        print("Video downloaded successfully.")
    except Exception as e:
        print(f"Error downloading video: {e}")


def post_to_instagram():
    """
    Logs in to Instagram and posts the downloaded video using Selenium.
    """
    try:
        # Initialize WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Log in to Instagram
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        driver.find_element(By.NAME, "username").send_keys(TARGET_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(TARGET_PASSWORD)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)

        # Find the latest video to upload
        video_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.mp4')]
        if not video_files:
            print("No videos to post.")
            driver.quit()
            return

        latest_video = os.path.join(DOWNLOAD_FOLDER, video_files[0])

        # Navigate to the upload page
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        upload_button = driver.find_element(By.CSS_SELECTOR, "svg[aria-label='New Post']")
        upload_button.click()
        time.sleep(3)

        # Select and upload the video
        driver.find_element(By.XPATH, "//input[@type='file']").send_keys(latest_video)
        time.sleep(5)

        # Add a caption
        caption = "Reposting the latest video! #automation #bot"
        caption_area = driver.find_element(By.XPATH, "//textarea")
        caption_area.send_keys(caption)
        time.sleep(2)

        # Share the post
        share_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Share')]")
        share_button.click()
        time.sleep(5)

        print("Video posted successfully!")
        driver.quit()

        # Clean up the posted video
        os.remove(latest_video)
    except Exception as e:
        print(f"Error posting video: {e}")

# Step 3: Automate Daily Task
def daily_task():
    """
    Automates the daily process of downloading and posting a video.
    """
    download_latest_video()
    post_to_instagram()

# Schedule the task
schedule.every().day.at("10:00").do(daily_task)

print("Bot is running...")
while True:
    schedule.run_pending()
    time.sleep(1)
