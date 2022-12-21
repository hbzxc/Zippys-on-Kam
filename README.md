# Zippys-on-Kam
 
I made this program in two days instead of studying for a final.

Is it useful? Not really and it only works with locations on Oahu.

There are currently no air travel directions just driving instructions.

Why did I make this? I thought it would be funny.

This program was created using python, beautiful soup to scrape websites, plotly to visualize the data, and Bing maps get the geographic coordinates from the restaurant addresses.

Try it out: https://zippys_on_kam-hblazier.pythonanywhere.com/

How it works:

The program first scrapes the [Zippys](https://www.zippys.com/) website for a list of locations. It will then check each location to get an address, check if it is open, and record a list of service provided at each location.

Then these address are geocoded using Bing maps to get a coordinate.

Bing maps is also used to get directions between two sets of coordinates, provided a distance, drive time and traffic estimate.

The resulting coordinates are plotted and everything is mapped using plotly and mapbox.

<img class="ui image" src="https://github.com/hbzxc/hbzxc.github.io/blob/master/images/Zippys_on_Kam.PNG">
