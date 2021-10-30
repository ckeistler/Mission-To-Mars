# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = mars_hemispheres(browser)
    print(hemisphere_image_urls)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
        }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

 
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://mars.nasa.gov/all-about-mars/facts/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Earth', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemispheres(browser):
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)

    html_hemispheres = browser.html
    hemisphere_soup = soup(html_hemispheres, 'html.parser')
    items = hemisphere_soup.find_all('div', class_='item')
    hemispheres_base_url = 'https://astrogeology.usgs.gov'

    hemisphere_image_urls = []

    #try:
    for x in items: 
        hemispheres = {}    
        # Store title
        title = x.find('h3').text
        print(title)

        # Store link that leads to full image website
        img_url = x.find('a', class_='itemLink product-item')['href']
        print(img_url)    

        # Visit the link that contains the full image website 
        browser.visit(hemispheres_base_url + img_url)
                
        # HTML Object of individual hemisphere information website 
        img_html = browser.html
        print(img_html)        

        # Parse HTML with Beautiful Soup for every individual hemisphere information website 
        soup1 = soup(img_html, 'html.parser')
                
        # Retrieve full image source 
        for div in soup1.findAll('div', class_="downloads"):
            for a in div.findAll('a', href=True, target="_blank", text="Sample"):
                full_img_url = a.get('href')

        
        # Append the retreived information into a list of dictionaries 
    
        hemispheres['full_img_url'] = full_img_url
        hemispheres['title'] = title
        print(hemispheres)
        hemisphere_image_urls.append(hemispheres)
        print(hemisphere_image_urls)
        browser.back() 


    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())