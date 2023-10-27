from utility_functions import get_config
from Scraper import ScraperHLibertad


def main():
    """
    Main program
    """
    config = get_config()
    scraper = ScraperHLibertad(config)
    scraper.run()

if __name__ == "__main__":
    print("Start")
    main()
    print("End of program")