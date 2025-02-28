import threading
import time
import os
import logging
import colorama
import requests

from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from tqdm import tqdm

colorama.init(autoreset=True)

# Set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Set the logging level

# Create a file handler
file_handler = logging.FileHandler( "Directory_Listing_Downloader.log" )
file_handler.setLevel(logging.ERROR)  # Log only error messages to the file

# Create a formatter and set it for the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# done setting up our logger configurations


class Scraper(object):
    def __init__(self, url: str, retries: int, threads: int, timeout: int):
        self.url: str = url
        self.download_urls: list[str] = []
        self.retries: int = retries

        self.threads: int = threads
        self.Lock = threading.Lock()

        self.timeout: int = timeout
        
        # configured in main later
        self.pbar = None
        # # self.pbar = tqdm(total=len(self.urls), desc="[ Checking Domains... ]", lock_args=[self.Lock])

        # for example Downlaoded_Tree_172783/homework/homework1.pdf, and other files
        self.root_dir = f"Downloaded_Tree_{time.time()}"

        # that way in every single thread this isn't re-initialized
        self.request_config = {
            "headers":  { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" }
        }

        self.FAILED_REQ = "make_simple_get_failed_all"
    
    def make_simple_get( self, url: str ) -> str:
        """
        
            This will make a simple GET request, this makes it easier to deal with retries so I don't have 
            to create a for loop for every single little GET request.
        
        """
        data = self.FAILED_REQ
        for retry in range(self.retries):
            try:
                req = requests.get( url=url, headers=self.request_config['headers'], verify=False, timeout=self.timeout )
                
                # since we had a successful GET request, break out of the loop
                data = req.text
                break
            except Exception as err:
                logger.error( f"In {self.make_simple_get.__name__} --> {err} " )
        return data
    
    def download_file( self, url: str ) -> None:
        """
        
        Using a GET request this will download the actual URL resource. 
        Making sure we're using chunked downloading in case one of the files is like 12 GB you're not trying to 
        write the entire 12GB into your buffer.
        
        """
        # need to buffer the output for actual file downloads which is why we're not using make_simple_get:
        
        successful_GET = False
        
        
        # TODO: put this into its own function:
        # need to replicate the directory structure we're downloading from, for example
        # if there is homework/homeword1.pdf, we can't just download homework1.pdf.
        
        temp_url = url.replace('https://', '').replace('http://', '').replace('//', '/')
        fname_path = temp_url.split('/')[1:]
        fname_path.insert(0, self.root_dir)
        # the directory path except the filename
        # *fname_path[:-1] is same as fname_path[0], fname_path[1], etc
        directory_structure = os.path.join( *fname_path[:-1] )

        # make the directory structure, if it already exists throw no errors
        os.makedirs( directory_structure, exist_ok=True )

        # now join the directory tree we created with the file name we're going to download now:

        results_path = os.path.join( directory_structure, fname_path[-1] )
        
        # safer to work in bytes mode than writing string literals.
        results_file = open( results_path, 'wb' )

        for _ in range(self.retries):
            try:
                req = requests.get( url=url, headers=self.request_config['headers'], timeout=self.timeout, verify=False )
                # successfully made request
                successful_GET = True
                
                # we're going to download the file in 50KB chunks
                for chunk in req.iter_content( chunk_size=1024*50 ):
                    # if chunk exists (is not None), write it into the file
                    if chunk:
                        results_file.write(chunk)
                break
            except Exception as err:
                logger.error( f"[ In {self.download_file.__name__} --> {err} ]" )

        if successful_GET != True:
            # keeps us from missing out on files that failed to download:
            logger.error( f"[ In {self.download_file.__name__}  --> ** Unable to download the resource because all retries failed ! ** \'{url}\']" )
        
        # properly close the file
        results_file.close()

        # update the progress bar.
        
        self.Lock.acquire()
        self.pbar.update()
        self.Lock.release()
    
    def scrape_download_urls( self ) -> None:
        """
        
        This will scrape all of the urls to resources/files we need to download. This will also recursively 
        spider into folders and download those as well.
        
        """
        # first one in the list will be the root http server URL
        urls_to_scrape = [ self.url ]
        # have to use while loop otherwise the urls_to_scrape array won't dynamically update!
        while len(urls_to_scrape) != 0:
            for url in urls_to_scrape:
                print(f"{Fore.MAGENTA}[ GET  ] {url}")
                
                data = self.make_simple_get( url )
                
                # failed to make the request
                if self.FAILED_REQ == data:
                    logger.error( f"[ {self.scrape_download_urls.__name__} --> failed to make GET even with \'{self.retries}\' retries to resource \'{url}\']\n" )
                    continue
                else:
                    data = data.splitlines()
                
                

                for line in data:
                    # TODO: add support for other directory listings like Apache, Nginx, etc
                    if '<li><a ' in line:
                        fname = line = line.split('<li><a href="', 1)[1].split('"', 1)[0].strip().rstrip()                
                        
                        # is a directory, can use recursion to keep getting files in it as well!
                        if fname[-1] == '/':
                            # since this is a directory we need to put it in the urls_to_scrape
                            urls_to_scrape.append(f"{url}/{fname}")
                            print(f"{Fore.YELLOW} Found [ Directory: {fname} ]")
                        else:
                            print(f"{Fore.GREEN} Scraped [ File: {fname} ]")
                            self.download_urls.append(f"{url}/{fname}")
                
                # now that we've already scraped these file names we can remove it from the array
                urls_to_scrape.remove(url)


    def main( self ) -> None:

        print(f"{Fore.YELLOW}[ Scraping Download Urls... ]")
        self.scrape_download_urls()

        # make the root directory before downloading the URLs
        os.makedirs(self.root_dir)

        # progress bar for scraping progress:
        self.pbar = tqdm(total=len(self.download_urls), desc="[ Downloading Files... ]")

        # now that we have the direct download URLs we can go ahead and make GET requests to download the actual resources!
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map( self.download_file, self.download_urls )
        
        
        # kept on getting a really annoying SEGFAULT when the program finished, it's because the pbar object is never
        # cleaned up at the end of the program.
        self.pbar.close()

        
        

if __name__ == "__main__":
    python_server_url = input("[ Enter URL for Python3 HTTP web server ]: ").strip().rstrip()
    threads = int(input("[ Number of threads ]: ").strip().rstrip())
    retries = int(input("[ Number of Retries ]: ").strip().rstrip())
    timeout = int(input("[ Timeout (seconds) ]: ").strip().rstrip())

    downloaderObj = Scraper( url=python_server_url, retries=retries, threads=threads, timeout=timeout )
    downloaderObj.main()
