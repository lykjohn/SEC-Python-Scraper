
<p align="center">
  <a href="" rel="noopener"></a>
  <img src="images/banner.png" alt='Book Value' width='750' height='350' >
</p>
  
<h1  align='center' > U.S. Securities and Exchange Commission (SEC) Business Scraper </h1>


[![Build Status](https://img.shields.io/badge/build-passing-black.svg)](https://github.com/lykjohn/SEC-Business-Scraper.git)
[![Documentation Status](https://img.shields.io/badge/documentation-passing-green.svg)](https://github.com/lykjohn/SEC-Business-Scraper.git)
[![GitHub commits](https://img.shields.io/badge/last%20commit-today-yellow.svg)](https://github.com/lykjohn/SEC-Business-Scraper/commit/master)
[![Setup Automated](https://img.shields.io/badge/setup-automated-blue?logo=gitpod)](https://gitpod.io/from-referrer/)
[![GitHub license](https://img.shields.io/badge/license-MIT-red.svg)](https://github.com/lykjohn/SEC-Business-Scraper/blob/master/LICENSE)


[What is this about?](#about)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[How it workds](#how_it_works)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[Quick Start](#quick_start)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; [Examples](#examples)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[Why this scraper?](#unique)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[Acknowledgments](#acknowledgement)&nbsp;&nbsp;&nbsp;

## What is this about? <a name = "about"></a>
<p>
  In the era of information unity, the uncentralized fashion of delivering financial information page after page is becoming a less paceful practice. This package aims to provide dynamic functions to retrieve and centralize financial information from the U.S. Securities and Exchange Commission (SEC) EDGAR database, a web reposoitory that stores reliable filings and track records of all publicly-traded companies in the U.S.. Think of this as your "librarian, let it know the specific company statement(s) you are looking for, then it will gather, tidy, then delivery them to you. The major catch is that there is only one place to look, regardless how many statements you've requested.
  


## How does this work? <a name = "how_it_works"></a>
<p>
  The program takes an object-oriented apporach by having the user establish a business entity to store a specified type of financial information. The algorithm serves ready as a "librarian" in the entity to process your requests- curating, tidying, then sending them back to you all in one place. On the retrieving side, the "librarian" parses through the SEC database to look for the company's identity- this is identified by the company's Central Index Key (CIK), similar to a pereson's ID card number. then, the accession number of each filing requested, similar to the International Standard Book Number (ISBN) found on the back of a book. These are sufficient for the "librarian" to locate the HTML links to the full reports requested. To extract a specified financial statement within the report, the "librarian" virtually downloads the report section containing the specified statement, typically called "Item 8- Financial Statements and Supplementary Data" in an annual report (10-K) and "Item 1- Financial Statements" in a quarter report (10-Q); the report section will not be stored on your computer. Once downloaded, the "librarian" reads the section, grabs the financial statement table, and curates it into the "shelf" of your computer; "shelf" is a folder created by the "librarian" to centralize all financial statements you've requested. On the centralizing side, all your financial statements can be retrieved as many times as you want. You can choose which statments to keep and drop at all times. The "librarain" is also apt at tidying multiple financial statements into one table such that you only have to look at one place for comparing financial performances of a business over many years instead of jumping between several places. 
  The "librarian" also offers the classic way of report delivery, that is to deliver specified reports page by page. As long as you have Chrome, an internet browser, on your computer, the rest is taken care of by the "librarian". This works because once the "librarian" has located the HTML links to the full reports requested, it will load each full report on a seperate tab, with all tabs lined up in one browser window. You may then simply click around to compare business performances in that one window 
   
</p>


## Quick Start <a name = "quick_start"></a>
### Prerequisites
<p>
  
  <ol> 
   <strong><li> Install Chrome Driver (skip this if you've already done so):</li></strong>
      <ul>
        <li>If you are using Chrome version 85, please download ChromeDriver <a href="https://chromedriver.storage.googleapis.com/index.html?path=85.0.4183.38/"> 85.0.4183.38 </a> </li>
        <li>If you are using Chrome version 84, please download ChromeDriver <a href="https://chromedriver.storage.googleapis.com/index.html?path=84.0.4147.30/">84.0.4147.30 </a> </li>
        <li>If you are using Chrome version 83, please download ChromeDriver <a href="https://chromedriver.storage.googleapis.com/index.html?path=83.0.4103.39/">83.0.4103.39 </a> </li>
        <li>If your Chrome version is neither of the above, go <a href="https://chromedriver.chromium.org/downloads"> here</a> to select a version that suits.</li>
      </ul>
   <strong> <li> Install Pytohn Packages:</li></strong>
  
```bash
pip installl os
pip install pickle
pip install re
pip install bs4
pip install requests
pip install pandas
pip install numpy
pip install datetime 
pip install selenium
```
  </ol>
  
  


  </li> 
  
</p>



### Going to work

## Examples <a name = "examples"></a>

## How is this different from other scrapers? a name = "uniiqe"></a>
keyword is centralize

```
Give the example
```

## Acknowledgments <a name = "acknowledge"></a>


  
