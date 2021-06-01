import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from scipy.interpolate import spline 

# saved file name
name = "allRequests"

# collected from RT tickets, per month/year for all requests and sw-related
sw2019  = [18,17,20,20,23,25,29,35,27,30,10,11] 
a2019   = [125,95,208,175,128,97,148,157,121,148,76,73]
sw2020  = [19,23,11,25,18,16,11,15,23,11,23,20] 
a2020   = [138,118,125,160,116,103,105,117,113,108,135,112]
sw2021  = [28,22,21,16,7]   
a2021   = [228,163,136,157,86]

# points and labels for x-axis
total_m = len(sw2019) + len(sw2020) + len(sw2021) + 1
x = np.array(range(1,total_m)) #  months for 2019-2020-2021 (not full)
xlabels = ['2019-01','201902','2019-03','2019-04','2019-05','2019-06',
           '2019-07','2019-08','2019-09','2019-10','2019-11','2019-12',
           '2020-01','2020-02','2020-03','2020-04','2020-05','2020-06',
		   '2020-07','2020-08','2020-09','2020-10','2020-11','2020-12',
           '2021-01','2021-02','2021-03','2021-04','2021-05'
		  ]
# data points 
y1 = sw2019 + sw2020 + sw2021 # sw requests per month
y2 = a2019 + a2020 + a2021    # all requests per month
# smooth data over 300 points
x_smooth = np.linspace(x.min(), x.max(), 300)
y1_smooth = spline(x, y1, x_smooth)
y2_smooth = spline(x, y2, x_smooth)

# symbols and lines 
c2 = 'blue'  
c1 = 'crimson'
a = 0.4  #alpha
marker = '^'

# plot data
plt.plot(x_smooth,y2_smooth, label='all tickets', color=c2)
plt.plot(x, y2, marker, color=c2, alpha=a)
plt.plot(x_smooth,y1_smooth, label='software tickets', color=c1)
plt.plot(x, y1, marker, color=c1, alpha=a)

# set plot properties
plt.xlabel("Time", fontsize=14)
plt.ylabel("Number of requests", fontsize=14)
plt.title("RT tickets") 
plt.xticks(x-1, xlabels, rotation=15, fontsize=10)
yticks = range(1,int(max(y2)/10+5))
yticks = np.asarray(yticks) * 10
plt.yticks(yticks)
plt.grid(True)
plt.xlim(x[0]-0.25, x[-1]+0.25)
plt.ylim(0, (max(y2)/10+1)*10)
ytick_spacing = 20
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(ytick_spacing))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(5))

# make every 3rd label visible on xaxis
visible_labels = [lab for lab in plt.gca().get_xticklabels() if lab.get_visible() is True and lab.get_text() != '']
for i in range(len(x)):
    if x[i] % 3 : plt.setp(visible_labels[i], visible=False)
plt.legend(loc="best") # plot legend

# set axes params
params = {"axes.titleweight":"bold", 
          "figure.facecolor": (1.0, 1.0, 1.0, 1.0),
		  "axes.facecolor":(1.0, 1.0, 1.0, 1.0),
		  "axes.labelsize" : "small",
		  "axes.titlepad": 20,
		 }
plt.rcParams.update(params)
plt.subplots_adjust(bottom=0.12)  # gives space below xaxis title

# show and save
#plt.show()
plt.savefig("%s.png" % name)

#plt.rcParams.keys() # how to get all params names
