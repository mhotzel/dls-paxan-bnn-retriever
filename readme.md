# A little manual

## Summary
This  program retrieves the article list from the FTP-Server of https://www.hakopaxan-shop.de/ , a supplier for organic food products and other organic products.

You have to get a contract with the supplier if you want to get an account.

The supplier **'Pax an'** regularly provides two article files available via FTP. These article files can be retrieved using this small program.

The program downloads the file in text mode and writes it without any processing to the configured target directory. it reads the first line (header) of the file to get the valid-from-Date. It writes the file with the valid-from-date and the timestamp when it was retrieved to the target directory.

It is your goal to process the file after retrieving.

## Requirements
You need to install at least Python 3.9 on your machine.

Python > 3.9 is required because the ftp client built in in python only supports the encoding parameter in 3.9 or higher.

Of course - feel free to patch your own version if you want to use a python version < 3.9.

Furthermore, no further libraries are required.

## Configuration
When you have downloaded the program you have to do the setup:

 - Create or choose a folder for the retrieved file
 - do the neccessary configuration in the file "config.ini".

**Here are some notices to the parameters.**

*'target_dir':*
configure here the path to your chosen target directory. I think it's better to store an absolute path. The program didn't care about any paths for example where it was started from or so.

*'host', 'user', 'password':*
You get the connection parameters directly from 'pax an'. Don't ask me, please!

*'encoding':*
The file specification of the article file (you can get this document directly from 'pax an' too) says, there are two encodings possible:

- 'ansi'
- 'ascii'

that's why I have chosen "CP437" by default. It works for me.

*'source_filename':*
'pax an' provides two files:

- 'PL.BNN': This is the file for the most articles
- 'PLF.BNN': This file contains 'daily fresh articles', for example vegetables and so on.

**caution**: The file names on the FTP Server are case sensitive!

*'target_filename':*
the file name for the target file:

- {retrievets} will be replaced by the date and time of the retrieval.
- {validts} will be replaced by the valid-from-date and valid-from-time read from the first line in the retrieved file


***Have fun!***