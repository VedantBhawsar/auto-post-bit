import os
import time
import instaloader
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from instabot import Bot  

bot = Bot()
bot.login()


# Configuration
SOURCE_USERNAME = "kaccha.limboo"
TARGET_USERNAME = "addective_coder"
TARGET_PASSWORD = "Technoserver885@"
DOWNLOAD_FOLDER = "instagram_videos"


def download_latest_video():
    """
    Downloads the latest video from the source Instagram account.
    """
    try:
        loader = instaloader.Instaloader(download_videos=True, save_metadata=False)
        profile = instaloader.Profile.from_username(loader.context, SOURCE_USERNAME)
        latest_post = next(profile.get_posts())
        loader.download_post(latest_post, DOWNLOAD_FOLDER)
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
        # options.add_argument("--headless")  # Uncomment for headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Log in to Instagram
        driver.get("https://www.instagram.com/accounts/login/")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").send_keys(TARGET_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(TARGET_PASSWORD)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)  # Give some time for login to complete

        # Click the "New Post" button
        try:
            print("Waiting for 'New Post' button...")
            upload_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='New Post']"))
            )
            upload_button.click()
        except Exception as e:
            print("Error clicking 'New Post' button:", e)
            driver.quit()
            return

        # Wait for the file upload input field to appear
        try:
            print("Waiting for file upload input...")
            video_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
        except Exception as e:
            print("Error locating file upload input:", e)
            driver.quit()
            return

        # Find the latest video to upload
        video_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.mp4')]
        if not video_files:
            print("No videos to post.")
            driver.quit()
            return

        latest_video = os.path.join(DOWNLOAD_FOLDER, video_files[0])

        # Upload the video
        print(f"Uploading video: {latest_video}")
        video_input.send_keys(latest_video)
        time.sleep(5)  # Wait for the upload to complete

        # Add a caption to the post
        caption = "Reposting the latest video! #automation #bot"
        try:
            print("Adding caption...")
            caption_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea"))
            )
            caption_area.send_keys(caption)
        except Exception as e:
            print("Error adding caption:", e)
            driver.quit()
            return

        # Share the post
        try:
            print("Sharing the post...")
            share_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Share')]"))
            )
            share_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your post was shared')]"))
            )
        except Exception as e:
            print("Error posting the video:", e)

        print("Video posted successfully!")
        driver.quit()

        # Clean up the uploaded video
        os.remove(latest_video)
    except Exception as e:
        print(f"Error posting video: {e}")
        driver.quit()


def daily_task():
    """
    Automates the process of downloading and posting a video every day.
    """
    print("Starting daily task...")
    download_latest_video()
    post_to_instagram()


# Schedule the task to run daily at 10:00 AM
schedule.every().day.at("10:00").do(daily_task)

print("Bot is running...")
daily_task()  # Run once initially to start the process
while True:
    schedule.run_pending()
    time.sleep(1)
