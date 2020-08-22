
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
  The program takes an object-oriented apporach by having the user establish a business entity to store a specified type of financial information. The algorithm serves ready as a "librarian" in the entity to process your requests- curating, tidying, then sending them back to you all in one place. On the retrieving side, the "librarian" parses through the SEC database to look for the company's identity- this is identified by the company's Central Index Key (CIK), just like a pereson's ID card number. then, the accession number of each filing requested, just like the International Standard Book Number (ISBN) found on the back of a book. These are sufficient for the "librarian" to locate the HTML links to the full reports requested. To extract a specified financial statement within the report, the "librarian" virtually downloads the report section containing the specified statement, typically called "Item 8- Financial Statements and Supplementary Data" in an annual report (10-K) and "Item 1- Financial Statements" in a quarter report (10-Q); the report section will not be stored on your computer. Once downloaded, the "librarian" reads the section, grabs the financial statement table, and curates it into the "shelf" of your computer; "shelf" is a folder created by the "librarian" to centralize all financial statements you've requested. On the centralizing side, all your financial statements can be retrieved as many times as you want. You can choose which statments to keep and drop at all times. The "librarain" is also apt at tidying multiple financial statements into one table such that you only have to look at one place for comparing the financial performance of a business over many years.
   
</p>

and adds it to your computer. 








## Quick Start <a name = "quick_start"></a>
### Prerequisites
### Run Script

```
Give examples
```

## Examples <a name = "examples"></a>

## How is this different from other scrapers? a name = "uniiqe"></a>
keyword is centralize

```
Give the example
```

## Acknowledgments <a name = "acknowledge"></a>


```
until finished
```

End with an example of getting some data out of the system or using it for a little demo.

## 🔧 Running the tests <a name = "tests"></a>
Explain how to run the automated tests for this system.

### Break down into end to end tests
Explain what these tests test and why

```
Give an example
```

### And coding style tests
Explain what these tests test and why

```
Give an example
```

## 🎈 Usage <a name="usage"></a>
Add notes about how to use the system.

## 🚀 Deployment <a name = "deployment"></a>
Add additional notes about how to deploy this on a live system.

## ⛏️ Built Using <a name = "built_using"></a>
- [MongoDB](https://www.mongodb.com/) - Database
- [Express](https://expressjs.com/) - Server Framework
- [VueJs](https://vuejs.org/) - Web Framework
- [NodeJs](https://nodejs.org/en/) - Server Environment

## ✍️ Authors <a name = "authors"></a>
- [@kylelobo](https://github.com/kylelobo) - Idea & Initial work

See also the list of [contributors](https://github.com/kylelobo/The-Documentation-Compendium/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- Hat tip to anyone whose code was used
- Inspiration
- References




<h1> SEC-Business-Scraper</h1>
<h2> An off-the-shelf information tool to retrieve business financials </h2>
  
