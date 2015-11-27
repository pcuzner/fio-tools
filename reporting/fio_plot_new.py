__author__ = 'paul'

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


data={u'fio-clone-33s': [None, None, None, None, None, None, 79360, 84480, 109056], u'fio-clone-32s': [None, None, None, 37632, 44288, 56064, 86528, 144384, 86528], u'fio-clone-35s': [None, None, None, None, 54016, 69120, 74240, 103936, 168960], u'fio-clone-34s': [None, 24960, 27008, 33536, 43776, 103936, 39680, 31616, 48896], u'fio-clone-39s': [None, None, None, None, None, None, None, None, 114176], u'fio-clone-38s': [None, None, None, None, None, 79360, 100864, 113152, 101888], u'fio-clone-37s': [None, None, 30080, 31616, 51968, 61696, 120320, 47360, 38144], u'fio-clone-36s': [None, None, None, None, None, None, None, 103936, 113152], u'fio-clone-31s': [21376, 22144, 23168, 31360, 114176, 57600, 62208, 44288, 54528]}
data['Latency Ceiling (50ms)']=[50000]*9
x=[1,2,3,4,5,6,7,8,9]
xtickmarks=['1 job', '2 jobs', '3 jobs', '4 jobs', '5 jobs', '6 jobs', '7 jobs', '8 jobs', '9 jobs']


# set defaults for the figure facecolor in the interactive window and saved files to white
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['savefig.facecolor'] = 'white'
fig, ax = plt.subplots()
fig.set_size_inches(13,8)

plt.title("fio title")
plt.xticks(x, xtickmarks)
plt.ylabel("response time(usec)")
plt.xlabel("fio Job count")


plot_color=iter(plt.cm.Set1(np.linspace(0,1,12)))
for key in sorted(data):
    c=next(plot_color)
    lwidth=1
    if key.startswith('Latency'):
        lwidth=2
        c='r'
    ax.plot(x,data[key],c=c,linewidth=lwidth,label=key)


box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1,0.5),frameon=False)

plt.show()
#plt.savefig('myfile.png')


