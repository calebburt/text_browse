import url
import browser

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        b = browser.Browser()
        b.new_tab(url.URL(input("Enter URL: ")))
        b.loop()
    else:
        b = browser.Browser()
        b.new_tab(url.URL(sys.argv[1]))
        b.loop()