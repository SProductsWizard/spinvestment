from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import copy
from config import FinsightNIURL, HrefSubassetClassDict
from webdriver_manager.chrome import ChromeDriverManager


class ABSScrap:
    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def _waitGetElement(self, xpath, plural=False):

        try:
            el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        xpath,
                    )
                )
            )
            if plural:
                el = self.driver.find_elements(By.XPATH, xpath)

        except TimeoutException:
            # Check for the table again after a certain amount of time
            time.sleep(5)
            if plural:
                el = self.driver.find_elements(By.XPATH, xpath)
            else:
                el = self.driver.find_element_by_xpath(xpath)
        return el

    def runScrapBond(self, urlAssetClass="RMBS", cutDate=""):
        cutDate = pd.Timestamp.today() if cutDate == "" else pd.to_datetime(cutDate)

        df_list = []
        self.driver.get(FinsightNIURL[urlAssetClass])

        table = self._waitGetElement(
            xpath=r"/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/div[3]/table"
        )

        cell = self.driver.find_element_by_xpath(
            r"/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/div[4]/div[2]/div[2]/div/div[2]/input"
        )
        prev_df = pd.DataFrame()
        df = None
        page_num = 1

        # we will scarpe the first page anyways but if pricing date of a page <today, we stop getting the next page

        while df is None or not prev_df.equals(df):  # break when no new pages
            if df is not None:
                prev_df = copy.deepcopy(df)

            cell.send_keys(Keys.CONTROL + "a")  # works for Windows
            cell.send_keys(Keys.DELETE)

            cell.send_keys(Keys.COMMAND + "a")  # handle MacOS
            cell.send_keys(Keys.DELETE)

            cell.send_keys(page_num)
            cell.send_keys(Keys.RETURN)
            time.sleep(3)

            # Get the HTML content of the page
            html_content = self.driver.page_source

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            table = soup.find("table")
            html_string = str(table)
            df = pd.read_html(html_string)[0]
            df_list.append(df)
            last_date = pd.Timestamp(df["Pricing Date"].iloc[-1])
            if last_date < cutDate:
                break
            page_num += 1

        self.driver.close()
        df_total = pd.concat(df_list, ignore_index=True)

        return df_total

    def runScrapDeal(self, cutDate=""):
        cutDate = pd.Timestamp.today() if cutDate == "" else pd.to_datetime(cutDate)
        self.driver.get(FinsightNIURL["ABSDeal"])

        datesElements = self._waitGetElement(
            r"//div[contains(@class, 'dealCardItem')]//span[contains(@class, 'date')]",
            plural=True,
        )
        minIssueDateDisplayed = datesElements[-1].get_attribute("innerHTML")

        minIssueDateDisplayed_datetime = pd.to_datetime(minIssueDateDisplayed)

        while minIssueDateDisplayed_datetime > cutDate:
            moreWrapper = self._waitGetElement(
                r"//a[contains(@class, 'dealsList_moreBtn')]"
            )
            self.driver.execute_script("arguments[0].click();", moreWrapper)
            time.sleep(3)
            datesElements = self._waitGetElement(
                r"//div[contains(@class, 'dealCardItem')]//span[contains(@class, 'date')]",
                plural=True,
            )
            minIssueDateDisplayed = datesElements[-1].get_attribute("innerHTML")
            minIssueDateDisplayed_datetime = pd.to_datetime(minIssueDateDisplayed)

        dealName = [
            el.get_attribute("innerHTML")
            for el in self.driver.find_elements(
                By.XPATH,
                f"(//div[contains(@class, 'dealCardItem')]//div[1]/div[1]/div[4]/span[1]/span[1]/a[1])",
            )
        ]

        dealSector = [
            el.get_attribute("innerHTML")
            for el in self.driver.find_elements(
                By.XPATH,
                f"(//div[contains(@class, 'dealCardItem')]//div[1]/div[1]/div[2]/span[1]/span[1]/a[1])/div[1]",
            )
        ]

        dealHref = [
            el.get_attribute("href")
            for el in self.driver.find_elements(
                By.XPATH,
                f"(//div[contains(@class, 'dealCardItem')]//div[1]/div[1]/div[2]/span[1]/span[1]/a[1])",
            )
        ]

        dealPricingDate = [
            el.get_attribute("innerHTML")
            for el in self.driver.find_elements(
                By.XPATH,
                f"//div[contains(@class, 'dealCardItem')]//span[contains(@class, 'date')]",
            )
        ]

        dealIssuerName = [
            el.get_attribute("innerHTML")
            for el in self.driver.find_elements(
                By.XPATH,
                f"(//div[contains(@class, 'dealCardItem')]//div[1]/div[1]/div[5]/a[1])",
            )
        ]

        niDealDf = pd.DataFrame(
            {
                "Deal Name": dealName,
                "Sector": dealSector,
                "Subsector": dealHref,
                "Issuer Name": dealIssuerName,
                "Pricing Date": dealPricingDate,
            }
        )
        niDealDf["Pricing Date"] = pd.to_datetime(niDealDf["Pricing Date"])
        niDealDf["Deal Name"] = niDealDf["Deal Name"].apply(lambda x: x.split("(")[0])
        niDealDf["Deal Name"] = niDealDf["Deal Name"].str.strip()
        niDealDf["Subsector"] = niDealDf["Subsector"].apply(
            lambda x: HrefSubassetClassDict[x]
        )

        self.driver.close()

        return niDealDf
