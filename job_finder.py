# libraries
import requests
import pickle
from bs4 import BeautifulSoup
import pandas as pd
import itertools
from sqlalchemy import create_engine
engine = create_engine("sqlite:///jobs.db")

def job_finder_css(page_url):
  # processing listings page
  page = requests.get(page_url)
  soup = BeautifulSoup(page.text, 'html.parser')
  page_list =[]

  # finding all the jobs listed in page
  for job in soup.find_all('li', class_ = 'entry-list-item'):
    title_tag = job.find('h2',class_ = 'entry-title').a
    job_dict = {
                'job_title': title_tag.get_text(strip=True),
                'job_link': title_tag['href'],
                'date': job.find('time')['datetime']
                }
    page_list.append(job_dict)


  return page_list

def job_parser_css(job_url):
    # processing a particular job's webpage
    job_page = requests.get(job_url)
    job_soup = BeautifulSoup(job_page.text, "html.parser")

    # scraping the job description
    job_ul = job_soup.find_all('ul', class_='wp-block-list')

    job_description = []

    for ul in job_ul:
      for li in ul.find_all('li'):
          job_description.append(li.text)

    return job_description

def job_link_scraper_css(first_page, last_page):
  # processing a range of pages, finding the jobs and extracting the description
  page_urls = [
        f"https://www.corporatestaffing.co.ke/jobs/page/{i}"
        for i in range(first_page, last_page + 1)
    ]
  mega_list = []

  for i, url, fails in enumerate(page_urls, start=1):
    try:
      mega_list.append(job_finder_css(url))
      print(f"processing page {i}/{len(page_urls)}")

    except:
      print(f"Link failed. Failures = {fails}/{len(page_urls)}")
      continue

  # flattening the list
  mega_list = list(itertools.chain(*mega_list))

  # saving the list
  with open("job_links_css.pkl", "wb") as jl: 
    pickle.dump(mega_list, jl)
  
  return "job_links_css.pkl"

def job_desc_scraper_css(list_pickle, start_index, finish_index):
  with open(list_pickle, "rb") as jl:
    mega_list = pickle.load(jl)

  mega_list = mega_list[start_index:finish_index + 1]

  counter = 0
  running_list = []
  # parsing jobs
  for job in mega_list:
      job_link = job['job_link']
      job_desc = job_parser_css(job_link)
      job['description'] = " ".join(job_desc)

      counter+=1
      print(f"processed {counter} out of {len(mega_list)} jobs")

      running_list.append(job)

      if len(running_list) >= 1000:
        df = pd.DataFrame(running_list)
        df.to_sql(
        name='css_job_data',
        con=engine,
        if_exists='append',
        index=False
        )

        running_list.clear()
      else:
        continue

  if running_list:
    df = pd.DataFrame(running_list)

    df.to_sql(
        name='css_job_data',
        con=engine,
        if_exists='append',
        index=False
    )

  return

def job_finder_mjm(page_url):
  # processing listings page
  page = requests.get(page_url)
  soup = BeautifulSoup(page.text, 'html.parser')
  page_list =[]
  # finding all the jobs listed in page
  for job in soup.find_all('li', class_ = 'job-list-li'):
    try:
      h_tag = job.find('h2').a
      time_tag = job.find('li', class_ = 'job-item').ul

      job_dict = {
                  'job_title': h_tag.get_text(strip=True),
                  'job_link': 'https://www.myjobmag.co.ke' + h_tag['href'],
                  'date': time_tag.get_text(strip =True)
                  }
      page_list.append(job_dict)
    except:
      continue


  return page_list

def job_parser_mjm(job_url):
  # processing a particular job's webpage
  job_page = requests.get(job_url)
  job_soup = BeautifulSoup(job_page.text, "html.parser")

  # scraping the job description
  job_ul = job_soup.find('div', class_='job-details')

  try:
    job_description = job_ul.get_text(strip = True)
  except:
    job_description = None

  return job_description

def job_link_scraper_mjm(first_page, last_page):
  # processing a range of pages, finding the jobs and extracting the description
    page_urls = [
          f"https://www.myjobmag.co.ke/page/{i}"
          for i in range(first_page, last_page + 1)
      ]

    mega_list = []
    for i, url in enumerate(page_urls, start=1):
      mega_list.append(job_finder_mjm(url))
      print(f"processing page {i}/{len(page_urls)}")

      # flattening the list
    mega_list = list(itertools.chain(*mega_list))
    
    # saving the list
    with open("job_links_mjm.pkl", "wb") as jl: 
      pickle.dump(mega_list, jl)

    return "job_links_mjm.pkl"

def job_desc_scraper_mjm(list_pickle, start_index, finish_index):
  with open(list_pickle, "rb") as jl:
    mega_list = pickle.load(jl)

    mega_list = mega_list[start_index:finish_index + 1]

    counter = 0
    running_list = []
    # parsing jobs
    for job in mega_list:
        job_link = job['job_link']
        job_desc = job_parser_mjm(job_link)
        job['description'] = job_desc

        counter+=1
        print(f"processed {counter} out of {len(mega_list)} jobs")
         
        running_list.append(job)

        if len(running_list) >= 1000:
          df = pd.DataFrame(running_list)
          df.to_sql(
          name='mjm_job_data',
          con=engine,
          if_exists='append',
          index=False
          )

          running_list.clear()

        else:
          continue

  if running_list:
    print(running_list)
    df = pd.DataFrame(running_list)

    df.to_sql(
        name='mjm_job_data',
        con=engine,
        if_exists='append',
        index=False
    )

  return

css_pickle = r'D:\personal stuff\programming\ds\scraping\job_links_css.pkl'
job_desc_scraper_css(css_pickle, 22000, 46000)
print('CSS job processing done.')

mjm_pickle = r'D:\personal stuff\programming\ds\scraping\job_links_mjm.pkl'
job_desc_scraper_mjm(mjm_pickle, 92000, 100000)

print('MJM job processing done. Task complete!')
