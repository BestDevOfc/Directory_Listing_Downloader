# Directory Listing Downloader (Exfiltrator)
For downloading directory listing enabled endpoints, useful during red team engagements instead of having to scour every file you can download the whole index and look through it locally. This also utilizes multithreading using threadpools and downloads files in chunks for efficient memory management.

For example, it would work on a python one that's spun up using the following command:
```bash
python3 -m http.server 6969
```

<img width="565" alt="Screenshot 2025-01-31 at 9 16 03 PM" src="https://github.com/user-attachments/assets/ff033d14-04d1-4fce-aefe-d9657e9720c5" />


# Fast Multithreaded directory listing archiver/downloader + Logging



💙 **For issues contact me on discord: alimuhammadsecured_65817**

MacOSx/Linux/Windows Multi-threaded Directory Listing Downloader
=============

A simple, fast downloader for Directory Listing, this has been testing on simple Python3 -m http.server (s).

<img width="1175" alt="Screenshot 2025-01-31 at 8 37 08 PM" src="https://github.com/user-attachments/assets/341963bc-db8b-4025-82e2-2806e59708d6" />



# Installation
```bash
git clone https://github.com/BestDevOfc/Directory_Listing_Downloader.git
cd Directory_Listing_Downloader/
```

Installing the third-party modules:
```
python3 -m pip install -r requirements.txt

OR

pip install -r requirements.txt
```

Running the downloader:
```

python3 ./main.py

```



TODOs:
1. The initial process where it scrapes URLs to the files is not multi-threaded, in the future it will be.
2. Simple refactoring of the code
3. Support for future directory listing servers
4. Rotating user agents for better operational security during engagements (OPSEC)
5. Save failed downloads in an array and at the end ask the user if they would like to retry those downloads + save them in a file in case they fail again.


