# dashboard-carousel

A browser automation script to automate webpage-based dashboards presentation and rotation on big screens.
I created this project to put some important charts from various sources (Redash, Google Play, Adjust, etc...) on a TV screen in our office.

## Prerequisites
- [Python3](https://www.python.org/downloads/)
- Latest version of [geckodriver](https://github.com/mozilla/geckodriver/releases) 
- And latest [Firefox](https://www.mozilla.org/firefox/new/)

## Getting Started
1. Install depencies `pip install -r requirement.txt`
2. Put chart links and configs in `settings.py` (copy from `settings.py.sample`).
3. Run `python carousel.py`
4. Manually login whenever required
5. Voila! Now the charts will automatically rotates on the screen, and refresh every day!
