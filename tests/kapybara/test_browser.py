from kapybara.browserlib.custom_browser import create_browser
import time


def test_browser():
    driver = create_browser()

    time.sleep(5)

    driver.quit()


if __name__ == "__main__":
    test_browser()
