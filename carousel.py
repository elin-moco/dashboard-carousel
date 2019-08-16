import time
import settings
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from argparse import ArgumentParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from datetime import datetime,timedelta


def get_arg_parser():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fullscreen",
        default=True,
        action="store_true",
        help="The ETL task to run.",
    )
    parser.add_argument(
        "--elem-wait",
        type=int,
        default=10,
        help="Seconds to wait for elements.",
    )
    parser.add_argument(
        "--rotate-wait",
        type=int,
        default=10,
        help="Seconds to wait for carousel rotation.",
    )
    parser.add_argument(
        "--load-wait",
        type=int,
        default=10,
        help="Seconds to wait for page load.",
    )
    parser.add_argument(
        "--reload-time",
        type=int,
        default=9,
        help="Day of hour to reload all charts.",
    )
    parser.add_argument(
        "--login-time",
        type=int,
        default=30,
        help="Seconds wait for manual login.",
    )
    return parser


class DashboardCarousel:

    def __init__(self, charts, wait_sec, fullscreen, reload_hour, login_time, load_wait):
        self.charts = [x for x in charts if 'disabled' not in x or not x['disabled']]
        self.browser = Firefox()
        if fullscreen:
            self.browser.fullscreen_window()
        self.actions = ActionChains(self.browser)
        self.wait = WebDriverWait(self.browser, wait_sec)
        self.reload_hour = reload_hour
        self.last_reload = datetime.now()
        self.load_wait = load_wait
        self.logins = []
        self.login_time = login_time
        self.open_charts()

    def open_charts(self):
        first = True
        for chart in self.charts:
            if not first:
                self.browser.execute_script('window.open("about:blank", "_blank")')
                self.browser.switch_to.window(self.browser.window_handles[-1])
            login = False
            if 'login' in chart and chart['login'] and chart['site'] not in self.logins:
                self.logins += [chart['site']]
                login = True
            self.config_chart(chart, login)
            first = False

    def reload_charts(self):
        for index, chart in enumerate(self.charts):
            self.browser.switch_to.window(self.browser.window_handles[index])
            self.browser.refresh()
            self.config_chart(chart)
        self.last_reload = datetime.now()

    def config_chart(self, chart, login=False):

        if chart['site'] == 'adjust':
            current_date = datetime.today()
            prev_month = current_date - timedelta(days=30)
            url = chart['url'].format(prev_month.strftime('%Y-%m-%d'), current_date.strftime('%Y-%m-%d'))
        else:
            url = chart['url']

        self.browser.get(url)

        if login:
            # manual login
            time.sleep(self.login_time if 'login_wait' not in chart else chart['login_wait'])
            self.browser.get(url)

        time.sleep(self.load_wait)

        self.browser.execute_script('document.title="{}";'.format(chart['title']))

        if chart['site'] == 'surveygizmo':
            self.browser.execute_script(
                'var i= 0;var ids=[];'
                'for (var row of document.getElementsByClassName("report-row")) {ids.push(row.id);};'
                'setInterval(function(){if (i>=ids.length){i=0};window.location="#"+ids[i];i++;}, 4000)')

        if chart['site'] == 'gplay-console':
            hamburger = self.wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, '#gwt-uid-76')))
            hamburger.click()

        if chart['site'] == 'gplay':
            filter_select = self.wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, '.ry3kXd')))
            filter_select.click()
            filter_option = self.wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, '.OA0qNb > :first-child')))
            filter_option.click()

            self.browser.execute_script(
                'setInterval(function(){'
                'if((window.scrollMaxY-window.scrollY)<300){window.scroll(0,0);};window.scrollByLines(1);}, 100);')

        if chart['site'] == 'redash' and 'filter' in chart:
            country_select = self.wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, '.filters-wrapper .ant-select-enabled')))
            country_select.click()
            country_option = self.wait.until(
                ec.visibility_of_element_located(
                    (By.XPATH, '//li[contains(@class, "ant-select-dropdown-menu-item") and text() = "{}"]'
                     .format(chart['filter'][0]))))
            country_option.click()

        if 'scroll' in chart:
            self.browser.execute_script('window.scroll({}, {});'.format(chart['scroll'][0], chart['scroll'][1]))

        # doesn't work in Firefox
        if 'zoom' in chart:
            self.browser.execute_script('document.body.style.zoom="{};"'.format(chart['zoom']))

    def autorotate(self, secs):
        while True:
            for i, handle in enumerate(self.browser.window_handles):
                self.browser.switch_to.window(handle)
                time.sleep(secs if 'rotate_wait' not in self.charts[i] else self.charts[i]['rotate_wait'])
            current_time = datetime.now()
            if current_time.hour == self.reload_hour and (current_time - self.last_reload).seconds > (12 * 60 * 60):
                self.reload_charts()

    def shutdown(self):
        self.browser.quit()


def main():
    args = get_arg_parser().parse_args()
    carousel = DashboardCarousel(settings.CHARTS,
                                 wait_sec=args.elem_wait,
                                 fullscreen=args.fullscreen,
                                 reload_hour=args.reload_time,
                                 login_time=args.login_time,
                                 load_wait=args.load_wait)
    carousel.autorotate(args.rotate_wait)
    carousel.shutdown()


if __name__ == "__main__":
    main()