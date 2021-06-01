import matplotlib.pyplot as plt
import numpy as np

name = "swRequests"
# collected from RT tickets, per month/year
y1 = [18,17,20,20,23,25,29,35,27,30,10,11] # 2019
y2 = [19,23,11,25,18,16,11,15,23,11,23,20] # 2020
y3 = [28,22,21,16,7]                       # 2021

# points  and labels for x-axis
#i = [1,2,3,4,5,6,7,8,9,10,11,12]
x = np.array(range(1,13)) #  months 1:12
xlabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# bars colors by year
c1 = 'darkviolet'     # 2019
c2 = 'deepskyblue'    # 2020
c3 = 'crimson'        # 2021

# plot data
fig, ax = plt.subplots()

width = 0.25 # bar width
b1 = plt.bar(x, y1, width, color=c1, label="2019")
b2 = plt.bar(x+width, y2, width, color=c2,  label="2020")
b3 = plt.bar(x[0:5]+width*2, y3, width, color=c3,label="2021")

# set plot properties
plt.xticks(x+width*1.5, xlabels)
yticks = range(1,int(max(y1+y2+y3)/5+2))
yticks = np.asarray(yticks) * 5
plt.yticks(yticks)
plt.grid(axis='y', alpha=1.0)
plt.xlim(x[0]-0.5, x[-1]+1)
plt.xlabel("Time", fontsize=14)
plt.ylabel("Number of requests", fontsize=14)

# plot legend
yl = ["2019 (%d)" % sum(y1), "2020 (%d)" % sum(y2), "2021 (%d)" % sum(y3)]
plt.legend(yl)

# set axes params
params = {"axes.titleweight":"bold", 
          "figure.facecolor": (1.0, 1.0, 1.0, 1.0),
		  "axes.facecolor":(1.0, 1.0, 1.0, 1.0)}
          #"axes.labelcolor":'blue',
plt.rcParams.update(params)

#ax.bar_label(b1, padding=3)
#ax.bar_label(b2, padding=3)
#ax.bar_label(b3, padding=3)

# show and save
#plt.show()
plt.savefig("%s.png" % name)

# how to get all params names
#plt.rcParams.keys()
