from pathlib import Path
import yaml
from phis_login.LoginPage import LoginPage
from kapybara import CustomBrowser, WebDriver

CONF = Path(__file__).parent / 'default.yaml'


def test_main():
    driver: WebDriver = CustomBrowser()

    config_text = CONF.read_text(encoding='utf8')
    config = yaml.safe_load(config_text)

    driver.get(config['base_url'])

    workflow = config.get('workflow', [])
    if not workflow:
        raise ValueError('Workflow is empty or not defined in the configuration.')

    for action in workflow:
        key = action.keys()[0]
        if key != 'page':
            continue
        page_name = action['page']

        if page_name == 'login_page':
            args = {
                'args': action['args'],
                'wait': action.get('wait', 1),
                'check': action.get('check', ''),
                'retry': action.get('retry', 3),
                'then': action.get('then', []),
            }
            locators = config.get('locators', {}).get(page_name, {})
            page = LoginPage(locators, args)
            page.login()

            pass
    pass


if __name__ == '__main__':
    test_main()
