#------------------------------------------------------
# Information tool to retrieve business financials
#------------------------------------------------------

# import libraries 
# pip install spyder-notebook
import re
import requests
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
from datetime import datetime
from selenium import webdriver
import os
import pickle
import finviz

class Business:

    # Define a default constructor for the Business object
    def __init__(self, foreign, symbol, report_type, start_period, end_period ):
        self.foreign=foreign
        self.symbol=symbol
        self.report_type=report_type
        self.start_period=start_period
        self.end_period=end_period
        
    #-------------Retrieving Annual/Quarter Reports----------
    # Define a function to store the url(s) to a company's annual or quarter report(s)
    def ghost_report_url(self):
    ############## Check validity of inputs ############# 
        ## Error Message if the foreign argument is not logical 
        if (type(self.foreign)!=bool):
            raise TypeError("Invalid foreign type: foreign argument must be logical- True or False")
            
        ## Error message if the inputted ticker symbol is not a string
        if(type(self.symbol)!=str):
            raise TypeError("Invalid ticker symbol type: symbol argument must be a string")
            
        ## Error message if the inputted report type is neither 'annual' or 'quarter'
        if(self.report_type!='annual' and self.report_type!='quarter'):
            raise TypeError("Invalid report type: only 'annual' or 'quarter' report type is allowed")
            
        ## Error message if the specified start period or(and) end period is(are) not valid
        if ((len(str(self.start_period)))| (len(str(self.end_period)))!=8):
            raise ValueError("Invalid start period or(and) end period(s): start_period and end_period arguments must be in the form yyyymmdd")
            
        ## Error message to warn that foreign quarterly reports are not available on the SEC Edgar database 
        if(self.foreign==True and self.report_type=='quarter'):
            raise ValueError("Foreign quarterly report(s) not available: try 'annual' report instead")
            
        # Convert start_period and end_period inputs to a datetime object 
        start_period=datetime.strptime(str(self.start_period),"%Y%m%d").date()
        end_period=datetime.strptime(str(self.end_period),"%Y%m%d").date()
    
        ################# Retrieving Annual Report(s) (10-K or 20-F) ################
        
        if(self.report_type=='annual'):
            # Get the url to the company's historic 10-K (including 10-K/A) or 20-F (including 20-F/A) filings(s)
            historical_filings_url=r"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+self.symbol+"&type=10-k&dateb=&owner=exclude&count=100" if self.foreign==False else r"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+self.symbol+"&type=20-f&dateb=&owner=exclude&count=100"
        
            # Get table containing descriptions of the company's 10-K(include 10-K/A and others) or 20-F(include 20F/A and others) filings(s) 
            filings_description_table=pd.read_html(str(BeautifulSoup(requests.get(historical_filings_url).content,"html.parser").find("table",{"class":"tableFile2"})))[0]
            
            ## Stop and return an error message if the company has no filing type of 10-K or 20-F, given the company symbol and foreign logic
            if len(filings_description_table[(filings_description_table["Filings"]=="10-K")|(filings_description_table["Filings"]=="20-F")])==0:
                raise NameError("Invalid company symbol or(and) foreign logical")
        
            # Get the company's CIK (Central Index Key) number
            cik_number=re.search(r"(\d{10})",BeautifulSoup(requests.get(historical_filings_url).content,"html.parser").find("span",{"class":"companyName"}).text)[0]
            
            # Get a list of accession numbers of the historic 10-K or 20-F filing(s). raw_accesion_numbers because accession numbers seperated by dashes
            raw_accession_numbers=filings_description_table[(filings_description_table["Filings"]=="10-K")| (filings_description_table["Filings"]=="20-F")].Description.str.extract(r"(\d{10}\-\d{2}\-\d{6})",expand=False)
        
            # Get a list of url(s) to a company's historic 10-K or 20-F report(s) details
            filing_details_url=r"https://www.sec.gov/Archives/edgar/data/"+cik_number+r"/"+raw_accession_numbers+r"-index.html"
            filing_details_url=filing_details_url.to_list()
            
            # Get a list of url(s) to a company's 10-K or 20-F report(s) documentations
            document_details_url=r"https://www.sec.gov/cgi-bin/viewer?action=view&cik="+cik_number+"&accession_number="+raw_accession_numbers+"&xbrl_type=v"
            document_details_url=document_details_url.to_list()
            
            # Get report period(s), that is the 10-K or 20-F report(s) as of this(these) date(s)
            report_periods=[datetime.strptime(BeautifulSoup(requests.get(url).content,"html.parser").find("div",text=re.compile("Period of Report")).find_next("div").text,"%Y-%m-%d").date() for url in filing_details_url]
                
            # Get specified filing details url(s)
            filing_details_url=[filing_details_url[url] for url in range(len(report_periods)) if report_periods[url]>start_period and report_periods[url]<=end_period]
            
            # Get specified document details url(s)
            document_details_url=[document_details_url[url] for url in range(len(report_periods)) if report_periods[url]>start_period and report_periods[url]<=end_period]
            
            # Get download url(s) to the company's 10-K or 20F extracts
            annual_download_url=[]
            for url in document_details_url:
                soup=BeautifulSoup(requests.get(url).content,"html.parser").find('a', text = re.compile('View Excel Document'), attrs = {'class' : 'xbrlviewer'})
                if soup is not None:
                    annual_download_url.append(r"https://www.sec.gov"+soup['href'])
                else:
                    annual_download_url.append(None)

            # Get specified report period(s)
            report_periods=[report_periods[rp] for rp in range(len(report_periods)) if report_periods[rp]>start_period and report_periods[rp]<=end_period]
        
            # Get html table(s) of the document format files 
            tableFile=[BeautifulSoup(requests.get(url).content,"html.parser").find("table", { "summary" : "Document Format Files"}) for url in filing_details_url]
            
            # Get url(s) to the annual report html
            annual_report_url=[]
            for tab in range(len(tableFile)):
                if tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a").text.strip()!='':
                    if ".htm" in tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a").text.strip():
                        annual_report_url.append("https://www.sec.gov"+tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a")["href"].replace("/ix?doc=",""))
                    else:
                        annual_report_url.append("annual report is not in HTML format")
                else:
                    annual_report_url.append("annual report not available")
                    
            # Combine the company's report period(s), and annual report url(s) into a data frame
            annual_report_df=pd.DataFrame({'report_periods':report_periods,'annual_report_url':annual_report_url,'annual_download_url':annual_download_url},index=[self.symbol]*len(report_periods))
            
            # Return the data frame contructed above if it is not empty 
            if not annual_report_df.empty:
                return annual_report_df
            else:
                return "No annual report filing(s) for "+ self.symbol + " between "+ start_period.strftime("%Y-%m-%d")+" and "+end_period.strftime("%Y-%m-%d")
            
        ################# Retrieving Quarter Report(s) (10-Q) #########################
        if(self.report_type=='quarter'):
    
            # Get the url to the company's historic 10-Q
            historical_filings_url=r"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+self.symbol+"&type=10-q&dateb=&owner=exclude&count=100"
            
            # Get table containing descriptions of the company's 10-Q(include 10-Q/A and others) filings(s) 
            filings_description_table=pd.read_html(str(BeautifulSoup(requests.get(historical_filings_url).content,"html.parser").find("table",{"class":"tableFile2"})))[0]
            
            ## Stop and return an error message if the company has no filing type of 10-Q, given the company symbol and foreign logic
            if len(filings_description_table[filings_description_table["Filings"]=="10-Q"])==0:
                raise NameError("Invalid company symbol or(and) foreign logical")
                
            # Get the company's CIK (Central Index Key) number
            cik_number=re.search(r"(\d{10})",BeautifulSoup(requests.get(historical_filings_url).content,"html.parser").find("span",{"class":"companyName"}).text)[0]
            
            # Get a list of accession numbers of the historic 10-Q. raw_accesion_numbers because accession numbers seperated by dashes
            raw_accession_numbers=filings_description_table[filings_description_table["Filings"]=="10-Q"].Description.str.extract(r"(\d{10}\-\d{2}\-\d{6})",expand=False)
            
            # Get a list of url(s) to a company's historic 10-Q report(s) details
            filing_details_url=r"https://www.sec.gov/Archives/edgar/data/"+cik_number+r"/"+raw_accession_numbers+r"-index.html"
            filing_details_url=filing_details_url.to_list()
            
            # Get a list of url(s) to a company's 10-Q report(s) documentations
            document_details_url=r"https://www.sec.gov/cgi-bin/viewer?action=view&cik="+cik_number+"&accession_number="+raw_accession_numbers+"&xbrl_type=v"
            document_details_url=document_details_url.to_list()
            
            ## At this moment, documents before 2009 are not available. Documents of this type are not normally needed anyway
            
            # Get report period(s), that is the 10-Q report(s) as of this(these) date(s)
            report_periods=[datetime.strptime(BeautifulSoup(requests.get(url).content,"html.parser").find("div",text=re.compile("Period of Report")).find_next("div").text,"%Y-%m-%d").date() for url in filing_details_url]
                
            # Get specified filing details url(s)
            filing_details_url=[filing_details_url[url] for url in range(len(report_periods)) if report_periods[url]>start_period and report_periods[url]<=end_period]
            
            # Get specified document details url(s)
            document_details_url=[document_details_url[url] for url in range(len(report_periods)) if report_periods[url]>start_period and report_periods[url]<=end_period]
            
            # Get download url(s) to the company's 10-Q extracts
            quarter_download_url=[]
            for url in document_details_url:
                soup=BeautifulSoup(requests.get(url).content,"html.parser").find('a', text = re.compile('View Excel Document'), attrs = {'class' : 'xbrlviewer'})
                if soup is not None:
                    quarter_download_url.append(r"https://www.sec.gov"+soup['href'])
                else:
                   quarter_download_url.append(None)
            
            # Get specified report period(s)
            report_periods=[report_periods[rp] for rp in range(len(report_periods)) if report_periods[rp]>start_period and report_periods[rp]<=end_period]
        
            # Get html table(s) of the document format files 
            tableFile=[BeautifulSoup(requests.get(url).content,"html.parser").find("table", { "summary" : "Document Format Files"}) for url in filing_details_url]
            
            # Get url(s) to the quarterly report html
            quarter_report_url=[]
            for tab in range(len(tableFile)):
                if tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a").text.strip()!='':
                    if ".htm" in tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a").text.strip():
                        quarter_report_url.append("https://www.sec.gov"+tableFile[tab].findAll("tr")[1].findAll("td")[2].find("a")["href"].replace("/ix?doc=",""))
                    else:
                        quarter_report_url.append("quarterly report is not in HTML format")
                else:
                    quarter_report_url.append("quarterly report not available")
                           
            # Combine the company's report period(s), and quarterly report url(s) into a data frame
            quarter_report_df=pd.DataFrame({'report_periods':report_periods,'quarter_report_url':quarter_report_url,'quarter_download_url':quarter_download_url},index=[self.symbol]*len(report_periods))
            
            # Return the data frame contructed above if it is not empty 
            if not quarter_report_df.empty:
                return quarter_report_df
            else:
                return "No quarter report filing(s) for "+ self.symbol + " between "+ start_period.strftime("%Y-%m-%d")+" and "+end_period.strftime("%Y-%m-%d")
            
#------------------------ Best-scrolled to the most relevant financial exhibit------------------------
    # A function to exhibit financial statements 
    def financial_statements_exhibit(self):
        ## Errors checked in the ghost_report_url()
        
        # Target annual financial statements of U.S. businesses
        # Prioritize in the order of 'Consolidated Statements of Cash Flows', 'Consolidated Income Statements', 'Consolidated Statements of Operations', 'Consolidated Balance Sheets', 'Consolidated Statements of Financial Position', 'Financial Statements and Supplementary Data', 'Selected Financial Data'
        if (self.foreign==False and self.report_type=='annual'):
            # Import annual_report_url dataframe 
            annual_report_url=self.ghost_report_url().annual_report_url
            # Import report_periods dataframe
            report_periods=self.ghost_report_url().report_periods
            # Locate 'webdrive.exe' file to launch chrome browser
            driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
            # Recurrently pull up the best_scrolled financial exhibits
            for url_index in range(len(annual_report_url)):
                driver.get(annual_report_url[url_index])
                try: 
                    driver.find_element_by_partial_link_text('Consolidated Statements of Cash Flows').click()
                except:
                    try:
                        driver.find_element_by_partial_link_text('Consolidated Income Statements').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Consolidated Statements of Operations').click()
                        except:
                            try:
                                driver.find_element_by_partial_link_text('Consolidated Balance Sheets').click()
                            except:
                                try:
                                    driver.find_element_by_partial_link_text('Consolidated Statements of Financial Position').click()
                                except:
                                    try:
                                        driver.find_element_by_partial_link_text('Financial Statements and Supplementary Data').click()
                                    except:
                                        try:
                                            driver.find_element_by_partial_link_text('Selected Financial Data').click()
                                        except:
                                            print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual financial statements require manual browsing.')
                                            pass
                # Open new tab after pulling up the best-scrolled financial exhibit
                driver.execute_script("window.open('');")
                # Focus on the new tab for the next loop
                driver.switch_to.window(driver.window_handles[-1])
                
         # Target annual financial statements of foreign businesses
         # Prioritize in the order of 'Consolidated Statements of Cash Flows', 'Consolidated Income Statements', 'Consolidated Statements of Operations', 'Consolidated Balance Sheets', 'Consolidated Statements of Financial Position', 'FINANCIAL STATEMENTS', 'Financial Statements', 'Selected Financial Data'
        if (self.foreign==True and self.report_type=='annual'):
             # Import annual_report_url dataframe 
            annual_report_url=self.ghost_report_url().annual_report_url
            # Import report_periods dataframe
            report_periods=self.ghost_report_url().report_periods
            # Locate 'webdrive.exe' file to launch chrome browser
            driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
            # Recurrently pull up the most relevant financial exhibits 
            for url_index in range(len(annual_report_url)):
                driver.get(annual_report_url[url_index])
                try:
                    driver.find_element_by_partial_link_text('Consolidated Statements of Cash Flows').click()
                except:
                    try:
                        driver.find_element_by_partial_link_text('Consolidated Income Statements').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Consolidated Statements of Operations').click()
                        except:
                            try:
                                driver.find_element_by_partial_link_text('Consolidated Balance Sheets').click()
                            except:
                                try:
                                     driver.find_element_by_partial_link_text('Consolidated Statements of Financial Position').click()
                                except:
                                    try:
                                        driver.find_element_by_partial_link_text('FINANCIAL STATEMENTS').click()
                                    except:
                                        try:
                                            # Since the query is case insensitive, search in other cases
                                            driver.find_element_by_partial_link_text('Financial Statements').click()
                                        except:
                                            try:
                                                driver.find_element_by_partial_link_text('Selected Financial Data').click()    
                                            except:
                                                try:
                                                    driver.find_element_by_partial_link_text('KEY INFORMATION').click()    
                                                except:
                                                    print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual financial statements require manual browsing.')
                                                    pass
                # Open new tab after pulling up the best-scrolled financial exhibit
                driver.execute_script("window.open('');")
                # Focus on the new tab for the next loop
                driver.switch_to.window(driver.window_handles[-1])
                 
        # Target quarter financial statements of U.S. businesses
        # Prioritize in the order of 'Consolidated Balance Sheets', 'Consolidated Statements of Financial Position','Consolidated Statements of Cash Flows','Consolidated Income Statements' 'Consolidated Statements of Operations', 'FINANCIAL STATEMENTS', 'Financial Statements'
        if(self.foreign==False and self.report_type=='quarter'):
            # Import quarter_report_url dataframe 
            quarter_report_url=self.ghost_report_url().quarter_report_url
            # Import report_periods dataframe
            report_periods=self.ghost_report_url().report_periods
            # Locate 'webdrive.exe' file to launch chrome browser
            driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
            # Recurrently pull up best-scrolled financial exhibits
            for url_index in range(len(quarter_report_url)):
                driver.get(quarter_report_url[url_index])
                try:
                    driver.find_element_by_partial_link_text('Consolidated Balance Sheets').click()
                except:
                    try:
                        driver.find_element_by_partial_link_text('Consolidated Statements of Financial Position').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Consolidated Statements of Cash Flows').click()
                        except:
                            try:
                                driver.find_element_by_partial_link_text('Consolidated Income Statements').click()
                            except:
                                try:
                                    driver.find_element_by_partial_link_text('Consolidated Statements of Operations').click()
                                except:
                                    try:
                                        driver.find_element_by_partial_link_text('FINANCIAL STATEMENTS').click()
                                    except:
                                        try:
                                            driver.find_element_by_partial_link_text('Financial Statements').click()
                                        except:
                                            print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' quarter financial statements require manual browsing.' )
                                            pass          
                # Open new tab after pulling up the best-scrolled balance sheet section
                driver.execute_script("window.open('');")
                # Focus on the new tab for the next loop
                driver.switch_to.window(driver.window_handles[-1])

    #------------ Best-scrolled to the most relevant risk factor exhibit------------
    # A function to exhibit risk factors 
    def risk_factors_exhibit(self, risk_type):
        ## Previous errors checked in the ghost_report_url()
        ## Error message if the inputted risk type is neither 'enterprise' or 'market'
        if(risk_type!='enterprise' and risk_type!='market'):
            raise TypeError("Invalid risk type: only 'enterprise' or 'market' risk type is allowed")
        
        ########################### Enterprise Risk Exhibit ##################################
        if(risk_type=='enterprise'):
            # Target annual and quarter enterprise risk factors of U.S. businesses
            # Prioritize in the order of 'Risk Factors','RISK FACTORS'
            if (self.foreign==False and self.report_type=='annual'):
                # Import annual_report_url dataframe 
                annual_report_url=self.ghost_report_url().annual_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled enterprise risk factor exhibits
                for url_index in range(len(annual_report_url)):
                    driver.get(annual_report_url[url_index])
                    try: 
                        driver.find_element_by_partial_link_text('Risk Factors').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('RISK FACTORS').click()
                        except:
                            print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual enterprise risk factors require manual browsing.' )
                            pass
                    # Open new tab after pulling up the best-scrolled enterprise risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
            elif (self.foreign==False and self.report_type=='quarter'):
                # Import annual_report_url dataframe
                quarter_report_url=self.ghost_report_url().quarter_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled enterprise risk factor exhibits
                for url_index in range(len(quarter_report_url)):
                    driver.get(quarter_report_url[url_index])
                    try: 
                        driver.find_element_by_partial_link_text('Risk Factors').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('RISK FACTORS').click()
                        except:
                            print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' quarter enterprise risk factors require manual browsing.')
                            pass
                    # Open new tab after pulling up the best-scrolled enterprise risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
            
            # Target annual enterprise risk factors of foreign businesses
            # Prioritize in the order of 'Risk Factors', 'RISK FACTORS', 'KEY INFORMATION', 'Key Information'
            if (self.foreign==True and self.report_type=='annual'):
                # Import annual_report_url dataframe
                annual_report_url=self.ghost_report_url().annual_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled enterprise risk factor exhibits
                for url_index in range(len(annual_report_url)):
                    driver.get(annual_report_url[url_index])
                    try: 
                        driver.find_element_by_partial_link_text('Risk Factors').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('RISK FACTORS').click()
                        except:
                            try:
                                driver.find_element_by_partial_link_text('KEY INFORMATION').click()
                            except:
                                try:
                                    driver.find_element_by_partial_link_text('Key Information').click()
                                except:
                                    print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual enterprise risk factors require manual browsing.')
                                    pass
                    # Open new tab after pulling up the best-scrolled enterprise risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
                    
        ########################### Market Risk Exhibit #############################
        elif(risk_type=='market'):
            # Target annual and quarter market risk factors of U.S. businesses
            # Prioritize in the order of 'Quantitative and Qualitative Disclosures About Market Risk', 'QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK'
            if (self.foreign==False and self.report_type=='annual'):
                # Import annual_report_url dataframe
                annual_report_url=self.ghost_report_url().annual_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled market risk factor exhibits
                for url_index in range(len(annual_report_url)):
                    driver.get(annual_report_url[url_index])
                    try:
                        driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures about Market Risk').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures About Market Risk').click()
                        except:
                            try: 
                                driver.find_element_by_partial_link_text('QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK').click()
                            except:
                                print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual market risk factors require manual browsing.')
                                pass
                    # Open new tab after pulling up the best-scrolled market risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
            elif (self.foreign==False and self.report_type=='quarter'):
                # Import annual_report_url dataframe
                quarter_report_url=self.ghost_report_url().quarter_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled market risk factor exhibits
                for url_index in range(len(quarter_report_url)):
                    driver.get(quarter_report_url[url_index])
                    try:
                        driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures about Market Risk').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures About Market Risk').click()
                        except:
                            try: 
                                driver.find_element_by_partial_link_text('QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK').click()
                            except:
                                print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' quarter market risk factors require manual browsing.')
                                pass
                    # Open new tab after pulling up the best-scrolled market risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
            
            # Target annual market risk factors of foreign businesses
            # Prioritize in the order of 'Quantitative and Qualitative Disclosures About Market Risk','QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK'
            if (self.foreign==True and self.report_type=='annual'):
                # Import annual_report_url dataframe
                annual_report_url=self.ghost_report_url().annual_report_url
                # Import report_periods dataframe
                report_periods=self.ghost_report_url().report_periods
                # Locate 'webdrive.exe' file to launch chrome browser
                driver=webdriver.Chrome(os.getcwd()+'\\chromedriver.exe') 
                # Recurrently pull up the best_scrolled market risk factor exhibits
                for url_index in range(len(annual_report_url)):
                    driver.get(annual_report_url[url_index])
                    try:
                        driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures about Market Risk').click()
                    except:
                        try:
                            driver.find_element_by_partial_link_text('Quantitative and Qualitative Disclosures About Market Risk').click()
                        except:
                            try: 
                                driver.find_element_by_partial_link_text('QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK').click()
                            except:
                                print(self.symbol+' '+report_periods[url_index].strftime('%Y-%m-%d')+' annual market risk factors require manual browsing.')
                                pass
                    # Open new tab after pulling up the best-scrolled market risk factor exhibits
                    driver.execute_script("window.open('');")
                    # Focus on the new tab for the next loop
                    driver.switch_to.window(driver.window_handles[-1])
    
    #----------------------------- Curate Financial Statements -----------------------------------------
    # A function to curate income statements, balance sheets, and cah flow statements for U.S. and foreign businesses
    def curate_financial_statements(self,statement_type):   
        ## Error message if inputted statement type is not available
        if(statement_type!='income' and statement_type!='balance' and statement_type!='cashflow'):
            raise TypeError("Statement type not available: only 'income', 'balance', or 'cashflow' statement type is allowed")
        
        # Probable names for statement selection- may nave to update identifiers as different company uses different statement names 
        income_terms=['Consolidated Income Statement', 'Consolidated Statements of Income', 'Consolidated Statements of Earnings', 'Consolidated Statements of Operations','Consolidated Statements of Profit or Loss','Profit and Loss Statement','P&L Statement','P/L Statement','Consolidated Income Statement','Consolidated Statement of Income', 'Consolidated Statement of Earnings','Consolidated Statement of Operations','Consolidated Statement of Profit or Loss','Consolidated Profit and Loss Statement','Consolidated P&L Statement','Consolidated P/L Statement','Statement of Consolidated Operations','Statements of Consolidated Operations','Statement of Combined Operation','Statements of Combined Operation']
        
        balance_terms=['Consolidated Balance Sheets', 'Consolidated Balance Sheet','Consolidated Statements of Financial Position', 'Consolidated Statements of Financial Condition','Consolidated Statement of Financial Positions','Consolidated Statement of Financial Conditions', 'Statement of Consolidated Financial Position','Statements of Consolidated Financial Position', 'Statement of Consolidated Financial Condition', 'Statements of Consolidated Financial Condition','Combined Balance Sheet']
        cashflow_terms=['Consolidated Statements of Cash Flows','Consolidated Statement of Cash Flows','Cash Flow Statement','Consolidated Cash Flow Statement', 'Statement of Consolidated Cash Flows','Statements of Consolidated Cash Flows','Statement of Combined Cash Flow','Statements of Combined Cash Flow']
    
        # Set root diectory for file access
        root_path=os.getcwd()
        ########### Extract Annual and Quarter Financial Statements (U.S. and foreign businesses)#################
        # Retrieve periods and url(s) from the url table called by ghost_report_url()
        report_table=self.ghost_report_url()
        report_periods=report_table.report_periods.to_list()
        if(self.report_type=='annual'):
            download_url_container=report_table.annual_download_url.to_list()   # container to store the download urls of annual statements
        elif(self.report_type=='quarter'):
            download_url_container=report_table.quarter_download_url.to_list()  # container to store the download urls of quarter statements
        
        # Designate a directory to store downloaded statements (begin statement piling)
        statement_pile_path=os.path.join(root_path,'statement_pile')
        company_pile_path=os.path.join(statement_pile_path,self.symbol)            
        try:
            os.mkdir(statement_pile_path)   # Create the statement_pile_path path 
            os.mkdir(company_pile_path)   # Create the company_pile_path path
            os.chdir(company_pile_path)   # Tab into the company_pile_path path
        except:
            try:
                os.mkdir(company_pile_path)   # Create the company_pile_path path
                os.chdir(company_pile_path)   # Tab into the company_pile_path path
            except:
                os.chdir(company_pile_path)
            
        # Downlaod accessible statements into the statement_pile path
        # Construct a data frame to store the specified statement type
        period_container=[]   # container to store statement periods
        statement_container=[]   # container to store statement table
        for url_index in range(len(download_url_container)):
            statement_period=report_periods[url_index].strftime("%Y-%m-%d")
            if(download_url_container[url_index] is not None and download_url_container[url_index][download_url_container[url_index].rfind('.')+1:len(download_url_container[url_index])]!='xls'):
                    statement_file=requests.get(download_url_container[url_index])
                    file_name=self.symbol+statement_period+self.report_type+'.xlsx'   
                    with open(file_name, 'wb+') as fs: 
                        fs.write(statement_file.content)    # populating statement contents
                        dfs=pd.ExcelFile(fs)
                        sheet_headers=list(map(lambda x: x.lower().replace(' ','').replace('_','').replace('-','').replace(',','').replace("'","").replace('&','').replace('/',''), [dfs.parse(sn).columns[0] for sn in dfs.sheet_names]))
                        ############################ Income Statements ###################################
                        if (statement_type=='income'):   
                                income_term_header=list(map(lambda x: x.lower().replace(' ','').replace('&','').replace('/',''),income_terms))  
                                select_sheet_bool=[any(x in sheet_headers[i] for x in income_term_header) for i in range(len(sheet_headers))]
                                if(any(select_sheet_bool)):
                                    # Identify income statement and store in dataframe form
                                    income_statement=dfs.parse(dfs.sheet_names[select_sheet_bool.index(True)])
                                    # Store income statement into the statement container
                                    statement_container.append(income_statement)
                                    # Store income statement period into the period container
                                    period_container.append(statement_period)
                                    # Serialize the income statement dataframe into '.pickle'- to be accessed faster next time 
                                    income_statement.to_pickle(self.symbol+statement_period+self.report_type.capitalize()+statement_type.capitalize()+'.pickle')
                                else:
                                    # Store income statement as None in the statement container
                                    ## Because not identified or does not exist 
                                    statement_container.append(None)
                                    # Store income statement period into the period container
                                    period_container.append(statement_period)
                                    # Message to warn that income statement may be non-identified or simply not available
                                    print(self.symbol+' '+statement_period+ ' '+self.report_type+' income statement not identified or not available: update income statement identifiers or pass')     
    
                        ############################ Balance Sheets ###################################
                        if (statement_type=='balance'):   
                                balance_term_header=list(map(lambda x: x.lower().replace(' ','').replace('&','').replace('/',''), balance_terms))  
                                select_sheet_bool=[any(x in sheet_headers[i] for x in balance_term_header) for i in range(len(sheet_headers))]
                                if(any(select_sheet_bool)):
                                    # Identify balance sheet and store in dataframe form
                                    balance_sheet=dfs.parse(dfs.sheet_names[select_sheet_bool.index(True)])
                                    # Store balacne sheet into the statement container
                                    statement_container.append(balance_sheet)
                                    # Store balance sheet period into the period container
                                    period_container.append(statement_period)
                                    # Serialize the balance sheet dataframe into '.pickle'- to be accessed faster next time 
                                    balance_sheet.to_pickle(self.symbol+statement_period+self.report_type.capitalize()+statement_type.capitalize()+'.pickle')
                                else:
                                    # Store balance sheet as None in the statement container
                                    ## Because not identified or does not exist 
                                    statement_container.append(None)
                                    # Store balance sheet period into the period container
                                    period_container.append(statement_period)
                                    # Message to warn that balance sheet may be non-identified or simply not available
                                    print(self.symbol+' '+statement_period+ ' '+self.report_type+' balance sheet not identified or not available: update balance sheet identifiers or pass')     
                                    
                        ############################ Cash Flow Statements ###################################
                        if (statement_type=='cashflow'):   
                                cashflow_term_header=list(map(lambda x: x.lower().replace(' ','').replace('&','').replace('/',''), cashflow_terms))    
                                select_sheet_bool=[any(x in sheet_headers[i] for x in cashflow_term_header) for i in range(len(sheet_headers))]
                                if(any(select_sheet_bool)):
                                    # Identify cash flow statement and store in dataframe form
                                    cashflow_statement=dfs.parse(dfs.sheet_names[select_sheet_bool.index(True)])
                                    # Store cash flow statement into the statement container
                                    statement_container.append(cashflow_statement)
                                    # Store cash flow statement period into the period container
                                    period_container.append(statement_period)
                                    # Serialize the cash flow statement dataframe into '.pickle'- to be accessed faster next time 
                                    cashflow_statement.to_pickle(self.symbol+statement_period+self.report_type.capitalize()+statement_type.capitalize()+'.pickle')
                                else:
                                    # Store cash flow statement as None in the statement container
                                    ## Because not identified or does not exist 
                                    statement_container.append(None)
                                    # Store cash flow statement period into the period container
                                    period_container.append(statement_period)
                                    # Message to warn that cash flow statement  may be non-identified or simply not available
                                    print(self.symbol+' '+statement_period+ ' '+self.report_type+' cashflow statement not identified or not available: update cash flow statement identifiers or pass')     
                                    
                        fs.close()  # close the downloaded '.xlsx' file 
                    os.remove(file_name)    # remove the downloaded '.xlsx' file after extracting financial statements            
            else:
                print(self.symbol+' '+statement_period+' '+self.report_type+' '+statement_type+' statement not available')
        # Combine the conpany's income statement(s) or balance sheet(s) or cash flow statement(s), and statement periods into a dataframe
        statement_df=pd.DataFrame({'statement_periods':period_container,statement_type+'_statement':statement_container},index=[self.symbol]*len(period_container))  
        # Return back to root_path (end statement piling)
        os.chdir(root_path)
        # Return the data frame contructed above if it is not empty 
        if not statement_df.empty:
            return statement_df
        else:
            return 'No '+self.report_type+' '+statement_type+' statement for '+self.symbol+' between '+self.start_period.strftime("%Y-%m-%d")+' and '+self.end_period.strftime("%Y-%m-%d")    
        
    #------------------------Extract Most Recent Income Statements--------------------------------
    def ghost_income(self):  
        # Assuming the current directory is '...\BVTFilter' 
        bin_path=r'.\\statement_pile\\'+self.symbol
        if (os.path.isdir(bin_path)):
            bin_files=os.listdir(bin_path)
            pass
        else:
            os.makedirs(bin_path)
            bin_files=os.listdir(bin_path)
        
        # Convert start_period and end_period inputs to a datetime object 
        start_period=datetime.strptime(str(self.start_period),"%Y%m%d").date()
        end_period=datetime.strptime(str(self.end_period),"%Y%m%d").date()
            
        if(self.report_type=='annual'):
            if any(["AnnualIncome" in s for s in bin_files]):
                annual_income_file=[s for s in bin_files if "AnnualIncome" in s]
                annual_income_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),annual_income_file))
                annual_income_file=[annual_income_file[i] for i in range(len(annual_income_file)) if annual_income_periods[i]>start_period and annual_income_periods[i]<=end_period]
                annual_income_periods=[annual_income_periods[i] for i in range(len(annual_income_periods)) if annual_income_periods[i]>start_period and annual_income_periods[i]<=end_period]
                annual_income_file.reverse()
                annual_income_periods.reverse()
                    
                try:
                    binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[3]), pd.read_pickle(bin_path+'\\'+annual_income_file[6])], axis = 1)
                    binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[6]).group()
                except:
                    try:
                        binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[3]), pd.read_pickle(bin_path+'\\'+annual_income_file[5])], axis = 1)
                        binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[5]).group()
                    except:
                        try:
                            binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[3]), pd.read_pickle(bin_path+'\\'+annual_income_file[4])], axis = 1)
                            binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[4]).group()
                        except:
                            try:
                                binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[3])], axis = 1)
                                binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[3]).group()
                            except:
                                try:
                                    binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[2])], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[2]).group()
                                except:
                                    try:
                                        binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+annual_income_file[0]),pd.read_pickle(bin_path+'\\'+annual_income_file[1])], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[1]).group()
                                    except:
                                        try:
                                            binded_income=pd.read_pickle(bin_path+'\\'+annual_income_file[0])
                                            binded_message='Ghosted '+self.report_type+' income statments for '+re.search('\d{4}-\d{2}-\d{2}',annual_income_file[0]).group()
                                        except:
                                            binded_income=None
                                            binded_message='The specified time range is not available, try including a larger time range'
        
                                            
                if(len(annual_income_periods)>0):
                    if(end_period-annual_income_periods[0]).days>365:
                        print('Recommend updating to the latest annual income statements: update via .update_financial_statements("income"), then call this function again')
                             
            else:
                business_income=self.curate_financial_statements('income')
                try:
                    binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[3], business_income.income_statement[6]], axis = 1)
                    binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[3]+', '+business_income.statement_periods[6]
                except:
                    try:
                       binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[3], business_income.income_statement[5]], axis = 1)
                       binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[3]+', '+business_income.statement_periods[5]
                    except:
                        try:
                            binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[3], business_income.income_statement[4]], axis = 1)
                            binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[3]+', '+business_income.statement_periods[4]
                        except:
                            try:
                                binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[3]], axis = 1)
                                binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[3]
                            except:
                                try:
                                    binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[2]], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[2]
                                except:
                                    try:
                                        binded_income=pd.concat([business_income.income_statement[0],business_income.income_statement[1]], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]+', '+business_income.statement_periods[1]
                                    except:
                                        try:
                                            binded_income=business_income.income_statement[0]
                                            binded_message='Ghosted '+self.report_type+' income statments for '+business_income.statement_periods[0]
                                        except:
                                            binded_income=None
                                            binded_message='No '+self.report_type+' income statements for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                                            
        elif(self.report_type=='quarter'):
            if any(["QuarterIncome" in s for s in bin_files]):
                quarter_income_file=[s for s in bin_files if "QuarterIncome" in s]
                quarter_income_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),quarter_income_file))
                quarter_income_file=[quarter_income_file[i] for i in range(len(quarter_income_file)) if quarter_income_periods[i]>start_period and quarter_income_periods[i]<=end_period]
                quarter_income_periods=[quarter_income_periods[i] for i in range(len(quarter_income_periods)) if quarter_income_periods[i]>start_period and quarter_income_periods[i]<=end_period]
                quarter_income_file.reverse()
                quarter_income_periods.reverse()
                
                try:
                    binded_income=pd.concat([pd.read_pickle(bin_path+'\\'+f) for f in quarter_income_file], axis = 1)
                    binded_message='Ghosted '+self.report_type+' income statments for '+', '.join([re.search('\d{4}-\d{2}-\d{2}',f).group() for f in quarter_income_file])
                except:
                    binded_income=None
                    binded_message='The specified time range is not available, try including a larger time range'
                
                if(len(quarter_income_periods)>0):
                    if(end_period-quarter_income_periods[0]).days>180:
                        print('Recommend updating to the latest quarter income statements: update via .update_financial_statements("income") function, then call this function again')
                    
            else:
                business_income=self.curate_financial_statements('income')
                try:
                    binded_income=pd.concat(business_income.income_statement.to_list(), axis = 1)
                    binded_message='Ghosted '+self.report_type+' income statments for '+', '.join([business_income.statement_periods[i] for i in range(len(business_income.statement_periods))])
                except:
                    binded_income=None
                    binded_message='No '+self.report_type+' income statements for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                    
        print(binded_message)
        return binded_income
    
    #------------------------Extract Most Recent Balance Sheets--------------------------------
    def ghost_balance(self): 
        # Assuming the current directory is '...\BVTFilter' 
        bin_path=r'.\statement_pile\\'+self.symbol
        if (os.path.isdir(bin_path)):
            bin_files=os.listdir(bin_path)
            pass
        else:
            os.makedirs(bin_path)
            bin_files=os.listdir(bin_path)
        
        # Convert start_period and end_period inputs to a datetime object 
        start_period=datetime.strptime(str(self.start_period),"%Y%m%d").date()
        end_period=datetime.strptime(str(self.end_period),"%Y%m%d").date()
            
        if(self.report_type=='annual'):
            if any(["AnnualBalance" in s for s in bin_files]):
                annual_balance_file=[s for s in bin_files if "AnnualBalance" in s]
                annual_balance_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),annual_balance_file))
                annual_balance_file=[annual_balance_file[i] for i in range(len(annual_balance_file)) if annual_balance_periods[i]>start_period and annual_balance_periods[i]<=end_period]
                annual_balance_periods=[annual_balance_periods[i] for i in range(len(annual_balance_periods)) if annual_balance_periods[i]>start_period and annual_balance_periods[i]<=end_period]
                annual_balance_file.reverse()
                annual_balance_periods.reverse()
                
                try:
                    binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[4]), pd.read_pickle(bin_path+'\\'+annual_balance_file[6]), pd.read_pickle(bin_path+'\\'+annual_balance_file[8])], axis = 1)
                    binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[4]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[6]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[8]).group()
                except:
                    try:
                        binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[4]), pd.read_pickle(bin_path+'\\'+annual_balance_file[6]), pd.read_pickle(bin_path+'\\'+annual_balance_file[7])], axis = 1)
                        binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[4]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[6]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[7]).group()
                    except:
                        try:
                            binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[4]), pd.read_pickle(bin_path+'\\'+annual_balance_file[6])], axis = 1)
                            binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[4]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[6]).group()
                        except:
                            try:
                                binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[4]), pd.read_pickle(bin_path+'\\'+annual_balance_file[5])], axis = 1)
                                binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[4]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[5]).group()
                            except:
                                try:
                                    binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[4])], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[4]).group()
                                except:
                                    try:
                                        binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2]), pd.read_pickle(bin_path+'\\'+annual_balance_file[3])], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[3]).group()
                                    except:
                                        try:
                                            binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[2])], axis = 1)
                                            binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[2]).group()
                                        except:
                                            try:
                                                binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+annual_balance_file[0]),pd.read_pickle(bin_path+'\\'+annual_balance_file[1])], axis = 1)
                                                binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[1]).group()
                                            except:
                                                try:
                                                    binded_balance=pd.read_pickle(bin_path+'\\'+annual_balance_file[0])
                                                    binded_message='Ghosted '+self.report_type+' balance sheets for '+re.search('\d{4}-\d{2}-\d{2}',annual_balance_file[0]).group()
                                                except:
                                                    binded_balance=None
                                                    binded_message='The specified time range is not available, try including a larger time range'  
                                                    
                if(len(annual_balance_periods)>0):
                    if(end_period-annual_balance_periods[0]).days>365:
                        print('Recommend updating to the latest annual balance sheets: update via .update_financial_statements("balance") function, then call this function again')   
                                 
            else:
                business_balance=self.curate_financial_statements('balance')
                try:
                    binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[4],business_balance.balance_statement[6],business_balance.balance_statement[8]], axis = 1)
                    binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[4]+', '+business_balance.statement_periods[6]+', '+business_balance.statement_periods[8]
                except:
                    try:
                       binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[4],business_balance.balance_statement[6],business_balance.balance_statement[7]], axis = 1)
                       binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[4]+', '+business_balance.statement_periods[6]+', '+business_balance.statement_periods[7]
                    except:
                        try:
                            binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[4],business_balance.balance_statement[6]], axis = 1)
                            binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[4]+', '+business_balance.statement_periods[6]
                        except:
                            try:
                               binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[4],business_balance.balance_statement[5]], axis = 1)
                               binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[4]+', '+business_balance.statement_periods[5]
                            except:
                                try:
                                    binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[4]], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[4]
                                except:
                                    try:
                                        binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2], business_balance.balance_statement[3]], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]+', '+business_balance.statement_periods[3]
                                    except:
                                         try:
                                             binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[2]], axis = 1)
                                             binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[2]
                                         except:
                                             try:
                                                 binded_balance=pd.concat([business_balance.balance_statement[0],business_balance.balance_statement[1]], axis = 1)
                                                 binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]+', '+business_balance.statement_periods[1]
                                             except:
                                                 try:
                                                    binded_balance=business_balance.balance_statement[0]
                                                    binded_message='Ghosted '+self.report_type+' balance sheets for '+business_balance.statement_periods[0]
                                                 except:
                                                     binded_balance=None
                                                     binded_message='No '+self.report_type+' balance sheets for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                                                   
                                                                                  
        elif(self.report_type=='quarter'):
            if any(["QuarterBalance" in s for s in bin_files]):
                quarter_balance_file=[s for s in bin_files if "QuarterBalance" in s]
                quarter_balance_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),quarter_balance_file))
                quarter_balance_file=[quarter_balance_file[i] for i in range(len(quarter_balance_file)) if quarter_balance_periods[i]>start_period and quarter_balance_periods[i]<=end_period]
                quarter_balance_periods=[quarter_balance_periods[i] for i in range(len(quarter_balance_periods)) if quarter_balance_periods[i]>start_period and quarter_balance_periods[i]<=end_period]
                quarter_balance_file.reverse()
                quarter_balance_periods.reverse()
                
                try:
                    binded_balance=pd.concat([pd.read_pickle(bin_path+'\\'+f) for f in quarter_balance_file], axis = 1)
                    binded_message='Ghosted '+self.report_type+' balance sheets for '+', '.join([re.search('\d{4}-\d{2}-\d{2}',f).group() for f in quarter_balance_file])
                except:
                    binded_balance=None
                    binded_message='The specified time range is not available, try including a larger time range'
                
                if(len(quarter_balance_periods)>0):
                    if(end_period-quarter_balance_periods[0]).days>180:
                        print('Recommend updating to the latest quarter balance sheets: update via .update_financial_statements("balance") function, then call this function again')
                    
            else:
                business_balance=self.curate_financial_statements('balance')
                try:
                    binded_balance=pd.concat(business_balance.balance_statement.to_list(), axis = 1)
                    binded_message='Ghosted '+self.report_type+' balance sheets for '+', '.join([business_balance.statement_periods[i] for i in range(len(business_balance.statement_periods))])
                except:
                    binded_balance=None
                    binded_message='No '+self.report_type+' balance sheets for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                    
        print(binded_message)
        return binded_balance
    
    #------------------------Extract Most Recent Statement of Cash Flows--------------------------------
    def ghost_cashflow(self):   
        # Assuming the current directory is '...\BVTFilter' 
        bin_path=r'.\statement_pile\\'+self.symbol
        if (os.path.isdir(bin_path)):
            bin_files=os.listdir(bin_path)
            pass
        else:
            os.makedirs(bin_path)
            bin_files=os.listdir(bin_path)
        
        # Convert start_period and end_period inputs to a datetime object 
        start_period=datetime.strptime(str(self.start_period),"%Y%m%d").date()
        end_period=datetime.strptime(str(self.end_period),"%Y%m%d").date()
            
        if(self.report_type=='annual'):
            if any(["AnnualCashflow" in s for s in bin_files]):
                annual_cashflow_file=[s for s in bin_files if "AnnualCashflow" in s]
                annual_cashflow_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),annual_cashflow_file))
                annual_cashflow_file=[annual_cashflow_file[i] for i in range(len(annual_cashflow_file)) if annual_cashflow_periods[i]>start_period and annual_cashflow_periods[i]<=end_period]
                annual_cashflow_periods=[annual_cashflow_periods[i] for i in range(len(annual_cashflow_periods)) if annual_cashflow_periods[i]>start_period and annual_cashflow_periods[i]<=end_period]
                annual_cashflow_file.reverse()
                annual_cashflow_periods.reverse()
                
                try:
                    binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[3]), pd.read_pickle(bin_path+'\\'+annual_cashflow_file[6])], axis = 1)
                    binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[6]).group()
                except:
                    try:
                        binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[3]), pd.read_pickle(bin_path+'\\'+annual_cashflow_file[5])], axis = 1)
                        binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[5]).group()
                    except:
                        try:
                            binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[3]), pd.read_pickle(bin_path+'\\'+annual_cashflow_file[4])], axis = 1)
                            binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[3]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[4]).group()
                        except:
                            try:
                                binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[3])], axis = 1)
                                binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[3]).group()
                            except:
                                try:
                                    binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[2])], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[2]).group()
                                except:
                                    try:
                                        binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0]),pd.read_pickle(bin_path+'\\'+annual_cashflow_file[1])], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()+', '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[1]).group()
                                    except:
                                        try:
                                            binded_cashflow=pd.read_pickle(bin_path+'\\'+annual_cashflow_file[0])
                                            binded_message='Ghosted '+self.report_type+' cashflow statements for '+re.search('\d{4}-\d{2}-\d{2}',annual_cashflow_file[0]).group()
                                        except:
                                            binded_cashflow=None
                                            binded_message='The specified time range is not available, try including a larger time range'
                if(len(annual_cashflow_periods)>0):
                    if(end_period-annual_cashflow_periods[0]).days>365:
                        print('Recommend updating to the latest annual cashflow statements: update via .update_financial_statements("cashflow") function, then call this function again')                               
                    
            else:  
                business_cashflow=self.curate_financial_statements('cashflow')
                try:
                    binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[3], business_cashflow.cashflow_statement[6]], axis = 1)
                    binded_message='Ghosted '+self.report_type+' cashflow statements for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[3]+', '+business_cashflow.statement_periods[6]
                except:
                    try:
                       binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[3], business_cashflow.cashflow_statement[5]], axis = 1)
                       binded_message='Ghosted '+self.report_type+' cashflow statments for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[3]+', '+business_cashflow.statement_periods[5]
                    except:
                        try:
                            binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[3], business_cashflow.cashflow_statement[4]], axis = 1)
                            binded_message='Ghosted '+self.report_type+' cashflow statments for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[3]+', '+business_cashflow.statement_periods[4]
                        except:
                            try:
                                binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[3]], axis = 1)
                                binded_message='Ghosted '+self.report_type+' cashflow statments for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[3]
                            except:
                                try:
                                    binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[2]], axis = 1)
                                    binded_message='Ghosted '+self.report_type+' cashflow statments for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[2]
                                except:
                                    try:
                                        binded_cashflow=pd.concat([business_cashflow.cashflow_statement[0],business_cashflow.cashflow_statement[1]], axis = 1)
                                        binded_message='Ghosted '+self.report_type+' cashflow for '+business_cashflow.statement_periods[0]+', '+business_cashflow.statement_periods[1]
                                    except:
                                        try:
                                            binded_cashflow=business_cashflow.cashflow_statement[0]
                                            binded_message='Ghosted '+self.report_type+' cashflow statments for '+business_cashflow.statement_periods[0]
                                        except:
                                            binded_cashflow=None
                                            binded_message='No '+self.report_type+' cashflow statements for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                                            
        elif(self.report_type=='quarter'):
            if any(["QuarterCashflow" in s for s in bin_files]):
                quarter_cashflow_file=[s for s in bin_files if "QuarterCashflow" in s]
                quarter_cashflow_periods=list(map(lambda x: datetime.strptime(re.search('\d{4}-\d{2}-\d{2}',x).group(),"%Y-%m-%d").date(),quarter_cashflow_file))
                quarter_cashflow_file=[quarter_cashflow_file[i] for i in range(len(quarter_cashflow_file)) if quarter_cashflow_periods[i]>start_period and quarter_cashflow_periods[i]<=end_period]
                quarter_cashflow_periods=[quarter_cashflow_periods[i] for i in range(len(quarter_cashflow_periods)) if quarter_cashflow_periods[i]>start_period and quarter_cashflow_periods[i]<=end_period]
                quarter_cashflow_file.reverse()
                quarter_cashflow_periods.reverse()
               
                try:
                    binded_cashflow=pd.concat([pd.read_pickle(bin_path+'\\'+f) for f in quarter_cashflow_file], axis = 1)
                    binded_message='Ghosted '+self.report_type+' cashflow statments for '+', '.join([re.search('\d{4}-\d{2}-\d{2}',f).group() for f in quarter_cashflow_file])
                except:
                    binded_cashflow=None
                    binded_message='The specified time range is not available, try including a larger time range' 
                    
                if(len(quarter_cashflow_periods)>0):
                    if(end_period-quarter_cashflow_periods[0]).days>180:
                        print('Recommend updating to the latest quarter cashflow statements: update via .update_financial_statements("cashflow") function, then call this function again')
                    
            else:
                business_cashflow=self.curate_financial_statements('cashflow')
                try:
                    binded_cashflow=pd.concat(business_cashflow.cashflow_statement.to_list(), axis = 1)
                    binded_message='Ghosted '+self.report_type+' cashflow statments for '+', '.join([business_cashflow.statement_periods[i] for i in range(len(business_cashflow.statement_periods))])
                except:
                    binded_cashflow=None
                    binded_message='No '+self.report_type+' cashflow statements for '+self.symbol+' between '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' and '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d")
                    
        print(binded_message)
        return binded_cashflow
    
    #--------------------------Update statement pile------------------------------------
    def update_financial_statements(self,statement_type):
        income_temp=self.curate_financial_statements(statement_type)
        print(self.symbol+' '+self.report_type+' '+statement_type+ ' statements have been updated: updated to include time range '+datetime.strptime(str(self.start_period),"%Y%m%d").strftime("%Y-%m-%d")+' - '+datetime.strptime(str(self.end_period),"%Y%m%d").strftime("%Y-%m-%d"))
        del income_temp
        
        
        
    #--------------------------Extract Beta from Finviz------------------------------------
    def ghost_discount_rate(self):
        try:
            beta=round(float(finviz.get_stock(self.symbol).get("Beta")),1)
            if(self.foreign==False):
                if (beta<=0.8):
                    discount=0.046
                elif (beta==0.9):
                    discount=0.051
                elif (beta==1.0):
                    discount=0.056
                elif (beta==1.1):
                    discount=0.061
                elif (beta==1.2):
                    discount=0.066
                elif (beta==1.3):
                    discount=0.071
                elif (beta==1.4):
                    discount=0.076
                elif (beta==1.5):
                    discount=0.081
                elif (beta==1.6):
                    discount=0.0835
                elif (beta>1.6):
                    discount=0.086
            else:
                if (beta<=0.8):
                    discount=0.0588
                elif (beta==0.9):
                    discount=0.0654
                elif (beta==1.0):
                    discount=0.072
                elif (beta==1.1):
                    discount=0.0786
                elif (beta==1.2):
                    discount=0.0852
                elif (beta==1.3):
                    discount=0.0918
                elif (beta==1.4):
                    discount=0.0984
                elif (beta==1.5):
                    discount=0.105
                elif (beta==1.6):
                    discount=0.1083
                elif (beta>1.6):
                    discount=0.1116
            return discount
        except:
            print('Failed to find '+self.symbol+' on finviz.com.')
            
    #--------------------------Extract Current Number of Shares Outstanding from Finviz------------------------------------   
    def ghost_shs_outstand(self):
        try:
            shs_oustand=finviz.get_stock(self.symbol).get("Shs Outstand")
            return shs_oustand
        except:
            print('Failed to find '+self.symbol+' on finviz.com.')   
    
  
    
    
    
    
    
