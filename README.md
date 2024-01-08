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

All sheets in the example file will have some common formatting that is used to help understand the program: 
- Each sheet will start with two columns being: `properties` and `unit of measurement`. Each property indicates a statistic that the programm will use, and the unit of measurement indicates the unit in which that statistic should be supplied. 
- All cells/columns highlighted in gold are 'hardcoded' in the script and should not be changed. You still are in liberty to repurpose them to a likewise purpose, as long as you don't change the name or unit. E.G.: if you import sheep manure instead of chicken manure, you can simply put you statistics for everything pertaining sheep manure into all fields pertaining chicken manure. That way in everything but name you'd have the import of sheep manure implemented.
- All cells/rows highlighted in green are 'softcoded' and can either be renamed, or extended with additional entries. More on that later. 
- Some cells will contain a red corner, when hovering over them you will reveal a note with additional information pertaining to that cell. 
- All other (white) cells can be freely edited to contain the statistics as the are present on your farm. If the program regards a statistic that is not present on your farm, you can most likely put the value to 0 without much hinderance.

### the estate sheet:
The estate sheet contains all properties the pretain to your estate and all other properties of a singular value.

#### on crop rotations:
Say you have a piece of farmland that for some years serves the purpose for cropping land, and for other years serves the purpose for animal pastures. Since the core loop of the script only accounts for one year of time, you'd have to seperate that piece of farmland into yearly averages of occupancy.

E.G.: If you have 100 Ha of farmland that would rotate between three years of cropping, and two years of animal pastures. Then for each year of operation you'd virtually have 60 Ha of cropping land, and 40 Ha of animal pastures. These statistics should be supplied to the estate sheet as such.

#### on animal ratios:
The way the script is implemented the animal ratios (newborn, female, and male) only act as a desired ratio. This means that the actual numbers will vary but try to be as close as the ratio as possible. E.G.: in the example scenario for each fertile male the amount of fertile females would vary between 10 and 30 with a median of 24.

### the crops sheet:
In addition to the first two golden columns the estate sheet had, the crops sheet also has the first row green. This row contains all the different kinds of crops your farm might cultivate. You can freely add and remove crops in this sheet to fit your farm's opperations.

For each crop you indicate how much of it you'd like to cultivate in both `grassland_ratio` and `cropping_ratio` respectively. This can be done in total hectare amount, or percentage, or any onther number that would indicate the ratio in which amount each crop is cultivated. These ratios will be applied to the grassland and cropping land amounts you indicated in the estate sheet.

The crop yield for kilogram per hectare you can specify in the `yield_DM` row. We recommand using 'dry matter' wheight for all relevant variables, however you could use soley 'fresh matter' wheights or maybe even mix and match as long as you are able to keep all values consisten between all relevant variables.

In row five through nine you get to specify the different purposes your harvested crops can fulfill. The way the script works is that it will first assign valid crops to bedding, then to animal feed, followed by bioprocessor, mulch, and finally sales. A crop can thus fulfill multiple purposes and will be assigned in this order as needed on the farm. E.G.: If the harvest contains 100 Kg `oat feed grain` and 30 Kg would be needed to feed the animals, then 30 Kg will be fed and the remaining 70 Kg will be sold.

In the remaining rows you get to specify more direct statistics of all farm crops.

#### on compound crop products:
In real life it is normal that that one crops yields mutiple different kinds of products E.G.: grains and straws. This poses a problem to the script, since to the script one single crop is synonymous to one single product. This means you'd have to manually divide all different crops products a crop would yield over the area that crop would occupy. 

We will give an example on how this is done: Say you're growing wheat on your farm and one hectare of farmland for wheat yields 1200 Kg of grain and 1800 Kg of straw. Then you can say that one hectare of wheat farland produces 1200 + 1800 = 3000 Kg of products.
Within that hectare 1200 / 3000 = 0.4 Ha would be responsible for growing grain and likewise 1800 / 3000 = 0.6 Ha would be responsible for growing straw. This 0.4 : 0.6 is the ratio in which you will have to assing grain and hay to the amount of Ha wheat occupies. The yield of each seperate product will be the same as the yield total of wheat, which is 3000 Kg in this example. So if you're growing 200 Ha of wheat on your farm you'd have to note this as if you're growing 200 * 0.4 = 80 Ha of wheat grain on your farm, with a yield of 3000 Kg per hectare, and likewise you'd be growing 200 * 0.6 = 120 Ha of wheat straw with a yield of 3000 Kg per hectare.

### the animal sheet:
The animal sheet has again the first two columns golden and uneditable, and the first row green and editable. However the amount the first row can be edited is quite more restrictive than the crops sheet. The script is only made to simulate the presence of one species of animal of the farm, be it cow, or sheep, or horse the specific species does not matter. This species of farm animals will be divided into three categories, male, female, and castrated. The option of customization here is soley the different amlunt of ages you'd like to allow these categories to be on your farm. Say you want castrated animals age 3 and 4 also to be present on the farm, than you can simply add two columns to the sheet in the same name format of `male_castrated_x_year` where x of course is the age you'd like to add. The script automatically assumes that if an animal reaches an age that is not present in the sheet it will be sent off to slaughter.

#### on fertility:
The script only assigns fertile males and fertile females to the male / female ratio. The script considers an animal to be fertile if its `fertility rate` is set to be larger than 0. Castrated males are always considered to be infertile, but it still looks good to assing their `fertility rate` to 0 for sanity purposes. For females if their `fertility rate` is set between 0 and 1 then this signifies their chance to produce offspring at that age. E.G.: If you have 30 one year old females with a fertility rate of 0.6 that would mean that those females would produce 30 * 0.6 = 18 offspring. The script assumes that any female that does not produce offspring is infertile, It also considers these females to not be worthwhile and thus they will be send off to slaughter. Thus of these 30 one year old females 30 * 0.4 = 12 would be send off to slaughter, and only 30 * 0.6 = 18 would be aged to an age of two years.

### the biodigestor sheet:
Again in the biodigestor sheet the first two columns are golden and should not be altered. On top of this the first three entries in the first row are also hard coded. chicken and horse manure rever to the same named entries as in the estate sheet. deep litter is and animal waste product as specified in the animal sheet. Beyond this all the green entries in this row should be exact matches as the first row entries present in the crops sheet. The biodigestor sheet is quite simple as that it only indicates which product certain types of matter would yield if they were put into the biodigestor.
