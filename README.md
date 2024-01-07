# Farm Squire
Farm squire is a python script that models nutrient flow and yearly operations on farms. This first release was made with beef farms in mind but we strife to have any farm be able to be simulated.

## setup:
We recommend installing [anaconda](https://docs.anaconda.com/free/anaconda/install/index.html) in order to run this script. Anaconda contains the latest version of pyhton, and all python packages used by farm squire are contained in the base install of anaconda.

In order to download the files of this repository to your local device we recommend using [github desktop](https://desktop.github.com/).

## running farm_squire:
Once anaconda is installed, and you cloned this repository to your device you can open the windows powershell from you anaconda navigator. 

Inside the powershell you can [navigate](https://learn.microsoft.com/en-us/powershell/scripting/samples/managing-current-location?view=powershell-7.4) to the directory the repository is cloned. This is for example done with the command: `cd D:/some_folder/Farm_Squire`

Once in the right directory you can run the script by entering the command `python farm_squire input_file.xlsx` different excel documents can be used as input by changing the name of the input file. E.G. you can run the example file by typing the command `python farm_squire input_example.xlsx`. running the script will make excel file containing all relevant output data. The name format of th output file is `squire_results_date_time.xlsx`

## making your own input file:
You should use the profided `input_example.xlsx` file as a template for your own input file.

the input file contains four different sheets: estate, crops, animal, and biodigestor. Each of these sheets will contain data relevant to their name.

All sheets in the example file will have some common formatting that is used to help understand the program: Each sheet will start with two columns being: `properties` and `unit of measurement`. Each property indicates a statistic that the programm will use, and the unit of measurement indicates the unit in which that statistic should be supplied. All cells/columns highlighted in gold are 'hardcoded' in the script and should not be changed. All cells/rows highlighted in green are 'softcoded' and can either be renamed, or extended with additional entries. More on that later. Some cells will contain a red corner, when hovering over them you will reveal a note with additional information pertaining to that cell. All other (white) cells can be freely edited to contain the statistics as the are present on your farm. If the program regards a statistic that is not present on your farm, you can most likely put the value to 0 without much hinderance.

### to be extended
