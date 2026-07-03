import url
import browser

if __name__ == "__main__":
    import sys
    b = browser.Browser()
    b.load(url.URL(sys.argv[1]))
    b.loop()